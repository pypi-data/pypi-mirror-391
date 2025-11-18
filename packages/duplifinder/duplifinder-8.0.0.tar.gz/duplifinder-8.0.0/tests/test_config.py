# tests/test_config.py

"""Tests for Config validation."""

import pytest
from pathlib import Path
from duplifinder.config import Config, load_config_file


def test_valid_config_creation():
    """Test valid Config instantiation."""
    config = Config(root=Path("."), types_to_search={"class"})
    assert config.root == Path(".")
    assert config.types_to_search == {"class"}
    assert 0.0 <= config.similarity_threshold <= 1.0


def test_invalid_types_validation():
    """Test unsupported types raise ValueError."""
    with pytest.raises(ValueError, match="Unsupported types"):
        Config(types_to_search={"invalid"})


def test_regex_validation():
    """Test invalid regex raises ValueError."""
    with pytest.raises(ValueError, match="Invalid regex"):
        Config(pattern_regexes="[unclosed]") # Invalid regex


def test_search_specs_validation():
    """Test invalid search specs raise ValueError."""
    with pytest.raises(ValueError, match="Must be 'type name'"):
        Config(search_specs=["class"])  # Bare type

    with pytest.raises(ValueError, match="Invalid type"):
        Config(search_specs=["invalid Foo"])


def test_load_config_file_valid(tmp_path: Path):
    """Test loading valid YAML."""
    yaml_file = tmp_path / ".duplifinder.yaml"
    yaml_file.write_text("root: .\ntypes_to_search: [class]")
    config_dict = load_config_file(yaml_file)
    assert config_dict["root"] == "."
    assert config_dict["types_to_search"] == ["class"]


def test_load_config_file_invalid(tmp_path: Path):
    """Test loading invalid YAML raises ValueError."""
    yaml_file = tmp_path / "invalid.yaml"
    yaml_file.write_text("invalid: yaml: syntax")
    with pytest.raises(ValueError, match="Failed to load config"):
        load_config_file(yaml_file)
