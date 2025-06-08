#!/usr/bin/env python3
"""
Utilidades de desarrollo para Textiles ALS.
Incluye comandos para resetear datos, generar datos de prueba, y más.
"""

import sys
import os
import random
from datetime import datetime, timedelta
from faker import Faker

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.services.storage_service import StorageService
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.models.producto import Producto
from app.models.proceso import Proceso, TipoProceso
from app.models.pedido import Pedido, EstadoPedido, ItemPedido, PersonalizacionItem

fake = Faker(['es_ES'])


def reset_database():
    """Resetea completamente la base de datos."""
    print("🗑️  Reseteando base de datos...")
    
    response = input("⚠️  Esta operación eliminará TODOS los datos. ¿Continuar? (y/N): ")
    if response.lower() != 'y':
        print("Operación cancelada.")
        return
    
    storage = StorageService()
    redis_client = storage.get_redis_client()
    redis_client.flushall()
    
    print("✅ Base de datos reseteada completamente")


def generate_test_orders(count=20):
    """Genera pedidos de prueba aleatorios."""
    print(f"📦 Generando {count} pedidos de prueba...")
    
    # Obtener datos existentes
    clientes = Cliente.obtener_todos()
    productos = Producto.obtener_todos()
    procesos = Proceso.obtener_todos()
    
    if not clientes or not productos or not procesos:
        print("❌ Se necesitan clientes, productos y procesos existentes")
        return
    
    estados = list(EstadoPedido)
    created_count = 0
    
    for i in range(count):
        try:
            # Datos básicos del pedido
            cliente = random.choice(clientes)
            fecha_pedido = fake.date_between(start_date='-30d', end_date='today')
            fecha_entrega = fecha_pedido + timedelta(days=random.randint(7, 21))
            
            pedido_data = {
                'cliente_id': cliente.id,
                'fecha_pedido': fecha_pedido,
                'fecha_entrega_estimada': fecha_entrega,
                'estado': random.choice(estados).value,
                'observaciones': fake.text(max_nb_chars=200),
                'descuento_porcentaje': random.choice([0, 5, 10, 15]),
                'subtotal': 0,
                'total': 0
            }
            
            pedido = Pedido(**pedido_data)
            
            # Generar items del pedido
            num_items = random.randint(1, 5)
            total_pedido = 0
            
            for j in range(num_items):
                producto = random.choice(productos)
                proceso = random.choice(procesos)
                cantidad = random.randint(1, 20)
                
                # Datos del item
                item_data = {
                    'producto_id': producto.id,
                    'proceso_id': proceso.id,
                    'cantidad': cantidad,
                    'precio_unitario': producto.precio_base,
                    'subtotal': producto.precio_base * cantidad
                }
                
                item = ItemPedido(**item_data)
                
                # Generar personalización
                if proceso.tipo in [TipoProceso.DTF.value, TipoProceso.SUBLIMACION.value, TipoProceso.VINIL.value]:
                    ancho = random.uniform(5, 25)
                    alto = random.uniform(5, 25)
                    area = ancho * alto
                    precio_proceso = max(area * proceso.precio_base_cm2, proceso.precio_minimo)
                    
                    personalizacion = PersonalizacionItem(
                        item_id=item.id,
                        ancho_cm=ancho,
                        alto_cm=alto,
                        area_cm2=area,
                        colores=random.randint(1, 4),
                        precio_proceso=precio_proceso,
                        observaciones=f"Diseño {fake.word()}"
                    )
                    
                elif proceso.tipo == TipoProceso.BORDADO.value:
                    tamaño = random.choice(['pequeño', 'mediano', 'grande'])
                    precio_proceso = proceso.precios_bordado.get(tamaño, 10.00)
                    
                    personalizacion = PersonalizacionItem(
                        item_id=item.id,
                        tamaño_bordado=tamaño,
                        colores=random.randint(1, 3),
                        precio_proceso=precio_proceso,
                        observaciones=f"Bordado {fake.word()}"
                    )
                
                item.personalizaciones = [personalizacion]
                item.subtotal += precio_proceso * cantidad
                total_pedido += item.subtotal
                
                pedido.items.append(item)
            
            # Calcular totales
            descuento = total_pedido * (pedido.descuento_porcentaje / 100)
            pedido.subtotal = total_pedido
            pedido.total = total_pedido - descuento
            
            # Guardar pedido
            if pedido.guardar():
                created_count += 1
                if created_count % 5 == 0:
                    print(f"   ✅ Creados {created_count}/{count} pedidos...")
            
        except Exception as e:
            print(f"   ❌ Error creando pedido {i+1}: {str(e)}")
    
    print(f"✅ {created_count} pedidos de prueba creados")


