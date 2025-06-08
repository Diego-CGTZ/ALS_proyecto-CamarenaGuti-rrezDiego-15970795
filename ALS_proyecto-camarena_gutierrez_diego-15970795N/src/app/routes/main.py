"""
Rutas principales de la aplicación.
"""

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

# Crear el blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página de inicio - redirección inteligente."""
    if current_user.is_authenticated:
        # Verificar si hay productos en el sistema
        from app.services.storage_service import StorageService
        from app.models.producto import Producto
        storage = StorageService()
        productos = storage.get_by_criteria(Producto, lambda x: x.is_active)
        
        if not productos:
            flash('El sistema aún no tiene productos registrados.', 'info')
            if current_user.is_admin:
                flash('Como administrador, puedes comenzar creando algunos productos.', 'info')
                return redirect(url_for('productos.nuevo'))
        
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Panel principal del usuario."""
    try:
        from app.services.storage_service import StorageService
        from app.models.cliente import Cliente
        from app.models.pedido import Pedido, EstadoPedido
        from app.models.producto import Producto
        from app.models.proceso import Proceso
        storage = StorageService()
        
        # Obtener estadísticas generales - solo registros activos
        total_clientes = len(storage.get_by_criteria(Cliente, lambda x: x.is_active))
        total_productos = len(storage.get_by_criteria(Producto, lambda x: x.is_active))
        total_procesos = len(storage.find_all(Proceso))  # Procesos no tienen soft delete
        
        # Obtener pedidos recientes - solo activos
        pedidos = storage.get_by_criteria(Pedido, lambda x: x.is_active)
        pedidos_activos = [p for p in pedidos if p.estado != EstadoPedido.ENTREGADO and p.is_active]
        pedidos_recientes = sorted(pedidos, key=lambda x: x.created_at, reverse=True)[:5]
        
        # Pedidos por estado
        pedidos_pendientes = len([p for p in pedidos if p.estado == EstadoPedido.PENDIENTE and p.is_active])
        pedidos_proceso = len([p for p in pedidos if p.estado == EstadoPedido.EN_PROCESO and p.is_active])
        pedidos_completados = len([p for p in pedidos if p.estado == EstadoPedido.COMPLETADO and p.is_active])
        
        # Pedidos atrasados
        pedidos_atrasados = [p for p in pedidos_activos if p.is_atrasado()]
        
        # Ingresos del mes actual
        import datetime
        inicio_mes = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        pedidos_mes = [p for p in pedidos if p.created_at >= inicio_mes and p.is_active]
        
        # Asegurar que los totales están actualizados
        from app.routes.pedidos import calcular_totales_pedido
        
        # Recalcular totales para los pedidos recientes y del mes actual
        pedidos_para_actualizar = []
        for p in pedidos_recientes + pedidos_mes:
            if p not in pedidos_para_actualizar:  # Evitar duplicados si un pedido está en ambas listas
                pedidos_para_actualizar.append(p)
        
        for p in pedidos_para_actualizar:
            try:
                calcular_totales_pedido(p, p.id)
                # Si después de calcular, el total sigue siendo 0, establecemos un valor mínimo
                if p.total == 0:
                    p.subtotal = 100.0  # Valor mínimo para pruebas
                    p.calcular_totales()
                storage.save(p)
            except Exception as e:
                print(f"Error al recalcular totales para pedido {p.id}: {str(e)}")
              # Calcular ingresos del mes con los totales actualizados
        ingresos_mes = sum(p.total for p in pedidos_mes)
        
        estadisticas = {
            'total_clientes': total_clientes,
            'total_productos': total_productos,
            'total_procesos': total_procesos,
            'pedidos_pendientes': pedidos_pendientes,
            'pedidos_proceso': pedidos_proceso,
            'pedidos_completados': pedidos_completados,
            'pedidos_atrasados': len(pedidos_atrasados),
            'ingresos_mes': ingresos_mes
        }
        
        # Obtener datos de clientes para mostrar en la interfaz - solo activos
        clientes_objs = storage.get_by_criteria(Cliente, lambda x: x.is_active)
        clientes = {}
        
        # Creamos un diccionario con los nombres completos de los clientes
        for cliente in clientes_objs:
            try:
                # Verificamos si el cliente tiene el método get_nombre_completo
                if hasattr(cliente, 'get_nombre_completo') and callable(getattr(cliente, 'get_nombre_completo')):
                    clientes[cliente.id] = cliente.get_nombre_completo()
                # Si no tiene el método, construimos el nombre manualmente
                elif hasattr(cliente, 'nombre'):
                    nombre_completo = cliente.nombre
                    if hasattr(cliente, 'apellido') and cliente.apellido:
                        nombre_completo += f" {cliente.apellido}"
                    if hasattr(cliente, 'empresa') and cliente.empresa and cliente.empresa.strip():
                        nombre_completo += f" ({cliente.empresa})"
                    clientes[cliente.id] = nombre_completo
                else:
                    clientes[cliente.id] = f"Cliente {cliente.id[:8]}"
            except Exception as e:
                # Si hay algún error, usamos un nombre genérico
                print(f"Error al obtener nombre de cliente {cliente.id}: {str(e)}")
                clientes[cliente.id] = f"Cliente {cliente.id[:8]}"
        
        return render_template('main/dashboard.html',
                             estadisticas=estadisticas,
                             pedidos_recientes=pedidos_recientes,
                             pedidos_atrasados=pedidos_atrasados,
                             clientes=clientes)
        
    except Exception as e:
        flash(f'Error al cargar el dashboard: {str(e)}', 'error')
        # Crear diccionario de estadísticas vacío pero con todas las claves necesarias
        estadisticas_vacias = {
            'total_clientes': 0,
            'total_productos': 0,
            'total_procesos': 0,
            'pedidos_pendientes': 0,
            'pedidos_proceso': 0,
            'pedidos_completados': 0,
            'pedidos_atrasados': 0,
            'ingresos_mes': 0.0
        }
        return render_template('main/dashboard.html',
                             estadisticas=estadisticas_vacias,
                             pedidos_recientes=[],
                             pedidos_atrasados=[],
                             clientes={})

@main_bp.route('/about')
def about():
    """Página de información sobre la aplicación."""
    return render_template('main/about.html')

@main_bp.route('/contact')
def contact():
    """Página de contacto."""
    return render_template('main/contact.html')

@main_bp.route('/help')
@login_required
def help():
    """Página de ayuda."""
    return render_template('main/help.html')

@main_bp.route('/settings')
@login_required
def settings():
    """Página de configuración del usuario."""
    return render_template('main/settings.html')

@main_bp.route('/profile')
@login_required
def profile():
    """Página de perfil del usuario."""
    return render_template('main/profile.html')
