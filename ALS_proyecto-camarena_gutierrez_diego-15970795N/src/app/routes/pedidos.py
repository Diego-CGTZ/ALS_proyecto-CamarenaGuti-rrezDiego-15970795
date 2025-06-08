"""
Rutas para la gestión de pedidos - Versión corregida.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from werkzeug.exceptions import NotFound
from datetime import datetime
import uuid
import json
import traceback
import uuid
import json
import traceback

from app.models.pedido import Pedido, ItemPedido, Personalizacion
from app.models.cliente import Cliente
from app.models.producto import Producto
from app.models.proceso import Proceso, TipoProceso, TamañoBordado
from app.forms.pedido_forms import PedidoForm, ItemPedidoForm, PersonalizacionForm
from app.services.storage_service import StorageService

pedidos_bp = Blueprint('pedidos', __name__, url_prefix='/pedidos')
storage = StorageService()


def calcular_totales_pedido(pedido, pedido_id):
    """
    Calcular totales de un pedido de forma segura.
    
    Args:
        pedido: El objeto pedido
        pedido_id: ID del pedido para buscar items
    """
    try:
        # Buscar los items del pedido que estén activos (no eliminados)
        items = storage.get_by_criteria(ItemPedido, lambda x: x.pedido_id == pedido_id and x.is_active)
        
        # Actualizar el contador de items
        pedido.num_items = len(items)
        
        if items:
            # Recorremos cada item para asegurarnos de que sus subtotales estén actualizados
            for item in items:
                # Recalculamos el subtotal del item (precio unitario * cantidad)
                item.subtotal = item.precio_prenda * item.cantidad
                
                # Obtener y recalcular personalizaciones del item
                personalizaciones = storage.get_by_criteria(
                    Personalizacion, lambda x: x.item_pedido_id == item.id and x.is_active
                )
                
                # Recalcular subtotales de personalizaciones
                for pers in personalizaciones:
                    pers.subtotal = pers.precio_proceso * pers.cantidad
                    storage.save(pers)
                
                # Actualizar el subtotal de personalizaciones del item
                item.subtotal_personalizaciones = sum(p.subtotal for p in personalizaciones)
                
                # Guardar el item actualizado
                storage.save(item)
            
            # Calcular los subtotales del pedido completo
            subtotal_items = sum(item.subtotal for item in items)
            subtotal_personalizaciones = sum(item.subtotal_personalizaciones for item in items)
            
            # Calcular totales
            pedido.subtotal = subtotal_items + subtotal_personalizaciones
            pedido.calcular_totales()  # Esto calculará utilidad, IVA y total
        else:
            # Si no hay items, establecer totales en 0
            pedido.subtotal = 0.0
            pedido.calcular_totales()
            
        pedido.update_timestamp()
        
    except Exception as e:
        print(f"Error calculando totales: {e}")
        traceback.print_exc()
        # Establecer valores seguros en caso de error
        pedido.subtotal = 0.0
        pedido.iva = 0.0
        pedido.total = 0.0
        pedido.utilidad = 0.0
        pedido.saldo_pendiente = 0.0
        pedido.pago_completo = True


@pedidos_bp.route('/')
@login_required
def index():
    """Lista todos los pedidos activos (no eliminados)."""
    try:
        print("=== DEBUG PEDIDOS INDEX ===")
        # Filtrar solo pedidos activos (no eliminados con soft delete)
        pedidos = storage.get_by_criteria(Pedido, lambda x: x.is_active)
        print(f"Total pedidos activos encontrados: {len(pedidos)}")
        
        # Filtros opcionales
        estado = request.args.get('estado')
        cliente_id = request.args.get('cliente_id')
        prioridad = request.args.get('prioridad')
        print(f"Filtros aplicados - Estado: {estado}, Cliente: {cliente_id}, Prioridad: {prioridad}")
        
        if estado:
            # Manejar correctamente la comparación del enum
            pedidos = [p for p in pedidos if (
                (isinstance(p.estado, str) and p.estado == estado) or 
                (hasattr(p.estado, 'value') and p.estado.value == estado)
            )]
        
        if cliente_id:
            pedidos = [p for p in pedidos if p.cliente_id == cliente_id]
        
        if prioridad:
            # Manejar correctamente la comparación del enum de prioridad
            pedidos = [p for p in pedidos if (
                (isinstance(p.prioridad, str) and p.prioridad == prioridad) or 
                (hasattr(p.prioridad, 'value') and p.prioridad.value == prioridad)
            )]
                # Obtener clientes activos para el filtro
        clientes = storage.get_by_criteria(Cliente, lambda x: x.is_active)
        print(f"Total clientes activos encontrados: {len(clientes)}")
        
        # Incluir fecha actual para comparaciones en el template
        now = datetime.now()
        
        print(f"Enviando a template: {len(pedidos)} pedidos, {len(clientes)} clientes")
        return render_template('pedidos/index.html', 
                             pedidos=pedidos, 
                             clientes=clientes,
                             now=now)
    except Exception as e:
        print(f"ERROR en pedidos.index: {e}")
        traceback.print_exc()
        flash(f'Error al cargar pedidos: {str(e)}', 'error')
        return render_template('pedidos/index.html', 
                             pedidos=[], 
                             clientes=[])


@pedidos_bp.route('/crear', methods=['GET'])
@login_required
def crear():
    """Redirigir al paso 1 del nuevo flujo."""
    return redirect(url_for('pedidos.crear_paso1'))


@pedidos_bp.route('/crear/paso1', methods=['GET', 'POST'])
@login_required
def crear_paso1():
    """Paso 1: Información básica del pedido."""
    storage = StorageService()
    form = PedidoForm()
    clientes = storage.get_by_criteria(Cliente, lambda x: x.is_active)
    form.cliente_id.choices = [(c.id, c.get_nombre_completo()) for c in clientes]
    
    if form.validate_on_submit():
        # VALIDACIÓN DE INTEGRIDAD REFERENCIAL: Verificar que el cliente existe
        cliente_valido, mensaje_error = Pedido.validar_cliente_existe(form.cliente_id.data, storage)
        if not cliente_valido:
            flash(f'Error: {mensaje_error}', 'error')
            return render_template('pedidos/form_step1.html', form=form)
        
        # Guardar datos en sesión temporal
        pedido_temp_id = str(uuid.uuid4())
        session['pedido_temp_id'] = pedido_temp_id
        session['pedido_data'] = {
            'cliente_id': form.cliente_id.data,
            'fecha_entrega': str(form.fecha_entrega.data),
            'prioridad': form.prioridad.data,
            'descripcion': form.descripcion.data,
            'porcentaje_utilidad': float(form.porcentaje_utilidad.data)
        }
        return redirect(url_for('pedidos.crear_paso2'))
    
    return render_template('pedidos/form_step1.html', form=form)


@pedidos_bp.route('/crear/paso2', methods=['GET', 'POST'])
@login_required
def crear_paso2():
    """Paso 2: Configurar productos del pedido."""
    pedido_data = session.get('pedido_data')
    pedido_temp_id = session.get('pedido_temp_id')
    
    if not pedido_data:
        flash('Primero completa la información básica del pedido.', 'warning')
        return redirect(url_for('pedidos.crear_paso1'))
    
    if request.method == 'POST':
        products_data = request.form.get('products_data')
        
        if not products_data:
            flash('Debes agregar al menos un producto al pedido.', 'warning')
            return redirect(url_for('pedidos.crear_paso2'))
        
        try:
            products = json.loads(products_data)
            
            # VALIDACIÓN DE INTEGRIDAD REFERENCIAL: Verificar que el cliente existe
            cliente_id = pedido_data['cliente_id']
            cliente_valido, mensaje_error = Pedido.validar_cliente_existe(cliente_id, storage)
            if not cliente_valido:
                flash(f'Error: {mensaje_error}', 'error')
                session.pop('pedido_data', None)
                session.pop('pedido_temp_id', None)
                return redirect(url_for('pedidos.crear_paso1'))
            
            # Crear el pedido
            pedido = Pedido(
                cliente_id=pedido_data['cliente_id'],
                descripcion=pedido_data.get('descripcion', ''),
                fecha_entrega_estimada=datetime.fromisoformat(pedido_data['fecha_entrega']),
                prioridad=pedido_data.get('prioridad'),
                porcentaje_utilidad=pedido_data.get('porcentaje_utilidad', 30.0)
            )
            
            pedido_id = storage.save(pedido)
            
            # Crear items
            for prod in products:
                item = ItemPedido(
                    producto_id=prod['producto_id'],
                    talla=prod.get('talla', ''),
                    color=prod.get('color', ''),
                    cantidad=prod.get('cantidad', 1),
                    precio_prenda=prod.get('precio_base', 0.0)
                )
                item.pedido_id = pedido_id
                item.subtotal = item.precio_prenda * item.cantidad
                
                # Calcular costo de diseños
                designs_cost = 0
                for design in prod.get('designs', []):
                    designs_cost += design.get('precio', 0)
                
                item.subtotal_personalizaciones = designs_cost * item.cantidad
                
                storage.save(item)
            
            # Recalcular totales
            calcular_totales_pedido(pedido, pedido_id)
            storage.save(pedido)
            
            # Limpiar sesión temporal
            session.pop('pedido_data', None)
            session.pop('pedido_temp_id', None)
            
            flash('Pedido creado exitosamente.', 'success')
            return redirect(url_for('pedidos.detalle', id=pedido_id))
            
        except Exception as e:
            flash(f'Error al crear el pedido: {str(e)}', 'error')
      # Create a basic form for the template
    from flask_wtf import FlaskForm
    form = FlaskForm()
    
    return render_template('pedidos/form_step2.html', 
                         form=form,
                         pedido_data=pedido_data, 
                         pedido_temp_id=pedido_temp_id)


@pedidos_bp.route('/<string:id>')
@login_required
def detalle(id):
    """Ver detalles de un pedido."""
    try:
        pedido = storage.get(Pedido, id)
        if not pedido or not pedido.is_active:
            raise NotFound("Pedido no encontrado")
        
        # Obtener datos relacionados
        cliente = storage.get(Cliente, pedido.cliente_id)
        items = storage.get_by_criteria(ItemPedido, lambda x: x.pedido_id == id and x.is_active)
          # Cargar productos y procesos para cada item
        for item in items:
            item.producto = storage.get(Producto, item.producto_id)
            item.personalizaciones = storage.get_by_criteria(
                Personalizacion, 
                lambda x: x.item_pedido_id == item.id and x.is_active
            )
            for pers in item.personalizaciones:
                pers.proceso = storage.get(Proceso, pers.proceso_id)
        
        return render_template('pedidos/detalle.html',
                             pedido=pedido,
                             cliente=cliente,
                             items=items,
                             fecha_actual=datetime.now().date())
                             
    except NotFound:
        flash('Pedido no encontrado', 'error')
        return redirect(url_for('pedidos.index'))
    except Exception as e:
        flash(f'Error al cargar pedido: {str(e)}', 'error')
        return redirect(url_for('pedidos.index'))


@pedidos_bp.route('/<string:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar un pedido existente."""
    try:
        pedido = storage.get(Pedido, id)
        if not pedido or not pedido.is_active:
            raise NotFound("Pedido no encontrado")
        
        form = PedidoForm(obj=pedido)        
        # Cargar opciones para el formulario
        clientes = storage.get_by_criteria(Cliente, lambda x: x.is_active)
        form.cliente_id.choices = [(c.id, c.get_nombre_completo()) for c in clientes]
        
        if form.validate_on_submit():
            # VALIDACIÓN DE INTEGRIDAD REFERENCIAL: Verificar que el cliente existe
            cliente_valido, mensaje_error = Pedido.validar_cliente_existe(form.cliente_id.data, storage)
            if not cliente_valido:
                flash(f'Error: {mensaje_error}', 'error')
                return render_template('pedidos/form.html',
                                     form=form,
                                     pedido=pedido,
                                     titulo='Editar Pedido',
                                     action=url_for('pedidos.editar', id=id))
            
            # Actualizar los campos del pedido
            pedido.cliente_id = form.cliente_id.data
            pedido.fecha_entrega_estimada = form.fecha_entrega.data
            
            # Actualizar porcentaje de utilidad y recalcular
            if pedido.porcentaje_utilidad != form.porcentaje_utilidad.data:
                pedido.porcentaje_utilidad = form.porcentaje_utilidad.data
            
            # Actualizar otros campos si están disponibles
            if hasattr(form, 'prioridad') and form.prioridad.data:
                pedido.prioridad = form.prioridad.data
                
            if form.notas.data:
                pedido.notas = form.notas.data
                
            if hasattr(form, 'descuento_porcentaje'):
                pedido.descuento_porcentaje = form.descuento_porcentaje.data or 0
            
            # Recalcular totales con el nuevo porcentaje de utilidad
            calcular_totales_pedido(pedido, id)
            
            storage.save(pedido)
            flash('Pedido actualizado exitosamente', 'success')
            return redirect(url_for('pedidos.detalle', id=id))
        
        return render_template('pedidos/form.html',
                             form=form,
                             pedido=pedido,
                             titulo='Editar Pedido',
                             action=url_for('pedidos.editar', id=id))
                             
    except NotFound:
        flash('Pedido no encontrado', 'error')
        return redirect(url_for('pedidos.index'))
    except Exception as e:
        flash(f'Error al editar pedido: {str(e)}', 'error')
        return redirect(url_for('pedidos.index'))


