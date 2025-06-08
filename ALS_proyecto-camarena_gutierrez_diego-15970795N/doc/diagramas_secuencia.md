# DIAGRAMAS DE SECUENCIA - SISTEMA ALS

## 1. Diagrama de Secuencia - Crear Pedido Completo

```mermaid
sequenceDiagram
    participant U as Usuario
    participant R as Routes/Controller
    participant F as Forms
    participant M as Models
    participant S as StorageService
    participant DB as Base de Datos

    Note over U,DB: Proceso completo de creación de pedido

    %% Paso 1: Información básica
    U->>R: GET /pedidos/crear/paso1
    R->>S: get_by_criteria(Cliente, activos)
    S->>DB: Consultar clientes activos
    DB-->>S: Lista de clientes
    S-->>R: clientes
    R->>F: PedidoForm(choices=clientes)
    F-->>R: formulario_inicial
    R-->>U: render_template(paso1, form)

    U->>R: POST /pedidos/crear/paso1 (datos_basicos)
    R->>F: form.validate_on_submit()
    F->>M: Pedido.validar_cliente_existe()
    M->>S: get(Cliente, cliente_id)
    S->>DB: Buscar cliente
    DB-->>S: cliente_data
    S-->>M: cliente_valido
    M-->>F: validacion_ok
    F-->>R: validacion_exitosa
    R->>R: session['pedido_data'] = datos
    R-->>U: redirect(paso2)

    %% Paso 2: Agregar productos
    U->>R: GET /pedidos/crear/paso2
    R->>R: pedido_data = session['pedido_data']
    R-->>U: render_template(paso2)

    U->>R: POST /pedidos/crear/paso2 (productos_data)
    R->>R: products = json.loads(productos_data)
    
    loop Para cada producto
        R->>M: validar_producto_existe()
        M->>S: get(Producto, producto_id)
        S->>DB: Consultar producto
        DB-->>S: producto_data
        S-->>M: producto_valido
        M-->>R: validacion_ok
    end

    %% Crear pedido y items
    R->>M: Pedido(cliente_id, descripcion, fecha_entrega)
    M->>M: _generar_numero_pedido()
    M-->>R: pedido_instancia
    R->>S: save(pedido)
    S->>DB: INSERT pedido
    DB-->>S: pedido_id
    S-->>R: pedido_guardado

    loop Para cada producto en products
        R->>M: ItemPedido(producto_id, talla, color, cantidad, precio)
        M->>M: subtotal = precio * cantidad
        M-->>R: item_instancia
        R->>S: save(item)
        S->>DB: INSERT item_pedido
        DB-->>S: item_id
        S-->>R: item_guardado
    end

    %% Calcular totales
    R->>R: calcular_totales_pedido(pedido, pedido_id)
    R->>S: get_by_criteria(ItemPedido, pedido_items)
    S->>DB: Consultar items del pedido
    DB-->>S: items_list
    S-->>R: items
    R->>M: pedido.calcular_totales()
    M->>M: subtotal, iva, total, utilidad
    M-->>R: totales_calculados
    R->>S: save(pedido)
    S->>DB: UPDATE pedido SET totales
    DB-->>S: actualizado
    S-->>R: pedido_actualizado

    R-->>U: redirect(detalle_pedido)
```

## 2. Diagrama de Secuencia - Gestión de Productos (CRUD)

