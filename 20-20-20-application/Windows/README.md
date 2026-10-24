# EyeGuard for Windows (source distribution)

1. Extract this ZIP to a writable folder (not inside the ZIP viewer).
2. Run `install.bat`. It uses existing Python 3.11+, offers Microsoft Store first, and asks permission before using python.org as fallback.
3. Run `run.bat` to launch. Use `startup.bat` / `remove_startup.bat` for login startup.

Python dependencies are installed into a local `.venv` folder. The Windows installer EXE does **not** require Python.
All attached monitors are covered during a break; skip becomes available after 10 seconds.
Corporate endpoint policies can block Python, Store access or package downloads.
