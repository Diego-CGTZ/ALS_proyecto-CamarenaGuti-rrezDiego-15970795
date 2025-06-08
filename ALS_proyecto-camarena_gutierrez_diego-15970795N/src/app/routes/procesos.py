"""
Rutas para gestión de procesos de personalización.

Este módulo contiene todas las rutas relacionadas con la gestión de procesos de
personalización textil como DTF, sublimación, bordado y vinil.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required

from app.forms.proceso_forms import (
    ProcesoForm, ConfiguracionDTFForm, ConfiguracionSublimacionForm,
    ConfiguracionBordadoForm, ConfiguracionVinilForm, CalculadoraProcesoForm
)
from app.models.proceso import Proceso, TipoProceso, TamañoBordado
from app.services.storage_service import StorageService

# Definir el Blueprint
procesos_bp = Blueprint('procesos', __name__)


@procesos_bp.route('/')
@login_required
def listar():
    """
    Lista todos los procesos activos agrupados por tipo.
    
    Returns:
        str: Renderiza la plantilla procesos/index.html con los procesos.
    """
    storage = StorageService()
    
    try:
        # Obtener todos los procesos y filtrar solo los activos
        procesos = storage.find_all(Proceso)
        procesos_activos = [p for p in procesos if p.is_active]
        
        return render_template(
            'procesos/index.html',
            procesos=procesos_activos
        )
        
    except Exception as e:
        flash(f'Error al cargar los procesos: {str(e)}', 'error')
        return render_template(
            'procesos/index.html',
            procesos=[]
        )


@procesos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    """
    Crea un nuevo proceso de personalización.
    
    Returns:
        str: Redirecciona a la configuración del proceso o renderiza el formulario.
    """
    form = ProcesoForm()
    
    if form.validate_on_submit():
        storage = StorageService()
        
        try:
            # Crear nuevo proceso con los datos del formulario
            tipo_proceso = TipoProceso(form.tipo.data)
            proceso = Proceso(
                tipo=tipo_proceso,
                nombre=form.nombre.data,
                descripcion=form.descripcion.data or ""
            )
            
            # Guardar proceso en almacenamiento
            proceso_id = storage.save(proceso)
            
            if proceso_id:
                flash(f'Proceso "{proceso.nombre}" creado exitosamente.', 'success')
                return redirect(url_for('procesos.configurar', id=proceso_id))
            else:
                flash('Error al guardar el proceso. Inténtalo de nuevo.', 'error')
                
        except Exception as e:
            flash(f'Error al crear el proceso: {str(e)}', 'error')
    
    return render_template('procesos/nuevo.html', form=form)


@procesos_bp.route('/<id>')
@login_required
def ver(id):
    """
    Muestra los detalles de un proceso específico.
    
    Args:
        id (str): Identificador único del proceso
        
    Returns:
        str: Renderiza la plantilla con los detalles del proceso o redirecciona si no existe
    """
    storage = StorageService()
    
    try:
        # Cargar el proceso desde el almacenamiento
        proceso = storage.load(id)
        
        # Validar que exista y sea del tipo correcto
        if not proceso or not proceso.is_active or not isinstance(proceso, Proceso):
            flash('Proceso no encontrado o inactivo.', 'error')
            return redirect(url_for('procesos.listar'))
        
        return render_template('procesos/ver.html', proceso=proceso)
        
    except Exception as e:
        flash(f'Error al cargar el proceso: {str(e)}', 'error')
        return redirect(url_for('procesos.listar'))


@procesos_bp.route('/<id>/configurar', methods=['GET', 'POST'])
@login_required
def configurar(id):
    """
    Configura los precios y parámetros específicos de un proceso.
    
    Args:
        id (str): Identificador único del proceso
        
    Returns:
        str: Redirecciona a los detalles del proceso o renderiza el formulario de configuración
    """
    storage = StorageService()
    
    try:
        # Cargar el proceso desde el almacenamiento
        proceso = storage.load(id)
        
        # Validar que exista y sea del tipo correcto
        if not proceso or not proceso.is_active or not isinstance(proceso, Proceso):
            flash('Proceso no encontrado o inactivo.', 'error')
            return redirect(url_for('procesos.listar'))
        
        # Seleccionar formulario según el tipo de proceso
        form = _obtener_formulario_configuracion(proceso)
        
        # Si el formulario se envió y es válido, actualizar configuración
        if form.validate_on_submit():
            _actualizar_configuracion_proceso(proceso, form)
            storage.save(proceso)
            flash(f'Configuración de {proceso.tipo.value} actualizada exitosamente.', 'success')
            return redirect(url_for('procesos.ver', id=id))
        
        return render_template('procesos/configurar.html',
                              proceso=proceso,
                              form=form)
        
    except Exception as e:
        flash(f'Error al configurar el proceso: {str(e)}', 'error')
        return redirect(url_for('procesos.ver', id=id))


@procesos_bp.route('/calculadora', methods=['GET', 'POST'])
@login_required
def calculadora():
    """
    Calculadora de precios para diferentes procesos.
    
    Returns:
        str: Renderiza la plantilla con el formulario y resultados del cálculo si existen
    """
    form = CalculadoraProcesoForm()
    resultado = None
    
    try:
        # Usar procesos fijos predefinidos en lugar de cargar desde la base de datos
        procesos_fijos = [
            ('dtf', 'DTF - Transferencia Digital'),
            ('sublimacion', 'Sublimación - Impresión Térmica')
        ]
        form.proceso_id.choices = procesos_fijos
        
        # Procesar cálculo si el formulario es válido
        if form.validate_on_submit():
            resultado = _calcular_precio_proceso_fijo(form)
        
        return render_template('procesos/calculadora.html',
                              form=form,
                              resultado=resultado)
        
    except Exception as e:
        flash(f'Error en la calculadora: {str(e)}', 'error')
        return render_template('procesos/calculadora.html',
                              form=form,
                              resultado=None)


@procesos_bp.route('/<id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    """
    Realiza una eliminación lógica (soft delete) de un proceso.
    
    Args:
        id (str): Identificador único del proceso
        
    Returns:
        str: Redirecciona a la lista de procesos o a los detalles del proceso
    """
    storage = StorageService()
    
    try:
        # Cargar el proceso desde el almacenamiento
        proceso = storage.load(id)
        
        # Validar que exista y sea del tipo correcto
        if not proceso or not proceso.is_active or not isinstance(proceso, Proceso):
            flash('Proceso no encontrado o ya inactivo.', 'error')
            return redirect(url_for('procesos.listar'))
        
        # Verificar si el proceso está siendo usado
        from app.models.pedido import Personalizacion
        personalizaciones = storage.find_by_condition(
            Personalizacion,
            lambda p: p.proceso_id == id and p.is_active
        )
        
        # No permitir eliminar si está en uso
        if personalizaciones:
            flash(
                f'No se puede eliminar el proceso "{proceso.nombre}" porque está siendo '
                f'usado en personalizaciones activas.',
                'warning'
            )
            return redirect(url_for('procesos.ver', id=id))
        
        # Realizar soft delete
        proceso.soft_delete()
        storage.save(proceso)
        
        flash(f'Proceso "{proceso.nombre}" eliminado correctamente.', 'success')
        return redirect(url_for('procesos.listar'))
        
    except Exception as e:
        flash(f'Error al eliminar el proceso: {str(e)}', 'error')
        return redirect(url_for('procesos.ver', id=id))


def _obtener_formulario_configuracion(proceso):
    """
    Selecciona y prepara el formulario adecuado según el tipo de proceso.
    
    Args:
        proceso (Proceso): El proceso a configurar
        
    Returns:
        FlaskForm: Formulario correspondiente al tipo de proceso
    """
    if proceso.tipo == TipoProceso.DTF:
        form = ConfiguracionDTFForm()
        if hasattr(proceso, 'precio_por_metro'):
            form.precio_por_metro.data = proceso.precio_por_metro
    
    elif proceso.tipo == TipoProceso.SUBLIMACION:
        form = ConfiguracionSublimacionForm()
        if hasattr(proceso, 'precio_por_metro'):
            form.precio_por_metro.data = proceso.precio_por_metro
    
    elif proceso.tipo == TipoProceso.BORDADO:
        form = ConfiguracionBordadoForm()
        if hasattr(proceso, 'precio_setup'):
            form.precio_setup.data = proceso.precio_setup
        if hasattr(proceso, 'precios_por_tamaño'):
            form.precio_pequeño.data = proceso.precios_por_tamaño.get(TamañoBordado.PEQUEÑO, 0.0)
            form.precio_mediano.data = proceso.precios_por_tamaño.get(TamañoBordado.MEDIANO, 0.0)
            form.precio_grande.data = proceso.precios_por_tamaño.get(TamañoBordado.GRANDE, 0.0)
            form.precio_extra_grande.data = proceso.precios_por_tamaño.get(TamañoBordado.EXTRA_GRANDE, 0.0)
    
    elif proceso.tipo == TipoProceso.VINIL:
        form = ConfiguracionVinilForm()
        if hasattr(proceso, 'precio_por_cm2'):
            form.precio_por_cm2_base.data = proceso.precio_por_cm2
        
        # Cargar tipos de vinil existentes
        if hasattr(proceso, 'tipos_vinil') and proceso.tipos_vinil:
            # Limpiar formulario
            while len(form.tipos_vinil) > 0:
                form.tipos_vinil.pop_entry()
            
            # Añadir cada tipo de vinil
            for nombre, precio in proceso.tipos_vinil.items():
                form.tipos_vinil.append_entry()
                form.tipos_vinil[-1].nombre.data = nombre
                form.tipos_vinil[-1].precio_por_cm2.data = precio
    
    return form


def _actualizar_configuracion_proceso(proceso, form):
    """
    Actualiza la configuración del proceso con los datos del formulario.
    
    Args:
        proceso (Proceso): El proceso a actualizar
        form (FlaskForm): Formulario con los datos de configuración
    """
    if proceso.tipo == TipoProceso.DTF or proceso.tipo == TipoProceso.SUBLIMACION:
        proceso.configurar_precios(precio_por_metro=form.precio_por_metro.data)
    
    elif proceso.tipo == TipoProceso.BORDADO:
        precios_tamaños = {
            TamañoBordado.PEQUEÑO: form.precio_pequeño.data,
            TamañoBordado.MEDIANO: form.precio_mediano.data,
            TamañoBordado.GRANDE: form.precio_grande.data,
            TamañoBordado.EXTRA_GRANDE: form.precio_extra_grande.data
        }
        proceso.configurar_precios(
            precio_setup=form.precio_setup.data,
            precios_tamaños=precios_tamaños
        )
    
    elif proceso.tipo == TipoProceso.VINIL:
        tipos_vinil = {}
        for tipo_form in form.tipos_vinil:
            if tipo_form.nombre.data and tipo_form.precio_por_cm2.data:
                tipos_vinil[tipo_form.nombre.data] = tipo_form.precio_por_cm2.data
        
        proceso.configurar_precios(
            precio_por_cm2=form.precio_por_cm2_base.data,
            tipos_vinil=tipos_vinil
        )


def _calcular_precio_proceso(form, storage):
    """
    Calcula el precio de un proceso según los parámetros del formulario.
    
    Args:
        form (CalculadoraProcesoForm): Formulario con los datos para el cálculo
        storage (StorageService): Servicio de almacenamiento
    
    Returns:
        dict: Resultado del cálculo con proceso, cantidad, precios y detalles
    """
    proceso = storage.load(form.proceso_id.data)
    
    if not proceso:
        return None
        
    cantidad = form.cantidad.data
    precio_total = 0.0
    detalles = {}
    
    # Cálculo según tipo de proceso
    if proceso.tipo in [TipoProceso.DTF, TipoProceso.SUBLIMACION]:
        if form.ancho_diseño.data and form.alto_diseño.data:
            metros = proceso.calcular_metros_necesarios(
                form.ancho_diseño.data,
                form.alto_diseño.data,
                cantidad
            )
            precio_total = proceso.calcular_precio_dtf_sublimacion(
                form.ancho_diseño.data,
                form.alto_diseño.data,
                cantidad
            )
            detalles = {
                'metros_necesarios': metros,
                'precio_por_metro': getattr(proceso, 'precio_por_metro', 0.0),
                'ancho_disponible': proceso.ancho_disponible
            }
    
    elif proceso.tipo == TipoProceso.BORDADO and form.tamaño_bordado.data:
        tamaño = TamañoBordado(form.tamaño_bordado.data)
        precio_total = proceso.calcular_precio_bordado(tamaño, cantidad, True)
        detalles = {
            'precio_setup': getattr(proceso, 'precio_setup', 0.0),
            'precio_por_tamaño': getattr(proceso, 'precios_por_tamaño', {}).get(tamaño, 0.0)
        }
    
    elif proceso.tipo == TipoProceso.VINIL and form.tipo_vinil.data:
        if form.ancho_diseño.data and form.alto_diseño.data:
            precio_total = proceso.calcular_precio_vinil(
                form.ancho_diseño.data,
                form.alto_diseño.data,
                cantidad,
                form.tipo_vinil.data
            )
            area_cm2 = form.ancho_diseño.data * form.alto_diseño.data
            precio_cm2 = getattr(proceso, 'tipos_vinil', {}).get(
                            form.tipo_vinil.data,
                getattr(proceso, 'precio_por_cm2', 0.0)
            )
            detalles = {
                'area_cm2': area_cm2,
                'precio_por_cm2': precio_cm2
            }
    
    # Componer resultado
    costo_setup = 0.0
    if proceso.tipo == TipoProceso.BORDADO and form.incluir_setup_bordado.data:
        costo_setup = getattr(proceso, 'precio_setup', 0.0)
    
    subtotal = precio_total - costo_setup
    
    return {
        'nombre_proceso': proceso.nombre,
        'tipo_proceso': proceso.tipo.value,
        'ancho': form.ancho_diseño.data,
        'alto': form.alto_diseño.data,
        'cantidad': cantidad,
        'precio_unitario': subtotal / cantidad if cantidad > 0 else 0.0,
        'subtotal': subtotal,
        'costo_setup': costo_setup if costo_setup > 0 else None,
        'total': precio_total,
        'detalles': detalles
    }


def _calcular_precio_proceso_fijo(form):
    """
    Calcula el precio usando procesos fijos predefinidos para DTF y Sublimación.
    Calcula cuántas piezas caben en un metro y determina los metros necesarios.
    
    Args:
        form (CalculadoraProcesoForm): Formulario con los datos para el cálculo
    
    Returns:
        dict: Resultado del cálculo con proceso, cantidad, precios y detalles
    """
    proceso_id = form.proceso_id.data
    cantidad = form.cantidad.data
    ancho_diseño = form.ancho_diseño.data or 0.0
    alto_diseño = form.alto_diseño.data or 0.0
    
    # Configuración de procesos fijos con precios actualizados
    if proceso_id == 'dtf':
        nombre_proceso = 'DTF - Transferencia Digital'
        tipo_proceso = 'DTF'
        ancho_disponible = 27.5  # cm - ancho fijo para DTF
        precio_por_metro = 120.0  # MXN por metro
        
    elif proceso_id == 'sublimacion':
        nombre_proceso = 'Sublimación - Impresión Térmica'
        tipo_proceso = 'SUBLIMACION'
        ancho_disponible = 60.0  # cm - ancho fijo para Sublimación
        precio_por_metro = 90.0  # MXN por metro
        
    else:
        return None
    
    # Validar que se hayan proporcionado las dimensiones
    if not ancho_diseño or not alto_diseño:
        return None
    
    # Calcular cuántos diseños caben en el ancho disponible
    diseños_por_ancho = int(ancho_disponible // ancho_diseño)
    if diseños_por_ancho == 0:
        diseños_por_ancho = 1  # Al menos uno por fila si es más ancho que el material
    
    # Calcular cuántos diseños caben en un metro (100 cm de largo)
    diseños_por_metro_largo = int(100 // alto_diseño)
    if diseños_por_metro_largo == 0:
        diseños_por_metro_largo = 1  # Al menos uno si es más alto que un metro
    
    # Total de piezas que caben en un metro cuadrado
    piezas_por_metro = diseños_por_ancho * diseños_por_metro_largo
    
    # Calcular metros necesarios para la cantidad solicitada
    if piezas_por_metro > 0:
        metros_necesarios = cantidad / piezas_por_metro
        # Redondear hacia arriba porque no se puede comprar una fracción de metro
        metros_necesarios = round(metros_necesarios + 0.009, 2)  # Redondeo a 2 decimales hacia arriba
    else:
        metros_necesarios = cantidad * (alto_diseño / 100)  # Fallback: un diseño por fila
    
    # Calcular precio total
    precio_total = metros_necesarios * precio_por_metro
    precio_unitario = precio_total / cantidad if cantidad > 0 else 0.0
    
    return {
        'nombre_proceso': nombre_proceso,
        'tipo_proceso': tipo_proceso,
        'ancho': ancho_diseño,
        'alto': alto_diseño,
        'cantidad': cantidad,
        'precio_unitario': precio_unitario,
        'subtotal': precio_total,
        'costo_setup': None,  # DTF y Sublimación no tienen costo de setup
        'total': precio_total,
        'detalles': {
            'metros_necesarios': metros_necesarios,
            'precio_por_metro': precio_por_metro,
            'ancho_disponible': ancho_disponible,
            'diseños_por_ancho': diseños_por_ancho,
            'diseños_por_metro_largo': diseños_por_metro_largo,
            'piezas_por_metro': piezas_por_metro,
            'piezas_solicitadas': cantidad
        }
    }
