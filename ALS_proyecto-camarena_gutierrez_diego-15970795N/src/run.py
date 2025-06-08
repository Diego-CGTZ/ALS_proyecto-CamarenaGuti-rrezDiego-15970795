#!/usr/bin/env python3
"""
Aplicación principal - Sistema de Gestión de Pedidos Textiles
Aplicación web CRUD para gestionar pedidos de personalización textil.

Autor: [Tu nombre]
Fecha: Mayo 2025
"""

import os
from app import create_app


if __name__ == '__main__':
    # Crear aplicación
    app = create_app()
    
    # Ejecutar aplicación
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )
