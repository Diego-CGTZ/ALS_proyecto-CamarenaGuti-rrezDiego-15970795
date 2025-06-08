/**
 * Configuración global del sistema
 */
const CONFIG = {
    ANIMATION_DURATION: 300,
    DEBOUNCE_DELAY: 500,
    API_TIMEOUT: 5000
};

/**
 * Utilidades comunes
 */
const Utils = {
    /**
     * Función debounce para limitar la frecuencia de llamadas
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Formatear números como moneda
     */
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 2
        }).format(amount);
    },

    /**
     * Formatear fechas
     */
    formatDate: function(date, options = {}) {
        const defaultOptions = { 
            year: 'numeric', 
            month: '2-digit', 
            day: '2-digit' 
        };
        return new Intl.DateTimeFormat('es-CO', { ...defaultOptions, ...options }).format(new Date(date));
    },

    /**
     * Mostrar notificaciones toast
     */
    showToast: function(message, type = 'info', duration = 5000) {
        const toastContainer = document.querySelector('.toast-container') || this.createToastContainer();
        
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
        toastEl.setAttribute('role', 'alert');
        
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toastEl);
        
        const toast = new bootstrap.Toast(toastEl, { delay: duration });
        toast.show();
        
        // Limpiar el toast después de que se oculte
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    },

    /**
     * Crear contenedor de toasts si no existe
     */
    createToastContainer: function() {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    },

    /**
     * Validar email
     */
    isValidEmail: function(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    /**
     * Validar teléfono colombiano
     */
    isValidPhone: function(phone) {
        const phoneRegex = /^(\+57|57)?[1-9][0-9]{7,9}$/;
        return phoneRegex.test(phone.replace(/\s/g, ''));
    }
};

// Exportar para uso global
window.CONFIG = CONFIG;
window.Utils = Utils;
