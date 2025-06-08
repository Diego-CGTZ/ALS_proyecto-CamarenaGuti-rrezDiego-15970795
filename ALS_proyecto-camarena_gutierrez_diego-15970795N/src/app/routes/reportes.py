from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from app.models.proceso import TipoProceso
from app.services.storage_service import StorageService
from app.models.pedido import Pedido

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')
storage = StorageService()

@reportes_bp.route('/utilidad')
@login_required
def analisis_utilidad():
    """Página de análisis de utilidad"""
    
    # Obtener estadísticas de utilidad    stats = calcular_estadisticas_utilidad()
    
    return render_template('reportes/utilidad.html', stats=stats)

def calcular_estadisticas_utilidad():
    """
    Calcula estadísticas de utilidad basadas en los pedidos existentes
    """
    # Obtener todos los pedidos
    pedidos = storage.find_all(Pedido)
    
    if not pedidos:
        return {
            'promedio_utilidad': 30.0,
            'min_utilidad': 10.0,
            'max_utilidad': 50.0,
            'total_pedidos': 0,
            'utilidad_dtf': 32.0,
            'utilidad_sublimacion': 28.0,
            'utilidad_bordado': 35.0,
            'utilidad_vinil': 30.0
        }
    
    # Calcular estadísticas generales
    porcentajes_utilidad = [p.porcentaje_utilidad for p in pedidos]
    promedio_utilidad = sum(porcentajes_utilidad) / len(porcentajes_utilidad) if porcentajes_utilidad else 30.0
    min_utilidad = min(porcentajes_utilidad) if porcentajes_utilidad else 10.0
    max_utilidad = max(porcentajes_utilidad) if porcentajes_utilidad else 50.0
    
    # Estadísticas por tipo de proceso
    # Nota: Esta es una versión simplificada. En una implementación real,
    # necesitaríamos agrupar pedidos por tipo de proceso basado en los
    # items de personalización asociados.
    return {
        'promedio_utilidad': promedio_utilidad,
        'min_utilidad': min_utilidad,
        'max_utilidad': max_utilidad,
        'total_pedidos': len(pedidos),
        'utilidad_dtf': 32.0,  # Estos valores serían calculados en una implementación real
        'utilidad_sublimacion': 28.0,
        'utilidad_bordado': 35.0,
        'utilidad_vinil': 30.0
    }

@reportes_bp.route('/api/utilidad-resumen')
@login_required
def api_utilidad_resumen():
    """API para obtener datos resumidos de utilidad para visualizaciones"""
    stats = calcular_estadisticas_utilidad()
    
    # Formato para uso en gráficos
    data = {
        'labels': ['DTF', 'Sublimación', 'Bordado', 'Vinil'],
        'datasets': [{
            'label': 'Porcentaje de Utilidad',
            'data': [
                stats.get('utilidad_dtf', 32.0),
                stats.get('utilidad_sublimacion', 28.0),
                stats.get('utilidad_bordado', 35.0),
                stats.get('utilidad_vinil', 30.0)
            ],
            'backgroundColor': [
                'rgba(255, 99, 132, 0.7)',
                'rgba(54, 162, 235, 0.7)',
                'rgba(255, 206, 86, 0.7)',
                'rgba(75, 192, 192, 0.7)'
            ]
        }]
    }
    
    return jsonify(data)
