/**
 * Módulo de gestión de pedidos
 */
const PedidosManager = {
    init: function() {
        this.setupProductSelection();
        this.setupStatusChanges();
        this.setupItemManagement();
        this.setupCalculations();
    },

    /**
     * Configurar selección de productos
     */
    setupProductSelection: function() {
        const productSelect = document.getElementById('producto_id');
        const tallaSelect = document.getElementById('talla');
        const colorSelect = document.getElementById('color');

        if (productSelect) {
            productSelect.addEventListener('change', (e) => {
                const productId = e.target.value;
                if (productId) {
                    this.loadProductDetails(productId);
                } else {
                    this.clearProductDetails();
                }
            });
        }
    },

    /**
     * Cargar detalles del producto
     */
    loadProductDetails: function(productId) {
        const tallaSelect = document.getElementById('talla');
        const colorSelect = document.getElementById('color');
        
        // Limpiar opciones existentes
        this.clearProductDetails();

        fetch(`/pedidos/api/producto/${productId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name=csrf-token]')?.getAttribute('content')
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                this.populateOptions(tallaSelect, data.tallas, 'Seleccionar talla');
                this.populateOptions(colorSelect, data.colores, 'Seleccionar color');
                
                // Actualizar precio base si existe el campo
                const precioField = document.getElementById('precio_prenda');
                if (precioField && data.precio_base) {
                    precioField.value = data.precio_base;
                }
            } else {
                Utils.showToast('Error al cargar detalles del producto', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Utils.showToast('Error al conectar con el servidor', 'danger');
        });
    },

    /**
     * Limpiar detalles del producto
     */
    clearProductDetails: function() {
        const tallaSelect = document.getElementById('talla');
        const colorSelect = document.getElementById('color');
        
        if (tallaSelect) {
            tallaSelect.innerHTML = '<option value="">Seleccionar talla</option>';
        }
        if (colorSelect) {
            colorSelect.innerHTML = '<option value="">Seleccionar color</option>';
        }
    },

    /**
     * Poblar opciones de select
     */
    populateOptions: function(selectElement, options, defaultText) {
        if (!selectElement) return;
        
        selectElement.innerHTML = `<option value="">${defaultText}</option>`;
        
        if (Array.isArray(options)) {
            options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option;
                optionElement.textContent = option;
                selectElement.appendChild(optionElement);
            });
        }
    },

    /**
     * Configurar cambios de estado
     */
    setupStatusChanges: function() {
        const statusSelects = document.querySelectorAll('.status-change-select');
        
        statusSelects.forEach(select => {
            select.addEventListener('change', (e) => {
                const pedidoId = e.target.dataset.pedidoId;
                const nuevoEstado = e.target.value;
                const estadoAnterior = e.target.dataset.estadoAnterior;
                
                this.cambiarEstadoPedido(pedidoId, nuevoEstado, estadoAnterior, e.target);
            });
        });
    },

    /**
     * Cambiar estado del pedido
     */
    cambiarEstadoPedido: function(pedidoId, nuevoEstado, estadoAnterior, selectElement) {
        const loadingClass = 'loading';
        selectElement.classList.add(loadingClass);

        fetch(`/pedidos/${pedidoId}/estado`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name=csrf-token]')?.getAttribute('content')
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                estado: nuevoEstado
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Utils.showToast('Estado actualizado correctamente', 'success');
                
                // Actualizar la fila en la tabla si existe
                const row = selectElement.closest('tr');
                if (row) {
                    this.updateRowStatus(row, nuevoEstado);
                }
            } else {
                throw new Error(data.error || 'Error desconocido');
            }
        })
        .catch(error => {
            Utils.showToast('Error al cambiar estado: ' + error.message, 'danger');
            selectElement.value = estadoAnterior;
        })
        .finally(() => {
            selectElement.classList.remove(loadingClass);
        });
    },

    /**
     * Actualizar estado visual de la fila
     */
    updateRowStatus: function(row, estado) {
        // Remover clases de estado anteriores
        row.classList.remove('table-warning', 'table-info', 'table-success', 'table-danger');
        
        // Agregar clase según el nuevo estado
        const statusClasses = {
            'PENDIENTE': 'table-warning',
            'EN_PROCESO': 'table-info',
            'COMPLETADO': 'table-success',
            'CANCELADO': 'table-danger'
        };
        
        if (statusClasses[estado]) {
            row.classList.add(statusClasses[estado]);
        }
    },

    /**
     * Configurar gestión de items
     */
    setupItemManagement: function() {
        // Configurar botones de agregar/eliminar items
        this.setupAddItemButton();
        this.setupRemoveItemButtons();
    },

    /**
     * Configurar botón de agregar item
     */
    setupAddItemButton: function() {
        const addButton = document.getElementById('add-item-btn');
        if (addButton) {
            addButton.addEventListener('click', () => {
                this.addNewItem();
            });
        }
    },

    /**
     * Configurar botones de eliminar item
     */
    setupRemoveItemButtons: function() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-item-btn')) {
                e.preventDefault();
                this.removeItem(e.target);
            }
        });
    },

    /**
     * Agregar nuevo item
     */
    addNewItem: function() {
        const itemsContainer = document.getElementById('items-container');
        if (!itemsContainer) return;

        const itemCount = itemsContainer.children.length;
        const itemTemplate = this.getItemTemplate(itemCount);
        
        const itemDiv = document.createElement('div');
        itemDiv.innerHTML = itemTemplate;
        itemsContainer.appendChild(itemDiv.firstElementChild);
        
        // Reinicializar eventos para el nuevo item
        this.setupProductSelection();
    },

    /**
     * Eliminar item
     */
    removeItem: function(button) {
        const itemContainer = button.closest('.item-container');
        if (itemContainer) {
            itemContainer.remove();
            this.recalculateTotal();
        }
    },

    /**
     * Configurar cálculos automáticos
     */
    setupCalculations: function() {
        document.addEventListener('input', (e) => {
            if (e.target.matches('.cantidad-input, .precio-input')) {
                this.calculateItemTotal(e.target);
            }
        });
    },

    /**
     * Calcular total del item
     */
    calculateItemTotal: function(input) {
        const itemContainer = input.closest('.item-container');
        if (!itemContainer) return;

        const cantidad = parseFloat(itemContainer.querySelector('.cantidad-input')?.value) || 0;
        const precio = parseFloat(itemContainer.querySelector('.precio-input')?.value) || 0;
        const totalField = itemContainer.querySelector('.total-item');

        if (totalField) {
            const total = cantidad * precio;
            totalField.textContent = Utils.formatCurrency(total);
        }

        this.recalculateTotal();
    },

    /**
     * Recalcular total general
     */
    recalculateTotal: function() {
        const itemContainers = document.querySelectorAll('.item-container');
        let total = 0;

        itemContainers.forEach(container => {
            const cantidad = parseFloat(container.querySelector('.cantidad-input')?.value) || 0;
            const precio = parseFloat(container.querySelector('.precio-input')?.value) || 0;
            total += cantidad * precio;
        });

        const totalField = document.getElementById('total-pedido');
        if (totalField) {
            totalField.textContent = Utils.formatCurrency(total);
        }
    },

    /**
     * Obtener template para nuevo item
     */
    getItemTemplate: function(index) {
        return `
            <div class="item-container border rounded p-3 mb-3">
                <div class="row">
                    <div class="col-md-3">
                        <label class="form-label">Producto</label>
                        <select name="items[${index}][producto_id]" class="form-select" required>
                            <option value="">Seleccionar producto</option>
                        </select>
                    </div>
                    <div class="col-md-2">
                        <label class="form-label">Talla</label>
                        <select name="items[${index}][talla]" class="form-select" required>
                            <option value="">Seleccionar talla</option>
                        </select>
                    </div>
                    <div class="col-md-2">
                        <label class="form-label">Color</label>
                        <select name="items[${index}][color]" class="form-select" required>
                            <option value="">Seleccionar color</option>
                        </select>
                    </div>
                    <div class="col-md-2">
                        <label class="form-label">Cantidad</label>
                        <input type="number" name="items[${index}][cantidad]" class="form-control cantidad-input" min="1" required>
                    </div>
                    <div class="col-md-2">
                        <label class="form-label">Precio</label>
                        <input type="number" name="items[${index}][precio]" class="form-control precio-input" step="0.01" required>
                    </div>
                    <div class="col-md-1">
                        <label class="form-label">&nbsp;</label>
                        <button type="button" class="btn btn-danger remove-item-btn">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
};

// Exportar para uso global
window.PedidosManager = PedidosManager;
