# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import os
import subprocess
import sys
import traceback
import ctypes

GLOBAL_MUTEX_NAME = "PyRIT-Gradio"


def launch_app(open_browser: bool = False) -> None:
    # Launch a new process to run the gradio UI.
    # Locate the python executable and run this file.
    current_path = os.path.abspath(__file__)
    python_path = sys.executable

    # Start a new process to run it
    if sys.platform == "win32":
        subprocess.Popen(
            [python_path, current_path, str(open_browser)],
            creationflags=subprocess.CREATE_NEW_CONSOLE,  # type: ignore[attr-defined, unused-ignore]
        )
    else:
        subprocess.Popen([python_path, current_path, str(open_browser)])


def create_mutex() -> bool:
    if sys.platform != "win32":
        return True

    ctypes.windll.kernel32.CreateMutexW(None, False, GLOBAL_MUTEX_NAME)
    last_error = ctypes.windll.kernel32.GetLastError()
    return bool(last_error != 183)  # ERROR_ALREADY_EXISTS


def is_app_running() -> bool:
    if sys.platform != "win32":
        return False

    SYNCHRONIZE = 0x00100000
    mutex = ctypes.windll.kernel32.OpenMutexW(SYNCHRONIZE, False, GLOBAL_MUTEX_NAME)
    if not mutex:
        return False

    # Close the handle to the mutex
    ctypes.windll.kernel32.CloseHandle(mutex)
    return True


if __name__ == "__main__":

    if not create_mutex():
        print("Gradio UI is already running.")
        sys.exit(1)
    print("Starting Gradio Interface please wait...")
    try:
        open_browser = False
        if len(sys.argv) > 1:
            open_browser = sys.argv[1] == "True"

        from scorer import GradioApp

        app = GradioApp()
        app.start_gradio(open_browser=open_browser)
    except:  # noqa: E722
        # Print the error message and traceback
        print(traceback.format_exc())
        input("Press Enter to exit.")
