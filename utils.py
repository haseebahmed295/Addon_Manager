import subprocess
import threading
import os
def open_in_code(file_path: str) -> None:
    """Open the specified file in Visual Studio Code.

    Args:
        file_path (str): Path to the file to be opened.

    Returns:
        None
    """
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
        os.system(f'code "{(file_path)}"')
    except Exception as e:  # This catches the "Mocked OS error"
        print(f"An unexpected error occurred while trying to open in code: {e}")
        
def open_in_code_thread(file_path: str) -> None:
    """Launch a new thread to open the specified file in Visual Studio Code.

    Args:
        file_path (str): Path to the file to be opened.
    """
    thread = threading.Thread(target=open_in_code, args=(file_path,))
    thread.start()
    
