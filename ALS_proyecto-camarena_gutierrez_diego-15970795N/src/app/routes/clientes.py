"""
Rutas para gestión de clientes.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app, jsonify
from flask_login import login_required
from app.forms.cliente_forms import ClienteForm, BuscarClienteForm
from app.models.cliente import Cliente
from app.models.pedido import Pedido
from app.services.storage_service import StorageService

clientes_bp = Blueprint('clientes', __name__)


@clientes_bp.route('/')
@login_required
def listar():
    """Listar todos los clientes con búsqueda."""
    form = BuscarClienteForm()
    storage = StorageService()
    
    # No necesitamos volver a mostrar el mensaje de éxito
    # ya que ahora se muestra correctamente al redirigir
    if 'last_created_cliente_id' in session:
        session.pop('last_created_cliente_id', None)
    if 'last_created_cliente_nombre' in session:
        session.pop('last_created_cliente_nombre', None)
    
    try:
        clientes = storage.find_all(Cliente)
        clientes_activos = [c for c in clientes if c.is_active]
        
        # Aplicar filtro de búsqueda si se proporciona
        if form.validate_on_submit() and form.termino_busqueda.data:
            termino = form.termino_busqueda.data.lower()
            clientes_filtrados = []
            
            for cliente in clientes_activos:
                if (termino in cliente.nombre.lower() or
                    termino in cliente.email.lower() or
                    termino in cliente.empresa.lower()):
                    clientes_filtrados.append(cliente)
            
            clientes_activos = clientes_filtrados
        
        # Ordenar por nombre
        clientes_activos.sort(key=lambda x: x.nombre)
        
        return render_template('clientes/index.html',
                             clientes=clientes_activos,
                             form=form)
        
    except Exception as e:
        flash(f'Error al cargar los clientes: {str(e)}', 'error')
        return render_template('clientes/index.html',
                             clientes=[],
                             form=form)


@clientes_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    """Crear un nuevo cliente."""
    form = ClienteForm()
    
    if form.validate_on_submit():
        storage = StorageService()
        
        try:
            # Crear nuevo cliente
            cliente = Cliente(
                nombre=form.nombre.data,
                apellido=form.apellido.data or "",
                email=form.email.data or "",
                telefono=form.telefono.data or "",
                direccion=form.direccion.data or "",
                empresa=form.empresa.data or "",
                notas=form.notas.data or "",
                tipo_cliente=form.tipo_cliente.data or "particular",
                nit=form.nit.data or "",
                ciudad=form.ciudad.data or "",
                departamento=form.departamento.data or ""
            )            # Guardar cliente
            try:
                # Logging para depuración
                current_app.logger.info(f"Guardando cliente: {cliente.nombre} (ID: {cliente.id})")
                cliente_id = storage.save(cliente)
                current_app.logger.info(f"ID devuelto después de guardar: {cliente_id}")
                
                if cliente_id:
                    flash(f'Cliente "{cliente.nombre}" creado exitosamente.', 'success')
                    
                    # Guardamos el cliente directamente en la sesión para poder recuperarlo después
                    session['last_created_cliente_id'] = cliente_id
                    session['last_created_cliente_nombre'] = cliente.nombre
                    
                    # Ir directo al listado en lugar de intentar ver el detalle
                    # Esto evita problemas si el cliente no se puede cargar inmediatamente
                    return redirect(url_for('clientes.listar'))
                else:
                    flash('Error al crear el cliente. Inténtalo de nuevo.', 'error')
            except Exception as e:
                current_app.logger.error(f"Error al guardar cliente: {str(e)}", exc_info=True)
                flash(f'Error al crear el cliente: {str(e)}', 'error')
                
        except Exception as e:
            flash(f'Error al crear el cliente: {str(e)}', 'error')
    
    return render_template('clientes/nuevo.html', form=form)


@clientes_bp.route('/ajax/<id>')
@login_required
def ver_ajax(id):
    """Obtener detalles de un cliente específico vía AJAX."""
    storage = StorageService()
    
    try:
        # Intentamos cargar el cliente directamente
        cliente = storage.load(id)
        
        # Si no lo encontramos, intentamos buscarlo en todos los clientes
        if not cliente:
            clientes = storage.find_all(Cliente)
            for c in clientes:
                if c.id == id:
                    cliente = c
                    break
        
        if not cliente or not cliente.is_active or not isinstance(cliente, Cliente):
            return jsonify({'error': 'Cliente no encontrado'}), 404
        
        # Obtener pedidos del cliente
        pedidos = storage.find_by_condition(
            Pedido,
            lambda p: p.cliente_id == id and p.is_active
        )
        
        # Ordenar pedidos por fecha de creación (más recientes primero)
        pedidos.sort(key=lambda x: x.created_at, reverse=True)
          # Convertir a diccionario para JSON
        cliente_data = {
            'id': cliente.id,
            'nombre': getattr(cliente, 'nombre', ''),
            'apellido': getattr(cliente, 'apellido', ''),
            'email': getattr(cliente, 'email', ''),
            'telefono': getattr(cliente, 'telefono', ''),
            'direccion': getattr(cliente, 'direccion', ''),
            'empresa': getattr(cliente, 'empresa', ''),
            'notas': getattr(cliente, 'notas', ''),
            'tipo_cliente': getattr(cliente, 'tipo_cliente', 'particular'),
            'nit': getattr(cliente, 'nit', ''),
            'ciudad': getattr(cliente, 'ciudad', ''),
            'departamento': getattr(cliente, 'departamento', ''),
            'created_at': cliente.created_at.strftime('%d/%m/%Y %H:%M') if hasattr(cliente, 'created_at') and cliente.created_at else '',
            'updated_at': cliente.updated_at.strftime('%d/%m/%Y %H:%M') if hasattr(cliente, 'updated_at') and cliente.updated_at else ''
        }
        
        # Convertir pedidos a diccionario
        pedidos_data = []
        for pedido in pedidos[:5]:  # Solo los últimos 5 pedidos
            pedidos_data.append({
                'id': pedido.id,
                'numero_pedido': getattr(pedido, 'numero_pedido', 'N/A'),
                'fecha_pedido': pedido.created_at.strftime('%d/%m/%Y') if pedido.created_at else '',
                'estado': getattr(pedido, 'estado', 'N/A'),
                'total': getattr(pedido, 'total', 0)
            })
        
        return jsonify({
            'cliente': cliente_data,
            'pedidos': pedidos_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Error al cargar el cliente: {str(e)}'}), 500


@clientes_bp.route('/<id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar un cliente existente."""
    storage = StorageService()
    
    try:
        cliente = storage.load(id)
        
        if not cliente or not cliente.is_active or not isinstance(cliente, Cliente):
            flash('Cliente no encontrado.', 'error')
            return redirect(url_for('clientes.listar'))
        
        form = ClienteForm(obj=cliente)
        
        if form.validate_on_submit():
            # Actualizar datos del cliente
            cliente.nombre = form.nombre.data
            cliente.apellido = form.apellido.data or ""
            cliente.email = form.email.data or ""
            cliente.telefono = form.telefono.data or ""
            cliente.direccion = form.direccion.data or ""
            cliente.empresa = form.empresa.data or ""
            cliente.notas = form.notas.data or ""
            cliente.tipo_cliente = form.tipo_cliente.data or "particular"
            cliente.nit = form.nit.data or ""
            cliente.ciudad = form.ciudad.data or ""
            cliente.departamento = form.departamento.data or ""
            cliente.update_timestamp()
              # Guardar cambios
            storage.save(cliente)
            flash(f'Cliente "{cliente.nombre}" actualizado exitosamente.', 'success')
            return redirect(url_for('clientes.listar'))
        
        return render_template('clientes/editar.html',
                             form=form,
                             cliente=cliente)
        
    except Exception as e:
        flash(f'Error al editar el cliente: {str(e)}', 'error')
        return redirect(url_for('clientes.listar'))


