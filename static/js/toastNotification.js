/**
 * Elegant Toast Notification System for Axra Tutor CRM
 * Provides beautiful, customizable notifications in the Nawabi style
 */

// Create the ToastNotification class
class ToastNotification {
    constructor(options = {}) {
        // Default options
        this.options = {
            position: options.position || 'top-right',
            duration: options.duration || 3000,
            maxVisible: options.maxVisible || 5,
            container: options.container || document.body,
            theme: options.theme || 'light'
        };
        
        // Create toast container if it doesn't exist
        this.createContainer();
        
        // Queue to manage toasts
        this.queue = [];
    }
    
    // Create the toast container
    createContainer() {
        // Check if container already exists
        let container = document.querySelector('.toast-container-' + this.options.position);
        
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container toast-container-' + this.options.position;
            container.style.position = 'fixed';
            container.style.zIndex = '9999';
            
            // Position the container based on the position option
            switch (this.options.position) {
                case 'top-left':
                    container.style.top = '1rem';
                    container.style.left = '1rem';
                    break;
                case 'top-center':
                    container.style.top = '1rem';
                    container.style.left = '50%';
                    container.style.transform = 'translateX(-50%)';
                    break;
                case 'top-right':
                    container.style.top = '1rem';
                    container.style.right = '1rem';
                    break;
                case 'bottom-left':
                    container.style.bottom = '1rem';
                    container.style.left = '1rem';
                    break;
                case 'bottom-center':
                    container.style.bottom = '1rem';
                    container.style.left = '50%';
                    container.style.transform = 'translateX(-50%)';
                    break;
                case 'bottom-right':
                    container.style.bottom = '1rem';
                    container.style.right = '1rem';
                    break;
            }
            
            this.options.container.appendChild(container);
        }
        
