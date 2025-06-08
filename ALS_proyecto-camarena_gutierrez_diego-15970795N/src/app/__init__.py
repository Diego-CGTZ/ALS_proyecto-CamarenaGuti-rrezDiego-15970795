"""
Paquete principal de la aplicación de gestión textil.
"""

import os
from flask import Flask
from flask_login import LoginManager

__version__ = '1.0.0'
__author__ = 'Tu Nombre'


def create_app(config_name=None):
    """
    Factory function para crear la aplicación Flask.
    
    Args:
        config_name (str): Nombre de la configuración a usar
        
    Returns:
        Flask: Instancia de la aplicación configurada
    """
    # Crear instancia de Flask
    app = Flask(__name__)
    
    # Configurar aplicación
    from config import config
    config_name = config_name or os.getenv('FLASK_CONFIG', 'default')
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    init_extensions(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    return app


def init_extensions(app):
    """Inicializar extensiones de Flask."""
    
    # Añadir hasattr a los globales de Jinja2
    app.jinja_env.globals['hasattr'] = hasattr
    app.jinja_env.globals['str'] = str  # Añadir str para conversiones seguras
    
    # Inicializar filtros de template personalizados
    from app.utils.template_filters import init_template_filters
    init_template_filters(app)
    
    # Inicializar Flask-WTF/CSRF
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect()
    csrf.init_app(app)
    
    # Añadir función csrf_token al contexto de templates
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf)
    
    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = app.config['LOGIN_VIEW']
    login_manager.login_message = app.config['LOGIN_MESSAGE']
    login_manager.login_message_category = app.config['LOGIN_MESSAGE_CATEGORY']
    
    @login_manager.user_loader
    def load_user(user_id):
        """Cargar usuario por ID para Flask-Login."""
        from app.models.usuario import Usuario
        from app.services.storage_service import StorageService
        
        try:
            # Registrar el intento de carga para depuración
            app.logger.info(f"Intentando cargar usuario con ID: {user_id}")
            
            # Asegurarse de que user_id es un string
            if isinstance(user_id, str):
                storage = StorageService()
                
                # En lugar de usar load(), usar find_first para buscar por ID
                usuario = storage.find_first(
                    Usuario,
                    lambda u: u.id == user_id and u.is_active
                )
                
                if usuario:
                    app.logger.info(f"Usuario cargado con éxito: {usuario.username}")
                    return usuario
                else:
                    app.logger.warning(f"No se encontró ningún usuario con ID: {user_id}")
            else:
                app.logger.error(f"ID de usuario inválido: {user_id}, tipo: {type(user_id)}")
            
            return None
            
        except Exception as e:
            app.logger.error(f"Error al cargar usuario: {str(e)}")
            import traceback
            app.logger.error(f"Traceback completo: {traceback.format_exc()}")
            return None


def register_blueprints(app):
    """Registrar todos los blueprints de la aplicación."""
    
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.clientes import clientes_bp
    from app.routes.pedidos import pedidos_bp
    from app.routes.productos import productos_bp
    from app.routes.procesos import procesos_bp
    from app.routes.reportes import reportes_bp
    
    # Registrar blueprints con prefijos
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(clientes_bp, url_prefix='/clientes')
    app.register_blueprint(pedidos_bp, url_prefix='/pedidos')
    app.register_blueprint(productos_bp, url_prefix='/productos')
    app.register_blueprint(procesos_bp, url_prefix='/procesos')
    app.register_blueprint(reportes_bp, url_prefix='/reportes')


def register_error_handlers(app):
    """Registrar manejadores de errores personalizados."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('errors/403.html'), 403
