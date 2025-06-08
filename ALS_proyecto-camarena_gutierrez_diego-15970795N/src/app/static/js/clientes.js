/**
 * Sistema de Gestión Textil - Módulo de Clientes
 * Gestión de funcionalidades específicas de clientes
 */

const ClientesManager = {
    init: function() {
        console.log('📱 Inicializando módulo de clientes');
        this.setupEventListeners();
        this.initializeClienteForm();
        this.setupClienteSearch();
        this.setupClienteStats();
    },

    /**
     * Configurar event listeners
     */
    setupEventListeners: function() {
        // Validación de formulario de cliente
        const clienteForm = document.getElementById('cliente-form');
        if (clienteForm) {
            clienteForm.addEventListener('submit', this.handleClienteSubmit.bind(this));
        }

        // Búsqueda de clientes
        const searchInput = document.getElementById('cliente-search');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.searchClientes(e.target.value);
                }, 300);
            });
        }

        // Filtros de clientes
        const filterSelect = document.getElementById('cliente-filter');
        if (filterSelect) {
            filterSelect.addEventListener('change', this.filterClientes.bind(this));
        }

        // Acciones en tabla de clientes
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="view-cliente"]')) {
                this.viewCliente(e.target.dataset.clienteId);
            }
            if (e.target.matches('[data-action="edit-cliente"]')) {
                this.editCliente(e.target.dataset.clienteId);
            }
            if (e.target.matches('[data-action="delete-cliente"]')) {
                this.deleteCliente(e.target.dataset.clienteId);
            }
        });
    },

    /**
     * Inicializar formulario de cliente
     */
    initializeClienteForm: function() {
        const form = document.getElementById('cliente-form');
        if (!form) return;

        // Validación en tiempo real
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
        });

        // Formateo automático de teléfono
        const telefonoInput = form.querySelector('#telefono');
        if (telefonoInput) {
            telefonoInput.addEventListener('input', this.formatTelefono);
        }

        // Formateo automático de RUT/NIT
        const documentoInput = form.querySelector('#documento');
        if (documentoInput) {
            documentoInput.addEventListener('input', this.formatDocumento);
        }
    },

    /**
     * Configurar búsqueda de clientes
     */
    setupClienteSearch: function() {
        const searchContainer = document.getElementById('cliente-search-container');
        if (!searchContainer) return;

        // Crear dropdown de resultados
        const dropdown = document.createElement('div');
        dropdown.className = 'search-dropdown';
        dropdown.style.display = 'none';
        searchContainer.appendChild(dropdown);
    },

    /**
     * Configurar estadísticas de cliente
     */
    setupClienteStats: function() {
        const statsContainer = document.querySelector('.cliente-stats');
        if (!statsContainer) return;

        // Cargar estadísticas si estamos en la página de detalle
        const clienteId = Utils.getUrlParameter('id') || 
                         document.querySelector('[data-cliente-id]')?.dataset.clienteId;
        
        if (clienteId) {
            this.loadClienteStats(clienteId);
        }
    },

    /**
     * Manejar envío del formulario de cliente
     */
    handleClienteSubmit: function(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        
        // Validar formulario completo
        if (!this.validateClienteForm(form)) {
            Utils.showToast('Por favor, corrija los errores en el formulario', 'error');
            return;
        }

        // Mostrar loading
        Utils.showLoading(true);
        
        // Enviar datos
        const url = form.action || form.dataset.submitUrl;
        const method = form.method || 'POST';

        fetch(url, {
            method: method,
            body: formData,
            headers: {
                'X-CSRFToken': Utils.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            Utils.showLoading(false);
            
            if (data.success) {
                Utils.showToast(data.message || 'Cliente guardado exitosamente', 'success');
                
                // Redirigir si es necesario
                if (data.redirect_url) {
                    setTimeout(() => {
                        window.location.href = data.redirect_url;
                    }, 1500);
                }
            } else {
                Utils.showToast(data.message || 'Error al guardar cliente', 'error');
                
                // Mostrar errores específicos
                if (data.errors) {
                    this.showFormErrors(form, data.errors);
                }
            }
        })
        .catch(error => {
            Utils.showLoading(false);
            console.error('Error:', error);
            Utils.showToast('Error de conexión', 'error');
        });
    },

    /**
     * Buscar clientes
     */
    searchClientes: function(query) {
        if (query.length < 2) {
            this.hideSearchResults();
            return;
        }

        fetch(`/clientes/search?q=${encodeURIComponent(query)}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            this.showSearchResults(data.clientes);
        })
        .catch(error => {
            console.error('Error en búsqueda:', error);
        });
    },

    /**
     * Mostrar resultados de búsqueda
     */
    showSearchResults: function(clientes) {
        const dropdown = document.querySelector('.search-dropdown');
        if (!dropdown) return;

        if (clientes.length === 0) {
            dropdown.innerHTML = '<div class="search-no-results">No se encontraron clientes</div>';
        } else {
            dropdown.innerHTML = clientes.map(cliente => `
                <div class="search-result-item" data-cliente-id="${cliente.id}">
                    <div class="search-result-name">${cliente.nombre}</div>
                    <div class="search-result-info">${cliente.email} - ${cliente.telefono}</div>
                </div>
            `).join('');
        }

        dropdown.style.display = 'block';

        // Manejar selección
        dropdown.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', () => {
                this.selectCliente(item.dataset.clienteId);
                this.hideSearchResults();
            });
        });
    },

    /**
     * Ocultar resultados de búsqueda
     */
    hideSearchResults: function() {
        const dropdown = document.querySelector('.search-dropdown');
        if (dropdown) {
            dropdown.style.display = 'none';
        }
    },

    /**
     * Seleccionar cliente
     */
    selectCliente: function(clienteId) {
        window.location.href = `/clientes/${clienteId}`;
    },

    /**
     * Filtrar clientes
     */
    filterClientes: function(e) {
        const filter = e.target.value;
        const currentUrl = new URL(window.location);
        
        if (filter) {
            currentUrl.searchParams.set('filter', filter);
        } else {
            currentUrl.searchParams.delete('filter');
        }
        
        window.location.href = currentUrl.toString();
    },

    /**
     * Ver cliente
     */
    viewCliente: function(clienteId) {
        window.location.href = `/clientes/${clienteId}`;
    },

    /**
     * Editar cliente
     */
    editCliente: function(clienteId) {
        window.location.href = `/clientes/${clienteId}/editar`;
    },

    /**
     * Eliminar cliente
     */
    deleteCliente: function(clienteId) {
        if (!confirm('¿Está seguro de que desea eliminar este cliente?')) {
            return;
        }

        Utils.showLoading(true);

        fetch(`/clientes/${clienteId}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': Utils.getCSRFToken(),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            Utils.showLoading(false);
            
            if (data.success) {
                Utils.showToast('Cliente eliminado exitosamente', 'success');
                
                // Remover fila de la tabla o recargar página
                const row = document.querySelector(`[data-cliente-id="${clienteId}"]`).closest('tr');
                if (row) {
                    row.remove();
                } else {
                    window.location.reload();
                }
            } else {
                Utils.showToast(data.message || 'Error al eliminar cliente', 'error');
            }
        })
        .catch(error => {
            Utils.showLoading(false);
            console.error('Error:', error);
            Utils.showToast('Error de conexión', 'error');
        });
    },

    /**
     * Cargar estadísticas del cliente
     */
    loadClienteStats: function(clienteId) {
        fetch(`/clientes/${clienteId}/stats`)
        .then(response => response.json())
        .then(data => {
            this.updateClienteStats(data);
        })
        .catch(error => {
            console.error('Error cargando estadísticas:', error);
        });
    },

    /**
     * Actualizar estadísticas del cliente
     */
    updateClienteStats: function(stats) {
        const statsContainer = document.querySelector('.cliente-stats');
        if (!statsContainer) return;

        // Actualizar contadores
        const totalPedidos = statsContainer.querySelector('.stat-total-pedidos');
        const totalFacturado = statsContainer.querySelector('.stat-total-facturado');
        const ultimoPedido = statsContainer.querySelector('.stat-ultimo-pedido');

        if (totalPedidos) totalPedidos.textContent = stats.total_pedidos || 0;
        if (totalFacturado) totalFacturado.textContent = Utils.formatCurrency(stats.total_facturado || 0);
        if (ultimoPedido) ultimoPedido.textContent = stats.ultimo_pedido || 'Nunca';
    },

    /**
     * Validar campo individual
     */
    validateField: function(field) {
        const value = field.value.trim();
        let isValid = true;
        let message = '';

        // Validaciones específicas por campo
        switch (field.id || field.name) {
            case 'nombre':
                if (!value) {
                    isValid = false;
                    message = 'El nombre es requerido';
                } else if (value.length < 2) {
                    isValid = false;
                    message = 'El nombre debe tener al menos 2 caracteres';
                }
                break;

            case 'email':
                if (value && !Utils.isValidEmail(value)) {
                    isValid = false;
                    message = 'Email inválido';
                }
                break;

            case 'telefono':
                if (value && !Utils.isValidPhone(value)) {
                    isValid = false;
                    message = 'Teléfono inválido';
                }
                break;
        }

        // Actualizar UI del campo
        this.updateFieldValidation(field, isValid, message);
        return isValid;
    },

    /**
     * Validar formulario completo
     */
    validateClienteForm: function(form) {
        const fields = form.querySelectorAll('input, select, textarea');
        let isValid = true;

        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    },

    /**
     * Actualizar validación visual del campo
     */
    updateFieldValidation: function(field, isValid, message) {
        field.classList.remove('is-valid', 'is-invalid');
        
        const feedback = field.parentNode.querySelector('.invalid-feedback, .valid-feedback');
        if (feedback) {
            feedback.remove();
        }

        if (isValid) {
            field.classList.add('is-valid');
        } else {
            field.classList.add('is-invalid');
            
            const feedbackDiv = document.createElement('div');
            feedbackDiv.className = 'invalid-feedback';
            feedbackDiv.textContent = message;
            field.parentNode.appendChild(feedbackDiv);
        }
    },

    /**
     * Mostrar errores del formulario
     */
    showFormErrors: function(form, errors) {
        Object.keys(errors).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                this.updateFieldValidation(field, false, errors[fieldName]);
            }
        });
    },

    /**
     * Formatear teléfono
     */
    formatTelefono: function(e) {
        let value = e.target.value.replace(/\D/g, '');
        
        // Formato: (XXX) XXX-XXXX
        if (value.length >= 6) {
            value = `(${value.slice(0, 3)}) ${value.slice(3, 6)}-${value.slice(6, 10)}`;
        } else if (value.length >= 3) {
            value = `(${value.slice(0, 3)}) ${value.slice(3)}`;
        }
        
        e.target.value = value;
    },

    /**
     * Formatear documento
     */
    formatDocumento: function(e) {
        let value = e.target.value.replace(/\D/g, '');
        
        // Formato simple: XXX.XXX.XXX-X
        if (value.length > 3) {
            value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{1,2})/, '$1.$2.$3-$4');
        }
        
        e.target.value = value;
    }
};

// Inicializar automáticamente si estamos en una página de clientes
if (window.location.pathname.includes('/clientes')) {
    document.addEventListener('DOMContentLoaded', () => {
        ClientesManager.init();
    });
}
