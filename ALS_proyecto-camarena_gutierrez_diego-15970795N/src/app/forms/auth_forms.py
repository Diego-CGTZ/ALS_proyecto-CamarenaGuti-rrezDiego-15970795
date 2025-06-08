"""
Formularios de autenticación.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.services.storage_service import StorageService
from app.models.usuario import Usuario


class LoginForm(FlaskForm):
    """Formulario de inicio de sesión."""
    
    username = StringField(
        'Usuario',
        validators=[DataRequired(message='El usuario es requerido')],
        render_kw={'placeholder': 'Ingresa tu usuario', 'class': 'form-control'}
    )
    
    password = PasswordField(
        'Contraseña',
        validators=[DataRequired(message='La contraseña es requerida')],
        render_kw={'placeholder': 'Ingresa tu contraseña', 'class': 'form-control'}
    )
    
    remember_me = BooleanField(
        'Recordarme',
        render_kw={'class': 'form-check-input'}
    )
    
    submit = SubmitField(
        'Iniciar Sesión',
        render_kw={'class': 'btn btn-primary w-100'}
    )


class RegisterForm(FlaskForm):
    """Formulario de registro de usuarios."""
    
    username = StringField(
        'Usuario',
        validators=[
            DataRequired(message='El usuario es requerido'),
            Length(min=3, max=20, message='El usuario debe tener entre 3 y 20 caracteres')
        ],
        render_kw={'placeholder': 'Elige un nombre de usuario', 'class': 'form-control'}
    )
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='El email es requerido'),
            Email(message='Ingresa un email válido')
        ],
        render_kw={'placeholder': 'tu@email.com', 'class': 'form-control'}
    )
    
    nombre = StringField(
        'Nombre',
        validators=[DataRequired(message='El nombre es requerido')],
        render_kw={'placeholder': 'Tu nombre', 'class': 'form-control'}
    )
    
    apellidos = StringField(
        'Apellidos',
        validators=[DataRequired(message='Los apellidos son requeridos')],
        render_kw={'placeholder': 'Tus apellidos', 'class': 'form-control'}
    )
    
    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es requerida'),
            Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
        ],
        render_kw={'placeholder': 'Elige una contraseña segura', 'class': 'form-control'}
    )
    
    password2 = PasswordField(
        'Confirmar Contraseña',
        validators=[
            DataRequired(message='Confirma tu contraseña'),
            EqualTo('password', message='Las contraseñas deben coincidir')
        ],
        render_kw={'placeholder': 'Repite tu contraseña', 'class': 'form-control'}
    )
    
    submit = SubmitField(
        'Registrarse',
        render_kw={'class': 'btn btn-success w-100'}
    )
    
    def validate_username(self, username):
        """Validar que el usuario no exista."""
        storage = StorageService()
        usuario = storage.find_first(
            Usuario, 
            lambda u: u.username == username.data and u.is_active
        )
        if usuario:
            raise ValidationError('Este nombre de usuario ya está en uso.')
    
    def validate_email(self, email):
        """Validar que el email no exista."""
        storage = StorageService()
        usuario = storage.find_first(
            Usuario,
            lambda u: u.email == email.data and u.is_active
        )
        if usuario:
            raise ValidationError('Este email ya está registrado.')


class ChangePasswordForm(FlaskForm):
    """Formulario para cambiar contraseña."""
    
    current_password = PasswordField(
        'Contraseña Actual',
        validators=[DataRequired(message='Ingresa tu contraseña actual')],
        render_kw={'placeholder': 'Tu contraseña actual', 'class': 'form-control'}
    )
    
    new_password = PasswordField(
        'Nueva Contraseña',
        validators=[
            DataRequired(message='Ingresa una nueva contraseña'),
            Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
        ],
        render_kw={'placeholder': 'Nueva contraseña', 'class': 'form-control'}
    )
    
    new_password2 = PasswordField(
        'Confirmar Nueva Contraseña',
        validators=[
            DataRequired(message='Confirma tu nueva contraseña'),
            EqualTo('new_password', message='Las contraseñas deben coincidir')
        ],
        render_kw={'placeholder': 'Repite la nueva contraseña', 'class': 'form-control'}
    )
    
    submit = SubmitField(
        'Cambiar Contraseña',
        render_kw={'class': 'btn btn-warning'}
    )
