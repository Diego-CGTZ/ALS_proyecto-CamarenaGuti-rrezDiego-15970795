"""
Formularios para gestión de pedidos y personalizaciones.
"""

from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, FloatField, IntegerField, 
                     SelectField, DateTimeField, BooleanField, SubmitField, 
                     FieldList, FormField, HiddenField)
from wtforms.validators import DataRequired, NumberRange, Length, Optional, ValidationError
from datetime import datetime, timedelta
from app.models.proceso import TipoProceso, TamañoBordado


class PersonalizacionForm(FlaskForm):
    """Formulario para una personalización individual."""
    
    proceso_id = SelectField(
        'Proceso *',
        validators=[DataRequired(message='Selecciona un proceso')],
        render_kw={'class': 'form-select'}
    )
    
    posicion = SelectField(
        'Posición en la Prenda *',
        choices=[
            (1, '1 - Pecho izquierdo'),
            (2, '2 - Pecho derecho'),
            (3, '3 - Pecho centro'),
            (4, '4 - Espalda superior'),
            (5, '5 - Espalda centro'),
            (6, '6 - Espalda inferior'),
            (7, '7 - Manga izquierda'),
            (8, '8 - Manga derecha'),
            (9, '9 - Cuello'),
            (10, '10 - Personalizado')
        ],
        validators=[DataRequired(message='Selecciona una posición')],
        coerce=int,
        render_kw={'class': 'form-select'}
    )
    
    descripcion = TextAreaField(
        'Descripción',
        validators=[
            Optional(),
            Length(max=200, message='La descripción no puede exceder 200 caracteres')
        ],
        render_kw={
            'placeholder': 'Describe la personalización...',
            'class': 'form-control',
            'rows': 2
        }
    )
    
    ancho_diseño = FloatField(
        'Ancho del Diseño (cm)',
        validators=[
            Optional(),
            NumberRange(min=0.1, max=100, message='El ancho debe estar entre 0.1 y 100 cm')
        ],
        render_kw={'placeholder': '0.0', 'class': 'form-control', 'step': '0.1'}
    )
    
    alto_diseño = FloatField(
        'Alto del Diseño (cm)',
        validators=[
            Optional(),
            NumberRange(min=0.1, max=100, message='El alto debe estar entre 0.1 y 100 cm')
        ],
        render_kw={'placeholder': '0.0', 'class': 'form-control', 'step': '0.1'}
    )
    
    # Campos específicos para bordado
    tamaño_bordado = SelectField(
        'Tamaño de Bordado',
        choices=[
            ('', 'Seleccionar...'),
            (TamañoBordado.PEQUEÑO.value, 'Pequeño'),
            (TamañoBordado.MEDIANO.value, 'Mediano'),
            (TamañoBordado.GRANDE.value, 'Grande'),
            (TamañoBordado.EXTRA_GRANDE.value, 'Extra Grande')
        ],
        validators=[Optional()],
        render_kw={'class': 'form-select'}
    )
    
    incluir_setup_bordado = BooleanField(
        'Incluir Setup de Bordado',
        default=True,
        render_kw={'class': 'form-check-input'}
    )
    
    # Campo específico para vinil
    tipo_vinil = StringField(
        'Tipo de Vinil',
        validators=[Optional()],
        render_kw={'placeholder': 'Tipo de vinil a usar', 'class': 'form-control'}
    )


