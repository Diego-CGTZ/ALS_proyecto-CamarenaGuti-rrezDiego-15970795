/**
 * Sistema de Gestión Textil - Módulo de Productos
 * Gestión de funcionalidades específicas de productos
 */

const ProductosManager = {
    init: function() {
        console.log('📦 Inicializando módulo de productos');
        this.setupEventListeners();
        this.initializeProductoForm();
        this.setupProductoSearch();
        this.setupProductoGrid();
        this.setupInventoryManager();
        this.setupImportManager();
    },

    /**
     * Configurar event listeners
     */
    setupEventListeners: function() {
        // Formulario de producto
        const productoForm = document.getElementById('producto-form');
        if (productoForm) {
            productoForm.addEventListener('submit', this.handleProductoSubmit.bind(this));
        }

        // Búsqueda de productos
        const searchInput = document.getElementById('producto-search');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.searchProductos(e.target.value);
                }, 300);
            });
        }

        // Filtros de productos
        const categoryFilter = document.getElementById('categoria-filter');
        if (categoryFilter) {
            categoryFilter.addEventListener('change', this.filterByCategory.bind(this));
        }

        const stockFilter = document.getElementById('stock-filter');
        if (stockFilter) {
            stockFilter.addEventListener('change', this.filterByStock.bind(this));
        }

        // Acciones de productos
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="view-producto"]')) {
                this.viewProducto(e.target.dataset.productoId);
            }
            if (e.target.matches('[data-action="edit-producto"]')) {
                this.editProducto(e.target.dataset.productoId);
            }
            if (e.target.matches('[data-action="delete-producto"]')) {
                this.deleteProducto(e.target.dataset.productoId);
            }
            if (e.target.matches('[data-action="adjust-stock"]')) {
                this.adjustStock(e.target.dataset.productoId);
            }
            if (e.target.matches('[data-action="duplicate-producto"]')) {
                this.duplicateProducto(e.target.dataset.productoId);
            }
        });

        // Calculadora de costos
        const costInputs = document.querySelectorAll('.cost-input');
        costInputs.forEach(input => {
            input.addEventListener('input', this.calculateProductCost.bind(this));
        });
    },

    /**
     * Inicializar formulario de producto
     */
    initializeProductoForm: function() {
        const form = document.getElementById('producto-form');
        if (!form) return;

        // Validación en tiempo real
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
        });

        // Subida de imágenes
        const imageInput = form.querySelector('#imagen');
        if (imageInput) {
            imageInput.addEventListener('change', this.handleImageUpload.bind(this));
        }

        // Generación automática de código
        const nombreInput = form.querySelector('#nombre');
        const codigoInput = form.querySelector('#codigo');
        if (nombreInput && codigoInput && !codigoInput.value) {
            nombreInput.addEventListener('input', () => {
                this.generateProductCode(nombreInput.value, codigoInput);
            });
        }

        // Cálculo automático de precios
        this.setupPriceCalculator(form);
    },

    /**
     * Configurar búsqueda de productos
     */
    setupProductoSearch: function() {
        const searchContainer = document.getElementById('producto-search-container');
        if (!searchContainer) return;

        // Crear dropdown de resultados
        const dropdown = document.createElement('div');
        dropdown.className = 'search-dropdown producto-search-dropdown';
        dropdown.style.display = 'none';
        searchContainer.appendChild(dropdown);
    },

    /**
     * Configurar grid de productos
     */
    setupProductoGrid: function() {
        const grid = document.querySelector('.producto-grid');
        if (!grid) return;

        // Configurar vista (grid/lista)
        const viewButtons = document.querySelectorAll('[data-view]');
        viewButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const view = e.target.dataset.view;
                this.changeView(view);
            });
        });

        // Configurar ordenamiento
        const sortSelect = document.getElementById('sort-productos');
        if (sortSelect) {
            sortSelect.addEventListener('change', this.sortProductos.bind(this));
        }
    },

    /**
     * Configurar gestor de inventario
     */
    setupInventoryManager: function() {
        // Alertas de stock bajo
        this.checkLowStock();

        // Actualización automática de stock
        setInterval(() => {
            this.refreshStockStatus();
        }, 300000); // 5 minutos
    },

    /**
     * Configura funcionalidad para importación de productos
     */
    setupImportManager: function() {
        const importBtn = document.querySelector('[data-bs-target="#importModal"]');
        if (!importBtn) return;

        const importModal = document.getElementById('importModal');
        if (importModal) {
            // Mejora en la visualización de archivos seleccionados
            const importFile = importModal.querySelector('#importFile');
            const fileLabel = importModal.querySelector('.file-label') || 
                             document.createElement('div');
            
            if (!importModal.querySelector('.file-label')) {
                fileLabel.className = 'file-label mt-2';
                if (importFile.parentElement) {
                    importFile.parentElement.appendChild(fileLabel);
                }
            }

            if (importFile) {
                importFile.addEventListener('change', (e) => {
                    const file = e.target.files[0];
                    if (file) {
                        fileLabel.textContent = `Archivo seleccionado: ${file.name}`;
                        fileLabel.className = 'file-label mt-2 text-success';
                    } else {
                        fileLabel.textContent = '';
                    }
                });
            }
        }

        // Agregar event listener global para el botón de importar
        document.addEventListener('click', (e) => {
            if (e.target.matches('[onclick="importarProductos()"]') || 
                e.target.closest('[onclick="importarProductos()"]')) {
                e.preventDefault();
                this.importarProductos();
            }
        });
    },

    /**
     * Manejar envío del formulario de producto
     */
    handleProductoSubmit: function(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        
        // Validar formulario
        if (!this.validateProductoForm(form)) {
            Utils.showToast('Por favor, corrija los errores en el formulario', 'error');
            return;
        }

        Utils.showLoading(true);
        
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
                Utils.showToast(data.message || 'Producto guardado exitosamente', 'success');
                
                if (data.redirect_url) {
                    setTimeout(() => {
                        window.location.href = data.redirect_url;
                    }, 1500);
                }
            } else {
                Utils.showToast(data.message || 'Error al guardar producto', 'error');
                
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
     * Buscar productos
     */
    searchProductos: function(query) {
        if (query.length < 2) {
            this.hideSearchResults();
            return;
        }

        fetch(`/productos/search?q=${encodeURIComponent(query)}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            this.showSearchResults(data.productos);
        })
        .catch(error => {
            console.error('Error en búsqueda:', error);
        });
    },

    /**
     * Mostrar resultados de búsqueda
     */
    showSearchResults: function(productos) {
        const dropdown = document.querySelector('.producto-search-dropdown');
        if (!dropdown) return;

        if (productos.length === 0) {
            dropdown.innerHTML = '<div class="search-no-results">No se encontraron productos</div>';
        } else {
            dropdown.innerHTML = productos.map(producto => `
                <div class="search-result-item" data-producto-id="${producto.id}">
                    <div class="search-result-info">
                        <div class="search-result-name">${producto.nombre}</div>
                        <div class="search-result-details">
                            <span class="badge bg-primary">${producto.codigo}</span>
                            <span class="text-muted">${Utils.formatCurrency(producto.precio)}</span>
                            <span class="badge ${producto.stock > 0 ? 'bg-success' : 'bg-danger'}">
                                Stock: ${producto.stock}
                            </span>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        dropdown.style.display = 'block';

        // Manejar selección
        dropdown.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', () => {
                this.selectProducto(item.dataset.productoId);
                this.hideSearchResults();
            });
        });
    },

    /**
     * Ocultar resultados de búsqueda
     */
    hideSearchResults: function() {
        const dropdown = document.querySelector('.producto-search-dropdown');
        if (dropdown) {
            dropdown.style.display = 'none';
        }
    },

    /**
     * Filtrar por categoría
     */
    filterByCategory: function(e) {
        const category = e.target.value;
        this.applyFilter('categoria', category);
    },

    /**
     * Filtrar por stock
     */
    filterByStock: function(e) {
        const stockFilter = e.target.value;
        this.applyFilter('stock', stockFilter);
    },

    /**
     * Aplicar filtro
     */
    applyFilter: function(filterType, value) {
        const currentUrl = new URL(window.location);
        
        if (value) {
            currentUrl.searchParams.set(filterType, value);
        } else {
            currentUrl.searchParams.delete(filterType);
        }
        
        window.location.href = currentUrl.toString();
    },

    /**
     * Cambiar vista (grid/lista)
     */
    changeView: function(view) {
        const grid = document.querySelector('.producto-grid');
        const viewButtons = document.querySelectorAll('[data-view]');
        
        // Actualizar clases
        grid.className = `producto-grid view-${view}`;
        
        // Actualizar botones
        viewButtons.forEach(button => {
            button.classList.toggle('active', button.dataset.view === view);
        });
        
        // Guardar preferencia
        localStorage.setItem('producto-view', view);
    },

    /**
     * Ordenar productos
     */
    sortProductos: function(e) {
        const sortBy = e.target.value;
        const currentUrl = new URL(window.location);
        
        if (sortBy) {
            currentUrl.searchParams.set('sort', sortBy);
        } else {
            currentUrl.searchParams.delete('sort');
        }
        
        window.location.href = currentUrl.toString();
    },

    /**
     * Ver producto
     */
    viewProducto: function(productoId) {
        // Using the correct route name 'productos.ver'
        window.location.href = `/productos/${productoId}`;
    },

    /**
     * Editar producto
     */
    editProducto: function(productoId) {
        window.location.href = `/productos/${productoId}/editar`;
    },

    /**
     * Mostrar mensaje cuando no hay productos
     */
    showNoProductsMessage: function() {
        const container = document.getElementById('productsContainer');
        if (!container) return;
        
        container.innerHTML = `
            <div class="col-12">
                <div class="text-center py-5">
                    <i class="fas fa-tshirt fa-3x text-muted mb-3"></i>
                    <h4 class="text-muted">No hay productos disponibles</h4>
                    <p class="text-muted">No se encontraron productos con los criterios seleccionados</p>
                    <button class="btn btn-outline-secondary mt-2" onclick="clearFilters()">
                        <i class="fas fa-sync me-2"></i>Limpiar filtros
                    </button>
                </div>
            </div>
        `;
    },    /**
     * Eliminar producto
     */
    deleteProducto: function(productoId) {
        console.log('🗑️ Iniciando eliminación del producto:', productoId);
        
        // Obtener el nombre del producto desde el DOM
        const productElement = document.querySelector(`[data-producto-id="${productoId}"]`);
        const nombreProducto = productElement ? productElement.dataset.productoNombre || "este producto" : "este producto";
        
        // Usar la función confirmarEliminacion que está en el HTML para asegurar consistencia
        if (typeof confirmarEliminacion === 'function') {
            console.log('✅ Usando función confirmarEliminacion del HTML');
            confirmarEliminacion(productoId, nombreProducto);
        } else {
            console.error('⚠️ La función confirmarEliminacion no está definida. Usando implementación alternativa.');
            // Fallback por si acaso la función no está disponible
            if (confirm(`¿Está seguro de que desea eliminar "${nombreProducto}"?`)) {
                this.enviarSolicitudEliminacion(productoId, nombreProducto);
            }
        }
    },

    /**
     * Envía la solicitud de eliminación al servidor
     */
    enviarSolicitudEliminacion: function(productoId, nombreProducto) {
        Utils.showLoading(true);
        console.log('🔄 Enviando solicitud de eliminación para producto:', productoId);
        
        const formData = new FormData();
        formData.append('csrf_token', Utils.getCSRFToken());
        
        fetch(`/productos/${productoId}/eliminar`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            Utils.showLoading(false);
            console.log('✅ Respuesta recibida:', response.status);
            
            if (response.redirected) {
                console.log('🔄 Redireccionando a:', response.url);
                window.location.href = response.url;
                return;
            }
    
            return response.json().catch(() => null);
        })
        .then(data => {
            if (!data) {
                // Si no hay datos pero la respuesta fue exitosa, consideramos que funcionó
                console.log('✅ Producto eliminado correctamente (sin datos de retorno)');
                Utils.showToast(`Producto "${nombreProducto}" eliminado exitosamente`, 'success');
                
                // Disparar evento personalizado para actualizar la UI
                document.dispatchEvent(new CustomEvent('producto-eliminado', { 
                    detail: { productoId: productoId } 
                }));
                
                // Remover de la vista con animación
                const productCard = document.querySelector(`[data-producto-id="${productoId}"]`);
                if (productCard) {
                    productCard.classList.add('fade-out');
                    setTimeout(() => {
                        productCard.remove();
                        // Verificar si no quedan productos
                        if (document.querySelectorAll('.product-item').length === 0) {
                            this.showNoProductsMessage();
                        }
                    }, 300);
                } else {
                    setTimeout(() => window.location.reload(), 1000);
                }
                
                return;
            }
            
            if (data.success) {
                console.log('✅ Producto eliminado correctamente');
                Utils.showToast('Producto eliminado exitosamente', 'success');
                
                // Disparar evento personalizado para actualizar la UI
                document.dispatchEvent(new CustomEvent('producto-eliminado', { 
                    detail: { productoId: productoId } 
                }));
                
                // Remover de la vista con animación
                const productCard = document.querySelector(`[data-producto-id="${productoId}"]`);
                if (productCard) {
                    productCard.classList.add('fade-out');
                    setTimeout(() => {
                        productCard.remove();
                        // Verificar si no quedan productos
                        if (document.querySelectorAll('.product-item').length === 0) {
                            this.showNoProductsMessage();
                        }
                    }, 300);
                } else {
                    setTimeout(() => window.location.reload(), 1000);
                }
            } else if (data && data.message) {
                console.error('❌ Error al eliminar:', data.message);
                Utils.showToast(data.message, 'error');
            }
        })
        .catch(error => {
            Utils.showLoading(false);
            console.error('❌ Error de conexión:', error);
            Utils.showToast('Error de conexión: ' + error.message, 'error');
        });
    },

    /**
     * Ajustar stock
     */
    adjustStock: function(productoId) {
        const newStock = prompt('Ingrese la nueva cantidad de stock:');
        if (newStock === null || newStock === '') return;

        const stock = parseInt(newStock);
        if (isNaN(stock) || stock < 0) {
            Utils.showToast('Stock inválido', 'error');
            return;
        }

        Utils.showLoading(true);

        fetch(`/productos/${productoId}/stock`, {
            method: 'PUT',
            headers: {
                'X-CSRFToken': Utils.getCSRFToken(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ stock: stock })
        })
        .then(response => response.json())
        .then(data => {
            Utils.showLoading(false);
            
            if (data.success) {
                Utils.showToast('Stock actualizado exitosamente', 'success');
                
                // Actualizar display
                const stockElement = document.querySelector(`[data-producto-id="${productoId}"] .stock-value`);
                if (stockElement) {
                    stockElement.textContent = stock;
                    
                    // Actualizar badge de stock
                    const stockBadge = stockElement.closest('.stock-badge');
                    if (stockBadge) {
                        stockBadge.className = `badge stock-badge ${stock > 0 ? 'bg-success' : 'bg-danger'}`;
                    }
                }
            } else {
                Utils.showToast(data.message || 'Error al actualizar stock', 'error');
            }
        })
        .catch(error => {
            Utils.showLoading(false);
            console.error('Error:', error);
            Utils.showToast('Error de conexión', 'error');
        });
    },

    /**
     * Duplicar producto
     */
    duplicateProducto: function(productoId) {
        Utils.showLoading(true);

        fetch(`/productos/${productoId}/duplicate`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': Utils.getCSRFToken(),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            Utils.showLoading(false);
            
            if (data.success) {
                Utils.showToast('Producto duplicado exitosamente', 'success');
                window.location.href = `/productos/${data.nuevo_producto_id}/editar`;
            } else {
                Utils.showToast(data.message || 'Error al duplicar producto', 'error');
            }
        })
        .catch(error => {
            Utils.showLoading(false);
            console.error('Error:', error);
            Utils.showToast('Error de conexión', 'error');
        });
    },

    /**
     * Verificar stock bajo
     */
    checkLowStock: function() {
        fetch('/productos/low-stock')
        .then(response => response.json())
        .then(data => {
            if (data.productos && data.productos.length > 0) {
                this.showLowStockAlert(data.productos);
            }
        })
        .catch(error => {
            console.error('Error verificando stock:', error);
        });
    },

    /**
     * Mostrar alerta de stock bajo
     */
    showLowStockAlert: function(productos) {
        const alertHtml = `
            <div class="alert alert-warning alert-dismissible fade show" role="alert">
                <h6><i class="bi bi-exclamation-triangle"></i> Stock Bajo</h6>
                <p>Los siguientes productos tienen stock bajo:</p>
                <ul class="mb-0">
                    ${productos.map(p => `<li>${p.nombre} (${p.stock} unidades)</li>`).join('')}
                </ul>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const alertContainer = document.querySelector('.alert-container') || document.body;
        alertContainer.insertAdjacentHTML('afterbegin', alertHtml);
    },

    /**
     * Refrescar estado del stock
     */
    refreshStockStatus: function() {
        const stockElements = document.querySelectorAll('.stock-value');
        if (stockElements.length === 0) return;

        const productoIds = Array.from(stockElements).map(el => 
            el.closest('[data-producto-id]').dataset.productoId
        );

        fetch('/productos/stock-status', {
            method: 'POST',
            headers: {
                'X-CSRFToken': Utils.getCSRFToken(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ producto_ids: productoIds })
        })
        .then(response => response.json())
        .then(data => {
            data.productos.forEach(producto => {
                const stockElement = document.querySelector(
                    `[data-producto-id="${producto.id}"] .stock-value`
                );
                if (stockElement && stockElement.textContent !== producto.stock.toString()) {
                    stockElement.textContent = producto.stock;
                    
                    // Actualizar badge
                    const stockBadge = stockElement.closest('.stock-badge');
                    if (stockBadge) {
                        stockBadge.className = `badge stock-badge ${
                            producto.stock > 0 ? 'bg-success' : 'bg-danger'
                        }`;
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error refrescando stock:', error);
        });
    },

    /**
     * Generar código de producto
     */
    generateProductCode: function(nombre, codigoInput) {
        if (!nombre || codigoInput.value) return;

        const prefix = nombre.substring(0, 3).toUpperCase();
        const timestamp = Date.now().toString().slice(-4);
        const codigo = `${prefix}-${timestamp}`;
        
        codigoInput.value = codigo;
    },

    /**
     * Configurar calculadora de precios
     */
    setupPriceCalculator: function(form) {
        const costoInput = form.querySelector('#costo');
        const margenInput = form.querySelector('#margen');
        const precioInput = form.querySelector('#precio');

        if (!costoInput || !margenInput || !precioInput) return;

        const calculatePrice = () => {
            const costo = parseFloat(costoInput.value) || 0;
            const margen = parseFloat(margenInput.value) || 0;
            
            if (costo > 0 && margen > 0) {
                const precio = costo * (1 + margen / 100);
                precioInput.value = precio.toFixed(2);
            }
        };

        costoInput.addEventListener('input', calculatePrice);
        margenInput.addEventListener('input', calculatePrice);
    },

    /**
     * Manejar subida de imagen
     */
    handleImageUpload: function(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Validar tipo de archivo
        if (!file.type.startsWith('image/')) {
            Utils.showToast('Por favor seleccione una imagen válida', 'error');
            e.target.value = '';
            return;
        }

        // Validar tamaño (5MB máximo)
        if (file.size > 5 * 1024 * 1024) {
            Utils.showToast('La imagen no puede ser mayor a 5MB', 'error');
            e.target.value = '';
            return;
        }

        // Mostrar preview
        const preview = document.getElementById('image-preview');
        if (preview) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.innerHTML = `<img src="${e.target.result}" alt="Preview" class="img-thumbnail" style="max-width: 200px;">`;
            };
            reader.readAsDataURL(file);
        }
    },

    /**
     * Validar campo individual
     */
    validateField: function(field) {
        const value = field.value.trim();
        let isValid = true;
        let message = '';

        switch (field.id || field.name) {
            case 'nombre':
                if (!value) {
                    isValid = false;
                    message = 'El nombre es requerido';
                }
                break;

            case 'codigo':
                if (!value) {
                    isValid = false;
                    message = 'El código es requerido';
                }
                break;

            case 'precio':
                const precio = parseFloat(value);
                if (!value || precio <= 0) {
                    isValid = false;
                    message = 'El precio debe ser mayor a 0';
                }
                break;

            case 'stock':
                const stock = parseInt(value);
                if (value && (isNaN(stock) || stock < 0)) {
                    isValid = false;
                    message = 'El stock debe ser un número positivo';
                }
                break;
        }

        this.updateFieldValidation(field, isValid, message);
        return isValid;
    },

    /**
     * Validar formulario completo
     */
    validateProductoForm: function(form) {
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
     * Seleccionar producto
     */
    selectProducto: function(productoId) {
        window.location.href = `/productos/${productoId}`;
    },

    /**
     * Importar productos desde archivo CSV
     */
    importarProductos: function() {
        console.log('📥 Iniciando importación de productos');
        
        const fileInput = document.getElementById('importFile');
        if (!fileInput || !fileInput.files.length) {
            Utils.showToast('Selecciona un archivo CSV', 'warning');
            return;
        }
        
        const file = fileInput.files[0];
        
        // Validar tipo de archivo
        if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
            Utils.showToast('El archivo debe ser un CSV válido', 'error');
            return;
        }
        
        // Mostrar indicador de carga
        Utils.showLoading(true);
        const importModal = document.getElementById('importModal');
        const modal = importModal ? bootstrap.Modal.getInstance(importModal) : null;
        
        // Crear FormData para enviar el archivo
        const formData = new FormData();
        formData.append('archivo_csv', file);
        formData.append('csrf_token', Utils.getCSRFToken());
        
        // Enviar archivo al servidor
        fetch('/productos/importar', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            Utils.showLoading(false);
            
            if (data.success) {
                // Cerrar modal
                if (modal) modal.hide();
                
                // Mostrar resultados de la importación
                Utils.showToast(data.message || 'Productos importados exitosamente', 'success');
                
                // Mostrar detalles de la importación
                this.showImportResults(data);
                
                // Recargar la página después de un tiempo
                setTimeout(() => {
                    window.location.reload();
                }, 3000);
            } else {
                Utils.showToast(data.message || 'Error al importar productos', 'error');
                console.error('Error de importación:', data.errors);
                
                // Mostrar errores específicos si existen
                if (data.errors && data.errors.length) {
                    this.showImportErrors(data.errors);
                }
            }
        })
        .catch(error => {
            Utils.showLoading(false);
            console.error('Error:', error);
            Utils.showToast('Error de conexión: ' + error.message, 'error');
        });
    },
    
    /**
     * Mostrar resultados de la importación
     */
    showImportResults: function(data) {
        if (!data.productos_importados) return;
        
        const importModal = document.getElementById('importModal');
        if (!importModal) return;
        
        // Crear resumen de resultados
        const resultadosHtml = `
            <div class="import-results mt-3">
                <div class="alert alert-success">
                    <h6><i class="fas fa-check-circle me-2"></i>Importación exitosa</h6>
                    <p>Se han importado <strong>${data.productos_importados.length}</strong> productos.</p>
                    <ul class="mb-0 small">
                        ${data.productos_importados.map(p => 
                            `<li>${p.nombre} (${p.categoria}) - $${p.precio_base}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
        
        // Insertar resultados en el modal
        const resultadosContainer = importModal.querySelector('.import-results') || document.createElement('div');
        if (!importModal.querySelector('.import-results')) {
            resultadosContainer.className = 'import-results mt-3';
            importModal.querySelector('.modal-body').appendChild(resultadosContainer);
        }
        
        resultadosContainer.innerHTML = resultadosHtml;
    },
    
    /**
     * Mostrar errores de la importación
     */
    showImportErrors: function(errors) {
        const importModal = document.getElementById('importModal');
        if (!importModal) return;
        
        // Crear lista de errores
        const erroresHtml = `
            <div class="import-errors mt-3">
                <div class="alert alert-danger">
                    <h6><i class="fas fa-exclamation-triangle me-2"></i>Errores en la importación</h6>
                    <ul class="mb-0 small">
                        ${errors.map(error => `<li>${error}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
        
        // Insertar errores en el modal
        const erroresContainer = importModal.querySelector('.import-errors') || document.createElement('div');
        if (!importModal.querySelector('.import-errors')) {
            erroresContainer.className = 'import-errors mt-3';
            importModal.querySelector('.modal-body').appendChild(erroresContainer);
        }
        
        erroresContainer.innerHTML = erroresHtml;
    }
};

// Inicializar automáticamente si estamos en una página de productos
if (window.location.pathname.includes('/productos')) {
    document.addEventListener('DOMContentLoaded', () => {
        ProductosManager.init();
    });
}
