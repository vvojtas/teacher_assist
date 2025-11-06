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
