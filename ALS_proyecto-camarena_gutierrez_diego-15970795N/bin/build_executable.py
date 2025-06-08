#!/usr/bin/env python3
"""
Script para compilar la aplicación Flask en un ejecutable independiente.
Este script crea un ejecutable estático que incluye todas las dependencias.

Uso: python build_executable.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    """Función principal para compilar el ejecutable."""
    print("🚀 Iniciando proceso de compilación del ejecutable...")
    print("=" * 60)
    
    # Verificar que PyInstaller esté disponible
    try:
        import PyInstaller
        print(f"✅ PyInstaller encontrado: versión {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller no está instalado.")
        print("💡 Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller instalado correctamente.")
    
    # Rutas del proyecto
    current_dir = Path(__file__).parent
    src_dir = current_dir.parent / "src"
    dist_dir = current_dir / "dist"
    build_dir = current_dir / "build"
    
    # Limpiar directorios anteriores
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print("🗑️  Directorio dist limpiado")
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("🗑️  Directorio build limpiado")
    
    # Crear el archivo de entrada para el ejecutable
    launcher_path = current_dir / "textiles_als_launcher.py"
    create_launcher_script(launcher_path, src_dir)
    
    # Comando PyInstaller
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",  # Crear un solo archivo ejecutable
        "--windowed",  # Sin ventana de consola (comentar si quieres ver debug)
        "--name=TextilesALS",
        "--icon=icon.ico",  # Opcional: añadir icono
        "--add-data", f"{src_dir / 'app' / 'templates'};app/templates",
        "--add-data", f"{src_dir / 'app' / 'static'};app/static",
        "--hidden-import=app",
        "--hidden-import=app.models",
        "--hidden-import=app.routes",
        "--hidden-import=app.forms",
        "--hidden-import=app.services",
        "--hidden-import=flask",
        "--hidden-import=flask_login",
        "--hidden-import=flask_wtf",
        "--hidden-import=wtforms",
        "--hidden-import=sirope",
        "--hidden-import=redis",
        "--clean",  # Limpiar cache de PyInstaller
        str(launcher_path)
    ]
    
    print(f"🔨 Ejecutando comando: {' '.join(pyinstaller_cmd)}")
    print("⏳ Este proceso puede tardar varios minutos...")
    
    try:
        # Cambiar al directorio bin para ejecutar PyInstaller
        os.chdir(current_dir)
        subprocess.check_call(pyinstaller_cmd)
        
        print("✅ Compilación completada exitosamente!")
        
        # Verificar que el ejecutable se creó
        exe_path = dist_dir / "TextilesALS.exe"
        if exe_path.exists():
            exe_size = exe_path.stat().st_size / (1024 * 1024)  # MB
            print(f"📦 Ejecutable creado: {exe_path}")
            print(f"📏 Tamaño: {exe_size:.1f} MB")
            
            # Crear script de instalación
            create_install_script(current_dir)
            
            print("\n🎉 ¡Proceso completado!")
            print("=" * 60)
            print("El ejecutable se encuentra en: bin/dist/TextilesALS.exe")
            print("Para usar:")
            print("1. Copiar TextilesALS.exe a donde desees")
            print("2. Ejecutar directamente - no necesita Python ni librerías externas")
            print("3. La aplicación se ejecutará en http://localhost:5000")
            
        else:
            print("❌ Error: No se pudo crear el ejecutable")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error durante la compilación: {e}")
        return False
    
    # Limpiar archivo temporal
    if launcher_path.exists():
        launcher_path.unlink()
        print("🗑️  Archivo temporal limpiado")
    
    return True

def create_launcher_script(launcher_path, src_dir):
    """Crear el script de lanzamiento para el ejecutable."""
    
    launcher_content = f'''#!/usr/bin/env python3
"""
Launcher para el ejecutable de Sistema de Gestión Textiles ALS.
Este archivo es usado por PyInstaller para crear el ejecutable.
"""

import sys
import os
from pathlib import Path

# Configurar rutas para el ejecutable
if getattr(sys, 'frozen', False):
    # Si estamos ejecutando desde el ejecutable
    application_path = Path(sys.executable).parent
    # PyInstaller crea un directorio temporal en sys._MEIPASS
    base_path = Path(sys._MEIPASS)
else:
    # Si estamos ejecutando desde código fuente
    base_path = Path(__file__).parent.parent / "src"
    application_path = base_path

# Agregar el directorio de la aplicación al path
sys.path.insert(0, str(base_path))

def main():
    """Función principal del ejecutable."""
    try:
        print("🚀 Iniciando Sistema de Gestión Textiles ALS...")
        print("=" * 50)
        print("📍 Aplicación web disponible en: http://localhost:5000")
        print("🔑 Usuario por defecto: admin / contraseña: admin123")
        print("⚠️  Presiona Ctrl+C para detener el servidor")
        print("=" * 50)
        
        # Importar y crear la aplicación
        from app import create_app
        
        app = create_app()
        
        # Configurar para ejecución como ejecutable
        app.config['DEBUG'] = False
        app.config['ENV'] = 'production'
        
        # Ejecutar servidor
        import webbrowser
        import threading
        import time
        
        def abrir_navegador():
            """Abrir navegador después de un breve retraso."""
            time.sleep(2)
            try:
                webbrowser.open('http://localhost:5000')
            except:
                pass  # Si no puede abrir el navegador, no es crítico
        
        # Abrir navegador en segundo plano
        threading.Thread(target=abrir_navegador, daemon=True).start()
        
        # Ejecutar aplicación
        app.run(
            host='127.0.0.1',  # Solo localhost por seguridad
            port=5000,
            debug=False,
            use_reloader=False,  # Importante para el ejecutable
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\\n👋 Aplicación detenida por el usuario.")
        print("¡Gracias por usar Sistema de Gestión Textiles ALS!")
        
    except Exception as e:
        print(f"❌ Error al iniciar la aplicación: {{e}}")
        print("💡 Verifica que el puerto 5000 no esté en uso.")
        input("Presiona Enter para salir...")

if __name__ == '__main__':
    main()
'''
    
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print(f"✅ Script launcher creado: {launcher_path}")

def create_install_script(bin_dir):
    """Crear script de instalación para el usuario final."""
    
    install_script = bin_dir / "INSTRUCCIONES_EJECUTABLE.txt"
    
    content = """
