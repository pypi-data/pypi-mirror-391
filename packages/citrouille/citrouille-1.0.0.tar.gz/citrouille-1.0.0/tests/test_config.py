import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

from citrouille.config import load_config, resolve_namespace, get_config_path


class TestConfigPath:
    #
    # test_get_config_path
    # Tests that config path is correctly constructed
    #
    def test_get_config_path(self):
        path = get_config_path()
        assert path == Path.home() / ".config" / "citrouille" / "config.yaml"
        assert isinstance(path, Path)


class TestLoadConfig:
    #
    # test_load_config_file_not_found
    # Tests that missing config file returns empty dict without error
    #
    def test_load_config_file_not_found(self):
        with patch("citrouille.config.get_config_path") as mock_path:
            mock_path.return_value = Path("/nonexistent/config.yaml")
            config = load_config()
            assert config == {}

    #
    # test_load_config_valid_yaml
    # Tests loading a valid YAML configuration file
    #
    def test_load_config_valid_yaml(self):
        valid_yaml = """
kubeconfig: /path/to/kubeconfig
namespaces:
  prod: production
  stg: staging
"""
        with patch("citrouille.config.get_config_path") as mock_path:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                f.write(valid_yaml)
                temp_path = Path(f.name)

            try:
                mock_path.return_value = temp_path
                config = load_config()

                assert config["kubeconfig"] == "/path/to/kubeconfig"
                assert config["namespaces"]["prod"] == "production"
                assert config["namespaces"]["stg"] == "staging"
            finally:
                temp_path.unlink()

    #
    # test_load_config_empty_file
    # Tests that empty YAML file returns empty dict
    #
    def test_load_config_empty_file(self):
        with patch("citrouille.config.get_config_path") as mock_path:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                f.write("")
                temp_path = Path(f.name)

            try:
                mock_path.return_value = temp_path
                config = load_config()
                assert config == {}
            finally:
                temp_path.unlink()

    #
    # test_load_config_invalid_yaml
    # Tests that invalid YAML returns empty dict with warning
    #
    def test_load_config_invalid_yaml(self):
        invalid_yaml = """
kubeconfig: /path
  invalid: yaml: structure
    - broken
"""
        with patch("citrouille.config.get_config_path") as mock_path:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                f.write(invalid_yaml)
                temp_path = Path(f.name)

            try:
                mock_path.return_value = temp_path
                config = load_config()
                assert config == {}
            finally:
                temp_path.unlink()

    #
    # test_load_config_non_dict_yaml
    # Tests that YAML with non-dict content returns empty dict
    #
    def test_load_config_non_dict_yaml(self):
        non_dict_yaml = """
- item1
- item2
- item3
"""
        with patch("citrouille.config.get_config_path") as mock_path:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                f.write(non_dict_yaml)
                temp_path = Path(f.name)

            try:
                mock_path.return_value = temp_path
                config = load_config()
                assert config == {}
            finally:
                temp_path.unlink()


class TestResolveNamespace:
    #
    # test_resolve_namespace_with_alias
    # Tests that namespace alias is correctly resolved
    #
    def test_resolve_namespace_with_alias(self):
        config = {"namespaces": {"prod": "production", "stg": "staging"}}

        assert resolve_namespace("prod", config) == "production"
        assert resolve_namespace("stg", config) == "staging"

    #
    # test_resolve_namespace_without_alias
    # Tests that non-aliased namespace is returned unchanged
    #
    def test_resolve_namespace_without_alias(self):
        config = {"namespaces": {"prod": "production"}}

        assert resolve_namespace("default", config) == "default"
        assert resolve_namespace("kube-system", config) == "kube-system"

    #
    # test_resolve_namespace_no_namespaces_section
    # Tests that namespace is returned unchanged when no namespaces section exists
    #
    def test_resolve_namespace_no_namespaces_section(self):
        config = {"kubeconfig": "/path/to/config"}

        assert resolve_namespace("production", config) == "production"
        assert resolve_namespace("default", config) == "default"

    #
    # test_resolve_namespace_empty_config
    # Tests that namespace is returned unchanged with empty config
    #
    def test_resolve_namespace_empty_config(self):
        config = {}

        assert resolve_namespace("production", config) == "production"
        assert resolve_namespace("default", config) == "default"

    #
    # test_resolve_namespace_invalid_namespaces_section
    # Tests that namespace is returned unchanged when namespaces section is invalid
    #
    def test_resolve_namespace_invalid_namespaces_section(self):
        config = {"namespaces": "not-a-dict"}

        assert resolve_namespace("production", config) == "production"

    #
    # test_resolve_namespace_case_sensitive
    # Tests that namespace alias resolution is case-sensitive
    #
    def test_resolve_namespace_case_sensitive(self):
        config = {"namespaces": {"prod": "production"}}

        assert resolve_namespace("prod", config) == "production"
        assert resolve_namespace("Prod", config) == "Prod"
        assert resolve_namespace("PROD", config) == "PROD"

    #
    # test_resolve_namespace_complex_aliases
    # Tests resolving complex namespace names
    #
    def test_resolve_namespace_complex_aliases(self):
        config = {
            "namespaces": {
                "prod": "microservices-production-us-east-1",
                "stg": "microservices-staging-us-west-2",
                "dev": "microservices-development",
            }
        }

        assert resolve_namespace("prod", config) == "microservices-production-us-east-1"
        assert resolve_namespace("stg", config) == "microservices-staging-us-west-2"
        assert resolve_namespace("dev", config) == "microservices-development"
