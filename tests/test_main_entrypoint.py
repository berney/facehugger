#!/usr/bin/env python3
"""
Pytest-compatible test: Tests for the main entrypoint logic.
Detect if main() is called when module runs as __main__.
"""

import sys
import runpy


class MainCalled(Exception):
    """Exception raised when main() is detected."""

    pass


def test_module_can_be_run_as_script():
    """
    Test that main() is called when ran with __name__ == '__main__'.

    This test:
    - Uses sys.settrace() to detect when main() is about to execute
    - Uses runpy to execute with __name__ == '__main__'
    - Raises exception to prevent real main() from executing
    - Asserts that main() was detected

    No source reading. No patching. Just tracing.
    """
    detected = False

    def hook(frame, event, arg):
        """Trace hook that detects main() call."""
        nonlocal detected
        if event == "call" and frame.f_code.co_name == "main":
            if "facehugger.py" in frame.f_code.co_filename:
                detected = True
                raise MainCalled()
        return hook

    # Install trace hook
    sys.settrace(hook)

    try:
        # Run asdf.py with __name__ == '__main__'
        runpy.run_path("facehugger/facehugger.py", run_name="__main__")

        # If we get here, main was never called - test should fail
        # If main was called, the tracing hook should have thrown an exception
        assert False, "main() was never called"

    except MainCalled:
        # Expected - main() was about to be called
        pass

    finally:
        # Always clean up trace hook
        sys.settrace(None)

    # Assert that we detected the call
    assert detected, "main() should have been called when __name__ == '__main__'"


def test_main_not_called_when_imported():
    """Verify main() is NOT called during normal import."""
    detected = False

    def hook(frame, event, arg):
        """Trace hook that detects main() call."""
        nonlocal detected
        if event == "call" and frame.f_code.co_name == "main":
            if "facehugger.py" in frame.f_code.co_filename:
                detected = True
                raise MainCalled()
        return hook

    # Install trace hook
    sys.settrace(hook)

    try:
        import facehugger.facehugger

        # If we get here, main was never called - test should fail
        # If main was called, the tracing hook should have thrown an exception
        assert True, "main() was never called"
        assert hasattr(facehugger.facehugger, "main")
        assert callable(facehugger.facehugger.main)

    except MainCalled:
        # Expected - main() was about to be called
        assert False, "main() was called"

    finally:
        # Always clean up trace hook
        sys.settrace(None)

    # Assert that we detected the call
    assert not detected, "main() should NOT have been called when module importede"
