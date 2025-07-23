#!/usr/bin/env python3
"""
Script para inicializar datos de demostración en producción.
"""

import os
import sys
from datetime import datetime, timedelta

# Añadir el directorio src al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services.storage_service import StorageService
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.models.producto import Producto
from app.models.proceso import Proceso
from werkzeug.security import generate_password_hash


def init_demo_data():
    """Inicializar datos de demostración."""
    
    # Importar aquí para evitar imports circulares
    from flask import current_app
    from app.services.storage_service import StorageService
    from app.models.usuario import Usuario
    from app.models.cliente import Cliente
    from app.models.producto import Producto
    from app.models.proceso import Proceso
    from werkzeug.security import generate_password_hash
    
    storage = StorageService()
    
    print("🚀 Inicializando datos de demostración...")
    if current_app:
        current_app.logger.info("🚀 Inicializando datos de demostración...")
        
        # 1. Crear usuario demo
        try:
            # Verificar si ya existe
            existing_user = storage.find_first(Usuario, lambda u: u.username == 'demo')
            if not existing_user:
                demo_user = Usuario(
                    username='demo',
                    email='demo@textiles-als.com',
                    password_hash=generate_password_hash('demo123'),
                    nombre='Usuario Demo',
                    apellido='Textiles ALS',
                    telefono='555-0123',
                    es_admin=True,
                    is_active=True
                )
                storage.save(demo_user)
                print("✅ Usuario demo creado: demo/demo123")
            else:
                print("ℹ️  Usuario demo ya existe")
        except Exception as e:
            print(f"❌ Error creando usuario demo: {e}")
        
        # 2. Crear procesos de ejemplo
        procesos_data = [
            {
                'nombre': 'Bordado',
                'descripcion': 'Bordado personalizado en prendas',
                'precio_base': 25.00,
                'tiempo_estimado': 2,
                'activo': True
            },
            {
                'nombre': 'Serigrafía',
                'descripcion': 'Impresión serigráfica de alta calidad',
                'precio_base': 15.00,
                'tiempo_estimado': 1,
                'activo': True
            },
            {
                'nombre': 'Vinil Textil',
                'descripcion': 'Aplicación de vinil cortado',
                'precio_base': 20.00,
                'tiempo_estimado': 1,
                'activo': True
            },
            {
                'nombre': 'Sublimación',
                'descripcion': 'Impresión por sublimación',
                'precio_base': 30.00,
                'tiempo_estimado': 2,
                'activo': True
            }
        ]
        
        try:
            for proceso_data in procesos_data:
                existing = storage.find_first(Proceso, lambda p: p.nombre == proceso_data['nombre'])
                if not existing:
                    proceso = Proceso(**proceso_data)
                    storage.save(proceso)
                    print(f"✅ Proceso creado: {proceso_data['nombre']}")
        except Exception as e:
            print(f"❌ Error creando procesos: {e}")
        
        # 3. Crear productos de ejemplo
        productos_data = [
            {
                'nombre': 'Playera Básica',
                'descripcion': 'Playera de algodón 100%',
                'precio': 120.00,
                'categoria': 'Playeras',
                'stock': 100,
                'activo': True
            },
            {
                'nombre': 'Sudadera con Capucha',
                'descripcion': 'Sudadera de algodón con capucha',
                'precio': 350.00,
                'categoria': 'Sudaderas',
                'stock': 50,
                'activo': True
            },
            {
                'nombre': 'Polo Empresarial',
                'descripcion': 'Polo de piqué para uniformes',
                'precio': 180.00,
                'categoria': 'Polos',
                'stock': 75,
                'activo': True
            },
            {
                'nombre': 'Gorra Snapback',
                'descripcion': 'Gorra ajustable de algodón',
                'precio': 150.00,
                'categoria': 'Gorras',
                'stock': 80,
                'activo': True
            }
        ]
        
        try:
            for producto_data in productos_data:
                existing = storage.find_first(Producto, lambda p: p.nombre == producto_data['nombre'])
                if not existing:
                    producto = Producto(**producto_data)
                    storage.save(producto)
                    print(f"✅ Producto creado: {producto_data['nombre']}")
        except Exception as e:
            print(f"❌ Error creando productos: {e}")
        
        # 4. Crear clientes de ejemplo
        clientes_data = [
            {
                'nombre': 'Empresa Demo S.A.',
                'contacto': 'Juan Pérez',
                'email': 'juan@empresademo.com',
                'telefono': '555-1234',
                'direccion': 'Av. Principal 123, Ciudad Demo',
                'activo': True
            },
            {
                'nombre': 'Escuela Secundaria Demo',
                'contacto': 'María González',
                'email': 'maria@escuelademo.edu',
                'telefono': '555-5678',
                'direccion': 'Calle Educación 456, Ciudad Demo',
                'activo': True
            }
        ]
        
        try:
            for cliente_data in clientes_data:
                existing = storage.find_first(Cliente, lambda c: c.email == cliente_data['email'])
                if not existing:
                    cliente = Cliente(**cliente_data)
                    storage.save(cliente)
                    print(f"✅ Cliente creado: {cliente_data['nombre']}")
        except Exception as e:
            print(f"❌ Error creando clientes: {e}")
        
        print("🎉 Inicialización de datos de demostración completada!")
        print("\n📋 Datos creados:")
        print("   👤 Usuario: demo / demo123")
        print("   🏭 4 Procesos de personalización")
        print("   👕 4 Productos base")
        print("   🏢 2 Clientes de ejemplo")
        print("\n🌐 La aplicación está lista para usar!")


if __name__ == '__main__':
    # Cuando se ejecuta directamente, crear app context
    from app import create_app
    app = create_app('production')
    with app.app_context():
        init_demo_data()
