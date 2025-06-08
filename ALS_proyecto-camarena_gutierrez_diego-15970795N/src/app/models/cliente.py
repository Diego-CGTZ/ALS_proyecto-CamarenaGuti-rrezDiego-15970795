"""
Modelo de Cliente para gestionar información de clientes.
"""

from typing import List
from .base_model import BaseModel


class Cliente(BaseModel):
    """
    Modelo de Cliente para el sistema de gestión textil.
    Almacena información de contacto y datos relevantes del cliente.
    """
    
    def __init__(self, nombre: str, email: str = "", telefono: str = "", 
                 direccion: str = "", empresa: str = "", notas: str = "", apellido: str = "", 
                 tipo_cliente: str = "particular", nit: str = "", ciudad: str = "", 
                 departamento: str = ""):
        """
        Inicializar cliente.
        
        Args:
            nombre: Nombre del cliente
            email: Email del cliente
            telefono: Teléfono de contacto
            direccion: Dirección del cliente
            empresa: Empresa del cliente (opcional)
            notas: Notas adicionales
            apellido: Apellido del cliente (opcional)
            tipo_cliente: Tipo de cliente ('particular' o 'empresa')
            nit: NIT o Identificación Fiscal (opcional)
            ciudad: Ciudad de residencia o ubicación (opcional)
            departamento: Departamento o Estado (opcional)
        """
        super().__init__()
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.direccion = direccion
        self.empresa = empresa
        self.notas = notas
        self.apellido = apellido
        self.tipo_cliente = tipo_cliente if tipo_cliente in ['particular', 'empresa'] else 'particular'
        self.nit = nit
        self.ciudad = ciudad
        self.departamento = departamento
        
        # Estadísticas del cliente
        self.total_pedidos = 0
        self.total_gastado = 0.0
    
    def actualizar_estadisticas(self, monto_pedido: float):
        """
        Actualizar estadísticas del cliente.
        
        Args:
            monto_pedido: Monto del nuevo pedido
        """
        self.total_pedidos += 1
        self.total_gastado += monto_pedido
        self.update_timestamp()
    
    def get_nombre_completo(self) -> str:
        """
        Obtener nombre completo del cliente.
        
        Returns:
            str: Nombre completo del cliente
        """
        if hasattr(self, 'apellido') and self.apellido:
            return f"{self.nombre} {self.apellido}"
        else:
            if hasattr(self, 'empresa') and self.empresa:
                return f"{self.nombre} ({self.empresa})"
            else:
                return self.nombre
    
    @property
    def nombre_completo(self) -> str:
        """
        Propiedad para acceder al nombre completo.
        
        Returns:
            str: Nombre completo del cliente
        """
        return self.get_nombre_completo()
    
    def get_info_contacto(self) -> dict:
        """
        Obtener información de contacto estructurada.
        
        Returns:
            dict: Información de contacto
        """
        return {
            'email': self.email,
            'telefono': self.telefono,
            'direccion': self.direccion
        }
    
    def __str__(self) -> str:
        """Representación en string."""
        return f"Cliente({self.get_nombre_completo()})"
    
    def puede_ser_eliminado(self, storage_service) -> tuple[bool, str]:
        """
        Verificar si el cliente puede ser eliminado de forma segura.
        
        Args:
            storage_service: Instancia del servicio de almacenamiento
            
        Returns:
            tuple[bool, str]: (puede_eliminarse, motivo_si_no_puede)
        """
        try:
            from .pedido import Pedido  # Importación circular evitada
            
            # Buscar pedidos relacionados
            pedidos_relacionados = storage_service.find_by_condition(
                Pedido,
                lambda p: p.cliente_id == self.id and p.is_active
            )
            
            if not pedidos_relacionados:
                return True, "Cliente sin pedidos asociados"
            
            # Verificar si hay pedidos activos
            pedidos_activos = [p for p in pedidos_relacionados 
                             if hasattr(p.estado, 'value') and p.estado.value not in ['ENTREGADO', 'CANCELADO']]
            
            if pedidos_activos:
                estados = [p.estado.value if hasattr(p.estado, 'value') else str(p.estado) for p in pedidos_activos]
                return False, f"Cliente tiene {len(pedidos_activos)} pedido(s) activo(s) en estado: {', '.join(set(estados))}"
            
            # Si solo tiene pedidos entregados o cancelados
            return False, f"Cliente tiene {len(pedidos_relacionados)} pedido(s) en el historial que deben eliminarse primero"
            
        except Exception as e:
            return False, f"Error al verificar integridad: {str(e)}"
