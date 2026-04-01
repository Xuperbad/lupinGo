@echo off
setlocal

cd /d "%~dp0"

python -m PyInstaller --noconfirm level-generator-gui.spec

if errorlevel 1 (
  echo.
  echo Build failed.
  exit /b 1
)

if exist "dist\level-generator-gui.exe" (
  del /f /q "dist\level-generator-gui.exe"
)

echo.
echo Build completed:
echo dist\level-generator-gui\level-generator-gui.exe
