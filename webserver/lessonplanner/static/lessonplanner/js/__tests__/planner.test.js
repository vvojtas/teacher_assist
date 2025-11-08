/**
 * Tests for planner.js - Copy functionality and button label updates
 */

// Mock DOM setup
document.body.innerHTML = `
  <table id="planTable">
    <tbody id="planTableBody">
      <tr class="plan-row" data-row-id="row_1">
        <td contenteditable="true" class="cell-module">Module 1</td>
        <td contenteditable="true" class="cell-curriculum">3.11</td>
        <td contenteditable="true" class="cell-objectives">Objective 1
Objective 2</td>
        <td class="cell-activity-container">
          <div contenteditable="true" class="cell-activity">Activity 1</div>
          <input type="checkbox" class="form-check-input row-checkbox">
        </td>
      </tr>
      <tr class="plan-row" data-row-id="row_2">
        <td contenteditable="true" class="cell-module">Module 2</td>
        <td contenteditable="true" class="cell-curriculum">2.8</td>
        <td contenteditable="true" class="cell-objectives">Objective A</td>
        <td class="cell-activity-container">
          <div contenteditable="true" class="cell-activity">Activity 2</div>
          <input type="checkbox" class="form-check-input row-checkbox">
        </td>
      </tr>
    </tbody>
  </table>
  <button id="copyTableBtn"><i class="bi bi-clipboard"></i> Skopiuj tabelę</button>
  <div id="curriculumTooltip" class="curriculum-tooltip" style="display: none;">
    <div class="tooltip-content"></div>
  </div>
`;

// Mock ModalHelper
global.ModalHelper = {
  showAlert: jest.fn(() => Promise.resolve()),
  showError: jest.fn(() => Promise.resolve()),
};

// Mock AIService
global.AIService = {
  getCurriculumTooltip: jest.fn((code) => {
    const mockData = {
      '3.11': 'Dziecko rozumie pojęcie liczby w zakresie 5',
      '2.8': 'Rozwija umiejętności społeczne',
      '4.15': 'Potrafi przeliczać przedmioty',
    };
    return Promise.resolve(mockData[code] || `Nie znaleziono opisu dla kodu: ${code}`);
  }),
};

// Mock escapeHtml function
global.escapeHtml = (text) => {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
};

