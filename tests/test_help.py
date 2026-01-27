from unittest.mock import patch
from io import StringIO
from facehugger.facehugger import main


def test_main_help_flag():
    """Test that main function handles --help flag correctly."""
    # Capture stdout and stderr
    stdout_capture = StringIO()
    stderr_capture = StringIO()

    with patch("sys.argv", ["facehugger", "--help"]):
        with patch("sys.stdout", stdout_capture):
            with patch("sys.stderr", stderr_capture):
                try:
                    main()
                    # If we get here, main() completed successfully
                    assert True
                except SystemExit as e:
                    # SystemExit is expected when --help is used
                    # Check that exit code is 0 (success)
                    assert e.code == 0
                    # Check that help text was printed to stdout
                    help_output = stdout_capture.getvalue()
                    assert (
                        "Download models defined in a facehugger.yaml manifest file"
                        in help_output
                    )
                    assert "--help" in help_output
                    assert "--version" in help_output
                    assert "--dry-run" in help_output
