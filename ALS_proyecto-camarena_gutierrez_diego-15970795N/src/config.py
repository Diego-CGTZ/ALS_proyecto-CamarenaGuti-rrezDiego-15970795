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
    
    # Configuración de Redis para Sirope
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    
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
    
    # En producción sin Redis, usar backend en memoria
    # NOTA: Los datos se perderán al reiniciar el servicio
    # Para persistencia real, configurar Redis en la nube
    USE_REDIS = False
    
    @staticmethod
    def init_app(app):
        """Configuración especial para producción."""
        # Log que estamos en producción
        import logging
        logging.basicConfig(level=logging.INFO)
        app.logger.info("=== APLICACIÓN EN MODO PRODUCCIÓN ===")
        app.logger.info("Backend: Memoria (demo) - Los datos no persisten")
        app.logger.info("Para persistencia real, configurar Redis externo")
    
class TestingConfig(Config):
    """Configuración de pruebas."""
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
