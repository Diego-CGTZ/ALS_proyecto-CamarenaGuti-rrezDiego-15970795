# Textiles ALS - Sistema de Gestión de Personalización Textil

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3+-green)
![Redis](https://img.shields.io/badge/Redis-6.0+-red)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)

Sistema web completo para la gestión de pedidos de personalización textil, desarrollado con Flask, Jinja2 y Sirope/Redis. Incluye funcionalidades CRUD para clientes, productos, procesos y pedidos, con cálculos automáticos de precios para diferentes tipos de personalización.

## 🚀 Características Principales

### 📊 Gestión Completa
- **Clientes**: Gestión de clientes individuales, empresariales e institucionales
- **Productos**: Catálogo de prendas con múltiples tallas y colores
- **Procesos**: Configuración de procesos de personalización (DTF, Sublimación, Bordado, Vinil)
- **Pedidos**: Sistema completo de pedidos con items y personalizaciones

### 💰 Cálculo Automático de Precios
- **DTF**: Precio por cm² con mínimo configurable
- **Sublimación**: Precio por área con soporte para diseños complejos
- **Bordado**: Precios fijos por tamaño (pequeño, mediano, grande)
- **Vinil**: Precio por cm² con recargo por colores adicionales

### 🔐 Autenticación y Seguridad
- Sistema de usuarios con roles (administrador/usuario)
- Autenticación con Flask-Login
- Sesiones seguras y protección CSRF
- Páginas de error personalizadas (404, 500, 403)

### 🎨 Interfaz Moderna
- Diseño responsive con Bootstrap 5
- Tema personalizado con gradientes y animaciones
- Dashboard con estadísticas en tiempo real
- Interfaz intuitiva y moderna

### ⚡ Funcionalidades Avanzadas
- Calculadora de precios en tiempo real
- Filtros y búsqueda en todas las secciones
- Actualizaciones AJAX sin recargar página
- Sistema de notificaciones toast
- Validación de formularios en cliente y servidor

## 🛠️ Tecnologías Utilizadas

### Backend
- **Flask 2.3+**: Framework web principal
- **Sirope**: ORM para Redis
- **Redis**: Base de datos NoSQL
- **Flask-Login**: Gestión de autenticación
- **Flask-WTF**: Formularios y validación
- **Werkzeug**: Utilities y seguridad

### Frontend
- **Jinja2**: Motor de plantillas
- **Bootstrap 5.3**: Framework CSS
- **Font Awesome 6**: Iconografía
- **JavaScript ES6+**: Interactividad
- **CSS3**: Estilos personalizados

### Desarrollo
- **Python 3.8+**: Lenguaje principal
- **pip**: Gestión de dependencias
- **python-dotenv**: Configuración con variables de entorno

## 📦 Instalación

### Prerrequisitos
- Python 3.8 o superior
- Redis Server 6.0 o superior
- Git (opcional)

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/textiles-als.git
cd textiles-als
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=tu-clave-secreta-muy-segura
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

### 5. Instalar y Configurar Redis
#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### Windows:
1. Descargar Redis desde [Microsoft Archive](https://github.com/microsoftarchive/redis/releases)
2. Instalar y ejecutar como servicio

#### macOS:
```bash
brew install redis
brew services start redis
```

### 6. Inicializar Base de Datos
```bash
python scripts/init_db.py
```

### 7. Ejecutar la Aplicación
```bash
python run.py
```

La aplicación estará disponible en `http://localhost:5000`

## 👤 Credenciales por Defecto

Después de ejecutar el script de inicialización:

- **Usuario**: admin@textiles-als.com
- **Contraseña**: admin123

⚠️ **IMPORTANTE**: Cambiar la contraseña inmediatamente después del primer acceso.

## 📁 Estructura del Proyecto

```
textiles-als/
├── app/                          # Aplicación principal
│   ├── __init__.py              # Factory de la aplicación
│   ├── models/                  # Modelos de datos
│   │   ├── base_model.py        # Modelo base
│   │   ├── usuario.py           # Usuario y autenticación
│   │   ├── cliente.py           # Gestión de clientes
│   │   ├── producto.py          # Catálogo de productos
│   │   ├── proceso.py           # Procesos de personalización
│   │   └── pedido.py            # Sistema de pedidos
│   ├── routes/                  # Controladores/Rutas
│   │   ├── __init__.py
│   │   ├── main.py              # Dashboard y rutas principales
│   │   ├── auth.py              # Autenticación
│   │   ├── clientes.py          # CRUD de clientes
│   │   ├── productos.py         # CRUD de productos
│   │   ├── procesos.py          # CRUD de procesos
│   │   └── pedidos.py           # CRUD de pedidos
│   ├── forms/                   # Formularios WTF
│   │   ├── auth_forms.py        # Formularios de autenticación
│   │   ├── cliente_forms.py     # Formularios de clientes
│   │   ├── producto_forms.py    # Formularios de productos
│   │   ├── proceso_forms.py     # Formularios de procesos
│   │   └── pedido_forms.py      # Formularios de pedidos
│   ├── services/                # Servicios
│   │   └── storage_service.py   # Servicio de almacenamiento Redis
│   ├── templates/               # Plantillas HTML
│   │   ├── base/                # Plantillas base
│   │   ├── auth/                # Autenticación
│   │   ├── main/                # Dashboard
│   │   ├── clientes/            # Gestión de clientes
│   │   ├── productos/           # Gestión de productos
│   │   ├── procesos/            # Gestión de procesos
│   │   ├── pedidos/             # Gestión de pedidos
│   │   └── errors/              # Páginas de error
│   └── static/                  # Archivos estáticos
│       ├── css/
│       │   └── style.css        # Estilos personalizados
│       └── js/
│           └── main.js          # JavaScript principal
├── scripts/                     # Scripts de utilidad
│   ├── init_db.py              # Inicialización de datos
│   ├── backup_manager.py       # Gestión de respaldos
│   └── dev_utils.py            # Utilidades de desarrollo
├── backups/                    # Respaldos automáticos
├── config.py                   # Configuración de la aplicación
├── run.py                      # Punto de entrada
├── requirements.txt            # Dependencias Python
├── .env                        # Variables de entorno (crear)
└── README.md                   # Este archivo
```

## 🚀 Uso del Sistema

### Dashboard Principal
El dashboard muestra:
- Estadísticas generales del sistema
- Pedidos recientes
- Accesos rápidos a funcionalidades principales
- Gráficos de rendimiento

### Gestión de Clientes
- **Tipos**: Individual, Empresarial, Institucional
- **Funcionalidades**: CRUD completo, descuentos por tipo, historial de pedidos
- **Filtros**: Por tipo de cliente, estado, fecha de registro

### Catálogo de Productos
- **Información**: Nombre, categoría, precio base, descripción
- **Opciones**: Tallas y colores disponibles
- **Gestión**: Categorización automática, precios dinámicos

### Procesos de Personalización
- **DTF**: Diseños complejos, precio por cm²
- **Sublimación**: Para prendas claras, colores vibrantes
- **Bordado**: Durabilidad máxima, precios por tamaño
- **Vinil**: Textos y formas simples, muy duradero

### Sistema de Pedidos
- **Creación**: Múltiples items por pedido
- **Personalización**: Configuración específica por item
- **Cálculos**: Precios automáticos según proceso y dimensiones
- **Estados**: Pendiente, En Proceso, Completado, Cancelado

## 🔧 Scripts de Utilidad

### Inicialización de Datos
```bash
python scripts/init_db.py
```
Crea datos iniciales: usuario admin, procesos básicos, productos ejemplo.

### Gestión de Respaldos
```bash
# Crear respaldo
python scripts/backup_manager.py backup

# Restaurar respaldo
python scripts/backup_manager.py restore archivo_respaldo.json.gz

# Listar respaldos
python scripts/backup_manager.py list

# Limpiar respaldos antiguos
python scripts/backup_manager.py cleanup --keep 5
```

### Utilidades de Desarrollo
```bash
# Generar datos de prueba
python scripts/dev_utils.py test-clients 50
python scripts/dev_utils.py test-orders 100

# Ver estadísticas
python scripts/dev_utils.py stats

# Resetear base de datos
python scripts/dev_utils.py reset

# Limpiar datos de prueba
python scripts/dev_utils.py cleanup
```

## 🔐 Configuración de Seguridad

### Variables de Entorno Importantes
```env
SECRET_KEY=clave-super-secreta-de-256-bits-minimo
FLASK_ENV=production  # En producción
```

### Redis en Producción
```env
REDIS_URL=redis://usuario:password@host:puerto/db
REDIS_PASSWORD=password-seguro
```

### Recomendaciones
- Cambiar contraseña del administrador
- Usar HTTPS en producción
- Configurar firewall para Redis
- Realizar respaldos regulares
- Monitorear logs de acceso

## 📊 API y Endpoints

### Autenticación
- `GET /auth/login` - Página de inicio de sesión
- `POST /auth/login` - Procesar login
- `GET /auth/register` - Registro de usuario
- `GET /auth/logout` - Cerrar sesión

### Dashboard
- `GET /` - Dashboard principal
- `GET /dashboard` - Dashboard principal

### Clientes
- `GET /clientes` - Listar clientes
- `GET /clientes/nuevo` - Formulario nuevo cliente
- `POST /clientes/nuevo` - Crear cliente
- `GET /clientes/<id>/editar` - Editar cliente
- `POST /clientes/<id>/editar` - Actualizar cliente
- `GET /clientes/<id>/eliminar` - Eliminar cliente

### Productos
- `GET /productos` - Listar productos
- `GET /productos/nuevo` - Formulario nuevo producto
- `POST /productos/nuevo` - Crear producto
- `GET /productos/<id>/editar` - Editar producto

### Procesos
- `GET /procesos` - Listar procesos
- `GET /procesos/nuevo` - Formulario nuevo proceso
- `POST /procesos/calcular` - API cálculo de precios

### Pedidos
- `GET /pedidos` - Listar pedidos
- `GET /pedidos/nuevo` - Formulario nuevo pedido
- `POST /pedidos/nuevo` - Crear pedido
- `GET /pedidos/<id>` - Ver detalle pedido
- `POST /pedidos/<id>/estado` - Actualizar estado (AJAX)

## 🧪 Testing y Desarrollo

### Entorno de Desarrollo
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python run.py
```

### Datos de Prueba
El sistema incluye generadores automáticos de datos de prueba para desarrollo y testing.

### Logs
Los logs se muestran en consola durante el desarrollo. En producción, configurar logging a archivos.

## 📈 Rendimiento

### Optimizaciones Implementadas
- Uso de Redis para almacenamiento rápido
- Carga lazy de datos en formularios
- Compresión de respaldos con gzip
- Cacheo de consultas frecuentes
- Minificación de assets estáticos

### Métricas Recomendadas
- Tiempo de respuesta < 200ms
- Uso de memoria Redis < 100MB
- Concurrencia hasta 100 usuarios
- Disponibilidad > 99.9%

## 🐛 Solución de Problemas

### Error de Conexión Redis
```bash
# Verificar estado de Redis
redis-cli ping

# Reiniciar Redis
sudo systemctl restart redis-server
```

### Error de Dependencias
```bash
# Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

### Error de Permisos
```bash
# Verificar permisos de archivos
chmod +x scripts/*.py
```

### Logs de Debug
```bash
# Ejecutar con debug activado
FLASK_DEBUG=1 python run.py
```

## 🤝 Contribución

### Cómo Contribuir
1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Estándares de Código
- PEP 8 para Python
- Comentarios en español
- Documentación en funciones
- Tests para funcionalidades críticas

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o consultas:

- **Email**: soporte@textiles-als.com
- **Documentación**: [Wiki del proyecto](wiki/)
- **Issues**: [GitHub Issues](issues/)

## 🚀 Roadmap

### Versión 2.0 (Próxima)
- [ ] API REST completa
- [ ] App móvil
- [ ] Integración con impresoras
- [ ] Sistema de inventarios
- [ ] Reportes avanzados
- [ ] Integración con sistemas de pago

### Versión 1.5
- [ ] Sistema de notificaciones email
- [ ] Exportación a PDF
- [ ] Importación masiva de datos
- [ ] Dashboard de analytics
- [ ] Sistema de roles avanzado

---

**Desarrollado con ❤️ para Textiles ALS**

*Sistema de gestión de personalización textil - Versión 1.0*
