"""
Clase base para todos los modelos de la aplicación.
Proporciona funcionalidad común y consistencia en el diseño.
"""

from datetime import datetime
from typing import Dict, Any
from enum import Enum
import uuid


class BaseModel:
    """
    Clase base para todos los modelos de datos.
    Proporciona funcionalidad común como ID, timestamps y validación.
    """
    
    def __init__(self):
        """Inicializar modelo base."""
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Solo establecer is_active si no es una property heredada (como en UserMixin)
        if not hasattr(type(self), 'is_active') or not isinstance(getattr(type(self), 'is_active'), property):
            self.is_active = True
        else:
            # Si is_active es una property heredada, crear un atributo privado para nuestro control
            self._is_active = True
        
    @property
    def safe_id(self):
        """
        Devuelve una versión segura del ID (siempre string).
        Útil para usar en templates donde se necesita un ID suscribible.
        """
        return str(self.id) if self.id is not None else ""
    
    @property
    def active_status(self):
        """
        Devuelve el estado activo del objeto, manejando tanto is_active directo
        como _is_active privado para casos de herencia conflictiva.
        """
        if hasattr(self, '_is_active'):
            return self._is_active
        elif hasattr(self, 'is_active'):
            return self.is_active
        else:
            return True  # Default to active if no status is set
    
    def update_timestamp(self):
        """Actualizar timestamp de modificación."""
        self.updated_at = datetime.now()
    
    def soft_delete(self):
        """Eliminación lógica (soft delete)."""
        if hasattr(self, '_is_active'):
            self._is_active = False
        else:
            self.is_active = False
        self.update_timestamp()
    
    def restore(self):
        """Restaurar objeto eliminado lógicamente."""
        if hasattr(self, '_is_active'):
            self._is_active = True
        else:
            self.is_active = True
        self.update_timestamp()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertir el objeto a diccionario.
        
        Returns:
            Dict[str, Any]: Representación en diccionario del objeto
        """
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif isinstance(value, Enum):
                    result[key] = value.value
                else:
                    result[key] = value
        return result
    
    def prepare_for_serialization(self):
        """
        Prepara el objeto para serialización de Sirope.
        Convierte los enums a sus valores para evitar errores de JSON.
        Retorna un diccionario con los valores originales para restaurar después.
        """
        original_values = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Enum):
                original_values[key] = value
                setattr(self, key, value.value)
        return original_values
    
    def restore_after_serialization(self, original_values: Dict[str, Any]):
        """
        Restaura los valores originales después de la serialización.
        
        Args:
            original_values: Diccionario con los valores originales de los enums
        """
        for key, value in original_values.items():
            setattr(self, key, value)
    
    def restore_enums_after_loading(self):
        """
        Restaura los enums después de cargar el objeto desde Sirope.
        Este método debe ser llamado después de cargar un objeto para 
        convertir strings de vuelta a enums donde sea apropiado.
        """
        # Este método debe ser sobrescrito en las clases hijas que tengan enums
        pass
    
    def __str__(self) -> str:
        """Representación en string del objeto."""
        return f"{self.__class__.__name__}(id={self.id})"
    
    def __repr__(self) -> str:
        """Representación para depuración."""
        return self.__str__()
