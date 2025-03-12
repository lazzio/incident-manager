/**
 * Component initialization script
 */

// Modal functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modals
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal-id');
            closeModal(modalId);
        });
    });
    
    // Close modal on backdrop click
    document.querySelectorAll('[id$="-modal"]').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                const modalId = this.id;
                closeModal(modalId);
            }
        });
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal-open');
            openModals.forEach(modal => {
                const modalId = modal.id;
                closeModal(modalId);
            });
        }
    });
    
    // Helper function to open a modal
    window.openModal = function(modalId, imageUrl, title) {
        const modal = document.getElementById(modalId);
        const modalContainer = document.getElementById(`${modalId}-container`);
        const modalTitle = document.getElementById(`${modalId}-title`);
        const modalContent = document.getElementById(`${modalId}-content`);
        const downloadLink = document.getElementById(`${modalId}-download`);
        
        if (title) modalTitle.textContent = title;
        
        if (imageUrl) {
            modalContent.innerHTML = `<img src="${imageUrl}" alt="${title || 'Preview'}" class="max-h-[70vh] max-w-full object-contain">`;
            if (downloadLink) downloadLink.href = imageUrl;
        }
        
        modal.classList.remove('pointer-events-none');
        void modal.offsetWidth; // Force reflow
        
        modal.classList.add('opacity-100');
        modal.classList.add('bg-black/50');
        modal.classList.add('modal-open');
        modalContainer.classList.remove('scale-95');
        modalContainer.classList.add('scale-100');
        
        document.body.style.overflow = 'hidden';
    }
    
    // Helper function to close a modal
    window.closeModal = function(modalId) {
        const modal = document.getElementById(modalId);
        const modalContainer = document.getElementById(`${modalId}-container`);
        
        modal.classList.remove('opacity-100');
        modal.classList.remove('bg-black/50');
        modal.classList.add('opacity-0');
        modal.classList.remove('modal-open');
        modalContainer.classList.remove('scale-100');
        modalContainer.classList.add('scale-95');
        
        setTimeout(() => {
            modal.classList.add('pointer-events-none');
            document.body.style.overflow = '';
        }, 300);
    }
});
