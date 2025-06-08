/**
 * Módulo de gestión de formularios
 */
const FormManager = {
    init: function() {
        this.setupFormValidation();
        this.setupDynamicFields();
        this.setupAutoSave();
    },

    /**
     * Configurar validación de formularios
     */
    setupFormValidation: function() {
        const forms = document.querySelectorAll('.needs-validation');
        
        forms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    },

    /**
     * Configurar campos dinámicos
     */
    setupDynamicFields: function() {
        // Email validation
        const emailFields = document.querySelectorAll('input[type="email"]');
        emailFields.forEach(field => {
            field.addEventListener('blur', function() {
                if (this.value && !Utils.isValidEmail(this.value)) {
                    this.setCustomValidity('Ingrese un email válido');
                } else {
                    this.setCustomValidity('');
                }
            });
        });

        // Phone validation
        const phoneFields = document.querySelectorAll('input[data-validate="phone"]');
        phoneFields.forEach(field => {
            field.addEventListener('blur', function() {
                if (this.value && !Utils.isValidPhone(this.value)) {
                    this.setCustomValidity('Ingrese un teléfono colombiano válido');
                } else {
                    this.setCustomValidity('');
                }
            });
        });

        // Currency formatting
        const currencyFields = document.querySelectorAll('input[data-format="currency"]');
        currencyFields.forEach(field => {
            field.addEventListener('blur', function() {
                if (this.value) {
                    const value = parseFloat(this.value.replace(/[^\d.]/g, ''));
                    if (!isNaN(value)) {
                        this.value = Utils.formatCurrency(value);
                    }
                }
            });
        });
    },

    /**
     * Configurar autoguardado
     */
    setupAutoSave: function() {
        const autoSaveForms = document.querySelectorAll('[data-autosave="true"]');
        
        autoSaveForms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                input.addEventListener('change', Utils.debounce(() => {
                    this.autoSaveForm(form);
                }, 2000));
            });
        });
    },

    /**
     * Guardar formulario automáticamente
     */
    autoSaveForm: function(form) {
        const formData = new FormData(form);
        const url = form.dataset.autosaveUrl || form.action;
        
        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Utils.showToast('Cambios guardados automáticamente', 'success', 2000);
            }
        })
        .catch(error => {
            console.error('Error en autoguardado:', error);
        });
    }
};

// Exportar para uso global
window.FormManager = FormManager;
