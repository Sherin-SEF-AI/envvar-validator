"""
File exporters for env-validator.
"""

import json
import yaml
import toml
from typing import Dict, Any


def export_to_dotenv(data: Dict[str, Any], file_path: str) -> None:
    """Export data to a .env file."""
    with open(file_path, 'w') as f:
        for key, value in data.items():
            f.write(f"{key}={value}\n")


def export_to_yaml(data: Dict[str, Any], file_path: str) -> None:
    """Export data to a YAML file."""
    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)


def export_to_json(data: Dict[str, Any], file_path: str) -> None:
    """Export data to a JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def export_to_toml(data: Dict[str, Any], file_path: str) -> None:
    """Export data to a TOML file."""
    with open(file_path, 'w') as f:
        toml.dump(data, f) 