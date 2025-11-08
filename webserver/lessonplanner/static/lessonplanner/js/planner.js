/**
 * Main Planner Application
 * Coordinates between TableManager and AIService
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize table with 5 empty rows
    TableManager.init();

    // Attach button event listeners
    attachMainButtonListeners();

    // Attach tooltip functionality
    attachTooltipListeners();

    // Attach checkbox change listeners
    attachCheckboxListeners();

    // Listen for generate metadata events from TableManager
    document.addEventListener('generateMetadata', handleGenerateMetadata);
});

/**
 * Attach event listeners to main action buttons
 */
function attachMainButtonListeners() {
    // Add Row button
    document.getElementById('addRowBtn').addEventListener('click', () => {
        TableManager.addRows(1);
    });

    // Clear All button
    document.getElementById('clearAllBtn').addEventListener('click', () => {
        TableManager.clearAll();
    });

    // Bulk Generate button - only generates for new rows without AI data or user input
    document.getElementById('bulkGenerateBtn').addEventListener('click', async () => {
        const theme = document.getElementById('themeInput').value.trim();
        const rows = TableManager.getRowsNeedingGeneration();

        if (rows.length === 0) {
            await ModalHelper.showAlert('Brak nowych aktywności do przetworzenia. Wszystkie wiersze są już wypełnione lub puste.');
            return;
        }

        try {
            await AIService.generateBulk(rows, theme);
        } catch (error) {
            console.error('Bulk generation failed:', error);
        }
    });

    // Copy Table button
    document.getElementById('copyTableBtn').addEventListener('click', async () => {
        await copyTableToClipboard();
    });
}

/**
 * Attach checkbox change listeners to update copy button label
 */
function attachCheckboxListeners() {
    const tbody = document.getElementById('planTableBody');

    // Event delegation for checkbox changes
    tbody.addEventListener('change', (e) => {
        if (e.target.classList.contains('row-checkbox')) {
            updateCopyButtonLabel();
        }
    });

    // Also update when rows are added/removed
    const observer = new MutationObserver(() => {
        updateCopyButtonLabel();
    });

    observer.observe(tbody, { childList: true, subtree: true });
}

/**
 * Update copy button label based on checkbox selection
 */
function updateCopyButtonLabel() {
    const tbody = document.getElementById('planTableBody');
    const copyBtn = document.getElementById('copyTableBtn');
    const allRows = tbody.querySelectorAll('tr.plan-row');

    const selectedCount = Array.from(allRows).filter(row => {
        const checkbox = row.querySelector('.row-checkbox');
        return checkbox && checkbox.checked;
    }).length;

    if (selectedCount > 0) {
        copyBtn.innerHTML = `<i class="bi bi-clipboard"></i> Skopiuj zaznaczone (${selectedCount})`;
    } else {
        copyBtn.innerHTML = `<i class="bi bi-clipboard"></i> Skopiuj tabelę`;
    }
}

/**
 * Copy table data to clipboard
 * Copies all rows if none are selected, or only selected rows
 * Format: HTML table for Google Docs compatibility
 */
