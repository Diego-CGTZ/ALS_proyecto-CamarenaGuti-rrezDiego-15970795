@echo off
REM Script para compilar el ejecutable del Sistema de Gestión Textiles ALS
REM Este script automatiza todo el proceso de creación del ejecutable

echo ========================================
echo  Sistema de Gestión Textiles ALS
echo  Compilador de Ejecutable Independiente
echo ========================================
echo.

echo [1/4] Verificando Python...
python --version
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python 3.8+ desde python.org
    pause
    exit /b 1
)

echo [2/4] Instalando dependencias del proyecto...
cd ..\src
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo [3/4] Instalando PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo ERROR: No se pudo instalar PyInstaller
    pause
    exit /b 1
)

echo [4/4] Compilando ejecutable...
cd ..\bin
python build_executable.py
if errorlevel 1 (
    echo ERROR: La compilación falló
    pause
    exit /b 1
)

echo.
echo ========================================
echo ¡COMPILACIÓN COMPLETADA EXITOSAMENTE!
echo ========================================
echo.
echo El ejecutable se encuentra en:
echo bin\dist\TextilesALS.exe
echo.
echo Para usar:
echo 1. Navegar a la carpeta bin\dist\
echo 2. Doble clic en TextilesALS.exe
echo 3. La aplicación se abrirá en http://localhost:5000
echo.
echo Credenciales por defecto:
echo Usuario: admin
echo Contraseña: admin123
echo.
pause
