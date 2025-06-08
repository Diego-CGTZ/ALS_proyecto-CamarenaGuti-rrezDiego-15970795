"""
Formularios para gestión de procesos.
"""

from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, FloatField, SelectField, 
                     SubmitField, FieldList, FormField, IntegerField, BooleanField)
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from app.models.proceso import TipoProceso, TamañoBordado


class ProcesoForm(FlaskForm):
    """Formulario para crear/editar procesos."""
    
    tipo = SelectField(
        'Tipo de Proceso *',
        choices=[
            (TipoProceso.DTF.value, 'DTF'),
            (TipoProceso.SUBLIMACION.value, 'Sublimación'),
            (TipoProceso.BORDADO.value, 'Bordado'),
            (TipoProceso.VINIL.value, 'Vinil')
        ],
        validators=[DataRequired(message='Selecciona el tipo de proceso')],
        render_kw={'class': 'form-select'}
    )
    
    nombre = StringField(
        'Nombre del Proceso *',
        validators=[
            DataRequired(message='El nombre es requerido'),
            Length(max=100, message='El nombre no puede exceder 100 caracteres')
        ],
        render_kw={'placeholder': 'Ej: DTF Premium, Bordado Básico', 'class': 'form-control'}
    )
    
    descripcion = TextAreaField(
        'Descripción',
        validators=[
            Optional(),
            Length(max=500, message='La descripción no puede exceder 500 caracteres')
        ],
        render_kw={
            'placeholder': 'Descripción detallada del proceso...',
            'class': 'form-control',
            'rows': 4
        }
    )
    
    submit = SubmitField(
        'Guardar Proceso',
        render_kw={'class': 'btn btn-primary'}
    )


class ConfiguracionDTFForm(FlaskForm):
    """Formulario para configurar precios de DTF."""
    
    precio_por_metro = FloatField(
        'Precio por Metro *',
        validators=[
            DataRequired(message='El precio por metro es requerido'),
            NumberRange(min=0.01, message='El precio debe ser mayor a 0')
        ],
        render_kw={'placeholder': '0.00', 'class': 'form-control', 'step': '0.01'}
    )
    
    submit = SubmitField(
        'Guardar Configuración',
        render_kw={'class': 'btn btn-success'}
    )


class ConfiguracionSublimacionForm(FlaskForm):
    """Formulario para configurar precios de Sublimación."""
    
    precio_por_metro = FloatField(
        'Precio por Metro *',
        validators=[
            DataRequired(message='El precio por metro es requerido'),
            NumberRange(min=0.01, message='El precio debe ser mayor a 0')
        ],
        render_kw={'placeholder': '0.00', 'class': 'form-control', 'step': '0.01'}
    )
    
    submit = SubmitField(
        'Guardar Configuración',
        render_kw={'class': 'btn btn-success'}
    )


class ConfiguracionBordadoForm(FlaskForm):
    """Formulario para configurar precios de Bordado."""
    
    precio_setup = FloatField(
        'Precio de Setup',
        validators=[
            NumberRange(min=0, message='El precio de setup no puede ser negativo')
        ],
        render_kw={'placeholder': '0.00', 'class': 'form-control', 'step': '0.01'},
        default=0.0
    )
    
    precio_pequeño = FloatField(
        'Precio Tamaño Pequeño *',
        validators=[
            DataRequired(message='El precio para tamaño pequeño es requerido'),
            NumberRange(min=0.01, message='El precio debe ser mayor a 0')
        ],
        render_kw={'placeholder': '0.00', 'class': 'form-control', 'step': '0.01'}
    )
    
    precio_mediano = FloatField(
        'Precio Tamaño Mediano *',
        validators=[
            DataRequired(message='El precio para tamaño mediano es requerido'),
            NumberRange(min=0.01, message='El precio debe ser mayor a 0')
        ],
        render_kw={'placeholder': '0.00', 'class': 'form-control', 'step': '0.01'}
    )
    
    precio_grande = FloatField(
        'Precio Tamaño Grande *',
        validators=[
            DataRequired(message='El precio para tamaño grande es requerido'),
            NumberRange(min=0.01, message='El precio debe ser mayor a 0')
        ],
        render_kw={'placeholder': '0.00', 'class': 'form-control', 'step': '0.01'}
    )
    
    precio_extra_grande = FloatField(
        'Precio Tamaño Extra Grande *',
        validators=[
            DataRequired(message='El precio para tamaño extra grande es requerido'),
            NumberRange(min=0.01, message='El precio debe ser mayor a 0')
        ],
        render_kw={'placeholder': '0.00', 'class': 'form-control', 'step': '0.01'}
    )
    
    submit = SubmitField(
        'Guardar Configuración',
        render_kw={'class': 'btn btn-success'}
    )


class TipoVinilForm(FlaskForm):
    """Formulario para un tipo de vinil."""
    
    nombre = StringField(
        'Nombre del Vinil *',
        validators=[
            DataRequired(message='El nombre es requerido'),
            Length(max=50, message='El nombre no puede exceder 50 caracteres')
        ],
        render_kw={'placeholder': 'Ej: Vinil Básico, Vinil Premium', 'class': 'form-control'}
    )
    
    precio_por_cm2 = FloatField(
        'Precio por cm² *',
        validators=[
            DataRequired(message='El precio por cm² es requerido'),
            NumberRange(min=0.001, message='El precio debe ser mayor a 0')
        ],
        render_kw={'placeholder': '0.000', 'class': 'form-control', 'step': '0.001'}
    )


class ConfiguracionVinilForm(FlaskForm):
    """Formulario para configurar tipos de vinil."""
    
    precio_por_cm2_base = FloatField(
        'Precio Base por cm²',
        validators=[
            NumberRange(min=0, message='El precio base no puede ser negativo')
        ],
        render_kw={'placeholder': '0.000', 'class': 'form-control', 'step': '0.001'},
        default=0.0
    )
    
    tipos_vinil = FieldList(FormField(TipoVinilForm), min_entries=1)
    
    submit = SubmitField(
        'Guardar Configuración',
        render_kw={'class': 'btn btn-success'}
    )


class CalculadoraProcesoForm(FlaskForm):
    """Formulario para calcular precios de procesos."""
    
    proceso_id = SelectField(
        'Proceso *',
        validators=[DataRequired(message='Selecciona un proceso')],
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
    
    tamaño_bordado = SelectField(
        'Tamaño de Bordado',
        choices=[
            ('', 'Seleccionar...'),
            (TamañoBordado.PEQUEÑO.value, 'Pequeño'),
            (TamañoBordado.MEDIANO.value, 'Mediano'),
            (TamañoBordado.GRANDE.value, 'Grande'),
            (TamañoBordado.EXTRA_GRANDE.value, 'Extra Grande')        ],
        validators=[Optional()],
        render_kw={'class': 'form-select'}
    )
    
    tipo_vinil = StringField(
        'Tipo de Vinil',
        validators=[Optional()],
        render_kw={'placeholder': 'Nombre del tipo de vinil', 'class': 'form-control'}
    )
    
    incluir_setup_bordado = BooleanField(
        'Incluir Setup de Bordado',
        default=True,
        render_kw={'class': 'form-check-input'}
    )
    
    submit = SubmitField(
        'Calcular Precio',
        render_kw={'class': 'btn btn-info'}
    )
