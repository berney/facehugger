import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from facehugger.facehugger import build_hf_command


def test_build_hf_command_basic():
    """Test basic command building without optional parameters."""
    result = build_hf_command("owner/model-repo")
    expected = "hf download owner/model-repo"
    assert result == expected


def test_build_hf_command_with_ref():
    """Test command building with revision/ref parameter."""
    result = build_hf_command("owner/model-repo", ref="main")
    expected = "hf download owner/model-repo@main"
    assert result == expected


def test_build_hf_command_with_include():
    """Test command building with include parameter as string."""
    result = build_hf_command("owner/model-repo", include="*.gguf")
    expected = "hf download owner/model-repo --include *.gguf"
    assert result == expected


def test_build_hf_command_with_exclude():
    """Test command building with exclude parameter as string."""
    result = build_hf_command("owner/model-repo", exclude="*.ckpt")
    expected = "hf download owner/model-repo --exclude *.ckpt"
    assert result == expected


def test_build_hf_command_with_include_and_exclude():
    """Test command building with both include and exclude parameters."""
    result = build_hf_command("owner/model-repo", include="*.gguf", exclude="*.ckpt")
    expected = "hf download owner/model-repo --include *.gguf --exclude *.ckpt"
    assert result == expected


def test_build_hf_command_with_ref_and_include():
    """Test command building with ref and include parameters."""
    result = build_hf_command("owner/model-repo", ref="main", include="*.gguf")
    expected = "hf download owner/model-repo@main --include *.gguf"
    assert result == expected


def test_build_hf_command_with_include_list():
    """Test command building with include parameter as list."""
    result = build_hf_command("owner/model-repo", include=["*.gguf", "*.safetensors"])
    expected = "hf download owner/model-repo --include *.gguf --include *.safetensors"
    assert result == expected


def test_build_hf_command_with_exclude_list():
    """Test command building with exclude parameter as list."""
    result = build_hf_command("owner/model-repo", exclude=["*.ckpt", "*.bin"])
    expected = "hf download owner/model-repo --exclude *.ckpt --exclude *.bin"
    assert result == expected


def test_build_hf_command_with_all_parameters():
    """Test command building with all parameters."""
    result = build_hf_command(
        "owner/model-repo", ref="main", include="*.gguf", exclude="*.ckpt"
    )
    expected = "hf download owner/model-repo@main --include *.gguf --exclude *.ckpt"
    assert result == expected