        this.container = container;
    }
    
    // Show a success toast
    success(message, title = 'Success') {
        this.show(message, title, 'success');
    }
    
    // Show an error toast
    error(message, title = 'Error') {
        this.show(message, title, 'error');
    }
    
    // Show a warning toast
    warning(message, title = 'Warning') {
        this.show(message, title, 'warning');
    }
    
    // Show an info toast
    info(message, title = 'Info') {
        this.show(message, title, 'info');
    }
    
    // Show a toast
    show(message, title = '', type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = 'toast toast-' + type;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        // Toast styling
        toast.style.minWidth = '250px';
        toast.style.maxWidth = '450px';
        toast.style.background = this.getBackgroundColor(type);
        toast.style.color = this.getTextColor(type);
        toast.style.borderRadius = '0.5rem';
        toast.style.padding = '1rem';
        toast.style.boxShadow = '0 0.5rem 1rem rgba(0, 0, 0, 0.15)';
        toast.style.marginBottom = '0.75rem';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
        toast.style.transition = 'all 0.3s ease-in-out';
        toast.style.overflow = 'hidden';
        toast.style.position = 'relative';
        
        // Add a colored border on the left
        toast.style.borderLeft = '4px solid ' + this.getBorderColor(type);
        
        // Create the content
        const content = document.createElement('div');
        content.className = 'toast-content';
        
        // Create title if provided
        if (title) {
            const titleElement = document.createElement('div');
            titleElement.className = 'toast-title';
            titleElement.textContent = title;
            titleElement.style.fontWeight = 'bold';
            titleElement.style.marginBottom = '0.25rem';
            titleElement.style.fontSize = '1.1rem';
            content.appendChild(titleElement);
        }
        
        // Create message
        const messageElement = document.createElement('div');
        messageElement.className = 'toast-message';
        messageElement.textContent = message;
        content.appendChild(messageElement);
        
        toast.appendChild(content);
        
        // Create close button
        const closeButton = document.createElement('button');
        closeButton.className = 'toast-close';
        closeButton.innerHTML = '&times;';
        closeButton.style.position = 'absolute';
        closeButton.style.top = '0.5rem';
        closeButton.style.right = '0.5rem';
        closeButton.style.background = 'transparent';
        closeButton.style.border = 'none';
        closeButton.style.color = 'inherit';
        closeButton.style.fontSize = '1.5rem';
        closeButton.style.cursor = 'pointer';
        closeButton.style.opacity = '0.7';
        closeButton.style.transition = 'opacity 0.2s ease';
        closeButton.style.padding = '0 0.5rem';
        
        // Hover effect for close button
        closeButton.addEventListener('mouseover', () => {
            closeButton.style.opacity = '1';
        });
        
        closeButton.addEventListener('mouseout', () => {
            closeButton.style.opacity = '0.7';
        });
        
        toast.appendChild(closeButton);
        
        // Add to container
        this.container.appendChild(toast);
        
        // Add to queue
        this.queue.push({
            element: toast,
            timeoutId: null
        });
        
        // Animate in
        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0)';
        }, 10);
        
        // Manage visible toasts
        this.manageQueue();
        
        // Close button click event
        closeButton.addEventListener('click', () => {
            this.close(toast);
        });
        
        // Auto-close toast after duration
        const timeoutId = setTimeout(() => {
            this.close(toast);
        }, this.options.duration);
        
        // Update timeout ID in queue
        const queueItem = this.queue.find(item => item.element === toast);
        if (queueItem) {
            queueItem.timeoutId = timeoutId;
        }
        
        // Return the toast element
        return toast;
    }
    
    // Close a toast
    close(toast) {
        // Animate out
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
        
        // Remove from queue
        const index = this.queue.findIndex(item => item.element === toast);
        if (index !== -1) {
            const item = this.queue[index];
            
            // Clear timeout
            if (item.timeoutId) {
                clearTimeout(item.timeoutId);
            }
            
            // Remove from queue
            this.queue.splice(index, 1);
        }
        
        // Remove from DOM after animation
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
            
            // Manage visible toasts
            this.manageQueue();
        }, 300);
    }
    
    // Manage queue of toasts
    manageQueue() {
        // If queue is longer than maxVisible, hide the overflowing toasts
        if (this.queue.length > this.options.maxVisible) {
            // Get overflowing toasts
            const overflowingToasts = this.queue.slice(this.options.maxVisible);
            
            // Hide overflowing toasts
            overflowingToasts.forEach(item => {
                item.element.style.display = 'none';
            });
        } else {
            // Show all toasts
            this.queue.forEach(item => {
                item.element.style.display = '';
            });
        }
    }
    
    // Get background color based on type
    getBackgroundColor(type) {
        switch (type) {
            case 'success':
                return 'rgba(4, 99, 7, 0.1)'; // emerald background with low opacity
            case 'error':
                return 'rgba(190, 0, 50, 0.1)'; // ruby background with low opacity
            case 'warning':
                return 'rgba(255, 215, 0, 0.1)'; // gold background with low opacity
            case 'info':
                return 'rgba(106, 13, 173, 0.1)'; // purple background with low opacity
            default:
                return 'rgba(255, 255, 255, 0.9)';
        }
    }
    
    // Get text color based on type
    getTextColor(type) {
        switch (type) {
            case 'success':
                return '#046307'; // emerald
            case 'error':
                return '#be0032'; // ruby
            case 'warning':
                return '#d4af37'; // dark gold
            case 'info':
                return '#6a0dad'; // purple
            default:
                return '#302942'; // dark gray
        }
    }
    
    // Get border color based on type
    getBorderColor(type) {
        switch (type) {
            case 'success':
                return '#046307'; // emerald
            case 'error':
                return '#be0032'; // ruby
            case 'warning':
                return '#ffd700'; // gold
            case 'info':
                return '#6a0dad'; // purple
            default:
                return '#6a0dad'; // purple
        }
    }
}

// Create global instance
const toast = new ToastNotification();

// Simple function to show toast (for backward compatibility)
function showToast(message, type = 'success', title = '') {
    switch (type) {
        case 'success':
            toast.success(message, title || 'Success');
            break;
        case 'error':
            toast.error(message, title || 'Error');
            break;
        case 'warning':
            toast.warning(message, title || 'Warning');
            break;
        case 'info':
            toast.info(message, title || 'Info');
            break;
        default:
            toast.success(message, title || 'Success');
    }
}

// Make toast available globally
window.ToastNotification = ToastNotification;
window.toast = toast;
window.showToast = showToast;

console.log('Toast notification system loaded');