@pedidos_bp.route('/<string:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    """Eliminar un pedido."""
    try:
        pedido = storage.get(Pedido, id)
        if not pedido or not pedido.is_active:
            raise NotFound("Pedido no encontrado")
        
        # Soft delete
        pedido.soft_delete()
        storage.save(pedido)
        
        flash('Pedido eliminado exitosamente', 'success')
        
    except NotFound:
        flash('Pedido no encontrado', 'error')
    except Exception as e:
        flash(f'Error al eliminar pedido: {str(e)}', 'error')
    
    return redirect(url_for('pedidos.index'))


@pedidos_bp.route('/api/productos')
@login_required
def api_productos():
    """API endpoint para obtener todos los productos activos."""
    try:
        productos = storage.get_by_criteria(Producto, lambda x: x.is_active)
        productos_data = []
        
        for producto in productos:
            productos_data.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'categoria': producto.categoria,
                'precio_base': float(producto.precio_base),
                'descripcion': producto.descripcion or ''
            })
        
        return jsonify(productos_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pedidos_bp.route('/api/producto/<string:producto_id>')
@login_required
def api_producto_detalle(producto_id):
    """API endpoint para obtener detalles de un producto específico."""
    try:
        producto = storage.get(Producto, producto_id)
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        return jsonify({
            'id': producto.id,
            'nombre': producto.nombre,
            'categoria': producto.categoria,
            'precio_base': float(producto.precio_base),
            'descripcion': producto.descripcion or '',
            'tallas_disponibles': producto.tallas_disponibles or [],
            'colores_disponibles': producto.colores_disponibles or []
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pedidos_bp.route('/api/procesos')
@login_required
def api_procesos():
    """API endpoint para obtener todos los procesos disponibles."""
    try:
        procesos = storage.find_all(Proceso)
        procesos_data = []
        
        for proceso in procesos:
            # Get base price depending on process type
            precio_base = 0.0
            if hasattr(proceso, 'precio_por_metro'):
                precio_base = float(proceso.precio_por_metro)
            elif hasattr(proceso, 'precio_setup'):
                precio_base = float(proceso.precio_setup)
            elif hasattr(proceso, 'precio_por_cm2'):
                precio_base = float(proceso.precio_por_cm2)
            
            procesos_data.append({
                'id': proceso.id,
                'nombre': proceso.nombre,
                'tipo': proceso.tipo.value if hasattr(proceso.tipo, 'value') else str(proceso.tipo),
                'precio_base': precio_base,
                'descripcion': proceso.descripcion or ''
            })
        
        return jsonify(procesos_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pedidos_bp.route('/api/proceso/<string:proceso_id>')
@login_required
def api_proceso_detalle(proceso_id):
    """API endpoint para obtener detalles de un proceso específico."""
    try:
        proceso = storage.get(Proceso, proceso_id)
        if not proceso:
            return jsonify({'error': 'Proceso no encontrado'}), 404
        
        # Determinar el precio base según el tipo de proceso
        precio_base = 0.0
        if hasattr(proceso, 'precio_por_metro'):
            precio_base = float(proceso.precio_por_metro)
        elif hasattr(proceso, 'precio_setup'):
            precio_base = float(proceso.precio_setup)
        elif hasattr(proceso, 'precio_por_cm2'):
            precio_base = float(proceso.precio_por_cm2)
        
        return jsonify({
            'id': proceso.id,
            'nombre': proceso.nombre,
            'tipo': proceso.tipo.value if hasattr(proceso.tipo, 'value') else str(proceso.tipo),
            'precio_base': precio_base,
            'descripcion': proceso.descripcion or ''
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pedidos_bp.route('/agregar_item/<string:pedido_id>', methods=['GET', 'POST'])
@login_required
def agregar_item(pedido_id):
    """Agregar un item a un pedido existente."""
    try:
        pedido = storage.get(Pedido, pedido_id)
        if not pedido or not pedido.is_active:
            raise NotFound("Pedido no encontrado")
          # Crear formulario para el item
        form = ItemPedidoForm()
        
        # Cargar opciones para el formulario
        productos = storage.get_by_criteria(Producto, lambda x: x.is_active)
        form.producto_id.choices = [(p.id, p.nombre) for p in productos]
          # Valores predeterminados para talla y color (se actualizarán por AJAX)
        form.talla.choices = [('', 'Seleccione un producto primero')]
        form.color.choices = [('', 'Seleccione un producto primero')]
        
        if form.validate_on_submit():
            # Crear nuevo item
            item = ItemPedido(
                producto_id=form.producto_id.data,
                talla=form.talla.data,
                color=form.color.data,
                cantidad=form.cantidad.data,
                precio_prenda=form.precio_prenda.data
            )
            item.pedido_id = pedido_id
            item.subtotal = item.precio_prenda * item.cantidad
            
            # Guardar el item
            item_id = storage.save(item)
            
            # Procesar diseños/personalizaciones si existen
            designs_data = request.form.get('designs_data')
            if designs_data:
                try:
                    designs = json.loads(designs_data)
                    for design_id, design_info in designs.items():
                        if design_info.get('proceso_id') and design_info.get('posicion'):
                            personalizacion = Personalizacion(
                                proceso_id=design_info['proceso_id'],
                                posicion=int(design_info['posicion']),
                                descripcion=design_info.get('descripcion', ''),
                                ancho=float(design_info.get('ancho', 0)) if design_info.get('ancho') else None,
                                alto=float(design_info.get('alto', 0)) if design_info.get('alto') else None
                            )
                            personalizacion.item_id = item_id
                            
                            # Calcular costo de la personalización
                            proceso = storage.get(Proceso, design_info['proceso_id'])
                            if proceso:
                                personalizacion.costo_personalizacion = proceso.precio * item.cantidad
                                personalizacion.costo_unitario = proceso.precio
                            
                            storage.save(personalizacion)
                except Exception as e:
                    print(f"Error procesando diseños: {e}")
            
            # Recalcular totales del pedido incluyendo personalizaciones
            calcular_totales_pedido(pedido, pedido_id)
            storage.save(pedido)
            
            flash('Item agregado exitosamente al pedido', 'success')
            return redirect(url_for('pedidos.detalle', id=pedido_id))
        
        return render_template('pedidos/item_form.html',
                              form=form,
                              pedido=pedido,
                              titulo='Agregar Item al Pedido',
                              action=url_for('pedidos.agregar_item', pedido_id=pedido_id))
        
    except NotFound:
        flash('Pedido no encontrado', 'error')
        return redirect(url_for('pedidos.index'))
    except Exception as e:
        flash(f'Error al agregar item: {str(e)}', 'error')
        return redirect(url_for('pedidos.detalle', id=pedido_id))


@pedidos_bp.route('/agregar_personalizacion/<string:item_id>', methods=['GET', 'POST'])
@login_required
def agregar_personalizacion(item_id):
    """Agregar una personalización a un item de pedido."""
    try:
        item = storage.get(ItemPedido, item_id)
        if not item or not item.is_active:
            raise NotFound("Item de pedido no encontrado")
        
        # Obtenemos el pedido al que pertenece el item
        pedido = storage.get(Pedido, item.pedido_id)
        if not pedido or not pedido.is_active:
            raise NotFound("Pedido asociado no encontrado")
        
        # Crear formulario para la personalización
        form = PersonalizacionForm()
        
        # Cargar opciones para el formulario
        procesos = storage.find_all(Proceso)
        form.proceso_id.choices = [(p.id, f"{p.nombre} ({p.tipo})") for p in procesos]
        
        if form.validate_on_submit():
            # Crear nueva personalización
            personalizacion = Personalizacion(
                proceso_id=form.proceso_id.data,
                precio_proceso=form.precio.data,
                cantidad=form.cantidad.data or 1
            )
            personalizacion.item_pedido_id = item_id
            personalizacion.descripcion = form.descripcion.data or ""
            personalizacion.ancho = form.ancho.data or 0
            personalizacion.alto = form.alto.data or 0
            personalizacion.colores = form.colores.data or ""
            personalizacion.cantidad_colores = form.cantidad_colores.data or 1
            personalizacion.notas = form.notas.data or ""
            
            # Guardar la personalización
            pers_id = storage.save(personalizacion)
            
            # Actualizar subtotales del item
            item_personalizaciones = storage.get_by_criteria(
                Personalizacion, lambda x: x.item_pedido_id == item_id
            )
            
            item.subtotal_personalizaciones = sum(p.subtotal for p in item_personalizaciones)
            storage.save(item)
            
            # Recalcular totales del pedido
            calcular_totales_pedido(pedido, item.pedido_id)
            storage.save(pedido)
            
            flash('Personalización agregada exitosamente', 'success')
            return redirect(url_for('pedidos.detalle', id=pedido.id))
        
        # Obtener el producto asociado al item para mostrar información
        producto = storage.get(Producto, item.producto_id)
        
        return render_template('pedidos/personalizacion_form.html',
                              form=form,
                              item=item,
                              pedido=pedido,
                              producto=producto,
                              titulo='Agregar Personalización',
                              action=url_for('pedidos.agregar_personalizacion', item_id=item_id))
        
    except NotFound as e:
        flash(str(e), 'error')
        return redirect(url_for('pedidos.index'))
    except Exception as e:
        flash(f'Error al agregar personalización: {str(e)}', 'error')
        return redirect(url_for('pedidos.index'))


@pedidos_bp.route('/editar_item/<string:item_id>', methods=['GET', 'POST'])
@login_required
def editar_item(item_id):
    """Editar un item de un pedido existente."""
    try:
        item = storage.get(ItemPedido, item_id)
        if not item or not item.is_active:
            raise NotFound("Item de pedido no encontrado")
        
        # Obtenemos el pedido al que pertenece el item
        pedido = storage.get(Pedido, item.pedido_id)
        if not pedido or not pedido.is_active:
            raise NotFound("Pedido asociado no encontrado")
          # Crear formulario para el item con datos precargados
        form = ItemPedidoForm(obj=item)
        
        # Cargar opciones para el formulario
        productos = storage.get_by_criteria(Producto, lambda x: x.is_active)
        form.producto_id.choices = [(p.id, p.nombre) for p in productos]
        
        # Obtener el producto actual para las opciones de talla y color
        producto_actual = next((p for p in productos if p.id == item.producto_id), None)
        
        if producto_actual:
            # Cargar tallas disponibles
            form.talla.choices = [(t, t) for t in producto_actual.tallas_disponibles or ['Única']]
            
            # Cargar colores disponibles
            form.color.choices = [(c, c) for c in producto_actual.colores_disponibles or ['Estándar']]
        else:
            form.talla.choices = [('', 'Seleccione un producto primero')]
            form.color.choices = [('', 'Seleccione un producto primero')]
        
        if form.validate_on_submit():
            # Guardar valores anteriores para comparación
            previous_producto_id = item.producto_id
            previous_cantidad = item.cantidad
            previous_precio = item.precio_prenda
            
            # Actualizar item
            item.producto_id = form.producto_id.data
            item.talla = form.talla.data
            item.color = form.color.data
            item.cantidad = form.cantidad.data
            item.precio_prenda = form.precio_prenda.data
            
            # Recalcular el subtotal con los nuevos valores
            item.subtotal = item.precio_prenda * item.cantidad
            
            # Si el producto cambió, verificar si necesitamos actualizar la información relacionada
            if previous_producto_id != item.producto_id:
                nuevo_producto = next((p for p in productos if p.id == item.producto_id), None)
                if nuevo_producto:
                    # Podríamos realizar acciones adicionales aquí si es necesario
                    # Por ejemplo, ajustar personalizaciones compatibles con el nuevo producto
                    pass
            
            # Guardar el item
            storage.save(item)
            
            # Si la cantidad cambió, necesitamos recalcular el subtotal de personalizaciones también
            if previous_cantidad != item.cantidad:
                # Obtener todas las personalizaciones del item
                personalizaciones = storage.get_by_criteria(
                    Personalizacion, lambda x: x.item_pedido_id == item_id and x.is_active
                )
                
                # El subtotal de personalizaciones debe reflejar la cantidad de items
                item.subtotal_personalizaciones = sum(p.subtotal for p in personalizaciones)
                storage.save(item)
            
            # Actualizar el pedido
            calcular_totales_pedido(pedido, pedido.id)
            storage.save(pedido)
            
            flash('Item actualizado exitosamente', 'success')
            return redirect(url_for('pedidos.detalle', id=pedido.id))
        
        return render_template('pedidos/item_form.html',
                              form=form,
                              pedido=pedido,
                              item=item,
                              titulo='Editar Item',
                              action=url_for('pedidos.editar_item', item_id=item_id))
        
    except NotFound as e:
        flash(str(e), 'error')
        return redirect(url_for('pedidos.index'))
    except Exception as e:
        flash(f'Error al editar item: {str(e)}', 'error')
        return redirect(url_for('pedidos.index'))


@pedidos_bp.route('/eliminar_item/<string:item_id>', methods=['POST'])
@login_required
def eliminar_item(item_id):
    """Eliminar un item de un pedido."""
    try:
        item = storage.get(ItemPedido, item_id)
        if not item or not item.is_active:
            raise NotFound("Item de pedido no encontrado")
        
        # Obtenemos el pedido al que pertenece el item
        pedido_id = item.pedido_id
        pedido = storage.get(Pedido, pedido_id)
        if not pedido or not pedido.is_active:
            raise NotFound("Pedido asociado no encontrado")
        
        # Eliminar personalizaciones asociadas al item
        personalizaciones = storage.get_by_criteria(
            Personalizacion, lambda x: x.item_pedido_id == item_id and x.is_active
        )
        
        for pers in personalizaciones:
            pers.soft_delete()
            storage.save(pers)
            
        # Eliminar item
        item.soft_delete()
        storage.save(item)
        
        # Actualizar el pedido
        calcular_totales_pedido(pedido, pedido_id)
        storage.save(pedido)
        
        flash('Item eliminado exitosamente', 'success')
        
    except NotFound as e:
        flash(str(e), 'error')
        return redirect(url_for('pedidos.index'))
    except Exception as e:
        flash(f'Error al eliminar item: {str(e)}', 'error')
        return redirect(url_for('pedidos.detalle', id=pedido_id))


@pedidos_bp.route('/eliminar_personalizacion/<string:personalizacion_id>', methods=['POST'])
@login_required
def eliminar_personalizacion(personalizacion_id):
    """Eliminar una personalización de un item."""
    try:
        personalizacion = storage.get(Personalizacion, personalizacion_id)
        if not personalizacion or not personalizacion.is_active:
            raise NotFound("Personalización no encontrada")
        
        # Obtenemos el item al que pertenece la personalización
        item_id = personalizacion.item_pedido_id
        item = storage.get(ItemPedido, item_id)
        if not item or not item.is_active:
            raise NotFound("Item de pedido no encontrado")
        
        # Obtenemos el pedido
        pedido_id = item.pedido_id
        pedido = storage.get(Pedido, pedido_id)
        if not pedido or not pedido.is_active:
            raise NotFound("Pedido asociado no encontrado")
        
        # Eliminar personalización
        personalizacion.soft_delete()
        storage.save(personalizacion)
        
        # Actualizar subtotales del item
        item_personalizaciones = storage.get_by_criteria(
            Personalizacion, lambda x: x.item_pedido_id == item_id and x.is_active
        )
        
        item.subtotal_personalizaciones = sum(p.subtotal for p in item_personalizaciones)
        storage.save(item)
        
        # Actualizar el pedido
        calcular_totales_pedido(pedido, pedido_id)
        storage.save(pedido)
        
        flash('Personalización eliminada exitosamente', 'success')
        
    except NotFound as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error al eliminar personalización: {str(e)}', 'error')
    
    return redirect(url_for('pedidos.detalle', id=pedido_id))


@pedidos_bp.route('/editar_personalizacion/<string:personalizacion_id>', methods=['GET', 'POST'])
@login_required
def editar_personalizacion(personalizacion_id):
    """Editar una personalización existente."""
    try:
        personalizacion = storage.get(Personalizacion, personalizacion_id)
        if not personalizacion:
            raise NotFound("Personalización no encontrada")
        
        # Obtenemos el item al que pertenece la personalización
        item_id = personalizacion.item_pedido_id
        item = storage.get(ItemPedido, item_id)
        if not item:
            raise NotFound("Item de pedido no encontrado")
        
        # Obtenemos el pedido
        pedido_id = item.pedido_id
        pedido = storage.get(Pedido, pedido_id)
        if not pedido:
            raise NotFound("Pedido asociado no encontrado")
        
        # Crear formulario para la personalización con datos precargados
        form = PersonalizacionForm(obj=personalizacion)
        
        # Cargar opciones para el formulario
        procesos = storage.find_all(Proceso)
        form.proceso_id.choices = [(p.id, f"{p.nombre} ({p.tipo})") for p in procesos]
        
        if form.validate_on_submit():
            # Guardar los valores anteriores para comparación
            previous_precio = personalizacion.precio_proceso
            previous_cantidad = personalizacion.cantidad
            
            # Actualizar personalización
            personalizacion.proceso_id = form.proceso_id.data
            personalizacion.precio_proceso = form.precio.data
            personalizacion.cantidad = form.cantidad.data or 1
            personalizacion.descripcion = form.descripcion.data or ""
            personalizacion.ancho = form.ancho.data or 0
            personalizacion.alto = form.alto.data or 0
            personalizacion.colores = form.colores.data or ""
            personalizacion.cantidad_colores = form.cantidad_colores.data or 1
            personalizacion.notas = form.notas.data or ""
            
            # Recalcular el subtotal de la personalización con los nuevos valores
            personalizacion.subtotal = personalizacion.precio_proceso * personalizacion.cantidad
            
            # Guardar la personalización
            storage.save(personalizacion)
            
            # Actualizar subtotales del item
            item_personalizaciones = storage.get_by_criteria(
                Personalizacion, lambda x: x.item_pedido_id == item_id and x.is_active
            )
            
            # Recalcular el subtotal de personalizaciones del item
            item.subtotal_personalizaciones = sum(p.subtotal for p in item_personalizaciones)
            storage.save(item)
            
            # Actualizar el pedido con los nuevos cálculos
            calcular_totales_pedido(pedido, pedido_id)
            storage.save(pedido)
            
            flash('Personalización actualizada exitosamente', 'success')
            return redirect(url_for('pedidos.detalle', id=pedido_id))
        
        # Obtener el producto asociado al item para mostrar información
        producto = storage.get(Producto, item.producto_id)
        
        # Obtener el proceso actual
        proceso = storage.get(Proceso, personalizacion.proceso_id)
        
        return render_template('pedidos/personalizacion_form.html',
                              form=form,
                              item=item,
                              pedido=pedido,
                              producto=producto,
                              proceso=proceso,
                              personalizacion=personalizacion,
                              titulo='Editar Personalización',
                              action=url_for('pedidos.editar_personalizacion', personalizacion_id=personalizacion_id))
        
    except NotFound as e:
        flash(str(e), 'error')
        return redirect(url_for('pedidos.index'))
    except Exception as e:
        flash(f'Error al editar personalización: {str(e)}', 'error')
        return redirect(url_for('pedidos.index'))


@pedidos_bp.route('/api/pedido/<string:pedido_id>/totales')
@login_required
def api_pedido_totales(pedido_id):
    """API endpoint para obtener los totales actualizados de un pedido."""
    try:
        pedido = storage.get(Pedido, pedido_id)
        if not pedido:
            return jsonify({'error': 'Pedido no encontrado'}), 404
        
        # Asegurar que los totales están actualizados
        calcular_totales_pedido(pedido, pedido_id)
        
        # No guardamos el pedido aquí, solo devolvemos los totales calculados
        
        return jsonify({
            'subtotal': float(pedido.subtotal),
            'iva': float(pedido.iva),
            'total': float(pedido.total),
            'utilidad': float(pedido.utilidad),
            'porcentaje_utilidad': float(pedido.porcentaje_utilidad)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Temporary test endpoint for debugging product selection
@pedidos_bp.route('/test/productos')
def test_productos():
    """Test endpoint to verify product data without authentication issues"""
    try:
        productos = storage.get_by_criteria(Producto, lambda x: x.is_active)
        productos_data = []
        
        for producto in productos:
            productos_data.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'categoria': producto.categoria,
                'precio_base': float(producto.precio_base),
                'descripcion': producto.descripcion or '',
                'tallas_disponibles': producto.tallas_disponibles or [],
                'colores_disponibles': producto.colores_disponibles or []
            })
        
        # Return as HTML for easy debugging
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Product Test</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .product {{ border: 1px solid #ccc; margin: 10px 0; padding: 10px; }}
                .product h3 {{ margin: 0 0 10px 0; color: #333; }}
                .detail {{ margin: 5px 0; }}
                .sizes, .colors {{ display: inline-block; margin-right: 20px; }}
            </style>
        </head>
        <body>
            <h1>Product Test - {len(productos_data)} products found</h1>
            <div id="products">
        """
        
        for product in productos_data:
            html_content += f"""
                <div class="product">
                    <h3>{product['nombre']} - ${product['precio_base']}</h3>
                    <div class="detail"><strong>ID:</strong> {product['id']}</div>
                    <div class="detail"><strong>Category:</strong> {product['categoria']}</div>
                    <div class="detail"><strong>Description:</strong> {product['descripcion']}</div>
                    <div class="detail">
                        <span class="sizes"><strong>Sizes:</strong> {', '.join(product['tallas_disponibles'])}</span>
                        <span class="colors"><strong>Colors:</strong> {', '.join(product['colores_disponibles'])}</span>
                    </div>
                </div>
            """
        
        html_content += """
            </div>
            <script>
                // Test JavaScript fetch to API
                console.log('Testing API access...');
                fetch('/pedidos/api/productos')
                    .then(response => {
                        console.log('API Response status:', response.status);
                        return response.text();
                    })
                    .then(data => {
                        console.log('API Response:', data.substring(0, 200));
                    })
                    .catch(error => {
                        console.error('API Error:', error);
                    });
            </script>
        </body>
        </html>
        """
        
        return html_content
        
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>", 500