def generate_test_clients(count=30):
    """Genera clientes de prueba aleatorios."""
    print(f"👥 Generando {count} clientes de prueba...")
    
    tipos_cliente = ['INDIVIDUAL', 'EMPRESARIAL', 'INSTITUCIONAL']
    created_count = 0
    
    for i in range(count):
        try:
            tipo = random.choice(tipos_cliente)
            
            if tipo == 'INDIVIDUAL':
                nombre = fake.name()
                email = fake.email()
                descuento = 0.0
            elif tipo == 'EMPRESARIAL':
                nombre = fake.company()
                email = fake.company_email()
                descuento = random.choice([5.0, 8.0, 10.0, 12.0])
            else:  # INSTITUCIONAL
                nombre = f"{random.choice(['Colegio', 'Universidad', 'Instituto'])} {fake.last_name()}"
                email = fake.email()
                descuento = random.choice([10.0, 15.0, 20.0])
            
            cliente_data = {
                'nombre': nombre,
                'email': email,
                'telefono': fake.phone_number(),
                'direccion': fake.address(),
                'tipo_cliente': tipo,
                'descuento': descuento,
                'observaciones': fake.text(max_nb_chars=150) if random.random() > 0.5 else '',
                'activo': True,
                'fecha_registro': fake.date_between(start_date='-1y', end_date='today')
            }
            
            # Verificar que no exista el email
            existing = Cliente.buscar({'email': email})
            if existing:
                continue
            
            cliente = Cliente(**cliente_data)
            if cliente.guardar():
                created_count += 1
                if created_count % 10 == 0:
                    print(f"   ✅ Creados {created_count}/{count} clientes...")
            
        except Exception as e:
            print(f"   ❌ Error creando cliente {i+1}: {str(e)}")
    
    print(f"✅ {created_count} clientes de prueba creados")


def show_statistics():
    """Muestra estadísticas del sistema."""
    print("📊 Estadísticas del Sistema")
    print("=" * 40)
    
    # Estadísticas generales
    usuarios = Usuario.obtener_todos()
    clientes = Cliente.obtener_todos()
    productos = Producto.obtener_todos()
    procesos = Proceso.obtener_todos()
    pedidos = Pedido.obtener_todos()
    
    print(f"👤 Usuarios: {len(usuarios)}")
    print(f"👥 Clientes: {len(clientes)}")
    print(f"👕 Productos: {len(productos)}")
    print(f"🎨 Procesos: {len(procesos)}")
    print(f"📦 Pedidos: {len(pedidos)}")
    print()
    
    # Estadísticas de clientes por tipo
    if clientes:
        tipos_cliente = {}
        for cliente in clientes:
            tipo = cliente.tipo_cliente
            tipos_cliente[tipo] = tipos_cliente.get(tipo, 0) + 1
        
        print("Clientes por tipo:")
        for tipo, count in tipos_cliente.items():
            print(f"   {tipo}: {count}")
        print()
    
    # Estadísticas de productos por categoría
    if productos:
        categorias = {}
        for producto in productos:
            cat = producto.categoria
            categorias[cat] = categorias.get(cat, 0) + 1
        
        print("Productos por categoría:")
        for categoria, count in categorias.items():
            print(f"   {categoria}: {count}")
        print()
    
    # Estadísticas de pedidos por estado
    if pedidos:
        estados = {}
        total_ventas = 0
        for pedido in pedidos:
            estado = pedido.estado
            estados[estado] = estados.get(estado, 0) + 1
            total_ventas += pedido.total or 0
        
        print("Pedidos por estado:")
        for estado, count in estados.items():
            print(f"   {estado}: {count}")
        print()
        print(f"💰 Total en ventas: Q{total_ventas:.2f}")


def cleanup_test_data():
    """Limpia datos de prueba generados."""
    print("🧹 Limpiando datos de prueba...")
    
    response = input("⚠️  Esto eliminará pedidos y clientes de prueba. ¿Continuar? (y/N): ")
    if response.lower() != 'y':
        print("Operación cancelada.")
        return
    
    # Eliminar pedidos de prueba (últimos 30 días)
    pedidos = Pedido.obtener_todos()
    pedidos_eliminados = 0
    
    for pedido in pedidos:
        try:
            if hasattr(pedido, 'observaciones') and 'prueba' in (pedido.observaciones or '').lower():
                if pedido.eliminar():
                    pedidos_eliminados += 1
        except:
            pass
    
    # Eliminar clientes de prueba (emails de faker)
    clientes = Cliente.obtener_todos()
    clientes_eliminados = 0
    
    for cliente in clientes:
        try:
            if '@example' in cliente.email or 'test' in cliente.email.lower():
                if cliente.eliminar():
                    clientes_eliminados += 1
        except:
            pass
    
    print(f"✅ Limpieza completada:")
    print(f"   📦 Pedidos eliminados: {pedidos_eliminados}")
    print(f"   👥 Clientes eliminados: {clientes_eliminados}")


def main():
    """Función principal del script."""
    if len(sys.argv) < 2:
        print("🛠️  Utilidades de Desarrollo - Textiles ALS")
        print("=" * 50)
        print("Comandos disponibles:")
        print("  reset          - Resetear base de datos")
        print("  test-orders    - Generar pedidos de prueba")
        print("  test-clients   - Generar clientes de prueba")
        print("  stats          - Mostrar estadísticas")
        print("  cleanup        - Limpiar datos de prueba")
        print()
        print("Uso: python dev_utils.py <comando> [opciones]")
        return
    
    command = sys.argv[1]
    
    # Crear la aplicación Flask
    app = create_app()
    
    with app.app_context():
        try:
            if command == 'reset':
                reset_database()
            
            elif command == 'test-orders':
                count = int(sys.argv[2]) if len(sys.argv) > 2 else 20
                generate_test_orders(count)
            
            elif command == 'test-clients':
                count = int(sys.argv[2]) if len(sys.argv) > 2 else 30
                generate_test_clients(count)
            
            elif command == 'stats':
                show_statistics()
            
            elif command == 'cleanup':
                cleanup_test_data()
            
            else:
                print(f"❌ Comando desconocido: {command}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            sys.exit(1)


if __name__ == '__main__':
    main()
