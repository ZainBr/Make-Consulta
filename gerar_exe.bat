@echo off
REM Script para criar o EXE da aplicação ConsultaNF
REM Clique duas vezes para executar

title Gerando ConsultaNF.exe...
color 0A

echo.
echo ========================================
echo    ConsultaNF - Gerador de EXE
echo ========================================
echo.
echo Instalando PyInstaller...

python -m pip install PyInstaller --quiet
if errorlevel 1 goto erro

echo.
echo Gerando executavel...
echo.

python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name=ConsultaNF ^
    app_launcher.py

if errorlevel 1 goto erro

if not exist dist\ConsultaNF.exe goto erro

echo.
echo ========================================
echo    Sucesso!
echo ========================================
echo.
echo Arquivo criado: dist\ConsultaNF.exe
echo.
echo Proximos passos:
echo 1. Execute: dist\ConsultaNF.exe
echo 2. Distribua o arquivo para seus colegas
echo 3. Eles clicam 2x para abrir
echo.
pause
exit /b 0

:erro
echo.
echo ========================================
echo    ERRO NA GERACAO DO EXE
echo ========================================
echo.
echo Verifique se o Python tem acesso a internet e tente novamente.
echo.
pause
exit /b 1
