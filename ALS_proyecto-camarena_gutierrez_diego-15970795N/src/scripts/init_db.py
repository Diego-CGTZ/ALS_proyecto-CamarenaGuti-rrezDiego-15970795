#!/usr/bin/env python3
"""
Script de inicialización para poblar la base de datos con datos predeterminados.
Este script debe ejecutarse después de configurar la aplicación por primera vez.
"""

print("🟢 Script init_db.py iniciado...")

import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.services.storage_service import StorageService
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.models.producto import Producto
from app.models.proceso import Proceso, TipoProceso
from app.models.pedido import Pedido, EstadoPedido


def init_default_admin():
    """Crea el usuario administrador por defecto."""
    print("🔧 Creando usuario administrador...")
    
    storage = StorageService()
    
    # Verificar si ya existe (método más simple)
    try:
        all_users = storage.find_all(Usuario)
        existing_admin = None
        for user in all_users:
            if hasattr(user, 'email') and user.email == 'admin@textiles-als.com' and user.is_active:
                existing_admin = user
                break
        
        if existing_admin:
            print("   ⚠️  El usuario administrador ya existe")
            return existing_admin
    except Exception as e:
        print(f"   ⚠️  Error verificando usuarios existentes: {e}")
        print("   📝 Continuando con la creación...")
    
    # Crear nuevo administrador
    admin = Usuario(
        username='admin',
        email='admin@textiles-als.com',
        password='admin123',  # Contraseña por defecto - CAMBIAR EN PRODUCCIÓN
        nombre='Administrador',
        apellidos='Sistema'
    )
    admin.is_admin = True
    
    try:
        admin_id = storage.save(admin)
        if admin_id:
            print(f"   ✅ Usuario administrador creado: {admin.username}")
            print(f"   📧 Email: {admin.email}")
            print("   🔑 Contraseña: admin123 (¡CAMBIAR INMEDIATAMENTE!)")
            return admin
        else:
            print("   ❌ Error al crear usuario administrador")
            return None
    except Exception as e:
        print(f"   ❌ Error al guardar usuario administrador: {e}")
        return None


def init_default_processes():
    """Crea los procesos de personalización por defecto."""
    print("🎨 Creando procesos de personalización...")
    
    storage = StorageService()
    
    processes_data = [
        {
            'tipo': TipoProceso.DTF,
            'nombre': 'DTF Premium',
            'descripcion': 'Transferencia DTF de alta calidad, ideal para diseños complejos y multicolor.',
        },
        {
            'tipo': TipoProceso.DTF,
            'nombre': 'DTF Económico',
            'descripcion': 'Transferencia DTF básica para diseños simples y presupuestos ajustados.',
        },
        {
            'tipo': TipoProceso.SUBLIMACION,
            'nombre': 'Sublimación Full Color',
            'descripcion': 'Sublimación de alta calidad para prendas claras. Colores vibrantes y duraderos.',
        },
        {
            'tipo': TipoProceso.BORDADO,
            'nombre': 'Bordado Tradicional',
            'descripcion': 'Bordado clásico de alta calidad. Máxima durabilidad y elegancia.',
        },
        {
            'tipo': TipoProceso.VINIL,
            'nombre': 'Vinil Textil',
            'descripcion': 'Aplicación de vinil textil. Ideal para textos y formas simples.',
        }
    ]
    
    created_count = 0
    for process_data in processes_data:
        # Verificar si ya existe (método más simple)
        try:
            all_processes = storage.find_all(Proceso)
            existing = None
            for process in all_processes:
                if (hasattr(process, 'tipo') and hasattr(process, 'nombre') and 
                    process.tipo == process_data['tipo'] and 
                    process.nombre == process_data['nombre'] and 
                    process.is_active):
                    existing = process
                    break
            
            if existing:
                print(f"   ⚠️  Proceso '{process_data['nombre']}' ya existe")
                continue
        except Exception as e:
            print(f"   ⚠️  Error verificando procesos: {e}")
        
        try:
            proceso = Proceso(
                tipo=process_data['tipo'],
                nombre=process_data['nombre'],
                descripcion=process_data['descripcion']
            )
            
            proceso_id = storage.save(proceso)
            if proceso_id:
                print(f"   ✅ Proceso creado: {process_data['nombre']} ({process_data['tipo'].value})")
                created_count += 1
            else:
                print(f"   ❌ Error al crear proceso: {process_data['nombre']}")
        except Exception as e:
            print(f"   ❌ Error al crear proceso {process_data['nombre']}: {e}")
    
    print(f"   📋 {created_count} procesos creados")


