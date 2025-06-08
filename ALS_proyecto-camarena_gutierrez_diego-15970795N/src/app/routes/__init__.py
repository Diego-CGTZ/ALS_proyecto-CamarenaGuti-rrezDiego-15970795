"""
Rutas de la aplicación.
"""

from .main import main_bp
from .auth import auth_bp
from .clientes import clientes_bp
from .productos import productos_bp
from .procesos import procesos_bp
from .pedidos import pedidos_bp

__all__ = [
    'main_bp',
    'auth_bp', 
    'clientes_bp',
    'productos_bp',
    'procesos_bp',
    'pedidos_bp'
]
