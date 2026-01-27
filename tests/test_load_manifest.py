import tempfile
import os
from pathlib import Path
import pytest
import yaml

from facehugger.facehugger import load_manifest
from facehugger.models import FacehuggerManifest


def test_load_manifest_file_exists():
    """Test that load_manifest reads and parses a valid YAML manifest file."""
    # Create a temporary manifest file
    manifest_content = {
        "models": [
            {
                "repo": "test/model1",
                "ref": "main",
                "include": "*.gguf",
                "exclude": "*.ckpt",
            },
            {"repo": "test/model2", "ref": "v1.0"},
        ]
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(manifest_content, f)
        temp_file_path = f.name

    try:
        # Test loading the manifest
        result = load_manifest(Path(temp_file_path))

        # Verify the result is a FacehuggerManifest instance
        assert isinstance(result, FacehuggerManifest)
        assert len(result.models) == 2

        # Check first model
        assert result.models[0].repo == "test/model1"
        assert result.models[0].ref == "main"
        assert result.models[0].include == "*.gguf"
        assert result.models[0].exclude == "*.ckpt"

        # Check second model
        assert result.models[1].repo == "test/model2"
        assert result.models[1].ref == "v1.0"
        assert result.models[1].include is None
        assert result.models[1].exclude is None

    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


def test_load_manifest_empty_file():
    """Test that load_manifest handles an empty manifest file."""
    # Create a temporary empty manifest file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("")
        temp_file_path = f.name

    try:
        # Test loading the empty manifest
        with pytest.raises(
            SystemExit, match="Facehugger manifest .* failed validation"
        ):
            load_manifest(Path(temp_file_path))
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


def test_load_manifest_models_key_empty():
    """Test that load_manifest handles an empty manifest key."""
    # Create a temporary empty manifest file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("models:\n")
        temp_file_path = f.name

    try:
        # Test loading the empty manifest
        with pytest.raises(
            SystemExit, match="Facehugger manifest .* failed validation"
        ):
            load_manifest(Path(temp_file_path))
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


def test_load_manifest_models_key_empty_no_nl():
    """Test that load_manifest handles an empty manifest key (no new line)."""
    # Create a temporary empty manifest file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("models:")
        temp_file_path = f.name

    try:
        # Test loading the empty manifest
        with pytest.raises(
            SystemExit, match="Facehugger manifest .* failed validation"
        ):
            load_manifest(Path(temp_file_path))
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


def test_load_manifest_no_models_key():
    """Test that load_manifest handles a manifest without models key."""
    # Create a temporary manifest file without models key
    manifest_content = {"other_key": "other_value"}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(manifest_content, f)
        temp_file_path = f.name

    try:
        with pytest.raises(
            SystemExit, match="Facehugger manifest .* failed validation"
        ):
            # Test loading the manifest
            load_manifest(Path(temp_file_path))
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


def test_load_manifest_invalid_yaml():
    """Test that load_manifest exits when manifest file contains invalid YAML."""
    # Create a temporary manifest file with invalid YAML
    invalid_yaml_content = """
models:
  - repo: test/model1
    ref: main
  - repo: test/model2
    ref: v1.0
invalid: yaml: content:
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(invalid_yaml_content)
        temp_file_path = f.name

    try:
        with pytest.raises(SystemExit, match="Failed to parse manifest file"):
            load_manifest(Path(temp_file_path))

    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)


def test_load_manifest_file_not_exists():
    """Test that load_manifest exits when manifest file does not exist."""
    # Create a Path object for a file that definitely doesn't exist
    # We can use a path in a non-existent directory to ensure it won't exist
    non_existing_file = Path("/tmp/facehugger_nonexistent_file_12345.yaml")

    # Verify the file doesn't exist (this is just a sanity check)
    assert not non_existing_file.exists()

    with pytest.raises(SystemExit, match="Manifest file not found"):
        load_manifest(non_existing_file)
