"""
Modelo de Usuario para autenticación con Flask-Login.
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .base_model import BaseModel


class Usuario(BaseModel, UserMixin):
    """
    Modelo de Usuario para el sistema.
    Extiende BaseModel y UserMixin para integración con Flask-Login.
    """
    
    def __init__(self, username: str, email: str, password: str, 
                 nombre: str = "", apellidos: str = ""):
        """
        Inicializar usuario.
        
        Args:
            username: Nombre de usuario único
            email: Email del usuario
            password: Contraseña en texto plano (se hasheará)
            nombre: Nombre del usuario
            apellidos: Apellidos del usuario
        """        # Inicializar BaseModel primero
        super().__init__()
        
        # Inicializar atributos específicos del usuario
        self.username = username
        self.email = email
        self.nombre = nombre
        self.apellidos = apellidos
        self.password_hash = generate_password_hash(password)
        self.is_admin = False
    
    def update_timestamp(self):
        """Actualizar timestamp de modificación."""
        from datetime import datetime
        self.updated_at = datetime.now()
    
    def set_password(self, password: str):
        """
        Establecer nueva contraseña.
        
        Args:
            password: Nueva contraseña en texto plano
        """
        self.password_hash = generate_password_hash(password)
        self.update_timestamp()
    
    def check_password(self, password: str) -> bool:
        """
        Verificar contraseña.
        
        Args:
            password: Contraseña a verificar
            
        Returns:
            bool: True si la contraseña es correcta
        """
        return check_password_hash(self.password_hash, password)
    def get_full_name(self) -> str:
        """
        Obtener nombre completo.
        
        Returns:
            str: Nombre completo del usuario
        """
        return f"{self.nombre} {self.apellidos}".strip()
    
    def to_dict(self) -> dict:
        """Convertir a diccionario (sin incluir password_hash)."""
        data = super().to_dict()
        # Remover información sensible
        data.pop('password_hash', None)
        return data
    
    def get_id(self):
        """Método requerido por Flask-Login."""
        return str(self.id) if self.id is not None else None
    
    def __str__(self) -> str:
        """Representación en string."""
        return f"Usuario({self.username} - {self.get_full_name()})"
