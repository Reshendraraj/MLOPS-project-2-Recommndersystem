import os
from src.logger import get_logger
from src.custom_exception import CustomException
import yaml
import pandas as pd

logger = get_logger(__name__)

def read_yaml(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File is not in the given path: {file_path}")

        with open(file_path, "r") as yaml_file:
            config = yaml.safe_load(yaml_file)
            logger.info(f"Successfully read the YAML file from: {file_path}")
            return config if config is not None else {}  # Return {} if config is None

    except FileNotFoundError as e:
        logger.error(f"Error: File not found at {file_path}")
        raise CustomException(f"Failed to read YAML file: File not found at {file_path}", e)

    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file at {file_path}: {e}")
        raise CustomException(f"Failed to read YAML file: Error parsing YAML at {file_path}", e)

    except Exception as e:
        logger.error(f"An unexpected error occurred while reading YAML at {file_path}: {e}")
        raise CustomException(f"Failed to read YAML file: Unexpected error at {file_path}", e)