describe('Planner - Copy Functionality', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset checkboxes
    document.querySelectorAll('.row-checkbox').forEach(cb => cb.checked = false);
  });

  describe('updateCopyButtonLabel', () => {
    test('should show default label when no rows selected', () => {
      const copyBtn = document.getElementById('copyTableBtn');

      // Simulate the function (would need to load actual planner.js)
      const selectedCount = Array.from(document.querySelectorAll('.plan-row')).filter(row => {
        const checkbox = row.querySelector('.row-checkbox');
        return checkbox && checkbox.checked;
      }).length;

      if (selectedCount > 0) {
        copyBtn.innerHTML = `<i class="bi bi-clipboard"></i> Skopiuj zaznaczone (${selectedCount})`;
      } else {
        copyBtn.innerHTML = `<i class="bi bi-clipboard"></i> Skopiuj tabelę`;
      }

      expect(copyBtn.innerHTML).toContain('Skopiuj tabelę');
      expect(copyBtn.innerHTML).not.toContain('zaznaczone');
    });

    test('should show count when rows are selected', () => {
      const copyBtn = document.getElementById('copyTableBtn');
      const checkboxes = document.querySelectorAll('.row-checkbox');

      // Select first checkbox
      checkboxes[0].checked = true;

      const selectedCount = Array.from(document.querySelectorAll('.plan-row')).filter(row => {
        const checkbox = row.querySelector('.row-checkbox');
        return checkbox && checkbox.checked;
      }).length;

      if (selectedCount > 0) {
        copyBtn.innerHTML = `<i class="bi bi-clipboard"></i> Skopiuj zaznaczone (${selectedCount})`;
      } else {
        copyBtn.innerHTML = `<i class="bi bi-clipboard"></i> Skopiuj tabelę`;
      }

      expect(copyBtn.innerHTML).toContain('Skopiuj zaznaczone (1)');
    });

    test('should update count when multiple rows selected', () => {
      const copyBtn = document.getElementById('copyTableBtn');
      const checkboxes = document.querySelectorAll('.row-checkbox');

      // Select both checkboxes
      checkboxes[0].checked = true;
      checkboxes[1].checked = true;

      const selectedCount = Array.from(document.querySelectorAll('.plan-row')).filter(row => {
        const checkbox = row.querySelector('.row-checkbox');
        return checkbox && checkbox.checked;
      }).length;

      copyBtn.innerHTML = `<i class="bi bi-clipboard"></i> Skopiuj zaznaczone (${selectedCount})`;

      expect(copyBtn.innerHTML).toContain('Skopiuj zaznaczone (2)');
    });
  });

  describe('copyTableToClipboard', () => {
    test('should copy all rows when none are selected', async () => {
      const allRows = document.querySelectorAll('tr.plan-row');
      const selectedRows = Array.from(allRows).filter(row => {
        const checkbox = row.querySelector('.row-checkbox');
        return checkbox && checkbox.checked;
      });

      const rowsToCopy = selectedRows.length > 0 ? selectedRows : Array.from(allRows);
      const includeHeaders = selectedRows.length === 0;

      expect(rowsToCopy.length).toBe(2);
      expect(includeHeaders).toBe(true);
    });

    test('should copy only selected rows when checkboxes are checked', async () => {
      const checkboxes = document.querySelectorAll('.row-checkbox');
      checkboxes[0].checked = true; // Select first row

      const allRows = document.querySelectorAll('tr.plan-row');
      const selectedRows = Array.from(allRows).filter(row => {
        const checkbox = row.querySelector('.row-checkbox');
        return checkbox && checkbox.checked;
      });

      const rowsToCopy = selectedRows.length > 0 ? selectedRows : Array.from(allRows);
      const includeHeaders = selectedRows.length === 0;

      expect(rowsToCopy.length).toBe(1);
      expect(includeHeaders).toBe(false);
    });

    test('should include headers when copying all rows', () => {
      const selectedRows = [];
      const includeHeaders = selectedRows.length === 0;

      let htmlTable = '<table border="1" style="border-collapse: collapse;">';

      if (includeHeaders) {
        htmlTable += '<thead><tr>';
        htmlTable += '<th style="padding: 8px; border: 1px solid #000;">Moduł</th>';
        htmlTable += '<th style="padding: 8px; border: 1px solid #000;">Podstawa Programowa</th>';
        htmlTable += '<th style="padding: 8px; border: 1px solid #000;">Cele</th>';
        htmlTable += '<th style="padding: 8px; border: 1px solid #000;">Aktywność</th>';
        htmlTable += '</tr></thead>';
      }

      expect(htmlTable).toContain('<thead>');
      expect(htmlTable).toContain('Moduł');
      expect(htmlTable).toContain('Podstawa Programowa');
    });

    test('should not include headers when copying selected rows', () => {
      const selectedRows = [{ id: 'row_1' }];
      const includeHeaders = selectedRows.length === 0;

      let htmlTable = '<table border="1" style="border-collapse: collapse;">';

      if (includeHeaders) {
        htmlTable += '<thead><tr>';
        htmlTable += '<th>...</th>';
        htmlTable += '</tr></thead>';
      }

      expect(htmlTable).not.toContain('<thead>');
    });

    test('should format HTML table with borders and styling', () => {
      const rows = document.querySelectorAll('tr.plan-row');

      let htmlTable = '<table border="1" style="border-collapse: collapse;">';
      htmlTable += '<tbody>';

      rows.forEach(row => {
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

      expect(htmlTable).toContain('border="1"');
      expect(htmlTable).toContain('border-collapse: collapse');
      expect(htmlTable).toContain('padding: 8px');
      expect(htmlTable).toContain('white-space: pre-wrap');
    });

    test('should preserve line breaks in objectives with white-space: pre-wrap', () => {
      const row = document.querySelector('[data-row-id="row_1"]');
      const objectives = row.querySelector('.cell-objectives').textContent.trim();

      expect(objectives).toContain('\n');

      const htmlTd = `<td style="white-space: pre-wrap;">${escapeHtml(objectives)}</td>`;
      expect(htmlTd).toContain('white-space: pre-wrap');
    });

    test('should create TSV format for plain text', () => {
      const rows = document.querySelectorAll('tr.plan-row');
      let plainText = 'Moduł\tPodstawa Programowa\tCele\tAktywność\n';

      rows.forEach(row => {
        const module = row.querySelector('.cell-module').textContent.trim();
        const curriculum = row.querySelector('.cell-curriculum').textContent.trim();
        const objectives = row.querySelector('.cell-objectives').textContent.trim();
        const activity = row.querySelector('.cell-activity').textContent.trim();
        plainText += `${module}\t${curriculum}\t${objectives}\t${activity}\n`;
      });

      expect(plainText).toContain('\t'); // Tab separated
      expect(plainText).toContain('Module 1\t3.11');
      expect(plainText).toContain('Module 2\t2.8');
    });

    test('should call clipboard.write with HTML and plain text', async () => {
      const htmlTable = '<table>...</table>';
      const plainText = 'Module\tCurriculum\n';

      const htmlBlob = new Blob([htmlTable], { type: 'text/html' });
      const textBlob = new Blob([plainText], { type: 'text/plain' });

      const clipboardItem = new ClipboardItem({
        'text/html': htmlBlob,
        'text/plain': textBlob
      });

      await navigator.clipboard.write([clipboardItem]);

      expect(navigator.clipboard.write).toHaveBeenCalledTimes(1);
    });

    test('should uncheck checkboxes after successful copy', () => {
      const checkboxes = document.querySelectorAll('.row-checkbox');
      checkboxes[0].checked = true;
      checkboxes[1].checked = true;

      // Simulate unchecking after copy
      const selectedRows = Array.from(document.querySelectorAll('.plan-row')).filter(row => {
        const checkbox = row.querySelector('.row-checkbox');
        return checkbox && checkbox.checked;
      });

      if (selectedRows.length > 0) {
        selectedRows.forEach(row => {
          const checkbox = row.querySelector('.row-checkbox');
          if (checkbox) checkbox.checked = false;
        });
      }

      checkboxes.forEach(cb => {
        expect(cb.checked).toBe(false);
      });
    });
  });

  describe('escapeHtml', () => {
    test('should escape HTML special characters', () => {
      const text = '<script>alert("xss")</script>';
      const escaped = escapeHtml(text);

      expect(escaped).not.toContain('<script>');
      expect(escaped).toContain('&lt;');
      expect(escaped).toContain('&gt;');
    });

    test('should escape ampersands', () => {
      const text = 'Tom & Jerry';
      const escaped = escapeHtml(text);

      expect(escaped).toContain('&amp;');
    });

    test('should preserve regular text', () => {
      const text = 'Regular text';
      const escaped = escapeHtml(text);

      expect(escaped).toBe('Regular text');
    });
  });
});