```mermaid
sequenceDiagram
    participant U as Usuario
    participant R as Routes/Controller
    participant F as Forms
    participant M as Models
    participant S as StorageService
    participant DB as Base de Datos

    Note over U,DB: Operaciones CRUD de Productos

    %% CREATE - Crear Producto
    rect rgb(200, 255, 200)
        Note over U,DB: CREATE - Nuevo Producto
        U->>R: GET /productos/nuevo
        R->>F: ProductoForm()
        F-->>R: formulario_vacio
        R-->>U: render_template(nuevo, form)

        U->>R: POST /productos/nuevo (datos_producto)
        R->>F: form.validate_on_submit()
        F->>F: validate_tallas_disponibles()
        F->>F: validate_colores_disponibles()
        F-->>R: validacion_exitosa
        R->>M: Producto(nombre, categoria, precio_base, descripcion, tallas, colores)
        M->>M: inicializar_posiciones_personalizacion()
        M->>M: inicializar_estadisticas()
        M-->>R: producto_instancia
        R->>S: save(producto)
        S->>DB: INSERT producto
        DB-->>S: producto_id
        S-->>R: producto_guardado
        R-->>U: redirect(ver_producto)
    end

    %% READ - Ver Productos
    rect rgb(200, 200, 255)
        Note over U,DB: READ - Listar Productos
        U->>R: GET /productos/
        R->>S: get_by_criteria(Producto, activos)
        S->>DB: SELECT * FROM productos WHERE is_active=true
        DB-->>S: lista_productos
        S-->>R: productos
        R-->>U: render_template(lista, productos)

        U->>R: GET /productos/{id}
        R->>S: load(producto_id)
        S->>DB: SELECT * FROM productos WHERE id=?
        DB-->>S: producto_data
        S-->>R: producto
        R->>S: find_by_condition(ItemPedido, producto_usado)
        S->>DB: SELECT items WHERE producto_id=?
        DB-->>S: items_estadisticas
        S-->>R: estadisticas_uso
        R-->>U: render_template(detalle, producto, estadisticas)
    end

    %% UPDATE - Actualizar Producto
    rect rgb(255, 255, 200)
        Note over U,DB: UPDATE - Editar Producto
        U->>R: GET /productos/{id}/editar
        R->>S: load(producto_id)
        S->>DB: SELECT producto
        DB-->>S: producto_data
        S-->>R: producto
        R->>F: ProductoForm(data=producto_data)
        F-->>R: formulario_prellenado
        R-->>U: render_template(editar, form)

        U->>R: POST /productos/{id}/editar (datos_actualizados)
        R->>F: form.validate_on_submit()
        F-->>R: validacion_exitosa
        R->>M: producto.actualizar(nuevos_datos)
        M->>M: update_timestamp()
        M-->>R: producto_actualizado
        R->>S: save(producto)
        S->>DB: UPDATE producto SET campos
        DB-->>S: actualizado
        S-->>R: guardado_exitoso
        R-->>U: redirect(ver_producto)
    end

    %% DELETE - Eliminar Producto
    rect rgb(255, 200, 200)
        Note over U,DB: DELETE - Eliminar Producto (Soft Delete)
        U->>R: POST /productos/{id}/eliminar
        R->>S: load(producto_id)
        S->>DB: SELECT producto
        DB-->>S: producto_data
        S-->>R: producto

        %% Verificar integridad referencial
        R->>S: find_by_condition(ItemPedido, items_activos)
        S->>DB: SELECT items WHERE producto_id=? AND is_active=true
        DB-->>S: items_activos
        S-->>R: items_encontrados

        alt items_activos existe
            R->>S: find_by_condition(Pedido, pedidos_activos)
            S->>DB: SELECT pedidos activos con items
            DB-->>S: pedidos_activos
            S-->>R: verificacion_pedidos
            R-->>U: error("Producto en uso en pedidos activos")
        else sin_items_activos
            R->>M: producto.soft_delete()
            M->>M: is_active = False
            M->>M: update_timestamp()
            M-->>R: producto_eliminado
            R->>S: save(producto)
            S->>DB: UPDATE producto SET is_active=false
            DB-->>S: actualizado
            S-->>R: eliminacion_exitosa
            R-->>U: success("Producto eliminado")
        end
    end
```

## 3. Diagrama de Secuencia - Autenticación de Usuario

```mermaid
sequenceDiagram
    participant U as Usuario
    participant R as Routes/Controller
    participant F as Forms
    participant A as Auth/Login
    participant S as StorageService
    participant DB as Base de Datos
    participant Sess as Session

    Note over U,DB: Proceso de Autenticación

    %% Login
    U->>R: GET /auth/login
    R->>F: LoginForm()
    F-->>R: formulario_login
    R-->>U: render_template(login, form)

    U->>R: POST /auth/login (username, password)
    R->>F: form.validate_on_submit()
    F-->>R: datos_validos
    R->>S: get_by_criteria(User, username)
    S->>DB: SELECT user WHERE username=?
    DB-->>S: user_data
    S-->>R: usuario

    alt usuario_existe
        R->>A: user.check_password(password)
        A->>A: verificar_hash_password
        A-->>R: password_correcto
        
        alt password_correcto
            R->>A: login_user(user)
            A->>Sess: crear_sesion_usuario
            Sess-->>A: sesion_creada
            A-->>R: login_exitoso
            R-->>U: redirect(dashboard)
        else password_incorrecto
            R-->>U: error("Credenciales inválidas")
        end
    else usuario_no_existe
        R-->>U: error("Usuario no encontrado")
    end

    %% Logout
    U->>R: GET /auth/logout
    R->>A: logout_user()
    A->>Sess: destruir_sesion
    Sess-->>A: sesion_destruida
    A-->>R: logout_exitoso
    R-->>U: redirect(login)
```

