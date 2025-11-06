/**
 * Modal Helper - Provides async functions for Bootstrap modals
 * Replaces native alert() and confirm() with Bootstrap modals
 */

const ModalHelper = {
    /**
     * Show a confirmation dialog with yes/no options
     *
     * @param {string} message - The message to display
     * @param {string} title - Optional title (default: "Potwierdzenie")
     * @returns {Promise<boolean>} - Resolves to true if confirmed, false if cancelled
     */
    showConfirm(message, title = 'Potwierdzenie') {
        return new Promise((resolve) => {
            const modal = document.getElementById('confirmModal');
            const modalTitle = document.getElementById('confirmModalTitle');
            const modalBody = document.getElementById('confirmModalBody');
            const confirmBtn = document.getElementById('confirmOkBtn');
            const cancelBtn = document.getElementById('confirmCancelBtn');

            // Set content
            modalTitle.textContent = title;
            modalBody.textContent = message;

            // Create Bootstrap modal instance
            const bsModal = new bootstrap.Modal(modal);

            // Handle confirm button
            const handleConfirm = () => {
                cleanup();
                resolve(true);
            };

            // Handle cancel button
            const handleCancel = () => {
                cleanup();
                resolve(false);
            };

            // Handle modal close (X button or backdrop click)
            const handleHide = () => {
                cleanup();
                resolve(false);
            };

            // Cleanup function to remove event listeners
            const cleanup = () => {
                confirmBtn.removeEventListener('click', handleConfirm);
                cancelBtn.removeEventListener('click', handleCancel);
                modal.removeEventListener('hidden.bs.modal', handleHide);
                bsModal.hide();
            };

            // Attach event listeners
            confirmBtn.addEventListener('click', handleConfirm);
            cancelBtn.addEventListener('click', handleCancel);
            modal.addEventListener('hidden.bs.modal', handleHide, { once: true });

            // Show modal
            bsModal.show();
        });
    },

    /**
     * Show an alert dialog with single OK button
     *
     * @param {string} message - The message to display
     * @param {string} title - Optional title (default: "Informacja")
     * @returns {Promise<void>} - Resolves when modal is closed
     */
    showAlert(message, title = 'Informacja') {
        return new Promise((resolve) => {
            const modal = document.getElementById('alertModal');
            const modalTitle = document.getElementById('alertModalTitle');
            const modalBody = document.getElementById('alertModalBody');
            const okBtn = document.getElementById('alertOkBtn');

            // Set content
            modalTitle.textContent = title;
            modalBody.textContent = message;

            // Create Bootstrap modal instance
            const bsModal = new bootstrap.Modal(modal);

            // Handle OK button
            const handleOk = () => {
                cleanup();
                resolve();
            };

            // Handle modal close (X button or backdrop click)
            const handleHide = () => {
                cleanup();
                resolve();
            };

            // Cleanup function to remove event listeners
            const cleanup = () => {
                okBtn.removeEventListener('click', handleOk);
                modal.removeEventListener('hidden.bs.modal', handleHide);
                bsModal.hide();
            };

            // Attach event listeners
            okBtn.addEventListener('click', handleOk);
            modal.addEventListener('hidden.bs.modal', handleHide, { once: true });

            // Show modal
            bsModal.show();
        });
    }
};
