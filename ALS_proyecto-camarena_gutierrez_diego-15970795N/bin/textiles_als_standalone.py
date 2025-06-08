#!/usr/bin/env python3
"""
Ejecutable principal del Sistema de Gestión Textiles ALS.
Versión independiente que puede ejecutarse sin dependencias externas.

Autor: Camarena Gutiérrez, Diego - 15970795N
Fecha: Diciembre 2025
Proyecto: ALS - Aplicación de Gestión Textil
"""

import sys
import os
import webbrowser
import threading
import time
from pathlib import Path

def verificar_requisitos():
    """Verificar que todos los requisitos estén disponibles."""
    try:
        # Verificar importaciones críticas
        import flask
        import flask_login
        import flask_wtf
        import sirope
        print("✅ Todas las dependencias verificadas")
        return True
    except ImportError as e:
        print(f"❌ Dependencia faltante: {e}")
        print("💡 Este ejecutable debe compilarse con todas las dependencias incluidas")
        return False

def configurar_entorno():
    """Configurar el entorno para la aplicación."""
    # Si estamos en un ejecutable de PyInstaller
    if getattr(sys, 'frozen', False):
        # Usar el directorio del ejecutable
        base_path = Path(sys._MEIPASS)
        app_path = Path(sys.executable).parent
    else:
        # Ejecutando desde código fuente
        base_path = Path(__file__).parent.parent / "src"
        app_path = base_path
    
    # Agregar al path de Python
    sys.path.insert(0, str(base_path))
    
    # Configurar variables de entorno
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = 'False'
    
    return base_path, app_path

def abrir_navegador_automatico():
    """Abrir el navegador web automáticamente después de un retraso."""
    def _abrir():
        time.sleep(3)  # Esperar 3 segundos para que el servidor inicie
        try:
            webbrowser.open('http://localhost:5000')
            print("🌐 Navegador abierto automáticamente")
        except Exception as e:
            print(f"⚠️  No se pudo abrir el navegador automáticamente: {e}")
            print("💡 Abre manualmente: http://localhost:5000")
    
    # Ejecutar en hilo separado para no bloquear
    thread = threading.Thread(target=_abrir, daemon=True)
    thread.start()

def mostrar_informacion_inicio():
    """Mostrar información de bienvenida."""
    print("=" * 60)
    print("🏭 SISTEMA DE GESTIÓN TEXTILES ALS")
    print("=" * 60)
    print("📋 Aplicación CRUD para gestión de pedidos textiles")
    print("👨‍💻 Autor: Camarena Gutiérrez, Diego - 15970795N")
    print("🎓 Proyecto: ALS - Universidad")
    print("=" * 60)
    print()
    print("🚀 Iniciando servidor web...")
    print("📍 URL: http://localhost:5000")
    print("🔑 Usuario por defecto: admin")
    print("🔒 Contraseña por defecto: admin123")
    print()
    print("⚠️  IMPORTANTE:")
    print("   - Mantén esta ventana abierta mientras uses la aplicación")
    print("   - Presiona Ctrl+C para detener el servidor")
    print("   - El navegador se abrirá automáticamente")
    print("=" * 60)
    print()

def main():
    """Función principal del ejecutable."""
    try:
        # Mostrar información inicial
        mostrar_informacion_inicio()
        
        # Configurar entorno
        base_path, app_path = configurar_entorno()
        print(f"📁 Directorio base: {base_path}")
        
        # Verificar requisitos
        if not verificar_requisitos():
            input("❌ Presiona Enter para salir...")
            return
        
        # Importar aplicación Flask
        print("📦 Importando aplicación Flask...")
        from app import create_app
        
        # Crear aplicación
        print("⚙️  Creando aplicación...")
        app = create_app()
        
        # Configuraciones específicas para ejecutable
        app.config.update({
            'DEBUG': False,
            'ENV': 'production',
            'TESTING': False,
            'SECRET_KEY': 'textiles-als-ejecutable-key-2025',
            'WTF_CSRF_ENABLED': True,
            'WTF_CSRF_TIME_LIMIT': 3600,
        })
        
        print("✅ Aplicación configurada para producción")
        
        # Inicializar datos si es necesario
        with app.app_context():
            try:
                from app.services.storage_service import StorageService
                from app.models.usuario import Usuario
                
                storage = StorageService()
                usuarios = storage.find_all(Usuario)
                
                if not usuarios:
                    print("🔧 Inicializando datos por defecto...")
                    # Crear usuario admin por defecto
                    admin = Usuario(
                        username='admin',
                        email='admin@textiles-als.com',
                        password='admin123',
                        nombre='Administrador',
                        apellidos='Sistema'
                    )
                    admin.is_admin = True
                    storage.save(admin)
                    print("✅ Usuario administrador creado")
                else:
                    print(f"✅ Sistema ya inicializado ({len(usuarios)} usuarios)")
                    
            except Exception as e:
                print(f"⚠️  Advertencia en inicialización: {e}")
        
        # Abrir navegador automáticamente
        abrir_navegador_automatico()
        
        print("🟢 ¡Servidor iniciado exitosamente!")
        print("🌐 Accede a la aplicación en tu navegador")
        print()
        
        # Ejecutar servidor Flask
        app.run(
            host='127.0.0.1',  # Solo localhost por seguridad
            port=5000,
            debug=False,
            use_reloader=False,  # Crítico para ejecutables
            threaded=True,
            use_debugger=False
        )
        
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("🛑 Aplicación detenida por el usuario")
        print("👋 ¡Gracias por usar Sistema de Gestión Textiles ALS!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        print("\n🔧 SOLUCIONES POSIBLES:")
        print("   1. Verificar que el puerto 5000 no esté en uso")
        print("   2. Ejecutar como administrador")
        print("   3. Verificar permisos de escritura en el directorio")
        print("   4. Comprobar que no hay antivirus bloqueando")
        print("\n💡 Si el problema persiste, contacta al desarrollador")
        input("\nPresiona Enter para salir...")

if __name__ == '__main__':
    main()
