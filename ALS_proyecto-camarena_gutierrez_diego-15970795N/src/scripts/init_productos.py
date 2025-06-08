#!/usr/bin/env python3
"""
Script para inicializar productos de ejemplo en la base de datos.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def init_productos():
    """Inicializar productos de ejemplo"""
    print("🔧 Creando productos de ejemplo...")
    
    from app import create_app
    from app.services.storage_service import StorageService
    from app.models.producto import Producto
    
    app = create_app()
    
    with app.app_context():
        storage = StorageService()
        
        # Lista de productos de ejemplo
        productos_ejemplo = [
            {
                'nombre': 'Camiseta Básica',
                'categoria': 'Camisetas',
                'precio_base': 15.00,
                'descripcion': 'Camiseta de algodón 100%, disponible en varios colores',
                'tallas_disponibles': ['XS', 'S', 'M', 'L', 'XL'],
                'colores_disponibles': ['Blanco', 'Negro', 'Gris', 'Azul']
            },
            {
                'nombre': 'Polo Clásico',
                'categoria': 'Polos',
                'precio_base': 25.00,
                'descripcion': 'Polo de algodón piqué, ideal para uso casual o deportivo',
                'tallas_disponibles': ['S', 'M', 'L', 'XL'],
                'colores_disponibles': ['Blanco', 'Negro', 'Azul marino', 'Rojo']
            },
            {
                'nombre': 'Sudadera con Capucha',
                'categoria': 'Sudaderas',
                'precio_base': 35.00,
                'descripcion': 'Sudadera cómoda con capucha ajustable',
                'tallas_disponibles': ['S', 'M', 'L', 'XL'],
                'colores_disponibles': ['Gris', 'Negro', 'Azul']
            }
        ]
        
        # Crear y guardar los productos
        for prod_data in productos_ejemplo:
            try:
                # Verificar si el producto ya existe
                productos_existentes = storage.find_all(Producto)
                existe = any(p.nombre == prod_data['nombre'] for p in productos_existentes if p.is_active)
                
                if not existe:
                    producto = Producto(
                        nombre=prod_data['nombre'],
                        categoria=prod_data['categoria'],
                        precio_base=prod_data['precio_base'],
                        descripcion=prod_data['descripcion'],
                        tallas_disponibles=prod_data['tallas_disponibles'],
                        colores_disponibles=prod_data['colores_disponibles']
                    )
                    storage.save(producto)
                    print(f"   ✅ Producto creado: {producto.nombre}")
                else:
                    print(f"   ⚠️  El producto {prod_data['nombre']} ya existe")
            except Exception as e:
                print(f"   ❌ Error creando producto {prod_data['nombre']}: {str(e)}")

if __name__ == '__main__':
    print("🟢 Iniciando creación de productos de ejemplo...")
    init_productos()
    print("🎉 Proceso completado!")
