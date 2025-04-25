/**
 * Toast Notification System for Axra Tutor CRM
 * A utility to show toast notifications for various actions
 */

class ToastNotification {
    constructor(options = {}) {
        this.container = options.container || '#toastContainer';
        this.defaultDuration = options.duration || 5000; // 5 seconds
        this.position = options.position || 'bottom-end';
        this.maxToasts = options.maxToasts || 3;
        
        // Initialize
        this.init();
    }
    
    init() {
        // Create container if it doesn't exist
        if ($(this.container).length === 0) {
            $('body').append(`<div id="${this.container.replace('#', '')}" class="toast-container position-fixed ${this.position} p-3"></div>`);
        }
        
        // Ensure container has the right classes
        $(this.container).addClass('toast-container position-fixed p-3');
        
        // Apply position classes
        if (this.position === 'bottom-end' || this.position === 'bottom-right') {
            $(this.container).addClass('bottom-0 end-0');
        } else if (this.position === 'bottom-start' || this.position === 'bottom-left') {
            $(this.container).addClass('bottom-0 start-0');
        } else if (this.position === 'top-end' || this.position === 'top-right') {
            $(this.container).addClass('top-0 end-0');
        } else if (this.position === 'top-start' || this.position === 'top-left') {
            $(this.container).addClass('top-0 start-0');
        } else if (this.position === 'middle-center') {
            $(this.container).addClass('top-50 start-50 translate-middle');
        }
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
        const { 
            title = 'Notification',
            message = '',
            type = 'info',
            duration = this.defaultDuration,
            autohide = true,
            icon = null
        } = options;
        
        // Check if we need to remove old toasts
        const toasts = $(this.container).children('.toast');
        if (toasts.length >= this.maxToasts) {
            // Remove the oldest toast
            $(toasts[0]).remove();
        }
        
        // Determine icon and color based on type
        let iconName = icon;
        let bgClass = '';
        
        if (!iconName) {
            switch (type) {
                case 'success':
                    iconName = 'check-circle';
                    bgClass = 'bg-success';
                    break;
                case 'error':
                    iconName = 'alert-circle';
                    bgClass = 'bg-danger';
                    break;
                case 'warning':
                    iconName = 'alert-triangle';
                    bgClass = 'bg-warning';
                    break;
                case 'info':
                default:
                    iconName = 'info';
                    bgClass = 'bg-info';
                    break;
            }
        }
        
        // Create a unique ID for this toast
        const toastId = 'toast-' + Date.now();
        
        // Create the toast HTML
        const toastHtml = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true"
                 data-bs-autohide="${autohide}" data-bs-delay="${duration}">
                <div class="toast-header ${bgClass} text-white">
                    <i data-feather="${iconName}" class="me-2"></i>
                    <strong class="me-auto">${title}</strong>
                    <small>${this.getTimeString()}</small>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        // Add the toast to the container
        $(this.container).append(toastHtml);
        
        // Initialize Feather icons
        feather.replace();
        
        // Initialize and show the toast
        const toastElement = new bootstrap.Toast(document.getElementById(toastId));
        toastElement.show();
        
        // Return the toast element for further manipulation
        return toastElement;
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
            autohide: false  // Errors often need user attention
        });
    }
    
    /**
     * Shorthand for showing a warning toast
     */
    warning(message, title = 'Warning') {
        return this.show({
            title: title,
            message: message,
            type: 'warning'
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
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        
        return `${hours}:${minutes}`;
    }
    
    /**
     * Clear all toasts
     */
    clearAll() {
        $(this.container).empty();
    }
}

// Global instance for easy access
window.toastNotification = new ToastNotification();

// Export for module support
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ToastNotification;
}