"""
Calculate Clinical Scores Pipeline Step

This module provides a Luigi pipeline task for calculating clinical scores
(e.g., MAGGIC, AUDIT, etc.) and adding them as columns to a dataset.

The task reads an input dataset, applies column name mappings from a configuration
file, calculates the specified score, and adds the results as new columns to the dataset.

This module is located at: dpplgngr/etl/calculate_scores.py

Author: SB
Date: 2025-10-30
"""

import pandas as pd
import numpy as np
import logging
import json
import os

# Try to import luigi, fallback to replacement if not available
try:
    import luigi
    _using_luigi_replacement = False
except ImportError:
    from dpplgngr.utils.luigi_replacement import Task, Parameter, LocalTarget, build as luigi_build
    # Create a mock luigi module for compatibility
    class MockLuigi:
        Task = Task
        Parameter = Parameter
        LocalTarget = LocalTarget
        
        @staticmethod
        def build(*args, **kwargs):
            return luigi_build(*args, **kwargs)
    
    luigi = MockLuigi()
    _using_luigi_replacement = True

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Available score calculators
AVAILABLE_SCORES = {
    'maggic': 'dpplgngr.scores.maggic.calculateMAGGIC',
    'audit': 'dpplgngr.scores.audit.calculateAUDIT',
    # Add more scores here as they become available
}


def get_score_calculator(score_name):
    """
    Dynamically import and return the score calculation function.
    
    Parameters
    ----------
    score_name : str
        Name of the score to calculate (e.g., 'maggic', 'audit')
    
    Returns
    -------
    callable
        The score calculation function
    
    Raises
    ------
    ValueError
        If the score is not available
    ImportError
        If the score module cannot be imported
    """
    if score_name.lower() not in AVAILABLE_SCORES:
        raise ValueError(
            f"Score '{score_name}' is not available. "
            f"Available scores: {list(AVAILABLE_SCORES.keys())}"
        )
    
    module_path = AVAILABLE_SCORES[score_name.lower()]
    module_name, func_name = module_path.rsplit('.', 1)
    
    try:
        import importlib
        module = importlib.import_module(module_name)
        score_func = getattr(module, func_name)
        return score_func
    except (ImportError, AttributeError) as e:
        raise ImportError(
            f"Failed to import score calculator '{score_name}' from {module_path}: {e}"
        )