async function copyTableToClipboard() {
    const tbody = document.getElementById('planTableBody');
    const allRows = tbody.querySelectorAll('tr.plan-row');

    // Find selected rows (rows with checked checkboxes)
    const selectedRows = Array.from(allRows).filter(row => {
        const checkbox = row.querySelector('.row-checkbox');
        return checkbox && checkbox.checked;
    });

    // Determine which rows to copy
    const rowsToCopy = selectedRows.length > 0 ? selectedRows : Array.from(allRows);
    const includeHeaders = selectedRows.length === 0; // Include headers only for full table

    if (rowsToCopy.length === 0) {
        await ModalHelper.showAlert('Brak wierszy do skopiowania.');
        return;
    }

    // Build HTML table
    let htmlTable = '<table border="1" style="border-collapse: collapse;">';

    // Add headers if copying whole table
    if (includeHeaders) {
        htmlTable += '<thead><tr>';
        htmlTable += '<th style="padding: 8px; border: 1px solid #000;">Moduł</th>';
        htmlTable += '<th style="padding: 8px; border: 1px solid #000;">Podstawa Programowa</th>';
        htmlTable += '<th style="padding: 8px; border: 1px solid #000;">Cele</th>';
        htmlTable += '<th style="padding: 8px; border: 1px solid #000;">Aktywność</th>';
        htmlTable += '</tr></thead>';
    }

    // Add data rows
    htmlTable += '<tbody>';
    rowsToCopy.forEach(row => {
        const module = row.querySelector('.cell-module').textContent.trim();
        const curriculum = row.querySelector('.cell-curriculum').textContent.trim();
        const objectives = row.querySelector('.cell-objectives').textContent.trim();
        const activity = row.querySelector('.cell-activity').textContent.trim();

        htmlTable += '<tr>';
        htmlTable += `<td style="padding: 8px; border: 1px solid #000; vertical-align: top;">${escapeHtml(module)}</td>`;
        htmlTable += `<td style="padding: 8px; border: 1px solid #000; vertical-align: top;">${escapeHtml(curriculum)}</td>`;
        htmlTable += `<td style="padding: 8px; border: 1px solid #000; vertical-align: top; white-space: pre-wrap;">${escapeHtml(objectives)}</td>`;
        htmlTable += `<td style="padding: 8px; border: 1px solid #000; vertical-align: top;">${escapeHtml(activity)}</td>`;
        htmlTable += '</tr>';
    });
    htmlTable += '</tbody></table>';

    // Build plain text version (TSV format)
    let plainText = '';
    if (includeHeaders) {
        plainText = 'Moduł\tPodstawa Programowa\tCele\tAktywność\n';
    }
    rowsToCopy.forEach(row => {
        const module = row.querySelector('.cell-module').textContent.trim();
        const curriculum = row.querySelector('.cell-curriculum').textContent.trim();
        const objectives = row.querySelector('.cell-objectives').textContent.trim();
        const activity = row.querySelector('.cell-activity').textContent.trim();
        plainText += `${module}\t${curriculum}\t${objectives}\t${activity}\n`;
    });

    // Copy to clipboard using Clipboard API with both HTML and plain text
    try {
        const htmlBlob = new Blob([htmlTable], { type: 'text/html' });
        const textBlob = new Blob([plainText], { type: 'text/plain' });

        const clipboardItem = new ClipboardItem({
            'text/html': htmlBlob,
            'text/plain': textBlob
        });

        await navigator.clipboard.write([clipboardItem]);

        // Show success message
        const rowCount = rowsToCopy.length;
        const message = selectedRows.length > 0
            ? `Skopiowano ${rowCount} zaznaczonych wierszy do schowka.`
            : `Skopiowano całą tabelę (${rowCount} wierszy) do schowka.`;

        await ModalHelper.showAlert(message);

        // Uncheck all checkboxes after successful copy
        if (selectedRows.length > 0) {
            selectedRows.forEach(row => {
                const checkbox = row.querySelector('.row-checkbox');
                if (checkbox) checkbox.checked = false;
            });
            updateCopyButtonLabel();
        }
    } catch (error) {
        console.error('Failed to copy to clipboard:', error);
        await ModalHelper.showError('Nie udało się skopiować do schowka. Spróbuj ponownie.');
    }
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Handle generate metadata event from TableManager
 */
async function handleGenerateMetadata(event) {
    const { rowId, activity } = event.detail;
    const theme = document.getElementById('themeInput').value.trim();

    try {
        await AIService.generateSingle(rowId, activity, theme);
    } catch (error) {
        console.error('Single generation failed:', error);
    }
}

/**
 * Attach tooltip functionality to curriculum reference codes
 */
function attachTooltipListeners() {
    const tbody = document.getElementById('planTableBody');
    const tooltip = document.getElementById('curriculumTooltip');
    const tooltipContent = tooltip.querySelector('.tooltip-content');

    let tooltipTimeout = null;
    let currentHoveredElement = null;

    // Event delegation for hover on curriculum cells
    tbody.addEventListener('mouseover', async (e) => {
        // Check if hovering over curriculum cell
        if (e.target.classList.contains('cell-curriculum') ||
            e.target.closest('.cell-curriculum')) {

            const cell = e.target.classList.contains('cell-curriculum')
                ? e.target
                : e.target.closest('.cell-curriculum');

            // Get text content
            const text = cell.textContent.trim();

            // Find curriculum codes (pattern: digits.digits or Roman.digits.digits)
            const codePattern = /[IVX]+\.\d+\.\d+|\d+\.\d+/g;
            const codes = text.match(codePattern);

            if (codes && codes.length > 0) {
                currentHoveredElement = cell;

                // Delay showing tooltip by 300ms
                clearTimeout(tooltipTimeout);
                tooltipTimeout = setTimeout(async () => {
                    if (currentHoveredElement === cell) {
                        // Fetch tooltip text for all codes
                        const tooltipTexts = await Promise.all(
                            codes.map(code => AIService.getCurriculumTooltip(code))
                        );

                        // Build tooltip content
                        let content = '';
                        codes.forEach((code, index) => {
                            content += `<strong>${code}:</strong> ${tooltipTexts[index]}`;
                            if (index < codes.length - 1) {
                                content += '<br><br>';
                            }
                        });

                        tooltipContent.innerHTML = content;

                        // Position tooltip
                        positionTooltip(tooltip, cell);

                        // Show tooltip
                        tooltip.style.display = 'block';
                    }
                }, 300);
            }
        }
    });

    // Hide tooltip on mouse leave
    tbody.addEventListener('mouseout', (e) => {
        if (e.target.classList.contains('cell-curriculum') ||
            e.target.closest('.cell-curriculum')) {

            clearTimeout(tooltipTimeout);
            currentHoveredElement = null;
            tooltip.style.display = 'none';
        }
    });

    // Also hide tooltip when hovering over tooltip itself (optional)
    tooltip.addEventListener('mouseenter', () => {
        // Keep tooltip visible when hovering over it
    });

    tooltip.addEventListener('mouseleave', () => {
        tooltip.style.display = 'none';
    });
}

/**
 * Position tooltip above or below the target element
 */
function positionTooltip(tooltip, targetElement) {
    const rect = targetElement.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();

    // Calculate position
    let top, left;

    // Try to position above first
    if (rect.top - tooltipRect.height - 10 > 0) {
        // Position above
        top = rect.top + window.scrollY - tooltipRect.height - 10;
    } else {
        // Position below
        top = rect.bottom + window.scrollY + 10;
    }

    // Center horizontally relative to target
    left = rect.left + window.scrollX + (rect.width / 2) - (tooltipRect.width / 2);

    // Ensure tooltip stays within viewport
    if (left < 10) {
        left = 10;
    } else if (left + tooltipRect.width > window.innerWidth - 10) {
        left = window.innerWidth - tooltipRect.width - 10;
    }

    tooltip.style.top = top + 'px';
    tooltip.style.left = left + 'px';
}

/**
 * Utility: Format objectives array for display
 */
function formatObjectives(objectives) {
    if (Array.isArray(objectives)) {
        return objectives.join('\n');
    }
    return objectives;
}

/**
 * Utility: Parse curriculum refs from string
 */
function parseCurriculumRefs(text) {
    const codePattern = /[IVX]+\.\d+\.\d+|\d+\.\d+/g;
    return text.match(codePattern) || [];
}

// Expose utilities globally if needed
window.LessonPlanner = {
    TableManager,
    AIService,
    formatObjectives,
    parseCurriculumRefs
};