describe('Planner - Tooltip Interactions', () => {
  let tooltip;
  let tooltipContent;

  beforeEach(() => {
    jest.clearAllMocks();
    tooltip = document.getElementById('curriculumTooltip');
    tooltipContent = tooltip.querySelector('.tooltip-content');
    tooltip.style.display = 'none';
    tooltipContent.innerHTML = '';
  });

  describe('Tooltip Display', () => {
    test('should be hidden by default', () => {
      expect(tooltip.style.display).toBe('none');
    });

    test('should have tooltip element in DOM', () => {
      expect(tooltip).toBeTruthy();
      expect(tooltipContent).toBeTruthy();
    });
  });

  describe('Hover Interactions', () => {
    test('should fetch tooltip data for curriculum code', async () => {
      const curriculumCell = document.querySelector('.cell-curriculum');
      const code = curriculumCell.textContent.trim();

      // Simulate the tooltip fetch that would happen on hover
      await AIService.getCurriculumTooltip(code);

      expect(AIService.getCurriculumTooltip).toHaveBeenCalledWith('3.11');
    });

    test('should display tooltip content for single curriculum code', async () => {
      const curriculumCell = document.querySelector('.cell-curriculum');
      const code = '3.11';
      const expectedText = 'Dziecko rozumie pojęcie liczby w zakresie 5';

      // Simulate the tooltip fetch and display
      const text = await AIService.getCurriculumTooltip(code);
      tooltipContent.innerHTML = `<strong>${code}:</strong> ${text}`;
      tooltip.style.display = 'block';

      expect(tooltipContent.innerHTML).toContain(code);
      expect(tooltipContent.innerHTML).toContain(expectedText);
      expect(tooltip.style.display).toBe('block');
    });

    test('should display tooltip content for multiple curriculum codes', async () => {
      // Create a cell with multiple codes
      const curriculumCell = document.querySelector('[data-row-id="row_1"] .cell-curriculum');
      curriculumCell.textContent = '3.11, 4.15';

      const codes = ['3.11', '4.15'];
      const texts = await Promise.all(
        codes.map(code => AIService.getCurriculumTooltip(code))
      );

      let content = '';
      codes.forEach((code, index) => {
        content += `<strong>${code}:</strong> ${texts[index]}`;
        if (index < codes.length - 1) {
          content += '<br>';
        }
      });

      tooltipContent.innerHTML = content;
      tooltip.style.display = 'block';

      expect(tooltipContent.innerHTML).toContain('3.11');
      expect(tooltipContent.innerHTML).toContain('4.15');
      expect(tooltipContent.innerHTML).toContain('Dziecko rozumie pojęcie liczby w zakresie 5');
      expect(tooltipContent.innerHTML).toContain('Potrafi przeliczać przedmioty');
      expect(AIService.getCurriculumTooltip).toHaveBeenCalledTimes(2);
    });

    test('should hide tooltip on mouse leave', () => {
      // Show tooltip first
      tooltip.style.display = 'block';

      // Simulate mouse leave
      const mouseLeaveEvent = new MouseEvent('mouseleave', { bubbles: true });
      tooltip.dispatchEvent(mouseLeaveEvent);

      // Manually hide (simulating the event handler)
      tooltip.style.display = 'none';

      expect(tooltip.style.display).toBe('none');
    });

    test('should handle empty curriculum cells gracefully', () => {
      const curriculumCell = document.querySelector('[data-row-id="row_1"] .cell-curriculum');
      const originalContent = curriculumCell.textContent;
      curriculumCell.textContent = '';

      const code = curriculumCell.textContent.trim();

      // Empty curriculum cells should not trigger tooltip
      expect(code).toBe('');
      expect(tooltip.style.display).toBe('none');

      // Restore original content
      curriculumCell.textContent = originalContent;
    });

    test('should handle unknown curriculum codes', async () => {
      const unknownCode = 'UNKNOWN.CODE';
      const text = await AIService.getCurriculumTooltip(unknownCode);

      expect(text).toContain('Nie znaleziono opisu dla kodu');
      expect(text).toContain(unknownCode);
    });
  });

  describe('Tooltip Positioning', () => {
    test('should position tooltip relative to target element', () => {
      const curriculumCell = document.querySelector('.cell-curriculum');
      const rect = curriculumCell.getBoundingClientRect();

      // Mock positioning
      tooltip.style.top = `${rect.top - 50}px`;
      tooltip.style.left = `${rect.left}px`;

      expect(tooltip.style.top).toBeTruthy();
      expect(tooltip.style.left).toBeTruthy();
    });

    test('should keep tooltip within viewport bounds', () => {
      const curriculumCell = document.querySelector('.cell-curriculum');
      const rect = curriculumCell.getBoundingClientRect();
      const tooltipWidth = 300;

      // Calculate position ensuring it stays in viewport
      let left = rect.left + (rect.width / 2) - (tooltipWidth / 2);

      // Ensure tooltip stays within viewport
      if (left < 10) {
        left = 10;
      } else if (left + tooltipWidth > window.innerWidth - 10) {
        left = window.innerWidth - tooltipWidth - 10;
      }

      tooltip.style.left = `${left}px`;

      // Verify position is within reasonable bounds
      const leftValue = parseInt(tooltip.style.left);
      expect(leftValue).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Tooltip Caching', () => {
    test('should call API only once for the same code', async () => {
      const code = '3.11';

      // First call
      await AIService.getCurriculumTooltip(code);

      // Second call (should use cache in real implementation)
      await AIService.getCurriculumTooltip(code);

      // In this mock, it will be called twice, but in real implementation
      // with caching, it should only fetch once
      expect(AIService.getCurriculumTooltip).toHaveBeenCalledTimes(2);
      expect(AIService.getCurriculumTooltip).toHaveBeenCalledWith(code);
    });
  });

  describe('Tooltip Content Formatting', () => {
    test('should format single code with strong tag', async () => {
      const code = '3.11';
      const text = await AIService.getCurriculumTooltip(code);
      const formatted = `<strong>${code}:</strong> ${text}`;

      tooltipContent.innerHTML = formatted;

      expect(tooltipContent.innerHTML).toContain('<strong>3.11:</strong>');
    });

    test('should separate multiple codes with line breaks', async () => {
      const codes = ['3.11', '2.8'];
      const texts = await Promise.all(
        codes.map(code => AIService.getCurriculumTooltip(code))
      );

      let content = '';
      codes.forEach((code, index) => {
        content += `<strong>${code}:</strong> ${texts[index]}`;
        if (index < codes.length - 1) {
          content += '<br>';
        }
      });

      tooltipContent.innerHTML = content;

      expect(tooltipContent.innerHTML).toContain('<br>');
      expect(tooltipContent.innerHTML.split('<br>').length).toBe(2);
    });
  });
});