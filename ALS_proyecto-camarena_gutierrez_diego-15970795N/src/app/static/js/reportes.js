/**
 * Sistema de Gestión Textil - Módulo de Reportes
 * Gestión de funcionalidades específicas de reportes y análisis
 */

const ReportesManager = {
    init: function() {
        console.log('📊 Inicializando módulo de reportes');
        this.setupEventListeners();
        this.initializeReportFilters();
        this.setupCharts();
        this.setupExportFunctions();
    },

    /**
     * Configurar event listeners
     */
    setupEventListeners: function() {
        // Filtros de fecha
        const fechaInicioInput = document.getElementById('fecha_inicio');
        const fechaFinInput = document.getElementById('fecha_fin');
        
        if (fechaInicioInput && fechaFinInput) {
            fechaInicioInput.addEventListener('change', this.updateReportData.bind(this));
            fechaFinInput.addEventListener('change', this.updateReportData.bind(this));
        }

        // Filtros de tipo de reporte
        const tipoReporteSelect = document.getElementById('tipo_reporte');
        if (tipoReporteSelect) {
            tipoReporteSelect.addEventListener('change', this.changeReportType.bind(this));
        }

        // Botones de exportación
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="export-pdf"]')) {
                this.exportToPDF();
            }
            if (e.target.matches('[data-action="export-excel"]')) {
                this.exportToExcel();
            }
            if (e.target.matches('[data-action="export-csv"]')) {
                this.exportToCSV();
            }
            if (e.target.matches('[data-action="print-report"]')) {
                this.printReport();
            }
            if (e.target.matches('[data-action="refresh-data"]')) {
                this.refreshReportData();
            }
        });

        // Auto-refresh de datos cada 5 minutos
        setInterval(() => {
            this.refreshReportData(true); // silent refresh
        }, 300000);
    },

    /**
     * Inicializar filtros de reportes
     */
    initializeReportFilters: function() {
        // Configurar rangos de fecha predefinidos
        const rangeButtons = document.querySelectorAll('[data-date-range]');
        rangeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const range = e.target.dataset.dateRange;
                this.setDateRange(range);
            });
        });

        // Configurar filtros avanzados
        const advancedFiltersToggle = document.getElementById('toggle-advanced-filters');
        if (advancedFiltersToggle) {
            advancedFiltersToggle.addEventListener('click', this.toggleAdvancedFilters.bind(this));
        }
    },

    /**
     * Configurar gráficos
     */
    setupCharts: function() {
        // Inicializar gráficos si están disponibles
        this.initializeVentasChart();
        this.initializeUtilidadChart();
        this.initializeProductosChart();
        this.initializeClientesChart();
    },

    /**
     * Configurar funciones de exportación
     */
    setupExportFunctions: function() {
        // Configurar opciones de exportación
        const exportOptions = document.getElementById('export-options');
        if (exportOptions) {
            exportOptions.addEventListener('change', this.updateExportOptions.bind(this));
        }
    },

    /**
     * Actualizar datos del reporte
     */
    updateReportData: function() {
        const fechaInicio = document.getElementById('fecha_inicio')?.value;
        const fechaFin = document.getElementById('fecha_fin')?.value;
        const tipoReporte = document.getElementById('tipo_reporte')?.value;

        if (!fechaInicio || !fechaFin) {
            return;
        }

        Utils.showLoading(true);

        const params = new URLSearchParams({
            fecha_inicio: fechaInicio,
            fecha_fin: fechaFin,
            tipo: tipoReporte || 'general'
        });

        fetch(`/reportes/data?${params}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            Utils.showLoading(false);
            
            if (data.success) {
                this.updateReportDisplay(data.data);
                this.updateCharts(data.charts);
            } else {
                Utils.showToast(data.message || 'Error al cargar datos del reporte', 'error');
            }
        })
        .catch(error => {
            Utils.showLoading(false);
            console.error('Error:', error);
            Utils.showToast('Error de conexión', 'error');
        });
    },

    /**
     * Cambiar tipo de reporte
     */
    changeReportType: function(e) {
        const tipoReporte = e.target.value;
        
        // Mostrar/ocultar secciones según el tipo
        this.toggleReportSections(tipoReporte);
        
        // Actualizar datos
        this.updateReportData();
    },

    /**
     * Alternar secciones del reporte
     */
    toggleReportSections: function(tipo) {
        const sections = {
            'ventas': ['.ventas-section', '.resumen-section'],
            'utilidad': ['.utilidad-section', '.margenes-section'],
            'productos': ['.productos-section', '.inventario-section'],
            'clientes': ['.clientes-section', '.analisis-section'],
            'general': ['.resumen-section', '.graficos-section']
        };

        // Ocultar todas las secciones
        document.querySelectorAll('.report-section').forEach(section => {
            section.style.display = 'none';
        });

        // Mostrar secciones relevantes
        if (sections[tipo]) {
            sections[tipo].forEach(selector => {
                const section = document.querySelector(selector);
                if (section) {
                    section.style.display = 'block';
                }
            });
        }
    },

    /**
     * Establecer rango de fechas
     */
    setDateRange: function(range) {
        const fechaFin = new Date();
        let fechaInicio = new Date();

        switch (range) {
            case 'hoy':
                fechaInicio = new Date();
                break;
            case 'semana':
                fechaInicio.setDate(fechaFin.getDate() - 7);
                break;
            case 'mes':
                fechaInicio.setMonth(fechaFin.getMonth() - 1);
                break;
            case 'trimestre':
                fechaInicio.setMonth(fechaFin.getMonth() - 3);
                break;
            case 'año':
                fechaInicio.setFullYear(fechaFin.getFullYear() - 1);
                break;
        }

        // Actualizar inputs
        const fechaInicioInput = document.getElementById('fecha_inicio');
        const fechaFinInput = document.getElementById('fecha_fin');

        if (fechaInicioInput && fechaFinInput) {
            fechaInicioInput.value = fechaInicio.toISOString().split('T')[0];
            fechaFinInput.value = fechaFin.toISOString().split('T')[0];
            
            // Actualizar datos
            this.updateReportData();
        }

        // Actualizar botones activos
        document.querySelectorAll('[data-date-range]').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-date-range="${range}"]`)?.classList.add('active');
    },

    /**
     * Alternar filtros avanzados
     */
    toggleAdvancedFilters: function() {
        const advancedFilters = document.getElementById('advanced-filters');
        if (advancedFilters) {
            const isVisible = advancedFilters.style.display !== 'none';
            advancedFilters.style.display = isVisible ? 'none' : 'block';
            
            const toggle = document.getElementById('toggle-advanced-filters');
            if (toggle) {
                toggle.textContent = isVisible ? 'Mostrar Filtros Avanzados' : 'Ocultar Filtros Avanzados';
            }
        }
    },

    /**
     * Actualizar display del reporte
     */
    updateReportDisplay: function(data) {
        // Actualizar métricas principales
        this.updateMetrics(data.metricas);
        
        // Actualizar tablas
        this.updateTables(data.tablas);
        
        // Actualizar resumen
        this.updateSummary(data.resumen);
    },

    /**
     * Actualizar métricas
     */
    updateMetrics: function(metricas) {
        if (!metricas) return;

        Object.keys(metricas).forEach(key => {
            const element = document.querySelector(`[data-metric="${key}"]`);
            if (element) {
                element.textContent = this.formatMetricValue(key, metricas[key]);
            }
        });
    },

    /**
     * Formatear valor de métrica
     */
    formatMetricValue: function(key, value) {
        if (key.includes('total') || key.includes('precio') || key.includes('utilidad')) {
            return Utils.formatCurrency(value);
        }
        if (key.includes('porcentaje')) {
            return `${value}%`;
        }
        return value;
    },

    /**
     * Actualizar tablas
     */
    updateTables: function(tablas) {
        if (!tablas) return;

        Object.keys(tablas).forEach(tableKey => {
            const tableContainer = document.querySelector(`[data-table="${tableKey}"]`);
            if (tableContainer) {
                this.renderTable(tableContainer, tablas[tableKey]);
            }
        });
    },

    /**
     * Renderizar tabla
     */
    renderTable: function(container, data) {
        if (!data || !data.headers || !data.rows) return;

        const table = document.createElement('table');
        table.className = 'table table-striped table-hover';

        // Crear encabezados
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        data.headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        // Crear filas
        const tbody = document.createElement('tbody');
        data.rows.forEach(row => {
            const tr = document.createElement('tr');
            row.forEach(cell => {
                const td = document.createElement('td');
                td.textContent = cell;
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        container.innerHTML = '';
        container.appendChild(table);
    },

    /**
     * Actualizar resumen
     */
    updateSummary: function(resumen) {
        if (!resumen) return;

        const summaryContainer = document.querySelector('.report-summary');
        if (summaryContainer) {
            summaryContainer.innerHTML = `
                <div class="row">
                    <div class="col-md-3">
                        <div class="summary-item">
                            <h6>Total Ventas</h6>
                            <h4>${Utils.formatCurrency(resumen.total_ventas || 0)}</h4>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="summary-item">
                            <h6>Total Pedidos</h6>
                            <h4>${resumen.total_pedidos || 0}</h4>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="summary-item">
                            <h6>Utilidad Total</h6>
                            <h4>${Utils.formatCurrency(resumen.utilidad_total || 0)}</h4>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="summary-item">
                            <h6>Margen Promedio</h6>
                            <h4>${resumen.margen_promedio || 0}%</h4>
                        </div>
                    </div>
                </div>
            `;
        }
    },

    /**
     * Actualizar gráficos
     */
    updateCharts: function(chartsData) {
        if (!chartsData) return;

        // Actualizar cada gráfico
        if (chartsData.ventas) {
            this.updateVentasChart(chartsData.ventas);
        }
        if (chartsData.utilidad) {
            this.updateUtilidadChart(chartsData.utilidad);
        }
        if (chartsData.productos) {
            this.updateProductosChart(chartsData.productos);
        }
        if (chartsData.clientes) {
            this.updateClientesChart(chartsData.clientes);
        }
    },

    /**
     * Inicializar gráfico de ventas
     */
    initializeVentasChart: function() {
        const canvas = document.getElementById('ventasChart');
        if (!canvas) return;

        // Implementar gráfico básico o usar librería como Chart.js
        this.ventasChart = this.createChart(canvas, 'line', {
            labels: [],
            datasets: [{
                label: 'Ventas',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        });
    },

    /**
     * Inicializar gráfico de utilidad
     */
    initializeUtilidadChart: function() {
        const canvas = document.getElementById('utilidadChart');
        if (!canvas) return;

        this.utilidadChart = this.createChart(canvas, 'bar', {
            labels: [],
            datasets: [{
                label: 'Utilidad',
                data: [],
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        });
    },

    /**
     * Inicializar gráfico de productos
     */
    initializeProductosChart: function() {
        const canvas = document.getElementById('productosChart');
        if (!canvas) return;

        this.productosChart = this.createChart(canvas, 'doughnut', {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF'
                ]
            }]
        });
    },

    /**
     * Inicializar gráfico de clientes
     */
    initializeClientesChart: function() {
        const canvas = document.getElementById('clientesChart');
        if (!canvas) return;

        this.clientesChart = this.createChart(canvas, 'bar', {
            labels: [],
            datasets: [{
                label: 'Pedidos por Cliente',
                data: [],
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }]
        });
    },

    /**
     * Crear gráfico básico (placeholder - usar Chart.js si está disponible)
     */
    createChart: function(canvas, type, data) {
        // Si Chart.js está disponible, usar esa librería
        if (typeof Chart !== 'undefined') {
            return new Chart(canvas, {
                type: type,
                data: data,
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Gráfico de Reportes'
                        }
                    }
                }
            });
        } else {
            // Placeholder simple
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = '#f8f9fa';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#6c757d';
            ctx.font = '16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Gráfico no disponible', canvas.width / 2, canvas.height / 2);
            return null;
        }
    },

    /**
     * Actualizar gráfico de ventas
     */
    updateVentasChart: function(data) {
        if (this.ventasChart && data) {
            this.ventasChart.data.labels = data.labels;
            this.ventasChart.data.datasets[0].data = data.values;
            this.ventasChart.update();
        }
    },

    /**
     * Actualizar gráfico de utilidad
     */
    updateUtilidadChart: function(data) {
        if (this.utilidadChart && data) {
            this.utilidadChart.data.labels = data.labels;
            this.utilidadChart.data.datasets[0].data = data.values;
            this.utilidadChart.update();
        }
    },

    /**
     * Actualizar gráfico de productos
     */
    updateProductosChart: function(data) {
        if (this.productosChart && data) {
            this.productosChart.data.labels = data.labels;
            this.productosChart.data.datasets[0].data = data.values;
            this.productosChart.update();
        }
    },

    /**
     * Actualizar gráfico de clientes
     */
    updateClientesChart: function(data) {
        if (this.clientesChart && data) {
            this.clientesChart.data.labels = data.labels;
            this.clientesChart.data.datasets[0].data = data.values;
            this.clientesChart.update();
        }
    },

    /**
     * Exportar a PDF
     */
    exportToPDF: function() {
        Utils.showLoading(true);
        
        const params = this.getReportParams();
        
        fetch('/reportes/export/pdf', {
            method: 'POST',
            headers: {
                'X-CSRFToken': Utils.getCSRFToken(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        })
        .then(response => {
            if (response.ok) {
                return response.blob();
            }
            throw new Error('Error al generar PDF');
        })
        .then(blob => {
            Utils.showLoading(false);
            
            // Descargar archivo
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `reporte_${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            Utils.showToast('PDF generado exitosamente', 'success');
        })
        .catch(error => {
            Utils.showLoading(false);
            console.error('Error:', error);
            Utils.showToast('Error al generar PDF', 'error');
        });
    },

    /**
     * Exportar a Excel
     */
    exportToExcel: function() {
        Utils.showLoading(true);
        
        const params = this.getReportParams();
        
        fetch('/reportes/export/excel', {
            method: 'POST',
            headers: {
                'X-CSRFToken': Utils.getCSRFToken(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        })
        .then(response => {
            if (response.ok) {
                return response.blob();
            }
            throw new Error('Error al generar Excel');
        })
        .then(blob => {
            Utils.showLoading(false);
            
            // Descargar archivo
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `reporte_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            Utils.showToast('Excel generado exitosamente', 'success');
        })
        .catch(error => {
            Utils.showLoading(false);
            console.error('Error:', error);
            Utils.showToast('Error al generar Excel', 'error');
        });
    },

    /**
     * Exportar a CSV
     */
    exportToCSV: function() {
        const params = this.getReportParams();
        
        // Generar CSV desde los datos actuales
        const csvData = this.generateCSVData();
        const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `reporte_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        Utils.showToast('CSV generado exitosamente', 'success');
    },

    /**
     * Imprimir reporte
     */
    printReport: function() {
        window.print();
    },

    /**
     * Refrescar datos del reporte
     */
    refreshReportData: function(silent = false) {
        if (!silent) {
            Utils.showToast('Actualizando datos...', 'info');
        }
        this.updateReportData();
    },

    /**
     * Obtener parámetros del reporte
     */
    getReportParams: function() {
        return {
            fecha_inicio: document.getElementById('fecha_inicio')?.value,
            fecha_fin: document.getElementById('fecha_fin')?.value,
            tipo_reporte: document.getElementById('tipo_reporte')?.value,
            filtros: this.getAdvancedFilters()
        };
    },

    /**
     * Obtener filtros avanzados
     */
    getAdvancedFilters: function() {
        const filters = {};
        
        const advancedFilters = document.getElementById('advanced-filters');
        if (advancedFilters) {
            const inputs = advancedFilters.querySelectorAll('input, select');
            inputs.forEach(input => {
                if (input.value) {
                    filters[input.name] = input.value;
                }
            });
        }
        
        return filters;
    },

    /**
     * Generar datos CSV
     */
    generateCSVData: function() {
        const tables = document.querySelectorAll('.report-table table');
        let csvContent = '';
        
        tables.forEach((table, index) => {
            if (index > 0) csvContent += '\n\n';
            
            // Encabezados
            const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent);
            csvContent += headers.join(',') + '\n';
            
            // Filas
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const cells = Array.from(row.querySelectorAll('td')).map(td => 
                    `"${td.textContent.replace(/"/g, '""')}"`
                );
                csvContent += cells.join(',') + '\n';
            });
        });
        
        return csvContent;
    },

    /**
     * Actualizar opciones de exportación
     */
    updateExportOptions: function(e) {
        const options = e.target.value;
        
        // Guardar preferencias de exportación
        localStorage.setItem('reporte-export-options', options);
    }
};

// Inicializar automáticamente si estamos en una página de reportes
if (window.location.pathname.includes('/reportes')) {
    document.addEventListener('DOMContentLoaded', () => {
        ReportesManager.init();
    });
}
