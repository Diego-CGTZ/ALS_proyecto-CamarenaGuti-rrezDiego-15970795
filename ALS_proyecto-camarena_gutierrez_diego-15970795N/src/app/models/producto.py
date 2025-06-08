"""
Modelo de Producto (Prenda) para el catálogo de productos.
"""

from typing import List, Dict
from .base_model import BaseModel


class Producto(BaseModel):
    """
    Modelo de Producto (Prenda) para el sistema.
    Representa las prendas disponibles en el catálogo.
    """
    
    def __init__(self, nombre: str, categoria: str, precio_base: float, 
                 descripcion: str = "", tallas_disponibles: List[str] = None,
                 colores_disponibles: List[str] = None):
        """
        Inicializar producto.
        
        Args:
            nombre: Nombre del producto
            categoria: Categoría del producto (camiseta, sudadera, etc.)
            precio_base: Precio base del producto
            descripcion: Descripción del producto
            tallas_disponibles: Lista de tallas disponibles
            colores_disponibles: Lista de colores disponibles
        """
        super().__init__()
        self.nombre = nombre
        self.categoria = categoria
        self.precio_base = precio_base
        self.descripcion = descripcion
        self.tallas_disponibles = tallas_disponibles or ["S", "M", "L", "XL"]
        self.colores_disponibles = colores_disponibles or ["Blanco", "Negro"]
        
        # Posiciones disponibles para personalización (1-10)
        self.posiciones_personalizacion = {
            1: "Pecho izquierdo",
            2: "Pecho derecho", 
            3: "Pecho centro",
            4: "Espalda superior",
            5: "Espalda centro",
            6: "Espalda inferior",
            7: "Manga izquierda",
            8: "Manga derecha",
            9: "Cuello",
            10: "Personalizado"
        }
        
        # Estadísticas del producto
        self.veces_pedido = 0
        self.total_vendido = 0.0
    
    def actualizar_estadisticas(self, cantidad: int, precio_total: float):
        """
        Actualizar estadísticas del producto.
        
        Args:
            cantidad: Cantidad vendida
            precio_total: Precio total de la venta
        """
        self.veces_pedido += cantidad
        self.total_vendido += precio_total
        self.update_timestamp()
    
    def get_posicion_nombre(self, posicion: int) -> str:
        """
        Obtener nombre de una posición de personalización.
        
        Args:
            posicion: Número de posición (1-10)
            
        Returns:
            str: Nombre de la posición
        """
        return self.posiciones_personalizacion.get(posicion, "Posición desconocida")
    
    def is_talla_disponible(self, talla: str) -> bool:
        """
        Verificar si una talla está disponible.
        
        Args:
            talla: Talla a verificar
            
        Returns:
            bool: True si la talla está disponible
        """
        return talla in self.tallas_disponibles
    
    def is_color_disponible(self, color: str) -> bool:
        """
        Verificar si un color está disponible.
        
        Args:
            color: Color a verificar
            
        Returns:
            bool: True si el color está disponible
        """
        return color in self.colores_disponibles
    
    def agregar_talla(self, talla: str):
        """
        Agregar nueva talla disponible.
        
        Args:
            talla: Nueva talla a agregar
        """
        if talla not in self.tallas_disponibles:
            self.tallas_disponibles.append(talla)
            self.update_timestamp()
    
    def agregar_color(self, color: str):
        """
        Agregar nuevo color disponible.
        
        Args:
            color: Nuevo color a agregar
        """
        if color not in self.colores_disponibles:
            self.colores_disponibles.append(color)
            self.update_timestamp()
    
    def calcular_precio_con_descuento(self, descuento_porcentaje: float = 0.0) -> float:
        """
        Calcular precio con descuento aplicado.
        
        Args:
            descuento_porcentaje: Porcentaje de descuento (0-100)
            
        Returns:
            float: Precio con descuento aplicado
        """
        descuento_decimal = descuento_porcentaje / 100
        return self.precio_base * (1 - descuento_decimal)
    
    def __str__(self) -> str:
        """Representación en string."""
        return f"Producto({self.nombre} - {self.categoria} - ${self.precio_base})"
