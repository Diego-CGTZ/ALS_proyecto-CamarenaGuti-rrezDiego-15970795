"""
Template filters para manejo seguro de IDs y otros valores.
"""

from flask import Flask

# Import opcional de bson para compatibilidad
try:
    from bson import ObjectId
    HAS_BSON = True
except ImportError:
    # Si no está disponible, crear una clase mock
    HAS_BSON = False
    class ObjectId:
        """Mock ObjectId para compatibilidad."""
        pass

def init_template_filters(app: Flask):
    """
    Inicializa los filtros de template personalizados.
    """
    
    @app.template_filter('safe_id')
    def safe_id_filter(value):
        """
        Convierte cualquier tipo de ID a string de forma segura.
        Útil para evitar errores 'OID object is not subscriptable'.
        """
        if value is None:
            return ""
        
        # Si es un ObjectId de MongoDB, convertir a string
        if HAS_BSON and isinstance(value, ObjectId):
            return str(value)
        elif hasattr(value, '__class__') and 'ObjectId' in value.__class__.__name__:
            return str(value)
        
        # Si ya es string, devolverlo tal como está
        if isinstance(value, str):
            return value
        
        # Para cualquier otro tipo, convertir a string
        return str(value)
    
    @app.template_filter('safe_slice')
    def safe_slice_filter(value, length=8):
        """
        Realiza un slice seguro de un ID, convirtiendo primero a string si es necesario.
        """
        safe_value = safe_id_filter(value)
        return safe_value[:length] if safe_value else ""
    
    @app.template_filter('cliente_display')
    def cliente_display_filter(cliente_id, clientes_dict):
        """
        Muestra el nombre del cliente de forma segura.
        """
        if not cliente_id:
            return "Cliente desconocido"
            
        safe_cliente_id = safe_id_filter(cliente_id)
        
        if safe_cliente_id in clientes_dict:
            return clientes_dict[safe_cliente_id]
        
        return f"Cliente #{safe_cliente_id[:8]}"
    
    @app.template_filter('enum_display')
    def enum_display_filter(enum_value):
        """
        Muestra el valor de un enum de forma segura.
        """
        if hasattr(enum_value, 'value'):
            return enum_value.value.replace('_', ' ').title()
        elif isinstance(enum_value, str):
            return enum_value.replace('_', ' ').title()
        else:
            return str(enum_value)
    
    return app
