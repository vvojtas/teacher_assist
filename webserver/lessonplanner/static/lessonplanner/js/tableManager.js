/**
 * Table Manager - Handles row operations and state management
 */

const TableManager = {
    // State tracking
    nextRowId: 1,
    rows: new Map(), // rowId -> {module, curriculum, objectives, activity, aiGenerated, userEdited}

    /**
     * Initialize the table with 5 empty rows and attach event listeners
     */
    init() {
        this.addRows(5);
        this.attachEventListeners();
    },

    /**
     * Add a specified number of empty rows to the table
     * @param {number} count - Number of rows to add (default: 1)
     */
    addRows(count = 1) {
        const tbody = document.getElementById('planTableBody');
        const template = document.getElementById('rowTemplate');

        for (let i = 0; i < count; i++) {
            const rowId = `row_${this.nextRowId++}`;
            const row = template.content.cloneNode(true);
            const tr = row.querySelector('tr');

            // Set row ID
            tr.setAttribute('data-row-id', rowId);

            // Initialize row state
            this.rows.set(rowId, {
                module: '',
                curriculum: '',
                objectives: '',
                activity: '',
                aiGenerated: false,
                userEdited: false
            });

            tbody.appendChild(row);
        }

        this.attachRowEventListeners();
    },

    /**
     * Delete a specific row from the table
     * @param {string} rowId - The ID of the row to delete
     */
    deleteRow(rowId) {
        const row = document.querySelector(`tr[data-row-id="${rowId}"]`);
        if (row) {
            row.remove();
            this.rows.delete(rowId);
        }
    },

    /**
     * Clear all rows and reset to 5 empty rows (with confirmation)
     * @returns {Promise<void>}
     */
    async clearAll() {
        // Confirmation dialog
        const confirmed = await ModalHelper.showConfirm('Czy na pewno chcesz wyczyść wszystkie wiersze?');
        if (!confirmed) {
            return;
        }

        // Clear the table
        const tbody = document.getElementById('planTableBody');
        tbody.innerHTML = '';

        // Reset state
        this.rows.clear();
        this.nextRowId = 1;

        // Add 5 new empty rows
        this.addRows(5);

        // Clear theme input
        document.getElementById('themeInput').value = '';
    },

    /**
     * Get data from a specific row
     * @param {string} rowId - The ID of the row
     * @returns {Object|null} Row data object or null if not found
     */
    getRowData(rowId) {
        const row = document.querySelector(`tr[data-row-id="${rowId}"]`);
        if (!row) return null;

        const state = this.rows.get(rowId) || {};

        return {
            id: rowId,
            module: row.querySelector('.cell-module').textContent.trim(),
            curriculum: row.querySelector('.cell-curriculum').textContent.trim(),
            objectives: row.querySelector('.cell-objectives').textContent.trim(),
            activity: row.querySelector('.cell-activity').textContent.trim(),
            aiGenerated: state.aiGenerated,
            userEdited: state.userEdited
        };
    },

    /**
     * Set data for a specific row
     * @param {string} rowId - The ID of the row
     * @param {Object} data - Data object with module, curriculum, objectives, activity, aiGenerated, userEdited
     */
    setRowData(rowId, data) {
        const row = document.querySelector(`tr[data-row-id="${rowId}"]`);
        if (!row) return;

        // Update DOM
        if (data.module !== undefined) {
            row.querySelector('.cell-module').textContent = data.module;
        }
        if (data.curriculum !== undefined) {
            // Join array if needed
            const curriculum = Array.isArray(data.curriculum)
                ? data.curriculum.join(', ')
                : data.curriculum;
            row.querySelector('.cell-curriculum').textContent = curriculum;
        }
        if (data.objectives !== undefined) {
            // Join array with newlines if needed
            const objectives = Array.isArray(data.objectives)
                ? data.objectives.join('\n')
                : data.objectives;
            row.querySelector('.cell-objectives').textContent = objectives;
        }
        if (data.activity !== undefined) {
            row.querySelector('.cell-activity').textContent = data.activity;
        }

        // Update state
        const state = this.rows.get(rowId);
        if (state) {
            if (data.aiGenerated !== undefined) {
                state.aiGenerated = data.aiGenerated;
            }
            if (data.userEdited !== undefined) {
                state.userEdited = data.userEdited;
            }
        }

        // Update button visibility
        this.updateRowButtons(rowId);
    },

    /**
     * Update button visibility based on row state
     * Show "Wypełnij AI" or "Generuj ponownie" based on aiGenerated flag
     * @param {string} rowId - The ID of the row
     */
    updateRowButtons(rowId) {
        const row = document.querySelector(`tr[data-row-id="${rowId}"]`);
        if (!row) return;

        const state = this.rows.get(rowId);
        const generateBtn = row.querySelector('.generate-btn');
        const regenerateBtn = row.querySelector('.regenerate-btn');

        if (state && state.aiGenerated) {
            // Show regenerate button, hide generate button
            generateBtn.style.display = 'none';
            regenerateBtn.style.display = 'inline-block';
        } else {
            // Show generate button, hide regenerate button
            generateBtn.style.display = 'inline-block';
            regenerateBtn.style.display = 'none';
        }
    },

    /**
     * Get all rows that have activities
     * @returns {Array} Array of row data objects
     */
    getRowsWithActivities() {
        const result = [];
        this.rows.forEach((state, rowId) => {
            const data = this.getRowData(rowId);
            if (data && data.activity) {
                result.push(data);
            }
        });
        return result;
    },

    /**
     * Get rows that need AI generation (have activity but no AI-generated metadata)
     * Used by bulk generate to only fill new rows, not override existing data
     * @returns {Array} Array of row data objects that need generation
     */
    getRowsNeedingGeneration() {
        const result = [];
        this.rows.forEach((state, rowId) => {
            const data = this.getRowData(rowId);
            // Include row if it has activity AND (no AI data OR completely empty metadata)
            if (data && data.activity && !state.aiGenerated && !state.userEdited) {
                // Check if metadata fields are empty
                const hasEmptyMetadata = !data.module && !data.curriculum && !data.objectives;
                if (hasEmptyMetadata) {
                    result.push(data);
                }
            }
        });
        return result;
    },

    /**
     * Mark row as loading or not loading
     * @param {string} rowId - The ID of the row
     * @param {boolean} loading - True to show loading state, false to hide
     */
    setRowLoading(rowId, loading) {
        const row = document.querySelector(`tr[data-row-id="${rowId}"]`);
        if (!row) return;

        if (loading) {
            row.classList.add('loading');
            // Disable buttons
            row.querySelectorAll('button').forEach(btn => btn.disabled = true);
        } else {
            row.classList.remove('loading');
            // Enable buttons
            row.querySelectorAll('button').forEach(btn => btn.disabled = false);
        }
    },

    /**
     * Attach event listeners to table buttons
     */
    attachEventListeners() {
        const tbody = document.getElementById('planTableBody');

        // Event delegation for row buttons
        tbody.addEventListener('click', (e) => {
            const btn = e.target.closest('button');
            if (!btn) return;

            const row = btn.closest('tr');
            const rowId = row.getAttribute('data-row-id');

            if (btn.classList.contains('delete-btn')) {
                this.deleteRow(rowId);
            } else if (btn.classList.contains('generate-btn')) {
                this.handleGenerate(rowId);
            } else if (btn.classList.contains('regenerate-btn')) {
                this.handleRegenerate(rowId);
            }
        });

        // Track user edits on contenteditable cells
        tbody.addEventListener('input', (e) => {
            if (e.target.hasAttribute('contenteditable')) {
                const row = e.target.closest('tr');
                const rowId = row.getAttribute('data-row-id');
                const state = this.rows.get(rowId);

                if (state && state.aiGenerated) {
                    state.userEdited = true;
                }
            }
        });
    },

    /**
     * Attach event listeners to newly added rows
     */
    attachRowEventListeners() {
        // This is handled by event delegation in attachEventListeners
        // Just update button states for all rows
        this.rows.forEach((state, rowId) => {
            this.updateRowButtons(rowId);
        });
    },

    /**
     * Handle generate button click for a row
     * @param {string} rowId - The ID of the row
     * @returns {Promise<void>}
     */
    async handleGenerate(rowId) {
        const data = this.getRowData(rowId);
        if (!data.activity) {
            await ModalHelper.showAlert('Pole "Aktywność" nie może być puste.');
            return;
        }

        // Check if user has already filled in metadata fields
        const hasManualData = data.module || data.curriculum || data.objectives;
        if (hasManualData) {
            const confirmed = await ModalHelper.showConfirm('Wiersz zawiera dane wprowadzone ręcznie. Nadpisać dane AI?');
            if (!confirmed) {
                return;
            }
        }

        // Trigger event for AI service
        const event = new CustomEvent('generateMetadata', {
            detail: { rowId, activity: data.activity }
        });
        document.dispatchEvent(event);
    },

    /**
     * Handle regenerate button click for a row
     * @param {string} rowId - The ID of the row
     * @returns {Promise<void>}
     */
    async handleRegenerate(rowId) {
        const state = this.rows.get(rowId);

        // Check if user edited the row
        if (state && state.userEdited) {
            const confirmed = await ModalHelper.showConfirm('Wiersz był zmodyfikowany. Nadpisać dane wprowadzone przez użytkownika?');
            if (!confirmed) {
                return;
            }
        }

        const data = this.getRowData(rowId);
        if (!data.activity) {
            await ModalHelper.showAlert('Pole "Aktywność" nie może być puste.');
            return;
        }

        // Trigger event for AI service
        const event = new CustomEvent('generateMetadata', {
            detail: { rowId, activity: data.activity }
        });
        document.dispatchEvent(event);
    }
};
