"""
File loaders for env-validator.
"""

import os
import json
import yaml
import toml
from pathlib import Path
from typing import Dict, Any


def load_dotenv(file_path: str) -> Dict[str, str]:
    """Load environment variables from a .env file."""
    result = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                result[key.strip()] = value.strip()
    return result


def load_yaml(file_path: str) -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def load_json(file_path: str) -> Dict[str, Any]:
    """Load configuration from a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def load_toml(file_path: str) -> Dict[str, Any]:
    """Load configuration from a TOML file."""
    with open(file_path, 'r') as f:
        return toml.load(f)


def load_environment_file(file_path: str) -> Dict[str, Any]:
    """Load configuration from any supported file format."""
    path = Path(file_path)
    if path.suffix.lower() in ['.yaml', '.yml']:
        return load_yaml(file_path)
    elif path.suffix.lower() == '.json':
        return load_json(file_path)
    elif path.suffix.lower() == '.toml':
        return load_toml(file_path)
    elif path.suffix.lower() == '.env':
        return load_dotenv(file_path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}") 