Sistema de Gestión Textiles ALS - Ejecutable Independiente
=========================================================

CONTENIDO DEL DIRECTORIO:
========================
- TextilesALS.exe          -> Ejecutable principal (en carpeta dist/)
- build_executable.py      -> Script de compilación 
- INSTRUCCIONES_EJECUTABLE.txt -> Este archivo

COMO USAR EL EJECUTABLE:
=======================

1. EJECUCIÓN SIMPLE:
   - Navegar a: bin/dist/
   - Doble clic en "TextilesALS.exe"
   - ¡Listo! La aplicación se abrirá automáticamente en tu navegador

2. EJECUCIÓN DESDE LÍNEA DE COMANDOS:
   - Abrir terminal/cmd en el directorio bin/dist/
   - Ejecutar: TextilesALS.exe
   - Abrir navegador en: http://localhost:5000

3. CREDENCIALES POR DEFECTO:
   - Usuario: admin
   - Contraseña: admin123

CARACTERÍSTICAS DEL EJECUTABLE:
==============================
✅ No requiere Python instalado
✅ No requiere librerías externas
✅ Todas las dependencias incluidas
✅ Ejecutable de un solo archivo
✅ Compatible con Windows
✅ Abre automáticamente el navegador
✅ Servidor web integrado

REQUISITOS DEL SISTEMA:
======================
- Windows 7 o superior
- Mínimo 4GB RAM
- Puerto 5000 disponible
- Navegador web moderno

SOLUCIÓN DE PROBLEMAS:
=====================
- Si no abre el navegador: Ir manualmente a http://localhost:5000
- Si dice "puerto en uso": Cerrar otras aplicaciones que usen puerto 5000
- Si no inicia: Ejecutar como administrador
- Si hay errores: Verificar antivirus no bloquee el archivo

ESTRUCTURA DE DATOS:
===================
La aplicación crea automáticamente:
- Base de datos local (archivos .json)
- Usuario administrador por defecto
- Estructura de carpetas necesaria

PARA DESARROLLADORES:
====================
Para recompilar el ejecutable:
1. python build_executable.py
2. El nuevo ejecutable estará en dist/TextilesALS.exe

INFORMACIÓN TÉCNICA:
===================
- Framework: Flask
- Base de datos: Sirope (archivos JSON)
- Compilado con: PyInstaller
- Tamaño aproximado: 40-60 MB
- Tipo: Aplicación web local

---
Proyecto ALS - Camarena Gutiérrez, Diego - 15970795N
Aplicación de gestión para personalización textil
"""
    
    with open(install_script, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Instrucciones creadas: {install_script}")

if __name__ == "__main__":
    success = main()
    if not success:
        input("❌ Presiona Enter para salir...")
    else:
        input("✅ Presiona Enter para salir...")
