"""
Configuración de la aplicación.
"""

import os
from datetime import timedelta

class Config:
    """Configuración base."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-123'
    LOGIN_VIEW = 'auth.login'
    LOGIN_MESSAGE = 'Por favor inicia sesión para acceder a esta página.'
    LOGIN_MESSAGE_CATEGORY = 'info'
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    
    @staticmethod
    def init_app(app):
        """Inicialización de la configuración."""
        pass

class DevelopmentConfig(Config):
    """Configuración de desarrollo."""
    DEBUG = True
    
class ProductionConfig(Config):
    """Configuración de producción."""
    DEBUG = False
    
class TestingConfig(Config):
    """Configuración de pruebas."""
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
