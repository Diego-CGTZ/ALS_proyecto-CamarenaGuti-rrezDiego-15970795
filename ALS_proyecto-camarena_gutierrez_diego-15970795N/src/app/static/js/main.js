/**
 * Sistema de Gestión Textil - JavaScript Principal
 * Orquestador principal de módulos del sistema
 */

// Aplicación principal
const TextilApp = {
    init: function() {
        console.log('🚀 Iniciando Sistema de Gestión Textil');
        
        // Inicializar módulos base
        this.initializeBaseModules();
        
        // Inicializar módulos específicos según la página
        this.initializePageModules();
        
        // Configurar eventos globales
        this.setupGlobalEvents();
        
        console.log('✅ Sistema inicializado correctamente');
    },

    /**
     * Inicializar módulos base que se usan en todas las páginas
     */
    initializeBaseModules: function() {
        // Los módulos base como Utils ya están cargados desde archivos separados
        if (typeof FormManager !== 'undefined') {
            FormManager.init();
        }
    },

    /**
     * Inicializar módulos específicos según la página actual
     */
    initializePageModules: function() {
        const currentPath = window.location.pathname;
        
        // Módulo de pedidos
        if (currentPath.includes('/pedidos') && typeof PedidosManager !== 'undefined') {
            PedidosManager.init();
        }
        
        // Módulo de clientes
        if (currentPath.includes('/clientes') && typeof ClientesManager !== 'undefined') {
            ClientesManager.init();
        }
        
        // Módulo de productos
        if (currentPath.includes('/productos') && typeof ProductosManager !== 'undefined') {
            ProductosManager.init();
        }
        
        // Módulo de reportes
        if (currentPath.includes('/reportes') && typeof ReportesManager !== 'undefined') {
            ReportesManager.init();
        }
        
        // Módulo del dashboard
        if (currentPath === '/' || currentPath.includes('/dashboard')) {
            this.initializeDashboard();
        }
    },

    /**
     * Configurar eventos globales
     */
    setupGlobalEvents: function() {
        // Confirmar eliminaciones
        this.setupDeleteConfirmations();
        
        // Tooltips de Bootstrap
        this.initializeTooltips();
        
        // Auto-dismiss de alertas
        this.setupAlertAutoDismiss();
        
        // Gestión de sesión
        this.setupSessionManagement();
    },

    /**
     * Configurar confirmaciones de eliminación
     */
    setupDeleteConfirmations: function() {
        document.addEventListener('click', function(e) {
            if (e.target.matches('[data-confirm-delete]') || e.target.closest('[data-confirm-delete]')) {
                const button = e.target.matches('[data-confirm-delete]') ? e.target : e.target.closest('[data-confirm-delete]');
                const message = button.dataset.confirmDelete || '¿Está seguro de que desea eliminar este elemento?';
                
                if (!confirm(message)) {
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                }
            }
        });
    },

    /**
     * Inicializar tooltips de Bootstrap
     */
    initializeTooltips: function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    /**
     * Configurar auto-dismiss de alertas
     */
    setupAlertAutoDismiss: function() {
        const alerts = document.querySelectorAll('.alert[data-auto-dismiss]');
        alerts.forEach(alert => {
            const delay = parseInt(alert.dataset.autoDismiss) || 5000;
            setTimeout(() => {
                const alertInstance = bootstrap.Alert.getOrCreateInstance(alert);
                alertInstance.close();
            }, delay);
        });
    },

    /**
     * Configurar gestión de sesión
     */
    setupSessionManagement: function() {
        // Advertir antes de que expire la sesión
        let sessionWarningShown = false;
        
        setInterval(() => {
            fetch('/auth/session-status', {
                method: 'GET',
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.expires_in < 300 && !sessionWarningShown) { // 5 minutos
                    sessionWarningShown = true;
                    Utils.showToast('Su sesión expirará pronto. Guarde su trabajo.', 'warning', 10000);
                }
                
                if (data.expired) {
                    window.location.href = '/auth/login?expired=1';
                }
            })
            .catch(error => {
                console.error('Error verificando sesión:', error);
            });
        }, 60000); // Verificar cada minuto
    },

    /**
     * Inicializar dashboard
     */
    initializeDashboard: function() {
        // Configurar actualización automática de estadísticas
        this.setupDashboardRefresh();
        
        // Configurar gráficos si existen
        this.initializeDashboardCharts();
    },

    /**
     * Configurar actualización del dashboard
     */
    setupDashboardRefresh: function() {
        const refreshButton = document.getElementById('refresh-dashboard');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => {
                this.refreshDashboardData();
            });
        }

        // Auto-refresh cada 5 minutos
        setInterval(() => {
            this.refreshDashboardData();
        }, 300000);
    },

    /**
     * Actualizar datos del dashboard
     */
    refreshDashboardData: function() {
        const statsCards = document.querySelectorAll('.stat-card[data-stat]');
        
        statsCards.forEach(card => {
            const statType = card.dataset.stat;
            const valueElement = card.querySelector('.stat-value');
            
            if (valueElement) {
                valueElement.innerHTML = '<i class="bi bi-arrow-clockwise spin"></i>';
                
                fetch(`/api/stats/${statType}`)
                .then(response => response.json())
                .then(data => {
                    valueElement.textContent = data.value;
                })
                .catch(error => {
                    console.error('Error actualizando estadística:', error);
                    valueElement.textContent = '—';
                });
            }
        });
    },

    /**
     * Inicializar gráficos del dashboard
     */
    initializeDashboardCharts: function() {
        // Solo si Chart.js está disponible
        if (typeof Chart !== 'undefined') {
            this.initializeUtilityChart();
            this.initializeOrdersChart();
        }
    },

    /**
     * Inicializar gráfico de utilidad
     */
    initializeUtilityChart: function() {
        const ctx = document.getElementById('utilityChart');
        if (!ctx) return;

        fetch('/api/charts/utility-data')
        .then(response => response.json())
        .then(data => {
            new Chart(ctx, {
                type: 'line',
                data: data.chartData,
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Evolución de Utilidad'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return Utils.formatCurrency(value);
                                }
                            }
                        }
                    }
                }
            });
        });
    },

    /**
     * Inicializar gráfico de pedidos
     */
    initializeOrdersChart: function() {
        const ctx = document.getElementById('ordersChart');
        if (!ctx) return;

        fetch('/api/charts/orders-data')
        .then(response => response.json())
        .then(data => {
            new Chart(ctx, {
                type: 'doughnut',
                data: data.chartData,
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Estado de Pedidos'
                        }
                    }
                }
            });
        });
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    TextilApp.init();
});

// Agregar estilos para animaciones
const style = document.createElement('style');
style.textContent = `
    .spin {
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .fade-in {
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
`;
document.head.appendChild(style);

// Exportar para uso global
window.TextilApp = TextilApp;
