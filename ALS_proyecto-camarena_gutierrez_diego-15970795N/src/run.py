#!/usr/bin/env python3
"""
Aplicación principal - Sistema de Gestión de Pedidos Textiles
Aplicación web CRUD para gestionar pedidos de personalización textil.

Autor: Diego Camarena Gutiérrez
Fecha: Mayo 2025
"""

import os
from app import create_app

# Crear aplicación para Gunicorn
app = create_app(os.getenv('FLASK_CONFIG', 'production'))

if __name__ == '__main__':
    # Solo para desarrollo local
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )
