"""
Modelo de Proceso para los diferentes tipos de personalización textil.
"""

from enum import Enum
from typing import Dict, Any
from .base_model import BaseModel


class TipoProceso(Enum):
    """Tipos de procesos disponibles."""
    DTF = "DTF"
    SUBLIMACION = "SUBLIMACION"
    BORDADO = "BORDADO"
    VINIL = "VINIL"


class TamañoBordado(Enum):
    """Tamaños de bordado disponibles."""
    PEQUEÑO = "PEQUEÑO"
    MEDIANO = "MEDIANO"
    GRANDE = "GRANDE"
    EXTRA_GRANDE = "EXTRA_GRANDE"


class Proceso(BaseModel):
    """
    Modelo de Proceso para gestionar los diferentes tipos de personalización.
    Cada proceso tiene características y cálculos de precio específicos.
    """
    
    def __init__(self, tipo: TipoProceso, nombre: str, descripcion: str = ""):
        """
        Inicializar proceso.
        
        Args:
            tipo: Tipo de proceso (DTF, SUBLIMACION, etc.)
            nombre: Nombre descriptivo del proceso
            descripcion: Descripción detallada del proceso
        """
        super().__init__()
        # Store enum as string value for JSON serialization
        self.tipo = tipo.value if isinstance(tipo, TipoProceso) else tipo
        self.nombre = nombre
        self.descripcion = descripcion
        
        # Configuración específica por tipo de proceso
        self._configurar_proceso()
    
    def _configurar_proceso(self):
        """Configurar parámetros específicos según el tipo de proceso."""
        tipo_enum = TipoProceso(self.tipo) if isinstance(self.tipo, str) else self.tipo
        
        if tipo_enum == TipoProceso.DTF:
            self.ancho_disponible = 27.5  # cm - Este es el ancho fijo del material DTF
            self.precio_por_metro = 200.0  # Precio por metro de material DTF
            self.requiere_aplicacion = True
            
        elif tipo_enum == TipoProceso.SUBLIMACION:
            self.ancho_disponible = 60.0  # cm - Este es el ancho fijo del material de sublimación
            self.precio_por_metro = 180.0  # Precio por metro de material de sublimación
            self.requiere_aplicacion = True
            
        elif tipo_enum == TipoProceso.BORDADO:
            self.precio_setup = 50.0  # Costo inicial de configuración del bordado
            # Store as string keys for JSON serialization
            self.precios_por_tamaño = {
                TamañoBordado.PEQUEÑO.value: 30.0,
                TamañoBordado.MEDIANO.value: 50.0,
                TamañoBordado.GRANDE.value: 80.0,
                TamañoBordado.EXTRA_GRANDE.value: 120.0
            }
            
        elif tipo_enum == TipoProceso.VINIL:
            self.precio_por_cm2 = 0.02  # Precio base por cm2 de vinil
            # Diferentes tipos de viniles con sus precios específicos por cm2
            self.tipos_vinil = {
                "Estándar": 0.02,
                "Textil": 0.03,
                "Reflectante": 0.05,
                "Glitter": 0.06,
                "Flock": 0.04,
                "Holográfico": 0.07
            }
    
    def calcular_metros_necesarios(self, ancho_diseño: float, alto_diseño: float, 
                                 cantidad: int) -> float:
        """
        Calcular metros necesarios para DTF o Sublimación.
        
        Args:
            ancho_diseño: Ancho del diseño en cm
            alto_diseño: Alto del diseño en cm
            cantidad: Cantidad de piezas a imprimir
            
        Returns:
            float: Metros necesarios
        """
        tipo_enum = TipoProceso(self.tipo) if isinstance(self.tipo, str) else self.tipo
        if tipo_enum not in [TipoProceso.DTF, TipoProceso.SUBLIMACION]:
            return 0.0
        
        # Calcular cuántos diseños caben por metro (considerando el ancho)
        diseños_por_ancho = int(self.ancho_disponible // ancho_diseño)
        if diseños_por_ancho == 0:
            diseños_por_ancho = 1  # Al menos uno por fila
        
        # Calcular metros necesarios
        filas_necesarias = cantidad // diseños_por_ancho
        if cantidad % diseños_por_ancho > 0:
            filas_necesarias += 1
        
        metros_necesarios = (filas_necesarias * alto_diseño) / 100  # Convertir cm a metros
        return metros_necesarios
    
    def calcular_precio_dtf_sublimacion(self, ancho_diseño: float, alto_diseño: float, 
                                      cantidad: int) -> float:
        """
        Calcular precio para DTF o Sublimación.
        
        Args:
            ancho_diseño: Ancho del diseño en cm
            alto_diseño: Alto del diseño en cm
            cantidad: Cantidad de piezas
            
        Returns:
            float: Precio total del proceso
        """
        metros = self.calcular_metros_necesarios(ancho_diseño, alto_diseño, cantidad)
        return metros * self.precio_por_metro
    
    def calcular_precio_bordado(self, tamaño: TamañoBordado, cantidad: int, 
                              incluir_setup: bool = True) -> float:
        """
        Calcular precio para bordado.
        
        Args:
            tamaño: Tamaño del bordado
            cantidad: Cantidad de piezas
            incluir_setup: Si incluir costo de setup
            
        Returns:
            float: Precio total del bordado
        """
        tamaño_key = tamaño.value if isinstance(tamaño, TamañoBordado) else tamaño
        precio_base = self.precios_por_tamaño.get(tamaño_key, 0.0) * cantidad
        if incluir_setup:
            precio_base += self.precio_setup
        return precio_base
    
    def calcular_precio_vinil(self, ancho_diseño: float, alto_diseño: float, 
                            cantidad: int, tipo_vinil: str) -> float:
        """
        Calcular precio para vinil.
        
        Args:
            ancho_diseño: Ancho del diseño en cm
            alto_diseño: Alto del diseño en cm
            cantidad: Cantidad de piezas
            tipo_vinil: Tipo de vinil a usar
            
        Returns:
            float: Precio total del vinil
        """
        area_cm2 = ancho_diseño * alto_diseño
        precio_por_cm2 = self.tipos_vinil.get(tipo_vinil, self.precio_por_cm2)
        return area_cm2 * precio_por_cm2 * cantidad
    
    def configurar_precios(self, **kwargs):
        """
        Configurar precios específicos del proceso.
        
        Args:
            **kwargs: Parámetros de precio específicos por tipo
        """
        tipo_enum = TipoProceso(self.tipo) if isinstance(self.tipo, str) else self.tipo
        
        if tipo_enum in [TipoProceso.DTF, TipoProceso.SUBLIMACION]:
            self.precio_por_metro = kwargs.get('precio_por_metro', 0.0)
            
        elif tipo_enum == TipoProceso.BORDADO:
            self.precio_setup = kwargs.get('precio_setup', 0.0)
            if 'precios_tamaños' in kwargs:
                self.precios_por_tamaño.update(kwargs['precios_tamaños'])
                
        elif tipo_enum == TipoProceso.VINIL:
            self.precio_por_cm2 = kwargs.get('precio_por_cm2', 0.0)
            if 'tipos_vinil' in kwargs:
                self.tipos_vinil.update(kwargs['tipos_vinil'])
        
        self.update_timestamp()
    
    def __str__(self) -> str:
        """Representación en string."""
        tipo_display = self.tipo if isinstance(self.tipo, str) else self.tipo.value
        return f"Proceso({tipo_display} - {self.nombre})"
    
    def get_tipo_enum(self) -> TipoProceso:
        """Get the enum type from stored string value."""
        return TipoProceso(self.tipo) if isinstance(self.tipo, str) else self.tipo
    
    def get_tamaño_bordado_enum(self, tamaño_str: str) -> TamañoBordado:
        """Convert string to TamañoBordado enum."""
        return TamañoBordado(tamaño_str)