## 4. Diagrama de Secuencia - Calculadora de Costes de Personalización

```mermaid
sequenceDiagram
    participant U as Usuario
    participant R as Routes/Controller
    participant F as Forms
    participant M as Models
    participant C as Calculadora
    participant S as StorageService
    participant DB as Base de Datos

    Note over U,DB: Cálculo de Costes de Personalización

    U->>R: GET /pedidos/agregar_item/{pedido_id}
    R->>S: get(Producto, productos_activos)
    S->>DB: SELECT productos WHERE is_active=true
    DB-->>S: productos_lista
    S-->>R: productos
    R->>F: ItemPedidoForm(choices=productos)
    F-->>R: formulario_item
    R-->>U: render_template(agregar_item, form)

    U->>R: POST /api/producto/{producto_id} (AJAX)
    R->>S: get(Producto, producto_id)
    S->>DB: SELECT producto
    DB-->>S: producto_data
    S-->>R: producto
    R-->>U: JSON(tallas, colores, precio_base)

    U->>R: POST /api/proceso/{proceso_id} (AJAX)
    R->>S: get(Proceso, proceso_id)
    S->>DB: SELECT proceso
    DB-->>S: proceso_data
    S-->>R: proceso
    R->>M: determinar_precio_base_proceso()
    M-->>R: precio_base_proceso
    R-->>U: JSON(proceso_info, precio_base)

    Note over U,R: Usuario configura personalización (tipo, tamaño, cantidad)

    U->>R: calcular_costo_personalizacion (AJAX)
    R->>M: proceso.tipo
    
    alt tipo == DTF || SUBLIMACION
        R->>C: calcular_precio_dtf_sublimacion(ancho, alto, cantidad)
        C->>C: metros = calcular_metros_necesarios()
        C->>C: precio = metros * precio_por_metro
        C-->>R: precio_calculado
    else tipo == BORDADO
        R->>C: calcular_precio_bordado(tamaño, cantidad, incluir_setup)
        C->>C: precio_base = tamaños_bordado[tamaño]
        C->>C: precio_total = (precio_base * cantidad) + setup
        C-->>R: precio_calculado
    else tipo == VINIL_TEXTIL
        R->>C: calcular_precio_vinil(tipo_vinil, area, cantidad)
        C->>C: precio = area * precio_por_cm2 * cantidad
        C-->>R: precio_calculado
    end

    R-->>U: JSON(precio_personalización)

    U->>R: POST /pedidos/agregar_item/{pedido_id} (item_completo)
    R->>F: form.validate_on_submit()
    F-->>R: validacion_exitosa
    R->>M: ItemPedido(producto_id, talla, color, cantidad, precio_prenda)
    M->>M: subtotal = precio_prenda * cantidad
    M-->>R: item_creado
    R->>S: save(item)
    S->>DB: INSERT item_pedido
    DB-->>S: item_id
    S-->>R: item_guardado

    %% Procesar personalizaciones
    loop Para cada diseño/personalización
        R->>M: Personalizacion(proceso_id, precio_proceso, cantidad)
        M->>M: subtotal = precio_proceso * cantidad
        M-->>R: personalizacion_creada
        R->>S: save(personalizacion)
        S->>DB: INSERT personalizacion
        DB-->>S: personalizacion_id
        S-->>R: personalizacion_guardada
    end

    %% Recalcular totales del pedido
    R->>R: calcular_totales_pedido(pedido, pedido_id)
    R->>S: get_by_criteria(ItemPedido, items_del_pedido)
    S->>DB: SELECT items WHERE pedido_id=?
    DB-->>S: items_lista
    S-->>R: items
    
    loop Para cada item
        R->>S: get_by_criteria(Personalizacion, personalizaciones_item)
        S->>DB: SELECT personalizaciones WHERE item_id=?
        DB-->>S: personalizaciones_lista
        S-->>R: personalizaciones
        R->>M: calcular_subtotal_personalizaciones()
        M-->>R: subtotal_pers
        R->>M: item.subtotal_personalizaciones = subtotal_pers
        M-->>R: item_actualizado
    end

    R->>M: pedido.subtotal = sum(item.subtotal + item.subtotal_personalizaciones)
    R->>M: pedido.calcular_totales(iva_porcentaje=16.0)
    M->>M: iva = subtotal * 0.16
    M->>M: utilidad = subtotal * (porcentaje_utilidad / 100)
    M->>M: total = subtotal + iva
    M-->>R: totales_calculados
    R->>S: save(pedido)
    S->>DB: UPDATE pedido SET subtotal, iva, total, utilidad
    DB-->>S: actualizado
    S-->>R: pedido_actualizado

    R-->>U: redirect(detalle_pedido)
```

