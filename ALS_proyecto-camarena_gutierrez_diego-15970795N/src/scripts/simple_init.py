#!/usr/bin/env python3
"""
Simple test script to initialize basic data.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("🚀 Iniciando script de inicialización simplificado...")

try:
    from app import create_app
    print("✅ Flask app importada")
    
    from app.services.storage_service import StorageService
    print("✅ StorageService importado")
    
    from app.models.usuario import Usuario
    print("✅ Usuario importado")
    
    app = create_app()
    print("✅ App creada")
    
    with app.app_context():
        print("✅ Contexto de app establecido")
        
        storage = StorageService()
        print("✅ Storage service inicializado")
        
        # Crear usuario admin
        admin = Usuario(
            username='admin',
            email='admin@textiles-als.com',
            password='admin123',
            nombre='Administrador',
            apellidos='Sistema'
        )
        admin.is_admin = True
        print("✅ Usuario admin creado")
        
        admin_id = storage.save(admin)
        print(f"✅ Usuario admin guardado con ID: {admin_id}")
        
        # Verificar que se guardó
        all_users = storage.find_all(Usuario)
        print(f"✅ Total usuarios en sistema: {len(all_users)}")
        
        print("🎉 Inicialización básica completada exitosamente!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
