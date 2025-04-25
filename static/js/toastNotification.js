/**
 * Toast Notification System for Axra Tutor CRM
 * A utility to show toast notifications for various actions
 */

// Create toast notification global instance
let toastNotification;

// Initialize when document is ready
jQueryReady(function() {
    // Create and initialize the global instance
    toastNotification = new ToastNotification();
    toastNotification.init();
});

class ToastNotification {
    constructor(options = {}) {
        this.defaultOptions = {
            container: '#toastContainer',
            defaultDuration: 3000,
            defaultType: 'info',
            defaultAutohide: true,
            position: 'bottom-end',
            maxToasts: 5
        };
        
        this.options = { ...this.defaultOptions, ...options };
        this.toastCount = 0;
        this.toastQueue = [];
    }
    
    init() {
        // Ensure container exists
        const container = document.querySelector(this.options.container);
        if (!container) {
            console.error('Toast container not found:', this.options.container);
            return;
        }
        
        // Set container position if specified
        if (this.options.position) {
            container.classList.add('position-fixed', this.options.position);
        }
        
        console.log('Toast notification system initialized');
    }
    
    /**
     * Show a toast notification
     * @param {Object} options - Configuration options
     * @param {String} options.title - Title of the toast
     * @param {String} options.message - Message content
     * @param {String} options.type - Type of toast: 'success', 'error', 'warning', 'info'
     * @param {Number} options.duration - Duration in ms
     * @param {Boolean} options.autohide - Whether to auto-hide the toast
     * @param {String} options.icon - Custom icon (feather icon name)
     */
    show(options = {}) {
        // Get container
        const container = document.querySelector(this.options.container);
        if (!container) return;
        
        // Process options
        const config = {
            title: options.title || 'Notification',
            message: options.message || '',
            type: options.type || this.options.defaultType,
            duration: options.duration || this.options.defaultDuration,
            autohide: options.autohide !== undefined ? options.autohide : this.options.defaultAutohide,
            icon: options.icon || null
        };
        
        // Get icon based on type
        let icon = config.icon;
        if (!icon) {
            switch (config.type) {
                case 'success':
                    icon = 'check-circle';
                    break;
                case 'error':
                    icon = 'alert-circle';
                    break;
                case 'warning':
                    icon = 'alert-triangle';
                    break;
                case 'info':
                default:
                    icon = 'info';
                    break;
            }
        }
        
        // Create toast ID
        const toastId = 'toast-' + Date.now();
        
        // Get color class based on type
        let colorClass = 'bg-primary';
        switch (config.type) {
            case 'success':
                colorClass = 'bg-success';
                break;
            case 'error':
                colorClass = 'bg-danger';
                break;
            case 'warning':
                colorClass = 'bg-warning text-dark';
                break;
            case 'info':
                colorClass = 'bg-info text-dark';
                break;
        }
        
        // Create toast HTML
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = 'toast fade-in mb-2 shadow-sm';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="toast-header ${colorClass} text-white">
                <div class="d-flex align-items-center flex-grow-1">
                    <i data-feather="${icon}" class="feather-sm me-2"></i>
                    <strong class="me-auto">${config.title}</strong>
                    <small>${this.getTimeString()}</small>
                </div>
                <button type="button" class="btn-close btn-close-white me-0" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${config.message}
            </div>
        `;
        
        // Manage toast count
        if (container.childElementCount >= this.options.maxToasts) {
            // Remove oldest toast
            container.removeChild(container.firstChild);
        }
        
        // Add toast to container
        container.appendChild(toast);
        
        // Initialize feather icons if available
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
        
        // Create Bootstrap Toast instance
        const toastInstance = new bootstrap.Toast(toast, {
            autohide: config.autohide,
            delay: config.duration
        });
        
        // Show the toast
        toastInstance.show();
        
        // Remove toast once hidden
        toast.addEventListener('hidden.bs.toast', function() {
            container.removeChild(toast);
        });
        
        return toastId;
    }
    
    /**
     * Shorthand for showing a success toast
     */
    success(message, title = 'Success') {
        return this.show({
            title: title,
            message: message,
            type: 'success'
        });
    }
    
    /**
     * Shorthand for showing an error toast
     */
    error(message, title = 'Error') {
        return this.show({
            title: title,
            message: message,
            type: 'error',
            duration: 5000 // Errors stay longer
        });
    }
    
    /**
     * Shorthand for showing a warning toast
     */
    warning(message, title = 'Warning') {
        return this.show({
            title: title,
            message: message,
            type: 'warning',
            duration: 4000
        });
    }
    
    /**
     * Shorthand for showing an info toast
     */
    info(message, title = 'Information') {
        return this.show({
            title: title,
            message: message,
            type: 'info'
        });
    }
    
    /**
     * Get a formatted time string for the toast
     */
    getTimeString() {
        const now = new Date();
        let hours = now.getHours();
        const minutes = now.getMinutes().toString().padStart(2, '0');
        const ampm = hours >= 12 ? 'PM' : 'AM';
        
        hours = hours % 12;
        hours = hours ? hours : 12; // Convert 0 to 12
        
        return hours + ':' + minutes + ' ' + ampm;
    }
    
    /**
     * Clear all toasts
     */
    clearAll() {
        const container = document.querySelector(this.options.container);
        if (!container) return;
        
        // Get all toasts
        const toasts = container.querySelectorAll('.toast');
        toasts.forEach(toast => {
            const toastInstance = bootstrap.Toast.getInstance(toast);
            if (toastInstance) {
                toastInstance.hide();
            }
        });
    }
}