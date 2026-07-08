@echo off
REM ===  tempmon  -  double-cliquez sur ce fichier pour lancer  ===
REM Ouvre le tableau de bord des temperatures dans votre navigateur.

cd /d "%~dp0"

REM Cherche Python (python ou py)
where python >nul 2>nul
if %errorlevel%==0 (
    python launcher.py
    goto :fin
)
where py >nul 2>nul
if %errorlevel%==0 (
    py launcher.py
    goto :fin
)

echo.
echo Python n'est pas installe.
echo Installez-le gratuitement depuis https://www.python.org/downloads/
echo ( cochez "Add Python to PATH" pendant l'installation ), puis relancez ce fichier.
echo.
pause

:fin
