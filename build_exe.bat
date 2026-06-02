@echo off
REM Build Yfix standalone executables (GUI + CLI)
REM Run this script from the Yfix folder

echo ============================================
echo Building Yfix.exe (GUI) via PyInstaller...
echo ============================================
echo.

"%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\Scripts\pyinstaller.exe" --onefile --windowed --name="Yfix" --hidden-import=psutil yfix_gui.py

echo.
if exist "dist\Yfix.exe" (
    echo SUCCESS: dist\Yfix.exe created!
    dir "dist\Yfix.exe"
) else (
    echo FAILED: dist\Yfix.exe not found. Check output above.
)

echo.
echo ============================================
echo Building Yfix-CLI.exe (Console) via PyInstaller...
echo ============================================
echo.

"%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\Scripts\pyinstaller.exe" --onefile --name="Yfix-CLI" --hidden-import=psutil yfix.py

echo.
if exist "dist\Yfix-CLI.exe" (
    echo SUCCESS: dist\Yfix-CLI.exe created!
    dir "dist\Yfix-CLI.exe"
) else (
    echo FAILED: dist\Yfix-CLI.exe not found. Check output above.
)

echo.
echo ============================================
echo Build complete! Files in dist\:
echo ============================================
dir "dist\"

pause
