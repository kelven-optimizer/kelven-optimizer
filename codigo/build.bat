@echo off
echo ========================================
echo  Kelven Optimizer PRO - Build Script
echo ========================================
echo.

echo [1/3] Instalando PyInstaller...
pip install pyinstaller --quiet

echo.
echo [2/3] Compilando para EXE...
python -m PyInstaller --noconfirm --onefile --windowed --name "kelven-optimizer2.0" --icon "kelvenos.ico" --add-data "kelvenos.ico;." "kelven-optimizer2.0.py"

echo.
echo [3/3] Limpando arquivos temporarios...
rmdir /s /q build
rmdir /s /q __pycache__
del /q "kelven-optimizer2.0.spec"

echo.
echo ========================================
echo  Compilacao concluida!
echo  Arquivo: dist\kelven-optimizer2.0.exe
echo ========================================
pause
