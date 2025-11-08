/**
 * AI Service - Handles API calls to Django backend
 */

const AIService = {
    // API endpoints
    endpoints: {
        fillWorkPlan: '/api/fill-work-plan/',
        curriculumTooltip: '/api/curriculum-refs/'
    },

    // Cache for curriculum tooltips
    tooltipCache: new Map(),

    // Request timeout in milliseconds (per PRD section 7.6)
    REQUEST_TIMEOUT: 120000,

    /**
     * Get user-friendly error message based on error type
     * @param {Error} error - The error object
     * @returns {string} User-friendly error message in Polish
     */
    getUserFriendlyErrorMessage(error) {
        if (error.name === 'AbortError') {
            return 'Żądanie przekroczyło limit czasu (120s). Spróbuj ponownie.';
        } else if (error.message?.includes('fetch') || error.message?.includes('NetworkError')) {
            return 'Nie można połączyć z usługą AI. Sprawdź połączenie internetowe.';
        } else {
            return error.message || 'Wystąpił nieoczekiwany błąd.';
        }
    },

    /**
     * Generate metadata for a single row
     * @param {string} rowId - The ID of the row to update
     * @param {string} activity - The activity text
     * @param {string} theme - The optional theme text
     * @returns {Promise<Object>} The generated metadata
     */
    async generateSingle(rowId, activity, theme = '') {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.REQUEST_TIMEOUT);

        try {
            // Show loading state
            TableManager.setRowLoading(rowId, true);

            // Make API request
            const response = await fetch(this.endpoints.fillWorkPlan, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    activity: activity,
                    theme: theme
                }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Błąd serwera');
            }

            // Update row with generated data
            TableManager.setRowData(rowId, {
                module: data.module,
                curriculum: data.curriculum_refs,
                objectives: data.objectives,
                aiGenerated: true,
                userEdited: false
            });

            return data;

        } catch (error) {
            clearTimeout(timeoutId);
            console.error('Error generating metadata:', error);
            this.showError(this.getUserFriendlyErrorMessage(error));
            throw error;

        } finally {
            // Hide loading state
            TableManager.setRowLoading(rowId, false);
        }
    },

    /**
     * Generate metadata for multiple rows (sequential operation)
     * Makes individual calls to fillWorkPlan for each row
     * @param {Array} rows - Array of row objects with id and activity
     * @param {string} theme - The optional theme text
     * @returns {Promise<void>}
     */
    async generateBulk(rows, theme = '') {
        try {
            // Show progress container
            const progressContainer = document.getElementById('progressContainer');
            const progressBar = document.getElementById('progressBar');
            const progressText = document.getElementById('progressText');

            progressContainer.style.display = 'block';
            progressBar.style.width = '0%';
            progressBar.setAttribute('aria-valuenow', 0);
            progressText.textContent = 'Przetwarzanie... (0/' + rows.length + ')';

            // Disable bulk generate button
            const bulkBtn = document.getElementById('bulkGenerateBtn');
            bulkBtn.disabled = true;
            bulkBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Przetwarzanie...';

            // Set all rows to inactive state at the beginning
            for (const row of rows) {
                TableManager.setRowLoading(row.id, false);
            }

            // Process each row sequentially
            let completed = 0;
            let succeeded = 0;

            for (const row of rows) {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.REQUEST_TIMEOUT);

                try {
                    // Set loading state for this row
                    TableManager.setRowLoading(row.id, true);

                    // Make individual API call for each row
                    const response = await fetch(this.endpoints.fillWorkPlan, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.getCsrfToken()
                        },
                        body: JSON.stringify({
                            activity: row.activity,
                            theme: theme
                        }),
                        signal: controller.signal
                    });

                    clearTimeout(timeoutId);

                    const data = await response.json();

                    if (response.ok) {
                        // Update row with generated data
                        TableManager.setRowData(row.id, {
                            module: data.module,
                            curriculum: data.curriculum_refs,
                            objectives: data.objectives,
                            aiGenerated: true,
                            userEdited: false
                        });
                        succeeded++;
                    } else {
                        const errorMsg = data.error || 'Błąd serwera';
                        console.error(`Error for row ${row.id}:`, errorMsg);

                        // Show error modal immediately
                        this.showError(
                            `Błąd dla aktywności:\n"${row.activity.substring(0, 50)}..."\n\n` +
                            `Szczegóły: ${errorMsg}`
                        );
                    }

                } catch (error) {
                    clearTimeout(timeoutId);
                    const errorMsg = error.name === 'AbortError'
                        ? 'Przekroczono limit czasu'
                        : (error.message || 'Nieznany błąd');
                    console.error(`Error generating metadata for row ${row.id}:`, errorMsg);

                    // Show error modal immediately
                    this.showError(
                        `Błąd dla aktywności:\n"${row.activity.substring(0, 50)}..."\n\n` +
                        `Szczegóły: ${errorMsg}`
                    );
                } finally {
                    // Clear loading state for this row
                    TableManager.setRowLoading(row.id, false);
                }

                // Update progress
                completed++;
                const progress = (completed / rows.length) * 100;
                progressBar.style.width = progress + '%';
                progressBar.setAttribute('aria-valuenow', progress);
                progressText.textContent = `Przetwarzanie... (${completed}/${rows.length})`;
            }

            // Show completion message
            progressText.textContent = `Ukończono: ${succeeded}/${rows.length}`;

            // Hide progress after delay
            setTimeout(() => {
                progressContainer.style.display = 'none';
            }, 2000);

        } catch (error) {
            console.error('Error in bulk generation:', error);
            this.showError(this.getUserFriendlyErrorMessage(error));
            throw error;

        } finally {
            // Re-enable bulk generate button
            const bulkBtn = document.getElementById('bulkGenerateBtn');
            bulkBtn.disabled = false;
            bulkBtn.innerHTML = '<i class="bi bi-magic"></i> Wypełnij wszystko AI';
        }
    },

    /**
     * Get curriculum reference text for tooltip
     * @param {string} code - The curriculum reference code (e.g., "I.1.2")
     * @returns {Promise<string>} The curriculum text
     */
    async getCurriculumTooltip(code) {
        // Check cache first
        if (this.tooltipCache.has(code)) {
            return this.tooltipCache.get(code);
        }

        try {
            const response = await fetch(this.endpoints.curriculumTooltip + code + '/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Nie znaleziono opisu');
            }

            // Cache the result
            this.tooltipCache.set(code, data.full_text);

            return data.full_text;

        } catch (error) {
            console.error('Error fetching tooltip:', error);
            return `Nie znaleziono opisu dla kodu: ${code}`;
        }
    },

    /**
     * Show error modal with a message
     * @param {string} message - The error message to display
     */
    showError(message) {
        const modal = new bootstrap.Modal(document.getElementById('errorModal'));
        const modalBody = document.getElementById('errorModalBody');

        modalBody.textContent = message;
        modal.show();
    },

    /**
     * Get CSRF token from cookies for Django requests
     * @returns {string|null} The CSRF token or null if not found
     */
    getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
};
