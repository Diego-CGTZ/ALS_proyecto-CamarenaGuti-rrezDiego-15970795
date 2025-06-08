"""
Formularios para gestión de productos (prendas).
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, FieldList, FormField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Optional


class ProductoForm(FlaskForm):
    """Formulario para crear/editar productos."""
    
    nombre = StringField(
        'Nombre del Producto *',
        validators=[
            DataRequired(message='El nombre es requerido'),
            Length(max=100, message='El nombre no puede exceder 100 caracteres')
        ],
        render_kw={'placeholder': 'Ej: Camiseta Básica', 'class': 'form-control'}
    )
    
    categoria = StringField(
        'Categoría *',
        validators=[
            DataRequired(message='La categoría es requerida'),
            Length(max=50, message='La categoría no puede exceder 50 caracteres')
        ],
        render_kw={'placeholder': 'Ej: Camisetas, Sudaderas, Gorras', 'class': 'form-control'}
    )
    
    precio_base = FloatField(
        'Precio Base *',
        validators=[
            DataRequired(message='El precio es requerido'),
            NumberRange(min=0.01, message='El precio debe ser mayor a 0')
        ],
        render_kw={'placeholder': '0.00', 'class': 'form-control', 'step': '0.01'}
    )
    
    descripcion = TextAreaField(
        'Descripción',
        validators=[
            Optional(),
            Length(max=500, message='La descripción no puede exceder 500 caracteres')
        ],
        render_kw={
            'placeholder': 'Descripción detallada del producto',
            'class': 'form-control',
            'rows': 4
        }
    )
    
    tallas_disponibles = StringField(
        'Tallas Disponibles',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Ej: S,M,L,XL,XXL (separadas por comas)',
            'class': 'form-control'
        },
        default='S,M,L,XL'
    )
    
    colores_disponibles = StringField(
        'Colores Disponibles',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Ej: Blanco,Negro,Azul (separados por comas)',
            'class': 'form-control'
        },
        default='Blanco,Negro'
    )
    
    submit = SubmitField(
        'Guardar Producto',
        render_kw={'class': 'btn btn-primary'}
    )
    
    def validate_tallas_disponibles(self, field):
        """Procesar y validar tallas."""
        if field.data:
            tallas = [talla.strip().upper() for talla in field.data.split(',') if talla.strip()]
            field.processed_data = tallas
        else:
            field.processed_data = ['S', 'M', 'L', 'XL']
    
    def validate_colores_disponibles(self, field):
        """Procesar y validar colores."""
        if field.data:
            colores = [color.strip().title() for color in field.data.split(',') if color.strip()]
            field.processed_data = colores
        else:
            field.processed_data = ['Blanco', 'Negro']


class BuscarProductoForm(FlaskForm):
    """Formulario para buscar productos."""
    
    termino_busqueda = StringField(
        'Buscar Producto',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Buscar por nombre o categoría...',
            'class': 'form-control'
        }
    )
    
    submit = SubmitField(
        'Buscar',
        render_kw={'class': 'btn btn-outline-primary'}
    )
