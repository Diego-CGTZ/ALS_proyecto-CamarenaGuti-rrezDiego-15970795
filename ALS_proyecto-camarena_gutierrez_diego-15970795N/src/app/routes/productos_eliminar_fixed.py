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
    
    try:
        producto = storage.load(id)
        print(f"[DEBUG] Producto encontrado: {producto.nombre if producto else 'None'}")
        
        if not producto:
            print(f"[DEBUG] ERROR: Producto no encontrado con ID {id}")
            flash('Producto no encontrado.', 'error')
            return redirect(url_for('productos.listar'))
            
        if not producto.is_active:
            print(f"[DEBUG] ERROR: Producto ya está inactivo")
            flash('El producto ya está eliminado.', 'warning')
            return redirect(url_for('productos.listar'))
            
        if not isinstance(producto, Producto):
            print(f"[DEBUG] ERROR: Objeto no es instancia de Producto")
            flash('Error en el tipo de objeto.', 'error')
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
                    flash(f'No se puede eliminar el producto "{producto.nombre}" porque está siendo usado en pedidos activos.', 'warning')
                    return redirect(url_for('productos.ver', id=id))
        
        # Realizar soft delete
        print(f"[DEBUG] Procediendo con la eliminación del producto")
        producto.soft_delete()
        storage.save(producto)
        
        print(f"[DEBUG] Producto eliminado correctamente")
        flash(f'Producto "{producto.nombre}" eliminado correctamente.', 'success')
        return redirect(url_for('productos.listar'))
        
    except Exception as e:
        print(f"[DEBUG] Error al eliminar producto: {str(e)}")
        flash(f'Error al eliminar el producto: {str(e)}', 'error')
        return redirect(url_for('productos.ver', id=id))