class ItemPedidoForm(FlaskForm):
    """Formulario para un item del pedido."""
    
    producto_id = SelectField(
        'Producto *',
        validators=[DataRequired(message='Selecciona un producto')],
        render_kw={'class': 'form-select'}
    )
    
    talla = SelectField(
        'Talla *',
        validators=[DataRequired(message='Selecciona una talla')],
        render_kw={'class': 'form-select'}
    )
    
    color = SelectField(
        'Color *',
        validators=[DataRequired(message='Selecciona un color')],
        render_kw={'class': 'form-select'}
    )
    
    cantidad = IntegerField(
        'Cantidad *',
        validators=[
            DataRequired(message='La cantidad es requerida'),
            NumberRange(min=1, max=1000, message='La cantidad debe estar entre 1 y 1000')
        ],
        render_kw={'placeholder': '1', 'class': 'form-control'},
        default=1
    )
    
    precio_prenda = FloatField(
        'Precio por Prenda *',
        validators=[
            DataRequired(message='El precio es requerido'),
            NumberRange(min=0.01, message='El precio debe ser mayor a 0')
        ],
        render_kw={'placeholder': '0.00', 'class': 'form-control', 'step': '0.01'}
    )
    
    # Lista de personalizaciones (se maneja dinámicamente)
    personalizaciones = FieldList(FormField(PersonalizacionForm), min_entries=0)


class PedidoForm(FlaskForm):
    """Formulario principal para crear/editar pedidos."""
    
    cliente_id = SelectField(
        'Cliente *',
        validators=[DataRequired(message='Selecciona un cliente')],
        render_kw={'class': 'form-select'}
    )
    
    fecha_entrega = DateTimeField(
        'Fecha de Entrega *',
        validators=[DataRequired(message='La fecha de entrega es requerida')],
        render_kw={'class': 'form-control', 'type': 'datetime-local'},
        format='%Y-%m-%dT%H:%M'
    )
    
    prioridad = SelectField(
        'Prioridad *',
        choices=[
            ('normal', 'Normal'),
            ('alta', 'Alta'),
            ('urgente', 'Urgente')        ],
        validators=[DataRequired(message='Selecciona una prioridad')],
        render_kw={'class': 'form-select'},
        default='normal'
    )
    
    porcentaje_utilidad = FloatField(
        'Porcentaje de Utilidad (%)',
        validators=[
            DataRequired(message='El porcentaje de utilidad es requerido'),
            NumberRange(min=0, max=100, message='El porcentaje debe estar entre 0 y 100')
        ],
        render_kw={'placeholder': '30.0', 'class': 'form-control', 'step': '0.1'},
        default=30.0
    )
    
    descripcion = TextAreaField(
        'Descripción',
        validators=[
            Optional(),
            Length(max=500, message='La descripción no puede exceder 500 caracteres')
        ],
        render_kw={
            'placeholder': 'Descripción opcional del pedido...',
            'class': 'form-control',
            'rows': 3
        }
    )
    
    # Campos para selección de prendas integrada
    incluir_garments = BooleanField(
        'Agregar Prendas al Pedido',
        default=False,
        render_kw={'class': 'form-check-input'}
    )
    
    producto_id = SelectField(
        'Producto',
        validators=[Optional()],
        render_kw={'class': 'form-select'},
        choices=[]
    )
    
    talla = SelectField(
        'Talla',
        validators=[Optional()],
        render_kw={'class': 'form-select'},
        choices=[]
    )
    
    color = SelectField(
        'Color', 
        validators=[Optional()],
        render_kw={'class': 'form-select'},
        choices=[]
    )
    
    cantidad_garment = IntegerField(
        'Cantidad',
        validators=[
            Optional(),
            NumberRange(min=1, max=1000, message='La cantidad debe estar entre 1 y 1000')
        ],
        render_kw={'placeholder': '1', 'class': 'form-control'},
        default=1
    )
    
    precio_unitario = FloatField(
        'Precio Unitario',
        validators=[Optional()],
        render_kw={'placeholder': '0.00', 'class': 'form-control', 'step': '0.01', 'readonly': True}
    )
    
    notas_garment = TextAreaField(
        'Notas de la Prenda',
        validators=[
            Optional(),
            Length(max=200, message='Las notas no pueden exceder 200 caracteres')
        ],
        render_kw={
            'placeholder': 'Instrucciones especiales para esta prenda...',
            'class': 'form-control',
            'rows': 2
        }
    )
    
    descuento_porcentaje = FloatField(
        'Descuento (%)',
        validators=[
            Optional(),
            NumberRange(min=0, max=100, message='El descuento debe estar entre 0 y 100')
        ],
        render_kw={'placeholder': '0.0', 'class': 'form-control', 'step': '0.01'},
        default=0.0
    )
    
    notas = TextAreaField(
        'Notas del Pedido',
        validators=[
            Optional(),
            Length(max=500, message='Las notas no pueden exceder 500 caracteres')
        ],
        render_kw={
            'placeholder': 'Notas e instrucciones especiales para el pedido...',
            'class': 'form-control',
            'rows': 3
        }
    )
    
    notas_internas = TextAreaField(
        'Notas Internas',
        validators=[
            Optional(),
            Length(max=500, message='Las notas internas no pueden exceder 500 caracteres')
        ],
        render_kw={
            'placeholder': 'Notas internas (no visible para el cliente)...',
            'class': 'form-control',
            'rows': 3
        }
    )
    
    submit = SubmitField(
        'Guardar Pedido',
        render_kw={'class': 'btn btn-primary'}
    )
    
    def validate_fecha_entrega(self, field):
        """Validar que la fecha de entrega sea futura."""
        if field.data and field.data < datetime.now():
            raise ValidationError('La fecha de entrega debe ser en el futuro.')


