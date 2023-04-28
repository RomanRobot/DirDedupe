
@echo off

setlocal
setlocal EnableExtensions
setlocal EnableDelayedExpansion


:SETUP
set "_filecwd=%~dp0"
pushd !_filecwd!


:VENV
if exist venv ( rmdir /S /Q venv )

echo. & echo Creating 'venv' & echo.
python -m venv venv --upgrade-deps

call venv\Scripts\activate

pip install -r requirements.txt


popd
