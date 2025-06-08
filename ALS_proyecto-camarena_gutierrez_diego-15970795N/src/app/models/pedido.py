"""
Modelos relacionados con Pedidos y Personalizaciones.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum
from .base_model import BaseModel
from .proceso import TipoProceso, TamañoBordado


class EstadoPedido(Enum):
    """Estados posibles de un pedido."""
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN_PROCESO"
    COMPLETADO = "COMPLETADO"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"


class PrioridadPedido(Enum):
    """Prioridades posibles de un pedido."""
    BAJA = "BAJA"
    NORMAL = "NORMAL"
    ALTA = "ALTA"
    URGENTE = "URGENTE"


class Personalizacion(BaseModel):
    """
    Modelo de Personalización individual.
    Representa una personalización específica en una prenda.
    """
    
    def __init__(self, proceso_id: str, precio_proceso: float, cantidad: int = 1):
        """
        Inicializar personalización.
        
        Args:
            proceso_id: ID del proceso de personalización
            precio_proceso: Precio del proceso
            cantidad: Cantidad de personalizaciones
        """
        super().__init__()
        self.proceso_id = proceso_id
        self.precio_proceso = precio_proceso
        self.cantidad = cantidad
        self.subtotal = precio_proceso * cantidad
        
    @property
    def costo(self):
        """
        Compatibilidad para templates que usan costo en lugar de precio_proceso o subtotal.
        """
        return self.precio_proceso
        

class ItemPedido(BaseModel):
    """
    Modelo de Item de Pedido.
    Representa una prenda específica con sus personalizaciones en un pedido.
    """
    
    def __init__(self, producto_id: str, talla: str, color: str, cantidad: int,
                 precio_prenda: float):
        """
        Inicializar item de pedido.
        
        Args:
            producto_id: ID del producto
            talla: Talla seleccionada
            color: Color seleccionado
            cantidad: Cantidad de prendas
            precio_prenda: Precio unitario de la prenda
        """
        super().__init__()
        self.producto_id = producto_id
        self.talla = talla
        self.color = color
        self.cantidad = cantidad
        self.precio_prenda = precio_prenda
        self.personalizaciones = []  # Lista de IDs de personalizaciones
        self.subtotal = precio_prenda * cantidad
        self.subtotal_personalizaciones = 0.0
        
    @property
    def precio_base(self):
        """
        Compatibilidad para templates que usan precio_base en lugar de precio_prenda.
        """
        return self.precio_prenda
        
    @property
    def precio_total(self):
        """
        Calcula el precio total del ítem incluyendo personalizaciones.
        """
        return self.subtotal + (self.subtotal_personalizaciones if hasattr(self, 'subtotal_personalizaciones') else 0)


class Pedido(BaseModel):
    """
    Modelo principal de Pedido.
    Gestiona toda la información de un pedido de personalización textil.
    """
    
    def __init__(self, cliente_id: str, descripcion: str = "",
                 fecha_entrega_estimada: datetime = None,
                 estado: EstadoPedido = EstadoPedido.PENDIENTE,
                 prioridad: PrioridadPedido = PrioridadPedido.NORMAL,
                 porcentaje_utilidad: float = 30.0):
        """
        Inicializar un nuevo pedido.
        
        Args:
            cliente_id: ID del cliente
            descripcion: Descripción del pedido
            fecha_entrega_estimada: Fecha estimada de entrega
            estado: Estado inicial del pedido
            prioridad: Prioridad del pedido
            porcentaje_utilidad: Porcentaje de utilidad (30% por defecto)
        """
        super().__init__()
        self.cliente_id = cliente_id
        self.descripcion = descripcion
        self.estado = estado
        self.prioridad = prioridad
        self.fecha_pedido = datetime.now()
        self.fecha_entrega_estimada = fecha_entrega_estimada or (datetime.now() + timedelta(days=7))
        self.numero_pedido = self._generar_numero_pedido()
        
        # Configuración de negocio
        self.porcentaje_utilidad = porcentaje_utilidad
        self.descuento_porcentaje = 0.0
        self.notas = ""        # Items y totales
        self.items = []  # Lista de IDs de items
        self.num_items = 0  # Contador de items activos
        self.subtotal = 0.0
        self.iva = 0.0
        self.total = 0.0
        self.utilidad = 0.0  # Utilidad calculada basada en porcentaje_utilidad
          # Pagos
        self.total_pagado = 0.0
        self.saldo_pendiente = 0.0
        self.pago_completo = False
        
        # Timestamps
        self.update_timestamp()
    
    def _generar_numero_pedido(self) -> str:
        """Generar número único de pedido."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"PED-{timestamp}"
    
    def calcular_totales(self, iva_porcentaje: float = 16.0):
        """
        Calcular totales del pedido.
        
        Args:
            iva_porcentaje: Porcentaje de IVA a aplicar
        """
        # Proteger contra división por cero
        if iva_porcentaje is None:
            iva_porcentaje = 16.0
            
        # self.items contiene IDs, no objetos, así que inicializamos en 0
        # Los totales deben calcularse desde los routes que tienen acceso al storage
        if hasattr(self, '_calculated_subtotal'):
            self.subtotal = self._calculated_subtotal
        else:
            self.subtotal = 0.0
            
        self.iva = self.subtotal * (iva_porcentaje / 100) if iva_porcentaje > 0 else 0.0
        self.total = self.subtotal + self.iva
        
        # Calcular utilidad basada en el subtotal
        self.utilidad = self.subtotal * (self.porcentaje_utilidad / 100)
        
        self.saldo_pendiente = self.total - self.total_pagado
        self.pago_completo = self.saldo_pendiente <= 0
        self.update_timestamp()
    
    def cambiar_estado(self, nuevo_estado: EstadoPedido):
        """
        Cambiar estado del pedido.
        
        Args:
            nuevo_estado: Nuevo estado del pedido
        """
        self.estado = nuevo_estado
        self.update_timestamp()
    
    def is_atrasado(self) -> bool:
        """
        Verificar si el pedido está atrasado.
        
        Returns:
            bool: True si el pedido está atrasado, False en caso contrario
        """
        if self.estado in [EstadoPedido.COMPLETADO, EstadoPedido.CANCELADO]:
            return False
        
        return datetime.now() > self.fecha_entrega_estimada
    
    def __str__(self) -> str:
        """Representación en string."""
        estado_value = self.estado.value if isinstance(self.estado, EstadoPedido) else self.estado
        return f"Pedido({self.numero_pedido} - {estado_value})"
    
    @staticmethod
    def validar_cliente_existe(cliente_id: str, storage_service) -> tuple[bool, str]:
        """
        Validar que un cliente existe y está activo antes de crear/editar un pedido.
        
        Args:
            cliente_id: ID del cliente a validar
            storage_service: Instancia del servicio de almacenamiento
            
        Returns:
            tuple[bool, str]: (es_valido, mensaje_error_si_no_valido)
        """
        try:
            from .cliente import Cliente  # Importación circular evitada
            
            cliente = storage_service.get(Cliente, cliente_id)
            if not cliente:
                return False, f"Cliente con ID {cliente_id} no existe"
            
            if not cliente.is_active:
                return False, f"Cliente {cliente.nombre_completo} ha sido eliminado"
            
            return True, "Cliente válido"
            
        except Exception as e:
            return False, f"Error al validar cliente: {str(e)}"