## 5. Diagrama de Secuencia - Gestión de Estados de Pedido

```mermaid
sequenceDiagram
    participant U as Usuario
    participant R as Routes/Controller
    participant F as Forms
    participant M as Models
    participant S as StorageService
    participant DB as Base de Datos
    participant N as Notificaciones

    Note over U,DB: Cambio de Estado de Pedido

    U->>R: GET /pedidos/{id}/cambiar_estado
    R->>S: get(Pedido, pedido_id)
    S->>DB: SELECT pedido
    DB-->>S: pedido_data
    S-->>R: pedido
    R->>F: CambiarEstadoPedidoForm(estado_actual)
    F-->>R: formulario_estados
    R-->>U: render_template(cambiar_estado, form)

    U->>R: POST /pedidos/{id}/cambiar_estado (nuevo_estado)
    R->>F: form.validate_on_submit()
    F-->>R: validacion_exitosa

    %% Validaciones de transición de estado
    R->>M: validar_transicion_estado(estado_actual, nuevo_estado)
    
    alt transicion_valida
        M-->>R: transicion_permitida
        R->>M: pedido.cambiar_estado(nuevo_estado)
        M->>M: estado = nuevo_estado
        M->>M: update_timestamp()
        
        alt nuevo_estado == COMPLETADO
            M->>M: fecha_completado = now()
            M-->>R: estado_actualizado
            R->>N: notificar_cliente_pedido_listo()
            N-->>R: notificacion_enviada
        else nuevo_estado == ENTREGADO
            M->>M: fecha_entrega_real = now()
            M->>M: validar_pago_completo()
            M-->>R: estado_actualizado
            R->>N: notificar_pedido_entregado()
            N-->>R: notificacion_enviada
        else nuevo_estado == CANCELADO
            M->>M: fecha_cancelacion = now()
            M->>M: motivo_cancelacion = form.motivo
            M-->>R: estado_actualizado
            R->>N: notificar_cancelacion()
            N-->>R: notificacion_enviada
        else otro_estado
            M-->>R: estado_actualizado
        end

        R->>S: save(pedido)
        S->>DB: UPDATE pedido SET estado, timestamps
        DB-->>S: actualizado
        S-->>R: guardado_exitoso
        R-->>U: success("Estado actualizado")
        
    else transicion_invalida
        M-->>R: transicion_no_permitida
        R-->>U: error("Transición de estado no válida")
    end
```

## Información Adicional

### Patrones de Interacción:

1. **Request-Response**: Comunicación HTTP estándar entre usuario y servidor
2. **AJAX/JSON**: Para actualizaciones dinámicas sin recarga de página
3. **Session Management**: Manejo de datos temporales durante procesos multi-paso
4. **Validation Chain**: Validación en múltiples capas (cliente, servidor, base de datos)

### Características de los Flujos:

1. **Integridad Referencial**: Validaciones antes de operaciones críticas
2. **Soft Delete**: Eliminación lógica para mantener historial
3. **Transaccionalidad**: Operaciones atómicas en procesos complejos
4. **Cálculos Automáticos**: Recálculo de totales tras cambios
5. **Notificaciones**: Comunicación de cambios de estado a usuarios

### Manejo de Errores:

- Validación en cada capa del sistema
- Rollback automático en caso de errores
- Mensajes descriptivos para el usuario
- Logging para auditoría y debugging