class PagoForm(FlaskForm):
    """Formulario para registrar pagos."""
    
    monto = FloatField(
        'Monto del Pago *',
        validators=[
            DataRequired(message='El monto es requerido'),
            NumberRange(min=0.01, message='El monto debe ser mayor a 0')
        ],
        render_kw={'placeholder': '0.00', 'class': 'form-control', 'step': '0.01'}
    )
    
    es_anticipo = BooleanField(
        'Es Anticipo (50%)',
        render_kw={'class': 'form-check-input'}
    )
    
    notas_pago = TextAreaField(
        'Notas del Pago',
        validators=[
            Optional(),
            Length(max=200, message='Las notas no pueden exceder 200 caracteres')
        ],
        render_kw={
            'placeholder': 'Método de pago, referencia, etc...',
            'class': 'form-control',
            'rows': 2
        }
    )
    
    submit = SubmitField(
        'Registrar Pago',
        render_kw={'class': 'btn btn-success'}
    )


class BuscarPedidoForm(FlaskForm):
    """Formulario para buscar pedidos."""
    
    termino_busqueda = StringField(
        'Buscar Pedido',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Buscar por número, cliente...',
            'class': 'form-control'
        }
    )
    
    estado = SelectField(
        'Estado',
        choices=[
            ('', 'Todos los estados'),
            ('PENDIENTE', 'Pendiente'),
            ('EN_PROCESO', 'En Proceso'),
            ('COMPLETADO', 'Completado'),
            ('ENTREGADO', 'Entregado'),
            ('CANCELADO', 'Cancelado')
        ],
        validators=[Optional()],
        render_kw={'class': 'form-select'}
    )
    
    submit = SubmitField(
        'Buscar',
        render_kw={'class': 'btn btn-outline-primary'}
    )


class CambiarEstadoPedidoForm(FlaskForm):
    """Formulario para cambiar estado de pedido."""
    
    nuevo_estado = SelectField(
        'Nuevo Estado *',
        choices=[
            ('PENDIENTE', 'Pendiente'),
            ('EN_PROCESO', 'En Proceso'),
            ('COMPLETADO', 'Completado'),
            ('ENTREGADO', 'Entregado'),
            ('CANCELADO', 'Cancelado')
        ],
        validators=[DataRequired(message='Selecciona un estado')],
        render_kw={'class': 'form-select'}
    )
    
    comentario = TextAreaField(
        'Comentario del Cambio',
        validators=[
            Optional(),
            Length(max=200, message='El comentario no puede exceder 200 caracteres')
        ],
        render_kw={
            'placeholder': 'Razón del cambio de estado...',
            'class': 'form-control',
            'rows': 2
        }
    )
    
    submit = SubmitField(
        'Cambiar Estado',
        render_kw={'class': 'btn btn-warning'}
    )
