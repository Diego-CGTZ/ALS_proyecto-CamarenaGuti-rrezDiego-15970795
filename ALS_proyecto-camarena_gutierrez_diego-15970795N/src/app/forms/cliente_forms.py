"""
Formularios para gestión de clientes.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Optional, Length


class ClienteForm(FlaskForm):
    """Formulario para crear/editar clientes."""
    nombre = StringField(
        'Nombre *',
        validators=[
            DataRequired(message='El nombre es requerido'),
            Length(max=100, message='El nombre no puede exceder 100 caracteres')
        ],
        render_kw={'placeholder': 'Nombre del cliente', 'class': 'form-control'}
    )
    
    apellido = StringField(
        'Apellido',
        validators=[
            Optional(),
            Length(max=100, message='El apellido no puede exceder 100 caracteres')
        ],
        render_kw={'placeholder': 'Apellido del cliente', 'class': 'form-control'}
    )
    
    email = StringField(
        'Email',
        validators=[
            Optional(),
            Email(message='Ingresa un email válido'),
            Length(max=120, message='El email no puede exceder 120 caracteres')
        ],
        render_kw={'placeholder': 'cliente@email.com', 'class': 'form-control'}
    )
    
    telefono = StringField(
        'Teléfono',
        validators=[
            Optional(),
            Length(max=20, message='El teléfono no puede exceder 20 caracteres')
        ],
        render_kw={'placeholder': '+52 123 456 7890', 'class': 'form-control'}
    )
    
    direccion = TextAreaField(
        'Dirección',
        validators=[
            Optional(),
            Length(max=200, message='La dirección no puede exceder 200 caracteres')
        ],        render_kw={
            'placeholder': 'Dirección completa del cliente',
            'class': 'form-control',
            'rows': 3
        }
    )
    
    empresa = StringField(
        'Empresa',
        validators=[
            Optional(),
            Length(max=100, message='El nombre de la empresa no puede exceder 100 caracteres')
        ],
        render_kw={'placeholder': 'Nombre de la empresa (opcional)', 'class': 'form-control'}
    )
    
    tipo_cliente = SelectField(
        'Tipo de Cliente',
        choices=[('particular', 'Particular'), ('empresa', 'Empresa')],
        default='particular',
        validators=[DataRequired(message='Selecciona el tipo de cliente')],
        render_kw={'class': 'form-select'}
    )
    
    nit = StringField(
        'NIT/Identificación Fiscal',
        validators=[
            Optional(),
            Length(max=20, message='El NIT no puede exceder 20 caracteres')
        ],
        render_kw={'placeholder': 'NIT o Identificación Fiscal', 'class': 'form-control'}
    )
    
    ciudad = StringField(
        'Ciudad',
        validators=[
            Optional(),
            Length(max=100, message='La ciudad no puede exceder 100 caracteres')
        ],
        render_kw={'placeholder': 'Ciudad', 'class': 'form-control'}
    )
    
    departamento = StringField(
        'Departamento/Estado',
        validators=[
            Optional(),
            Length(max=100, message='El departamento no puede exceder 100 caracteres')
        ],
        render_kw={'placeholder': 'Departamento o Estado', 'class': 'form-control'}
    )
    
    notas = TextAreaField(
        'Notas',
        validators=[
            Optional(),
            Length(max=500, message='Las notas no pueden exceder 500 caracteres')
        ],
        render_kw={
            'placeholder': 'Notas adicionales sobre el cliente',
            'class': 'form-control',
            'rows': 4
        }
    )
    
    submit = SubmitField(
        'Guardar Cliente',
        render_kw={'class': 'btn btn-primary'}
    )


class BuscarClienteForm(FlaskForm):
    """Formulario para buscar clientes."""
    
    termino_busqueda = StringField(
        'Buscar Cliente',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Buscar por nombre, email o empresa...',
            'class': 'form-control'
        }
    )
    
    submit = SubmitField(
        'Buscar',
        render_kw={'class': 'btn btn-outline-primary'}
    )
