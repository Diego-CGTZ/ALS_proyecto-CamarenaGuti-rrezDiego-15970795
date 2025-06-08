"""
Rutas para gestión de productos (prendas).
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.forms.producto_forms import ProductoForm, BuscarProductoForm
from app.models.producto import Producto
from app.models.pedido import ItemPedido
from app.services.storage_service import StorageService

productos_bp = Blueprint('productos', __name__)


@productos_bp.route('/')
@login_required
def listar():
    """Listar todos los productos con búsqueda."""
    form = BuscarProductoForm()
    storage = StorageService()
    
    try:
        productos = storage.find_all(Producto)
        productos_activos = [p for p in productos if p.is_active]
        
        # Aplicar filtro de búsqueda si se proporciona
        if form.validate_on_submit() and form.termino_busqueda.data:
            termino = form.termino_busqueda.data.lower()
            productos_filtrados = []
            
            for producto in productos_activos:
                if (termino in producto.nombre.lower() or
                    termino in producto.categoria.lower() or
                    termino in producto.descripcion.lower()):
                    productos_filtrados.append(producto)
            
            productos_activos = productos_filtrados
        
        # Ordenar por categoría y luego por nombre
        productos_activos.sort(key=lambda x: (x.categoria, x.nombre))
        
        return render_template('productos/index.html',
                             productos=productos_activos,
                             form=form)
        
    except Exception as e:
        flash(f'Error al cargar los productos: {str(e)}', 'error')
        return render_template('productos/index.html',
                             productos=[],
                             form=form)


@productos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    """Crear un nuevo producto."""
    form = ProductoForm()
    
    if form.validate_on_submit():
        storage = StorageService()
        
        try:
            # Procesar tallas y colores
            form.validate_tallas_disponibles(form.tallas_disponibles)
            form.validate_colores_disponibles(form.colores_disponibles)
            
            # Crear nuevo producto
            producto = Producto(
                nombre=form.nombre.data,
                categoria=form.categoria.data,
                precio_base=form.precio_base.data,
                descripcion=form.descripcion.data or "",
                tallas_disponibles=form.tallas_disponibles.processed_data,
                colores_disponibles=form.colores_disponibles.processed_data
            )
              # Guardar producto
            producto_id = storage.save(producto)
            
            if producto_id:
                flash(f'Producto "{producto.nombre}" creado exitosamente.', 'success')
                return redirect(url_for('productos.ver', id=producto_id))
            else:
                flash('Error al crear el producto. Inténtalo de nuevo.', 'error')
                
        except Exception as e:
            flash(f'Error al crear el producto: {str(e)}', 'error')
    
    # Create an empty product object for the form template
    producto_vacio = Producto(nombre="", categoria="", precio_base=0.0, descripcion="")
    return render_template('productos/form.html', form=form, producto=producto_vacio)


@productos_bp.route('/<id>')
@login_required
def ver(id):
    """Ver detalles de un producto específico."""
    storage = StorageService()
    
    try:
        producto = storage.load(id)
        
        if not producto:
            flash('El producto solicitado no existe.', 'error')
            return redirect(url_for('productos.listar'))
            
        if not isinstance(producto, Producto):
            flash('Tipo de producto inválido.', 'error')
            return redirect(url_for('productos.listar'))
            
        if not producto.is_active:
            flash('Este producto ha sido eliminado.', 'error')
            return redirect(url_for('productos.listar'))
        
        # Obtener estadísticas de uso del producto
        items_pedido = storage.find_by_condition(
            ItemPedido,
            lambda i: i.producto_id == id and i.is_active
        )
        
        total_vendido = sum(item.cantidad for item in items_pedido)
        ingresos_generados = sum(item.subtotal_total for item in items_pedido)
        
        estadisticas = {
            'total_vendido': total_vendido,
            'ingresos_generados': ingresos_generados,
            'pedidos_incluido': len(items_pedido)
        }
        
        return render_template('productos/ver.html',
                             producto=producto,
                             estadisticas=estadisticas)
        
    except Exception as e:
        flash(f'Error al cargar el producto: {str(e)}', 'error')
        return redirect(url_for('productos.listar'))


@productos_bp.route('/<id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar un producto existente."""
    storage = StorageService()
    
    try:
        producto = storage.load(id)
        
        if not producto or not producto.is_active or not isinstance(producto, Producto):
            flash('Producto no encontrado.', 'error')
            return redirect(url_for('productos.listar'))
        
        # Preparar datos para el formulario
        form_data = {
            'nombre': producto.nombre,
            'categoria': producto.categoria,
            'precio_base': producto.precio_base,
            'descripcion': producto.descripcion,
            'tallas_disponibles': ','.join(producto.tallas_disponibles),
            'colores_disponibles': ','.join(producto.colores_disponibles)
        }
        
        form = ProductoForm(data=form_data)
        
        if form.validate_on_submit():
            # Procesar tallas y colores
            form.validate_tallas_disponibles(form.tallas_disponibles)
            form.validate_colores_disponibles(form.colores_disponibles)
            
            # Actualizar datos del producto
            producto.nombre = form.nombre.data
            producto.categoria = form.categoria.data
            producto.precio_base = form.precio_base.data
            producto.descripcion = form.descripcion.data or ""
            producto.tallas_disponibles = form.tallas_disponibles.processed_data
            producto.colores_disponibles = form.colores_disponibles.processed_data
            producto.update_timestamp()
              # Guardar cambios
            storage.save(producto)
            flash(f'Producto "{producto.nombre}" actualizado exitosamente.', 'success')
            return redirect(url_for('productos.ver', id=id))
        
        return render_template('productos/form.html',
                             form=form,
                             producto=producto)
        
    except Exception as e:
        flash(f'Error al editar el producto: {str(e)}', 'error')
        return redirect(url_for('productos.listar'))


