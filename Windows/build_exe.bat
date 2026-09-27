@echo off
setlocal
py -3.11 -m pip install --upgrade pip
py -3.11 -m pip install "kivy[base]==2.3.0" pyinstaller
py -3.11 -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name MusicPlus ^
  --add-data "wallpaper.jpg;." ^
  --add-data "logo.gif;." ^
  main.py
echo.
echo EXE: dist\MusicPlus.exe
pause
