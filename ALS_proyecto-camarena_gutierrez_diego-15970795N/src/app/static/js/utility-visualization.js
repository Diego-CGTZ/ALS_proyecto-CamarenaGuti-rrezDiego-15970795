/**
 * Visualización de Utilidad - Módulo de gráficas para margen de utilidad
 * Complementa el sistema de gestión textil con visualizaciones interactivas
 */

const UtilityVisualization = {
    init: function() {
        // Inicializar visualizaciones cuando estamos en páginas relevantes
        if (document.querySelector('.utility-chart-container')) {
            this.setupCharts();
        }
        
        // Inicializar sliders interactivos para utilidad
        this.setupInteractiveSliders();
    },
    
    setupCharts: function() {
        const containers = document.querySelectorAll('.utility-chart-container');
        
        containers.forEach(container => {
            const canvas = container.querySelector('canvas');
            if (!canvas) return;
            
            const ctx = canvas.getContext('2d');
            const dataType = container.dataset.chartType || 'pie';
            const subtotal = parseFloat(container.dataset.subtotal || 0);
            const utility = parseFloat(container.dataset.utility || 0);
            const iva = parseFloat(container.dataset.iva || 0);
            
            this.createChart(ctx, dataType, {
                subtotal: subtotal,
                utility: utility,
                iva: iva
            });
        });
    },
    
    createChart: function(ctx, type, data) {
        // Crear gráfico usando Chart.js
        // Esta función requiere Chart.js incluido en el HTML
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js no está disponible. Agrega la biblioteca para visualizar gráficos.');
            return;
        }
        
        const colors = {
            subtotal: 'rgba(54, 162, 235, 0.7)',
            utility: 'rgba(255, 159, 64, 0.7)',
            iva: 'rgba(201, 203, 207, 0.7)'
        };
        
        let chartConfig;
        
        if (type === 'pie' || type === 'doughnut') {
            chartConfig = {
                type: type,
                data: {
                    labels: ['Costo Base', 'Utilidad', 'IVA'],
                    datasets: [{
                        data: [data.subtotal, data.utility, data.iva],
                        backgroundColor: [colors.subtotal, colors.utility, colors.iva],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        },
                        tooltip: {
                            callbacks: {                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.raw || 0;
                                    const total = data.subtotal + data.utility + data.iva;
                                    const safeTotal = total > 0 ? total : 1;
                                    const percentage = ((value / safeTotal) * 100).toFixed(1);
                                    return `${label}: $${value.toFixed(2)} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            };
        } else {
            // Gráfico de barras como alternativa
            chartConfig = {
                type: 'bar',
                data: {
                    labels: ['Composición del Precio Final'],
                    datasets: [
                        {
                            label: 'Costo Base',
                            data: [data.subtotal],
                            backgroundColor: colors.subtotal
                        },
                        {
                            label: 'Utilidad',
                            data: [data.utility],
                            backgroundColor: colors.utility
                        },
                        {
                            label: 'IVA',
                            data: [data.iva],
                            backgroundColor: colors.iva
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            stacked: true
                        },
                        y: {
                            stacked: true,
                            beginAtZero: true
                        }
                    }
                }
            };
        }
        
        return new Chart(ctx, chartConfig);
    },
    
    setupInteractiveSliders: function() {
        const sliders = document.querySelectorAll('.interactive-utility-slider');
        
        sliders.forEach(slider => {
            // Obtener elementos relacionados
            const container = slider.closest('.utility-interactive-container');
            if (!container) return;
            
            const valueDisplay = container.querySelector('.slider-value');
            const chartContainer = container.querySelector('.utility-chart-container');
            
            // Configurar eventos
            slider.addEventListener('input', function() {
                const value = parseFloat(this.value);
                if (valueDisplay) {
                    valueDisplay.textContent = value.toFixed(1) + '%';
                }
                
                // Si hay un contenedor de gráfico, actualizar en tiempo real
                if (chartContainer) {
                    this.updateChartWithNewValue(chartContainer, value);
                }
                
                // Disparar evento para que otros componentes puedan reaccionar
                const event = new CustomEvent('utility-changed', { 
                    detail: { value: value }
                });
                document.dispatchEvent(event);
            }.bind(this));
        });
    },
    
    updateChartWithNewValue: function(container, utilityPercentage) {
        const canvas = container.querySelector('canvas');
        if (!canvas || !canvas.chart) return;
        
        const subtotal = parseFloat(container.dataset.subtotal || 0);
        const utility = subtotal * (utilityPercentage / 100);
        const iva = (subtotal + utility) * 0.16;  // 16% fijo por ahora
        
        // Actualizar datos del gráfico
        const chart = canvas.chart;
        
        if (chart.config.type === 'pie' || chart.config.type === 'doughnut') {
            chart.data.datasets[0].data = [subtotal, utility, iva];
        } else {
            // Para gráfico de barras
            chart.data.datasets[1].data = [utility];
            chart.data.datasets[2].data = [iva];
        }
        
        chart.update();
        
        // Actualizar los dataset attributes para mantener consistencia
        container.dataset.utility = utility;
        container.dataset.iva = iva;
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Solo inicializar si estamos en una página relevante
    if (document.querySelector('.utility-chart-container') || 
        document.querySelector('.interactive-utility-slider')) {
        UtilityVisualization.init();
    }
});
