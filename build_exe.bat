@echo off
REM Build Yfix standalone executable
REM Run this script from the Yfix folder

echo Building Yfix.exe via PyInstaller...
echo.

pyinstaller --onefile --windowed --name="Yfix" --hidden-import=psutil yfix_gui.py

echo.
if exist "dist\Yfix.exe" (
    echo SUCCESS: dist\Yfix.exe created!
    dir "dist\Yfix.exe"
) else (
    echo FAILED: Check PyInstaller output above.
)

pause
