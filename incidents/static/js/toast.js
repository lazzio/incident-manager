/**
 * Toast notification system
 */
const toast = {
    /**
     * Show a success toast notification
     * @param {string} message - The message to display
     * @param {number} duration - Duration in ms (default: 3000)
     */
    success: function(message, duration = 3000) {
        this._showToast(message, 'success', duration);
    },
    
    /**
     * Show an error toast notification
     * @param {string} message - The message to display
     * @param {number} duration - Duration in ms (default: 5000)
     */
    error: function(message, duration = 5000) {
        this._showToast(message, 'error', duration);
    },
    
    /**
     * Show a warning toast notification
     * @param {string} message - The message to display
     * @param {number} duration - Duration in ms (default: 4000)
     */
    warning: function(message, duration = 4000) {
        this._showToast(message, 'warning', duration);
    },
    
    /**
     * Show an info toast notification
     * @param {string} message - The message to display
     * @param {number} duration - Duration in ms (default: 3000)
     */
    info: function(message, duration = 3000) {
        this._showToast(message, 'info', duration);
    },
    
    /**
     * Internal method to show a toast notification
     * @private
     */
    _showToast: function(message, type, duration) {
        // Get or create toast container
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast toast-top toast-center z-50';
            document.body.appendChild(container);
        }
        
        // Create alert element
        const alert = document.createElement('div');
        alert.className = `alert shadow-lg ${this._getAlertClass(type)} transform transition-transform duration-300 ease-out translate-y-[-20px] opacity-0`;
        
        // Set icon based on type
        const iconName = this._getIconName(type);
        
        // Set alert content
        alert.innerHTML = `
            <span class="material-symbols-rounded">${iconName}</span>
            <span>${message}</span>
            <button class="close-toast">
                <span class="material-symbols-rounded">close</span>
            </button>
        `;
        
        // Add to container
        container.appendChild(alert);
        
        // Trigger animation
        setTimeout(() => {
            alert.classList.remove('translate-y-[-20px]', 'opacity-0');
        }, 10);
        
        // Add click listener to close button
        const closeButton = alert.querySelector('.close-toast');
        closeButton.addEventListener('click', () => {
            this._removeToast(alert);
        });
        
        // Auto-remove after duration
        setTimeout(() => {
            this._removeToast(alert);
        }, duration);
    },
    
    /**
     * Get alert class based on type
     * @private
     */
    _getAlertClass: function(type) {
        switch (type) {
            case 'success':
                return 'alert-success';
            case 'error':
                return 'alert-error';
            case 'warning':
                return 'alert-warning';
            case 'info':
                return 'alert-info';
            default:
                return '';
        }
    },
    
    /**
     * Get icon name based on type
     * @private
     */
    _getIconName: function(type) {
        switch (type) {
            case 'success':
                return 'check_circle';
            case 'error':
                return 'error';
            case 'warning':
                return 'warning';
            case 'info':
                return 'info';
            default:
                return 'notifications';
        }
    },
    
    /**
     * Remove a toast from the DOM
     * @private
     */
    _removeToast: function(alert) {
        alert.classList.add('translate-y-[-20px]', 'opacity-0');
        
        // Wait for animation to finish before removing element
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
            
            // Remove container if empty
            const container = document.getElementById('toast-container');
            if (container && container.children.length === 0) {
                document.body.removeChild(container);
            }
        }, 300);
    }
};