def init_default_products():
    """Crea productos por defecto."""
    print("👕 Creando productos por defecto...")
    
    storage = StorageService()
    
    products_data = [
        {
            'nombre': 'Camiseta Básica Algodón',
            'categoria': 'Camisetas',
            'precio_base': 12.50,
            'descripcion': 'Camiseta básica 100% algodón, disponible en múltiples colores y tallas.',
            'tallas_disponibles': ['S', 'M', 'L', 'XL', 'XXL'],
            'colores_disponibles': ['Blanco', 'Negro', 'Azul', 'Rojo', 'Verde']
        },
        {
            'nombre': 'Polo Piqué Premium',
            'categoria': 'Polos',
            'precio_base': 18.00,
            'descripcion': 'Polo de piqué premium con cuello y puños reforzados.',
            'tallas_disponibles': ['S', 'M', 'L', 'XL', 'XXL'],
            'colores_disponibles': ['Blanco', 'Negro', 'Azul Marino', 'Gris']
        },
        {
            'nombre': 'Sudadera con Capucha',
            'categoria': 'Sudaderas',
            'precio_base': 25.00,
            'descripcion': 'Sudadera con capucha y bolsillo frontal tipo canguro.',
            'tallas_disponibles': ['S', 'M', 'L', 'XL', 'XXL'],
            'colores_disponibles': ['Negro', 'Gris', 'Azul Marino', 'Verde Oliva']
        },
        {
            'nombre': 'Gorra Snapback',
            'categoria': 'Gorras',
            'precio_base': 15.00,
            'descripcion': 'Gorra snapback con visera plana, ideal para bordado frontal.',
            'tallas_disponibles': ['Única'],
            'colores_disponibles': ['Negro', 'Blanco', 'Azul', 'Rojo']
        },
        {
            'nombre': 'Chaleco Corporativo',
            'categoria': 'Chalecos',
            'precio_base': 22.00,
            'descripcion': 'Chaleco corporativo con múltiples bolsillos, ideal para uniformes.',
            'tallas_disponibles': ['S', 'M', 'L', 'XL', 'XXL'],
            'colores_disponibles': ['Azul Marino', 'Negro', 'Gris']
        }
    ]
    
    created_count = 0
    for product_data in products_data:
        # Verificar si ya existe (método más simple)
        try:
            all_products = storage.find_all(Producto)
            existing = None
            for product in all_products:
                if (hasattr(product, 'nombre') and 
                    product.nombre == product_data['nombre'] and 
                    product.is_active):
                    existing = product
                    break
            
            if existing:
                print(f"   ⚠️  Producto '{product_data['nombre']}' ya existe")
                continue
        except Exception as e:
            print(f"   ⚠️  Error verificando productos: {e}")
        
        try:
            producto = Producto(
                nombre=product_data['nombre'],
                categoria=product_data['categoria'],
                precio_base=product_data['precio_base'],
                descripcion=product_data['descripcion'],
                tallas_disponibles=product_data['tallas_disponibles'],
                colores_disponibles=product_data['colores_disponibles']
            )
            
            producto_id = storage.save(producto)
            if producto_id:
                print(f"   ✅ Producto creado: {product_data['nombre']} - ${product_data['precio_base']}")
                created_count += 1
            else:
                print(f"   ❌ Error al crear producto: {product_data['nombre']}")
        except Exception as e:
            print(f"   ❌ Error al crear producto {product_data['nombre']}: {e}")
    
    print(f"   📋 {created_count} productos creados")


