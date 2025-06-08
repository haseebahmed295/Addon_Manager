import unittest
from unittest.mock import patch, MagicMock
import os
import threading  # Required if you need to reference threading objects/exceptions

# Import your functions from the module where you defined them
from utils import open_in_code, open_in_code_thread


class TestMyModule(unittest.TestCase):

    # --- Tests for open_in_code ---

    # Assume file exists by default
    @patch('utils.os.path.exists', return_value=True)
    @patch('utils.os.system')  # Mock os.system
    def test_open_in_code_success(self, mock_os_system, mock_os_path_exists):
        """
        Test that open_in_code calls os.system with the correct command
        when the file exists.
        """
        test_file_path = r"C:\Users\Admin\Documents\Clients\djurik25\RBX_Toolbox"

        open_in_code(test_file_path)

        # Assert that os.path.exists was called
        mock_os_path_exists.assert_called_once_with(test_file_path)

        # Assert that os.system was called with the correct command
        mock_os_system.assert_called_once_with(f"code {test_file_path}")

    # Simulate file not existing
    @patch('utils.os.path.exists', return_value=False)
    @patch('utils.os.system')  # Mock os.system (should not be called)
    @patch('builtins.print')  # Mock the print function to capture its output
    def test_open_in_code_file_not_found(self, mock_print, mock_os_system, mock_os_path_exists):
        """
        Test that open_in_code handles non-existent files correctly
        (prints message and does not call os.system).
        """
        test_file_path = "non_existent_file.txt"

        open_in_code(test_file_path)

        # Assert that os.path.exists was called
        mock_os_path_exists.assert_called_once_with(test_file_path)

        # Assert that os.system was NOT called
        mock_os_system.assert_not_called()

        # Assert that the correct "File not found" message was printed
        mock_print.assert_called_once_with(f"File not found: {test_file_path}")

    @patch('utils.os.path.exists', return_value=True)
    @patch('utils.os.system', side_effect=Exception("Mocked OS error"))
    @patch('builtins.print')  # Mock print to check error message
    def test_open_in_code_os_system_exception(self, mock_print, mock_os_system, mock_os_path_exists):
        """
        Test that open_in_code handles unexpected exceptions from os.system.
        """
        test_file_path = "file_with_os_error.txt"

        open_in_code(test_file_path)

        mock_os_path_exists.assert_called_once_with(test_file_path)
        mock_os_system.assert_called_once_with(f"code {test_file_path}")

        # Verify the error message was printed
        mock_print.assert_called_once()
        self.assertIn(
            "An unexpected error occurred while trying to open in code: Mocked OS error", mock_print.call_args[0][0])

    # --- Tests for open_in_code_thread ---

    # Mock threading.Thread to prevent actual thread creation
    # Mock utils.open_in_code because that's the *target* of the thread,
    # and we want to ensure the thread *tries* to call it, not actually execute it.
    @patch('utils.threading.Thread')
    @patch('utils.open_in_code')
    def test_open_in_code_thread_starts_correctly(self, mock_open_in_code, mock_thread_class):
        """
        Test that open_in_code_thread correctly creates and starts a thread
        with the right target and arguments.
        """
        test_file_path = r"C:\Users\Admin\Documents\Clients\djurik25\RBX_Toolbox\props.py"

        open_in_code_thread(test_file_path)

        # 1. Assert that threading.Thread was instantiated
        # It should be called with target=open_in_code and args=(file_path,)
        mock_thread_class.assert_called_once_with(
            target=mock_open_in_code,  # Assert it was called with the mocked open_in_code
            args=(test_file_path,)
        )

        # 2. Assert that the .start() method was called on the *instance* of the thread
        # To do this, we need to get the mock object that was returned by the constructor.
        # mock_thread_class.return_value gives us the instance that was created.
        mock_thread_instance = mock_thread_class.return_value
        mock_thread_instance.start.assert_called_once()

        # 3. Assert that open_in_code was NOT called directly by open_in_code_thread
        # This is important! The test is about whether the thread *would* call it,
        # not whether it calls it synchronously. The mocked open_in_code should
        # only be conceptually linked via the thread target.
        mock_open_in_code.assert_not_called()

        # If you wanted to test what happens *inside* the thread, that's more complex
        # and often involves separate unit tests for the 'target' function itself,
        # or integration tests that allow the thread to run.

    # Optional: Test for edge cases or invalid inputs for open_in_code_thread

    @patch('utils.threading.Thread')
    @patch('utils.open_in_code')
    def test_open_in_code_thread_with_empty_path(self, mock_open_in_code, mock_thread_class):
        """
        Test open_in_code_thread with an empty file path.
        It should still attempt to create and start the thread.
        """
        open_in_code_thread("")

        mock_thread_class.assert_called_once_with(
            target=mock_open_in_code,
            args=("",)  # Expect empty string to be passed
        )
        mock_thread_class.return_value.start.assert_called_once()
        mock_open_in_code.assert_not_called()


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
