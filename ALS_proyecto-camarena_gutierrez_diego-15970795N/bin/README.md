# Directorio bin/ - Ejecutables del Sistema

## Propósito

Este directorio contiene los **ejecutables independientes** del Sistema de Gestión Textiles ALS, cumpliendo con los requisitos académicos de crear aplicaciones que funcionen sin librerías externas.

## Contenido del directorio:

### Ejecutables compilados:
- `TextilesALS.exe` - **Ejecutable principal independiente** (se genera en `dist/`)
- `textiles_als_standalone.py` - Código fuente del ejecutable
- `build_executable.py` - Script de compilación automatizada

### Scripts de automatización:
- `compilar_ejecutable.bat` - Script Windows para compilación automática
- `textiles_als.spec` - Configuración de PyInstaller

### Archivos de soporte:
- `INSTRUCCIONES_EJECUTABLE.txt` - Manual de usuario del ejecutable
- `README.md` - Este archivo de documentación

## Características del ejecutable:

✅ **Totalmente independiente** - No requiere Python ni librerías externas  
✅ **Compilación estática** - Todas las DLLs y dependencias incluidas  
✅ **Un solo archivo** - Ejecutable portable de ~40-60MB  
✅ **Auto-contenido** - Servidor web Flask integrado  
✅ **Base de datos local** - Archivos JSON incluidos  
✅ **Interfaz web moderna** - Accesible vía navegador  

## Uso del ejecutable:

### Opción 1: Ejecutar directamente
```
1. Navegar a bin/dist/
2. Doble clic en TextilesALS.exe
3. ¡Listo! Se abre automáticamente en el navegador
```

### Opción 2: Desde línea de comandos
```cmd
cd bin\dist\
TextilesALS.exe
```

### Acceso a la aplicación:
- **URL:** http://localhost:5000
- **Usuario:** admin  
- **Contraseña:** admin123

## Compilación del ejecutable:

### Automática (recomendada):
```cmd
cd bin\
compilar_ejecutable.bat
```

### Manual:
```cmd
cd bin\
python build_executable.py
```

## Aplicación Flask original:

Para desarrollo, la aplicación Flask se ejecuta mediante:
- `src/run.py` - Archivo principal de desarrollo
- Scripts de utilidad en `src/scripts/`
- Comandos Flask estándar para desarrollo

## Nota académica:

Este directorio se incluye para cumplir con la estructura de entrega requerida por las especificaciones universitarias, aunque en aplicaciones web modernas como Flask, los archivos ejecutables principales se encuentran típicamente en el directorio raíz del proyecto.

---
**Proyecto ALS - Camarena Gutiérrez, Diego - 15970795N**