@clientes_bp.route('/<id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    """Eliminar (soft delete) un cliente."""
    storage = StorageService()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        cliente = storage.load(id)
        
        if not cliente or not cliente.is_active or not isinstance(cliente, Cliente):
            mensaje = 'Cliente no encontrado.'
            if is_ajax:
                return jsonify({'success': False, 'message': mensaje}), 404
            flash(mensaje, 'error')
            return redirect(url_for('clientes.listar'))
        
        # VALIDACIÓN DE INTEGRIDAD REFERENCIAL: Usar el método del modelo
        puede_eliminar, mensaje = cliente.puede_ser_eliminado(storage)
        if not puede_eliminar:
            if is_ajax:
                return jsonify({'success': False, 'message': mensaje}), 400
            flash(mensaje, 'warning')
            return redirect(url_for('clientes.listar'))
        
        # Realizar soft delete
        cliente.soft_delete()
        storage.save(cliente)
        
        mensaje = f'Cliente "{cliente.nombre}" eliminado correctamente.'
        
        if is_ajax:
            return jsonify({
                'success': True, 
                'message': mensaje,
                'cliente_id': id,
                'cliente_nombre': cliente.nombre
            })
        
        flash(mensaje, 'success')
        return redirect(url_for('clientes.listar'))
        
    except Exception as e:
        mensaje = f'Error al eliminar el cliente: {str(e)}'
        
        if is_ajax:
            return jsonify({'success': False, 'message': mensaje}), 500
        
        flash(mensaje, 'error')
        return redirect(url_for('clientes.listar'))
