import subprocess
import sys
from unittest.mock import patch
from importlib.metadata import version

from facehugger.facehugger import main


def test_version_command():
    """Test that --version prints the package version."""
    # Test the CLI version command
    result = subprocess.run(
        [sys.executable, "-m", "facehugger.facehugger", "--version"],
        capture_output=True,
        text=True,
        cwd=".",
    )

    # Check that the command succeeded
    assert result.returncode == 0

    # Check that output is not empty
    assert result.stdout.strip() != ""

    # Verify the version matches what importlib.metadata returns
    try:
        expected_version = version("facehugger")
    except Exception:
        # If we can't get version from metadata, expect "0.0.0"
        expected_version = "0.0.0"

    assert result.stdout.strip() == expected_version


def test_main_version_flag():
    """Test that main function handles --version flag correctly."""
    with patch("sys.argv", ["facehugger", "--version"]):
        with patch("sys.stdout") as mock_stdout:
            expected_version = version("facehugger")
            # This should not raise an exception and should print version
            try:
                main()
                # If we get here, main() completed successfully
                # Check that the version was printed to stdout (print adds a newline automatically)
                # The print() function calls write twice: once for the version and once for the newline
                mock_stdout.write.assert_any_call(expected_version)
                mock_stdout.write.assert_any_call("\n")
            except SystemExit:
                # SystemExit is expected when --version is used
                # Check that the version was still printed to stdout before exiting
                # The print() function calls write twice: once for the version and once for the newline
                mock_stdout.write.assert_any_call(expected_version)
                mock_stdout.write.assert_any_call("\n")