@productos_bp.route('/<id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    """Eliminar (soft delete) un producto."""
    print(f"[DEBUG] === INICIO ELIMINACIÓN ===")
    print(f"[DEBUG] ID del producto: {id}")
    print(f"[DEBUG] Método de la petición: {request.method}")
    print(f"[DEBUG] Headers: {dict(request.headers)}")
    print(f"[DEBUG] Form data: {dict(request.form)}")
    
    storage = StorageService()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        producto = storage.load(id)
        print(f"[DEBUG] Producto encontrado: {producto.nombre if producto else 'None'}")
        
        if not producto:
            print(f"[DEBUG] ERROR: Producto no encontrado con ID {id}")
            mensaje = 'Producto no encontrado.'
            if is_ajax:
                return {'success': False, 'message': mensaje}, 404
            flash(mensaje, 'error')
            return redirect(url_for('productos.listar'))
            
        if not producto.is_active:
            print(f"[DEBUG] ERROR: Producto ya está inactivo")
            mensaje = 'El producto ya está eliminado.'
            if is_ajax:
                return {'success': False, 'message': mensaje}, 400
            flash(mensaje, 'warning')
            return redirect(url_for('productos.listar'))
            
        if not isinstance(producto, Producto):
            print(f"[DEBUG] ERROR: Objeto no es instancia de Producto")
            mensaje = 'Error en el tipo de objeto.'
            if is_ajax:
                return {'success': False, 'message': mensaje}, 400
            flash(mensaje, 'error')
            return redirect(url_for('productos.listar'))
            
        # Verificar si el producto está siendo usado en pedidos activos
        items_activos = storage.find_by_condition(
            ItemPedido,
            lambda i: i.producto_id == id and i.is_active
        )
        print(f"[DEBUG] Items activos encontrados: {len(items_activos)}")
        
        if items_activos:
            print(f"[DEBUG] Producto está en uso en pedidos")
            # Verificar si algún item pertenece a un pedido activo
            from app.models.pedido import Pedido, EstadoPedido
            
            for item in items_activos:
                pedidos_con_item = storage.find_by_condition(
                    Pedido,
                    lambda p: item.id in p.items and p.is_active and p.estado != EstadoPedido.ENTREGADO
                )
                
                if pedidos_con_item:
                    print(f"[DEBUG] Producto en pedidos activos, no se puede eliminar")
                    mensaje = f'No se puede eliminar el producto "{producto.nombre}" porque está siendo usado en pedidos activos.'
                    if is_ajax:
                        return {'success': False, 'message': mensaje}, 400
                    flash(mensaje, 'warning')
                    return redirect(url_for('productos.ver', id=id))
        
        # Realizar soft delete
        print(f"[DEBUG] Procediendo con la eliminación del producto")
        producto.soft_delete()
        storage.save(producto)
        
        print(f"[DEBUG] Producto eliminado correctamente")
        mensaje = f'Producto "{producto.nombre}" eliminado correctamente.'
        
        if is_ajax:
            return {
                'success': True, 
                'message': mensaje,
                'producto_id': id,
                'producto_nombre': producto.nombre
            }
        
        flash(mensaje, 'success')
        return redirect(url_for('productos.listar'))
        
    except Exception as e:
        print(f"[DEBUG] Error al eliminar producto: {str(e)}")
        mensaje = f'Error al eliminar el producto: {str(e)}'
        
        if is_ajax:
            return {'success': False, 'message': mensaje}, 500
            
        flash(mensaje, 'error')
        return redirect(url_for('productos.ver', id=id))


@productos_bp.route('/categorias')
@login_required
def categorias():
    """Ver productos agrupados por categorías."""
    storage = StorageService()
    
    try:
        productos = storage.find_all(Producto)
        productos_activos = [p for p in productos if p.is_active]
        
        # Agrupar por categorías
        categorias = {}
        for producto in productos_activos:
            categoria = producto.categoria
            if categoria not in categorias:
                categorias[categoria] = []
            categorias[categoria].append(producto)
        
        # Ordenar productos dentro de cada categoría
        for categoria in categorias:
            categorias[categoria].sort(key=lambda x: x.nombre)
        
        return render_template('productos/categorias.html',
                             categorias=categorias)
        
    except Exception as e:
        flash(f'Error al cargar las categorías: {str(e)}', 'error')
        return render_template('productos/categorias.html',
                             categorias={})
