"""
Servicio simplificado de almacenamiento usando Sirope/Redis.
Centraliza todas las operaciones de persistencia de datos.
"""

import sirope
import redis
from typing import Any, List, Optional, Type
from flask import current_app


class StorageService:
    """
    Servicio centralizado para operaciones de almacenamiento.
    Encapsula la lógica de Sirope/Redis y proporciona una interfaz limpia.
    """
    
    def __init__(self):
        """Inicializar el servicio de almacenamiento."""
        self._sirope = None
    
    @property
    def sirope(self):
        """Obtener instancia de Sirope (lazy loading)."""
        if self._sirope is None:
            try:
                current_app.logger.info("Inicializando Sirope")
                # Creamos una instancia simple de Sirope
                self._sirope = sirope.Sirope()
                current_app.logger.info("Sirope inicializado con éxito")
            except Exception as e:
                current_app.logger.error(f"Error al inicializar Sirope: {e}")
                raise
        return self._sirope
    
    def save(self, obj: Any) -> str:
        """
        Guardar un objeto en el almacenamiento.
        
        Args:
            obj: Objeto a guardar
            
        Returns:
            str: ID del objeto guardado
        """
        try:
            # Añadir más detalles para depuración
            from flask import current_app
            from app.models.base_model import BaseModel
            
            obj_type = type(obj).__name__
            obj_id = getattr(obj, 'id', 'sin_id')
            current_app.logger.info(f"Guardando objeto de tipo: {obj_type}, ID actual: {obj_id}")
            
            # Si es un Usuario, registrar más información
            if obj_type == 'Usuario':
                username = getattr(obj, 'username', 'desconocido')
                current_app.logger.info(f"Guardando Usuario: {username}")
            
            # Comprobar que sirope está disponible
            if not hasattr(self, 'sirope') or self.sirope is None:
                current_app.logger.error("¡Error crítico! Sirope no está disponible")
                raise RuntimeError("Sirope no está disponible")
                
            # Preparar objeto para serialización si es BaseModel
            original_values = {}
            original_id = getattr(obj, 'id', None)
            
            if isinstance(obj, BaseModel):
                current_app.logger.info("Preparando objeto BaseModel para serialización")
                original_values = obj.prepare_for_serialization()
            
            try:
                # Guardar el objeto directamente
                obj_id = self.sirope.save(obj)
                
                if not obj_id:
                    current_app.logger.error("Sirope devolvió un ID vacío")
                    raise ValueError("Error al guardar: ID vacío")
                
                # Registrar éxito
                current_app.logger.info(f"Objeto de tipo {obj_type} guardado exitosamente con ID: {obj_id}")
                
                # Importante: Si teníamos un ID original, lo retornamos para mantener consistencia
                if original_id and isinstance(obj, BaseModel):
                    current_app.logger.info(f"Manteniendo ID original: {original_id}")
                    return original_id
                
                return obj_id
                
            finally:
                # Restaurar valores originales si es BaseModel
                if isinstance(obj, BaseModel) and original_values:
                    current_app.logger.info("Restaurando valores originales después de serialización")
                    obj.restore_after_serialization(original_values)
            
        except Exception as e:
            current_app.logger.error(f"Error guardando objeto: {e}", exc_info=True)
            raise
    
    def load(self, obj_id: str) -> Any:
        """
        Cargar un objeto por su ID.
        
        Args:
            obj_id: ID del objeto a cargar
            
        Returns:
            Any: Objeto cargado o None si no existe
        """
        try:
            current_app.logger.info(f"Intentando cargar objeto con ID: {obj_id}")
            try:
                obj = self.sirope.load(obj_id)
            except Exception as load_error:
                current_app.logger.error(f"Error cargando objeto {obj_id}: {load_error}")
                # Si hay error al cargar, intentamos búsqueda alternativa inmediatamente
                obj = None
            
            # Si es un BaseModel, restaurar enums automáticamente
            from app.models.base_model import BaseModel
            if obj and isinstance(obj, BaseModel):
                obj.restore_enums_after_loading()
                current_app.logger.info(f"Enums restaurados para objeto de tipo: {type(obj).__name__}")
                return obj
            
            if not obj:
                current_app.logger.warning(f"No se encontró objeto con ID: {obj_id}, intentando búsqueda alternativa")
                # Si no encontramos el objeto, intentamos una búsqueda alternativa
                # Podría estar en cualquier tipo de modelo, intentemos con los principales
                from app.models.cliente import Cliente
                from app.models.pedido import Pedido
                from app.models.producto import Producto
                
                for model_type in [Cliente, Pedido, Producto]:
                    all_objects = self.find_all(model_type)
                    for item in all_objects:
                        if item.id == obj_id:
                            current_app.logger.info(f"Encontrado objeto por búsqueda alternativa, tipo: {type(item).__name__}")
                            return item
            
            return obj
        except Exception as e:
            current_app.logger.error(f"Error cargando objeto {obj_id}: {e}")
            return None
    
    def get(self, class_type_or_id, obj_id=None) -> Any:
        """
        Obtener un objeto por su ID (alias de load para compatibilidad).
        Admite tanto get(id) como get(Class, id) para compatibilidad.
        
        Args:
            class_type_or_id: Clase del objeto o ID directo
            obj_id: ID del objeto (opcional si se proporciona class_type_or_id como ID)
            
        Returns:
            Any: Objeto obtenido o None si no existe
        """
        if obj_id is None:
            # Llamada con un solo parámetro: get(id)
            try:
                return self.load(class_type_or_id)
            except Exception as e:
                current_app.logger.error(f"Error en get(id) para {class_type_or_id}: {e}")
                # Si falla, podemos intentar buscar el objeto por ID en la colección completa
                from app.models.pedido import Pedido
                if class_type_or_id and isinstance(class_type_or_id, str):
                    pedidos = self.find_all(Pedido)
                    for pedido in pedidos:
                        if pedido.id == class_type_or_id:
                            current_app.logger.info(f"Se encontró pedido con ID alternativo: {class_type_or_id}")
                            # Arreglar el enum si es necesario
                            if pedido:
                                pedido.restore_enums_after_loading()
                            return pedido
                return None
        else:
            # Llamada con dos parámetros: get(Class, id)
            try:
                # Intentamos primero con la carga directa
                obj = self.load(obj_id)
                if obj:
                    return obj
                    
                # Si no funciona, buscamos en la colección
                if obj_id:
                    objects = self.find_all(class_type_or_id)
                    for obj in objects:
                        if obj.id == obj_id:
                            # Arreglar el enum si es necesario
                            if hasattr(obj, 'restore_enums_after_loading'):
                                obj.restore_enums_after_loading()
                            return obj
                return None
            except Exception as e:
                current_app.logger.error(f"Error en get(Class, id) para {class_type_or_id}, {obj_id}: {e}")
                return None
    
    def delete(self, obj_id: str) -> bool:
        """
        Eliminar un objeto por su ID.
        
        Args:
            obj_id: ID del objeto a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            self.sirope.delete(obj_id)
            return True
        except Exception as e:
            current_app.logger.error(f"Error eliminando objeto {obj_id}: {e}")
            return False
    
    def find_all(self, class_type: Type) -> List[Any]:
        """
        Encontrar todos los objetos de un tipo específico.
        
        Args:
            class_type: Tipo de clase a buscar
            
        Returns:
            List[Any]: Lista de objetos encontrados
        """
        try:
            # Agregar logs para depuración
            current_app.logger.info(f"Buscando todos los objetos de tipo: {class_type.__name__}")
            
            # Usar enumerate para obtener todos los objetos de un tipo
            objects = list(self.sirope.enumerate(class_type))
            
            # Imprimir información sobre los objetos encontrados
            current_app.logger.info(f"Se encontraron {len(objects)} objetos de tipo {class_type.__name__}")
            
            for i, obj in enumerate(objects):
                if hasattr(obj, 'nombre'):
                    current_app.logger.info(f"  - Objeto {i+1}: ID={getattr(obj, 'id', 'N/A')}, Nombre={obj.nombre}")
                else:
                    current_app.logger.info(f"  - Objeto {i+1}: ID={getattr(obj, 'id', 'N/A')}")
            
            # Restaurar enums en todos los objetos si son BaseModel
            from app.models.base_model import BaseModel
            for obj in objects:
                if isinstance(obj, BaseModel) and hasattr(obj, 'restore_enums_after_loading'):
                    obj.restore_enums_after_loading()
            
            return objects
        except Exception as e:
            current_app.logger.error(f"Error buscando objetos de tipo {class_type}: {e}")
            return []
    
    def find_first(self, class_type: Type, condition=None) -> Optional[Any]:
        """
        Encontrar el primer objeto que cumpla una condición.
        
        Args:
            class_type: Tipo de clase a buscar
            condition: Función de condición (opcional)
            
        Returns:
            Optional[Any]: Primer objeto encontrado o None
        """
        try:
            if condition:
                return self.sirope.find_first(class_type, condition)
            else:
                objects = self.find_all(class_type)
                return objects[0] if objects else None
        except Exception as e:
            current_app.logger.error(f"Error buscando primer objeto: {e}")
            return None
    
    def find_by_condition(self, class_type: Type, condition) -> List[Any]:
        """
        Encontrar objetos que cumplan una condición específica.
        
        Args:
            class_type: Tipo de clase a buscar
            condition: Función de condición
            
        Returns:
            List[Any]: Lista de objetos que cumplen la condición
        """
        try:
            return list(self.sirope.filter(class_type, condition))
        except Exception as e:
            current_app.logger.error(f"Error buscando objetos con condición: {e}")
            return []
    
    def get_by_criteria(self, class_type: Type, condition) -> List[Any]:
        """
        Obtener objetos que cumplan un criterio específico (alias de find_by_condition).
        
        Args:
            class_type: Tipo de clase a buscar
            condition: Función de condición
            
        Returns:
            List[Any]: Lista de objetos que cumplen la condición
        """
        return self.find_by_condition(class_type, condition)