def init_sample_clients():
    """Crea clientes de ejemplo."""
    print("👥 Creando clientes de ejemplo...")
    
    storage = StorageService()
    
    clients_data = [
        {
            'nombre': 'Empresa Desarrollo S.A.',
            'email': 'contacto@desarrollo.com',
            'telefono': '+502 2345-6789',
            'direccion': 'Zona 10, Ciudad de Guatemala',
            'empresa': 'Empresa Desarrollo S.A.',
            'notas': 'Cliente corporativo con descuento por volumen'
        },
        {
            'nombre': 'Colegio San Francisco',
            'email': 'uniformes@sanfrancisco.edu.gt',
            'telefono': '+502 3456-7890',
            'direccion': 'Zona 12, Ciudad de Guatemala',
            'empresa': 'Colegio San Francisco',
            'notas': 'Institución educativa - uniformes escolares'
        },
        {
            'nombre': 'Ana López',
            'email': 'ana.lopez@email.com',
            'telefono': '+502 4567-8901',
            'direccion': 'Zona 7, Ciudad de Guatemala',
            'empresa': '',
            'notas': 'Cliente individual frecuente'
        },
        {
            'nombre': 'Restaurante La Tradición',
            'email': 'gerencia@latradicion.com',
            'telefono': '+502 5678-9012',
            'direccion': 'Zona 1, Ciudad de Guatemala',
            'empresa': 'Restaurante La Tradición',
            'notas': 'Uniformes para personal de restaurante'
        }
    ]
    
    created_count = 0
    for client_data in clients_data:
        # Verificar si ya existe (método más simple)
        try:
            all_clients = storage.find_all(Cliente)
            existing = None
            for client in all_clients:
                if (hasattr(client, 'email') and 
                    client.email == client_data['email'] and 
                    client.is_active):
                    existing = client
                    break
            
            if existing:
                print(f"   ⚠️  Cliente '{client_data['nombre']}' ya existe")
                continue
        except Exception as e:
            print(f"   ⚠️  Error verificando clientes: {e}")
        
        try:
            cliente = Cliente(
                nombre=client_data['nombre'],
                email=client_data['email'],
                telefono=client_data['telefono'],
                direccion=client_data['direccion'],
                empresa=client_data['empresa'],
                notas=client_data['notas']
            )
            
            cliente_id = storage.save(cliente)
            if cliente_id:
                print(f"   ✅ Cliente creado: {client_data['nombre']}")
                created_count += 1
            else:
                print(f"   ❌ Error al crear cliente: {client_data['nombre']}")
        except Exception as e:
            print(f"   ❌ Error al crear cliente {client_data['nombre']}: {e}")
    
    print(f"   📋 {created_count} clientes creados")


def verify_data():
    """Verifica que los datos se hayan creado correctamente."""
    print("🔍 Verificando datos creados...")
    
    storage = StorageService()
    
    try:
        # Verificar usuarios
        usuarios = storage.find_all(Usuario)
        usuarios_activos = [u for u in usuarios if u.is_active]
        print(f"   👤 Usuarios en sistema: {len(usuarios_activos)}")
        
        # Verificar procesos
        procesos = storage.find_all(Proceso)
        procesos_activos = [p for p in procesos if p.is_active]
        print(f"   🎨 Procesos configurados: {len(procesos_activos)}")
        
        # Verificar productos
        productos = storage.find_all(Producto)
        productos_activos = [p for p in productos if p.is_active]
        print(f"   👕 Productos en catálogo: {len(productos_activos)}")
        
        # Verificar clientes
        clientes = storage.find_all(Cliente)
        clientes_activos = [c for c in clientes if c.is_active]
        print(f"   👥 Clientes registrados: {len(clientes_activos)}")
        
        print("   ✅ Verificación completada")
    except Exception as e:
        print(f"   ⚠️  Error durante la verificación: {e}")
        print("   📝 Algunos datos pueden no haberse cargado correctamente")


def main():
    """Función principal de inicialización."""
    print("="*60)
    print("🚀 INICIALIZACIÓN DE TEXTILES ALS")
    print("="*60)
    print()
    
    print("📝 Iniciando script de inicialización...")
    
    # Crear la aplicación
    print("🔧 Creando aplicación Flask...")
    app = create_app()
    print("✅ Aplicación Flask creada")
    
    print("🔗 Estableciendo contexto de aplicación...")
    with app.app_context():
        try:
            # Verificar conexión a la base de datos
            print("🔌 Inicializando servicio de almacenamiento...")
            storage = StorageService()
            print("✅ Conexión a Redis establecida")
            print()
            
            # Inicializar datos por defecto
            init_default_admin()
            print()
            
            init_default_processes()
            print()
            
            init_default_products()
            print()
            
            init_sample_clients()
            print()
            
            # Verificar datos
            verify_data()
            print()
            
            print("="*60)
            print("✅ INICIALIZACIÓN COMPLETADA EXITOSAMENTE")
            print("="*60)
            print()
            print("📋 INFORMACIÓN IMPORTANTE:")
            print("   • Usuario administrador: admin@textiles-als.com")
            print("   • Contraseña temporal: admin123")
            print("   • ⚠️  CAMBIAR CONTRASEÑA INMEDIATAMENTE")
            print("   • La aplicación está lista para usar")
            print()
            print("🚀 Para iniciar la aplicación ejecuta: python run.py")
            print()
            
        except Exception as e:
            print(f"❌ Error durante la inicialización: {str(e)}")
            print(f"📋 Detalles del error: {type(e).__name__}: {e}")
            import traceback
            print("📋 Stack trace completo:")
            traceback.print_exc()
            print("💡 Verifica la configuración de Redis y variables de entorno")
            sys.exit(1)


if __name__ == '__main__':
    main()
