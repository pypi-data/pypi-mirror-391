import sys
from pathlib import Path
from typing import Dict, Any

try:
    import yaml
except ImportError:
    yaml = None

#
# config.py
#
# This file handles loading and parsing the .citrouille configuration file
# Configuration provides:
# - Default kubeconfig path
# - Namespace aliases (user-friendly names for actual namespaces)
#


def get_config_path() -> Path:
    return Path.home() / ".config" / "citrouille" / "config.yaml"


def load_config() -> Dict[str, Any]:
    if yaml is None:
        print(
            "Warning: PyYAML not installed. Config file support disabled.",
            file=sys.stderr,
        )
        return {}

    config_path = get_config_path()

    if not config_path.exists():
        # No config file is fine - return empty config
        return {}

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            if config is None:
                # Empty YAML file
                return {}
            if not isinstance(config, dict):
                print(
                    f"Warning: Invalid config file format at {config_path}. "
                    "Expected YAML dictionary.",
                    file=sys.stderr,
                )
                return {}
            return config
    except yaml.YAMLError as e:
        print(
            f"Warning: Failed to parse config file at {config_path}: {e}",
            file=sys.stderr,
        )
        return {}
    except Exception as e:
        print(
            f"Warning: Failed to load config file at {config_path}: {e}",
            file=sys.stderr,
        )
        return {}


# namespace aliases
def resolve_namespace(namespace: str, config: Dict[str, Any]) -> str:
    if "namespaces" not in config:
        return namespace

    namespaces = config["namespaces"]
    if not isinstance(namespaces, dict):
        return namespace

    return namespaces.get(namespace, namespace)
