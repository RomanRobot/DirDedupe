rmdir output
mkdir output
pushd output
REM pip show customtkinter
pyinstaller --noconfirm --onedir --windowed --add-data "c:\users\me\appdata\local\programs\python\python310\lib\site-packages/customtkinter;customtkinter/"  "../DirDedupe.py"