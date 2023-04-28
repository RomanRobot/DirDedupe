
@echo off

setlocal
setlocal EnableExtensions
setlocal EnableDelayedExpansion


:SETUP
set "_filecwd=%~dp0"
pushd !_filecwd!


:VENV
if not exist "venv" ( call create_venv.bat )
call venv\Scripts\activate


:BUILD
rmdir /S /Q output
mkdir output
pushd output

echo. & echo Building 'DirDedupe' & echo.
pyinstaller --noconfirm --onedir --windowed --add-data "../venv/Lib/site-packages/customtkinter;customtkinter/"  "../DirDedupe.py"


popd
popd
