/**
 * AI Service - Handles API calls to Django backend
 */

const AIService = {
    // API endpoints
    endpoints: {
        generateMetadata: '/api/generate-metadata/',
        generateBulk: '/api/generate-bulk/',
        curriculumTooltip: '/api/curriculum/'
    },

    // Cache for curriculum tooltips
    tooltipCache: new Map(),

    /**
     * Generate metadata for a single row
     */
    async generateSingle(rowId, activity, theme = '') {
        try {
            // Show loading state
            TableManager.setRowLoading(rowId, true);

            // Make API request
            const response = await fetch(this.endpoints.generateMetadata, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    activity: activity,
                    theme: theme
                })
            });

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
            console.error('Error generating metadata:', error);
            this.showError(error.message || 'Nie można połączyć z usługą AI. Wypełnij dane ręcznie.');
            throw error;

        } finally {
            // Hide loading state
            TableManager.setRowLoading(rowId, false);
        }
    },

    /**
     * Generate metadata for multiple rows (bulk operation)
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

            // Set all rows to loading state
            rows.forEach(row => {
                TableManager.setRowLoading(row.id, true);
            });

            // Prepare activities for bulk request
            const activities = rows.map(row => ({
                id: row.id,
                activity: row.activity
            }));

            // Make bulk API request
            const response = await fetch(this.endpoints.generateBulk, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    theme: theme,
                    activities: activities
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Błąd serwera');
            }

            // Process results
            let completed = 0;
            for (const result of data.results) {
                if (result.success) {
                    // Update row with generated data
                    TableManager.setRowData(result.id, {
                        module: result.data.module,
                        curriculum: result.data.curriculum_refs,
                        objectives: result.data.objectives,
                        aiGenerated: true,
                        userEdited: false
                    });
                } else {
                    console.error(`Error for row ${result.id}:`, result.error);
                }

                // Update progress
                completed++;
                const progress = (completed / rows.length) * 100;
                progressBar.style.width = progress + '%';
                progressBar.setAttribute('aria-valuenow', progress);
                progressText.textContent = `Przetwarzanie... (${completed}/${rows.length})`;

                // Small delay for visual feedback
                await new Promise(resolve => setTimeout(resolve, 100));
            }

            // Show completion message
            progressText.textContent = `Ukończono: ${completed}/${rows.length}`;

            // Hide progress after delay
            setTimeout(() => {
                progressContainer.style.display = 'none';
            }, 2000);

        } catch (error) {
            console.error('Error in bulk generation:', error);
            this.showError(error.message || 'Nie można połączyć z usługą AI. Wypełnij dane ręcznie.');
            throw error;

        } finally {
            // Clear loading state for all rows
            rows.forEach(row => {
                TableManager.setRowLoading(row.id, false);
            });

            // Re-enable bulk generate button
            const bulkBtn = document.getElementById('bulkGenerateBtn');
            bulkBtn.disabled = false;
            bulkBtn.innerHTML = '<i class="bi bi-magic"></i> Wypełnij wszystko AI';
        }
    },

    /**
     * Get curriculum reference text for tooltip
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
            this.tooltipCache.set(code, data.text);

            return data.text;

        } catch (error) {
            console.error('Error fetching tooltip:', error);
            return `Nie znaleziono opisu dla kodu: ${code}`;
        }
    },

    /**
     * Show error modal
     */
    showError(message) {
        const modal = new bootstrap.Modal(document.getElementById('errorModal'));
        const modalBody = document.getElementById('errorModalBody');

        modalBody.textContent = message;
        modal.show();
    },

    /**
     * Get CSRF token from cookies
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
