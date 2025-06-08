"""
Rutas de autenticación (login, logout, registro).
Versión simplificada para depuración.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.forms.auth_forms import LoginForm, RegisterForm, ChangePasswordForm
from app.models.usuario import Usuario
from app.services.storage_service import StorageService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión."""
    # Importar logger
    from flask import current_app
    
    if current_user.is_authenticated:
        current_app.logger.info('Usuario ya autenticado, redirigiendo a dashboard')
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        storage = StorageService()
        
        try:
            # Buscar usuario por username
            current_app.logger.info(f'Intentando autenticar usuario: {form.username.data}')
            usuario = storage.find_first(
                Usuario,
                lambda u: u.username == form.username.data and u.is_active
            )
            
            if usuario:
                current_app.logger.info(f'Usuario encontrado: {usuario.username}')
                if usuario.check_password(form.password.data):
                    current_app.logger.info('Contraseña correcta, iniciando sesión')
                    login_success = login_user(usuario, remember=form.remember_me.data)
                    if login_success:
                        current_app.logger.info(f'Sesión iniciada correctamente: {current_user.is_authenticated}')
                        flash(f'¡Bienvenido, {usuario.get_full_name()}!', 'success')
                        
                        # Redireccionar a la página solicitada o al dashboard
                        next_page = request.args.get('next')
                        target_url = next_page or url_for('main.dashboard')
                        current_app.logger.info(f'Redirigiendo a: {target_url}')
                        return redirect(target_url)
                    else:
                        current_app.logger.error('login_user falló')
                        flash('Error al iniciar sesión. Contacte al administrador.', 'error')
                else:
                    current_app.logger.warning('Contraseña incorrecta')
                    flash('Usuario o contraseña incorrectos.', 'error')
            else:
                current_app.logger.warning(f'Usuario no encontrado: {form.username.data}')
                flash('Usuario o contraseña incorrectos.', 'error')
                
        except Exception as e:
            current_app.logger.error(f'Error durante login: {str(e)}')
            flash(f'Error en el sistema: {str(e)}', 'error')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro de usuarios."""
    # Importar logger
    from flask import current_app
    
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        storage = StorageService()
        
        try:
            # Verificar si ya existe un usuario con ese nombre o email
            usuario_existente = storage.find_first(
                Usuario,
                lambda u: u.username == form.username.data or u.email == form.email.data
            )
            
            if usuario_existente:
                if usuario_existente.username == form.username.data:
                    flash('Este nombre de usuario ya está en uso. Por favor elige otro.', 'error')
                else:
                    flash('Este email ya está registrado. Por favor utiliza otro.', 'error')
                return render_template('auth/register.html', form=form)
            
            # Crear nuevo usuario
            current_app.logger.info(f'Creando nuevo usuario: {form.username.data}')
            nuevo_usuario = Usuario(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                nombre=form.nombre.data,
                apellidos=form.apellidos.data
            )
            
            # Guardar usuario
            current_app.logger.info('Intentando guardar usuario en la base de datos')
            user_id = storage.save(nuevo_usuario)
            
            if user_id:
                current_app.logger.info(f'Usuario guardado exitosamente con ID: {user_id}')
                flash(f'Usuario {form.username.data} registrado exitosamente. ¡Ya puedes iniciar sesión!', 'success')
                return redirect(url_for('auth.login'))
            else:
                current_app.logger.error('Error al guardar usuario: no se obtuvo ID')
                flash('Error al registrar el usuario. Inténtalo de nuevo.', 'error')
                
        except Exception as e:
            current_app.logger.error(f'Error al registrar usuario: {str(e)}')
            flash(f'Error en el sistema: {str(e)}', 'error')
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión del usuario."""
    nombre_usuario = current_user.get_full_name()
    logout_user()
    flash(f'Sesión cerrada correctamente. ¡Hasta luego, {nombre_usuario}!', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Cambiar contraseña del usuario actual."""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            storage = StorageService()
            
            try:
                # Cambiar contraseña
                current_user.set_password(form.new_password.data)
                storage.save(current_user)
                
                flash('Contraseña cambiada exitosamente.', 'success')
                return redirect(url_for('main.profile'))
                
            except Exception as e:
                flash(f'Error al cambiar la contraseña: {str(e)}', 'error')
        else:
            flash('La contraseña actual es incorrecta.', 'error')
    
    return render_template('auth/change_password.html', form=form)
