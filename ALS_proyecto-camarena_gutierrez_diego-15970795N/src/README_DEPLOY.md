# Sistema de Gestión de Pedidos Textiles

## 🌟 Demo en Vivo
**URL de la aplicación**: [Próximamente en Render]

## 📋 Descripción
Aplicación web CRUD para gestionar pedidos de personalización textil. Permite gestionar clientes, productos, procesos de personalización y pedidos completos con cálculo automático de precios y seguimiento de pagos.

### ✨ Características principales:
- **Gestión de Clientes**: Registro y administración de información de clientes
- **Catálogo de Productos**: Gestión de prendas disponibles con precios
- **Procesos de Personalización**: Diferentes técnicas de personalización (bordado, serigrafía, etc.)
- **Gestión de Pedidos**: Creación completa de pedidos con múltiples productos y personalizaciones
- **Control de Pagos**: Seguimiento de pagos parciales y totales
- **Reportes**: Generación de reportes de ventas y pedidos
- **Sistema de Usuarios**: Autenticación y autorización

### 🛠️ Tecnologías utilizadas:
- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript, Jinja2
- **Base de datos**: Redis (a través de Sirope)
- **Autenticación**: Flask-Login
- **Formularios**: Flask-WTF
- **Despliegue**: Render

## 👨‍💻 Autor
**Diego Camarena Gutiérrez**
- Portfolio: [tu-portfolio-url]
- GitHub: [tu-github]
- LinkedIn: [tu-linkedin]

## 🚀 Usuario Demo
Para probar la aplicación:
- **Usuario**: demo
- **Contraseña**: demo123

## 📁 Estructura del proyecto
```
src/
├── app/
│   ├── models/          # Modelos de datos
│   ├── routes/          # Rutas/controladores
│   ├── forms/           # Formularios WTF
│   ├── templates/       # Plantillas Jinja2
│   ├── static/          # Archivos estáticos (CSS, JS, imágenes)
│   └── services/        # Servicios de negocio
├── scripts/             # Scripts de utilidad
├── config.py           # Configuración
├── run.py              # Punto de entrada
└── requirements.txt    # Dependencias
```

## 🔧 Instalación local

1. Clonar el repositorio
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar variables de entorno (copiar `.env.example` a `.env`)
4. Ejecutar: `python run.py`

## 📝 Características del negocio

Esta aplicación simula el sistema de una empresa de personalización textil que:
- Maneja 4 procesos diferentes de personalización
- Permite múltiples personalizaciones por prenda
- Gestiona posiciones específicas de personalización (1-10)
- Calcula precios automáticamente con IVA
- Controla pagos parciales (50% adelanto, 50% al finalizar)
- Genera reportes de ventas y seguimiento de pedidos

---
*Proyecto desarrollado como parte del portafolio profesional*