class CalculateScores(luigi.Task):
    """
    Luigi task to calculate clinical scores and add them as columns to a dataset.
    
    This task:
    1. Reads an input dataset (CSV, Parquet, or Feather)
    2. Loads score configuration with column mappings
    3. Calculates the specified score(s)
    4. Adds score results as new columns
    5. Saves the augmented dataset
    
    Parameters
    ----------
    input_file : str
        Path to the input dataset file
    output_file : str
        Path to save the output dataset with scores
    score_config : str
        Path to the JSON configuration file specifying:
        - score_name: Name of the score to calculate
        - column_mapping: Dictionary mapping score variables to dataset columns
    
    Example Configuration (score_config.json)
    ------------------------------------------
    {
        "score_name": "maggic",
        "column_mapping": {
            "sex": "Female",
            "smoking": "CurrentSmoker",
            "hist_diabetes": "Diabetes",
            "hist_copd": "COPD",
            "recent_hf": "HeartFailure_18M",
            "betablocker": "Medication_BetaBlocker",
            "ace_arb": "Medication_ACE_ARB",
            "lvef": "LVEF_percent",
            "nyha": "NYHA_class",
            "creatinine": "Creatinine_umol_L",
            "bmi": "BMI",
            "sbp": "SystolicBP",
            "age": "Age_years"
        }
    }
    
    Multiple Scores Example
    -----------------------
    {
        "scores": [
            {
                "score_name": "maggic",
                "column_mapping": { ... }
            },
            {
                "score_name": "audit",
                "column_mapping": { ... }
            }
        ]
    }
    """
    
    input_file = luigi.Parameter()
    output_file = luigi.Parameter()
    score_config = luigi.Parameter()
    depends_on_task = luigi.Parameter(default='')  # Task type that this depends on
    depends_on_config = luigi.Parameter(default='')  # Config for the dependency task
    
    def output(self):
        """Define the output target for this task."""
        return luigi.LocalTarget(self.output_file)
    
    def requires(self):
        """Require the imputation task to complete before calculating scores."""
        if self.depends_on_task and self.depends_on_config:
            if self.depends_on_task == 'ApplyGraphImputer':
                from dpplgngr.train.graph_imputation import ApplyGraphImputer
                # Need to extract etl_config from the apply_config
                import json
                with open(self.depends_on_config, 'r') as f:
                    config = json.load(f)
                # Try to infer etl_config from the input_file path
                etl_config = config.get('etl_config', '')
                return ApplyGraphImputer(apply_config=self.depends_on_config, etl_config=etl_config)
            elif self.depends_on_task == 'AlternativeImputation':
                from dpplgngr.train.alternative_imputation import AlternativeImputation
                import json
                with open(self.depends_on_config, 'r') as f:
                    config = json.load(f)
                return AlternativeImputation(
                    input_file=config['input_file'],
                    output_dir=config['output_dir'],
                    imputation_strategies=config.get('imputation_strategies', 'median,mice'),
                    prefix=config.get('prefix', 'imputed'),
                    etl_config=config.get('etl_config', '')
                )
        return []
    
    def run(self):
        """Execute the score calculation pipeline."""
        logger.info(f"Starting score calculation task")
        logger.info(f"Input file: {self.input_file}")
        logger.info(f"Output file: {self.output_file}")
        logger.info(f"Score config: {self.score_config}")
        
        # Load the score configuration
        logger.info("Loading score configuration...")
        with open(self.score_config, 'r') as f:
            config = json.load(f)
        
        # Load the input dataset
        logger.info("Loading input dataset...")
        data = self._load_dataset(self.input_file)
        logger.info(f"Loaded dataset with shape: {data.shape}")
        logger.info(f"Dataset columns: {data.columns.tolist()}")
        
        # Check if we have single or multiple scores
        if 'scores' in config:
            # Multiple scores configuration
            score_configs = config['scores']
        elif 'score_name' in config:
            # Single score configuration
            score_configs = [config]
        else:
            raise ValueError(
                "Configuration must contain either 'score_name' (single score) "
                "or 'scores' (list of score configurations)"
            )
        
        # Calculate each score
        for score_config in score_configs:
            data = self._calculate_single_score(data, score_config)
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(self.output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Save the augmented dataset
        logger.info("Saving output dataset...")
        self._save_dataset(data, self.output_file)
        logger.info(f"Score calculation complete. Output saved to: {self.output_file}")
    
    def _load_dataset(self, file_path):
        """
        Load dataset from various file formats.
        
        Parameters
        ----------
        file_path : str
            Path to the dataset file
        
        Returns
        -------
        pd.DataFrame
            Loaded dataset
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.csv':
            return pd.read_csv(file_path)
        elif file_ext == '.parquet':
            return pd.read_parquet(file_path)
        elif file_ext == '.feather':
            return pd.read_feather(file_path)
        elif file_ext == '.json':
            return pd.read_json(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        else:
            raise ValueError(
                f"Unsupported file format: {file_ext}. "
                f"Supported formats: .csv, .parquet, .feather, .json, .xlsx, .xls"
            )
    
    def _save_dataset(self, data, file_path):
        """
        Save dataset to various file formats.
        
        Parameters
        ----------
        data : pd.DataFrame
            Dataset to save
        file_path : str
            Path to save the dataset
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.csv':
            data.to_csv(file_path, index=True)
        elif file_ext == '.parquet':
            data.to_parquet(file_path, index=True)
        elif file_ext == '.feather':
            data.reset_index().to_feather(file_path)
        elif file_ext == '.json':
            data.to_json(file_path, orient='records')
        elif file_ext in ['.xlsx', '.xls']:
            data.to_excel(file_path, index=True)
        else:
            raise ValueError(
                f"Unsupported file format: {file_ext}. "
                f"Supported formats: .csv, .parquet, .feather, .json, .xlsx, .xls"
            )
    
    def _calculate_single_score(self, data, score_config):
        """
        Calculate a single score and add it to the dataset.
        
        Parameters
        ----------
        data : pd.DataFrame
            Input dataset
        score_config : dict
            Configuration for a single score containing:
            - score_name: Name of the score
            - column_mapping: Mapping from score variables to dataset columns
        
        Returns
        -------
        pd.DataFrame
            Dataset with score columns added
        """
        score_name = score_config['score_name']
        column_mapping = score_config['column_mapping']
        
        logger.info(f"Calculating score: {score_name}")
        logger.info(f"Column mapping: {column_mapping}")
        
        # Validate that all required columns exist in the dataset
        missing_columns = [col for col in column_mapping.values() if col not in data.columns]
        if missing_columns:
            logger.warning(
                f"The following columns required for {score_name} are missing from the dataset: "
                f"{missing_columns}. Score will be calculated with missing values."
            )
        
        # Get the score calculation function
        try:
            score_func = get_score_calculator(score_name)
        except (ValueError, ImportError) as e:
            logger.error(f"Failed to load score calculator: {e}")
            raise
        
        # Calculate the score
        try:
            score_results = score_func(data, column_mapping)
            
            # Add score results to the original dataset
            # The score function should return a DataFrame with the same index
            for col in score_results.columns:
                if col in data.columns:
                    logger.warning(
                        f"Column '{col}' already exists in dataset. "
                        f"It will be overwritten with the calculated score."
                    )
                data[col] = score_results[col]
            
            logger.info(f"Successfully calculated {score_name}. Added columns: {score_results.columns.tolist()}")
            
        except Exception as e:
            logger.error(f"Error calculating score '{score_name}': {e}")
            raise
        
        return data


def calculate_scores_standalone(input_file, output_file, score_config):
    """
    Standalone function to calculate scores without Luigi.
    
    This function can be used directly in scripts or notebooks without
    requiring the Luigi workflow framework.
    
    Parameters
    ----------
    input_file : str
        Path to the input dataset file
    output_file : str
        Path to save the output dataset with scores
    score_config : str or dict
        Path to the JSON configuration file or configuration dictionary
    
    Returns
    -------
    pd.DataFrame
        Dataset with calculated scores
    
    Example
    -------
    >>> from dpplgngr.etl.calculate_scores import calculate_scores_standalone
    >>> 
    >>> config = {
    ...     "score_name": "maggic",
    ...     "column_mapping": {
    ...         "sex": "Female",
    ...         "age": "Age_years",
    ...         # ... other mappings
    ...     }
    ... }
    >>> 
    >>> result_df = calculate_scores_standalone(
    ...     input_file="data/patient_data.csv",
    ...     output_file="data/patient_data_with_scores.csv",
    ...     score_config=config
    ... )
    """
    task = CalculateScores(
        input_file=input_file,
        output_file=output_file,
        score_config=score_config if isinstance(score_config, str) else 'temp_config.json'
    )
    
    # If config is a dictionary, write it to a temporary file
    if isinstance(score_config, dict):
        with open('temp_config.json', 'w') as f:
            json.dump(score_config, f, indent=2)
    
    try:
        task.run()
        
        # Load and return the result
        return task._load_dataset(output_file)
    finally:
        # Clean up temporary config file if created
        if isinstance(score_config, dict) and os.path.exists('temp_config.json'):
            os.remove('temp_config.json')


if __name__ == '__main__':
    # Run the Luigi task when executed as a script
    luigi.run()
