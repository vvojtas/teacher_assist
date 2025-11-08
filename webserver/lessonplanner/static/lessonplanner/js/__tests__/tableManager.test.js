/**
 * Tests for TableManager module
 */

// Mock DOM setup
document.body.innerHTML = `
  <table id="planTable">
    <tbody id="planTableBody"></tbody>
  </table>
  <input id="themeInput" type="text" />
  <template id="rowTemplate">
    <tr class="plan-row" data-row-id="">
      <td contenteditable="true" class="cell-module" data-field="module"></td>
      <td contenteditable="true" class="cell-curriculum" data-field="curriculum"></td>
      <td contenteditable="true" class="cell-objectives" data-field="objectives"></td>
      <td class="cell-activity-container">
        <div contenteditable="true" class="cell-activity" data-field="activity"></div>
        <div class="activity-buttons mt-2">
          <button class="btn btn-sm btn-primary generate-btn"></button>
          <button class="btn btn-sm btn-secondary regenerate-btn" style="display: none;"></button>
          <input type="checkbox" class="form-check-input row-checkbox me-2">
          <button class="btn btn-sm btn-danger delete-btn"></button>
        </div>
      </td>
    </tr>
  </template>
`;

// Mock ModalHelper
global.ModalHelper = {
  showConfirm: jest.fn(),
  showAlert: jest.fn(),
  showError: jest.fn(),
};

// Load TableManager
const TableManager = require('../tableManager.js').TableManager || eval(
  require('fs').readFileSync(
    __dirname + '/../tableManager.js',
    'utf8'
  ) + '; TableManager'
);

describe('TableManager', () => {
  beforeEach(() => {
    // Reset state
    document.getElementById('planTableBody').innerHTML = '';
    document.getElementById('themeInput').value = '';
    TableManager.rows.clear();
    TableManager.nextRowId = 1;
    jest.clearAllMocks();
  });

  describe('addRows', () => {
    test('should add specified number of rows to table', () => {
      TableManager.addRows(3);

      const tbody = document.getElementById('planTableBody');
      const rows = tbody.querySelectorAll('tr.plan-row');

      expect(rows.length).toBe(3);
      expect(TableManager.rows.size).toBe(3);
    });

    test('should assign unique row IDs', () => {
      TableManager.addRows(3);

      const rows = Array.from(TableManager.rows.keys());
      expect(rows).toEqual(['row_1', 'row_2', 'row_3']);
    });

    test('should initialize row state with empty values', () => {
      TableManager.addRows(1);

      const state = TableManager.rows.get('row_1');
      expect(state).toEqual({
        module: '',
        curriculum: '',
        objectives: '',
        activity: '',
        aiGenerated: false,
        userEdited: false,
      });
    });
  });

  describe('deleteRow', () => {
    beforeEach(() => {
      TableManager.addRows(3);
    });

    test('should remove row from DOM', () => {
      TableManager.deleteRow('row_2');

      const tbody = document.getElementById('planTableBody');
      const rows = tbody.querySelectorAll('tr.plan-row');

      expect(rows.length).toBe(2);
      expect(document.querySelector('[data-row-id="row_2"]')).toBeNull();
    });

    test('should remove row from state map', () => {
      TableManager.deleteRow('row_2');

      expect(TableManager.rows.has('row_2')).toBe(false);
      expect(TableManager.rows.size).toBe(2);
    });

    test('should handle non-existent row gracefully', () => {
      expect(() => TableManager.deleteRow('row_999')).not.toThrow();
    });
  });

  describe('getRowData', () => {
    beforeEach(() => {
      TableManager.addRows(1);
      const row = document.querySelector('[data-row-id="row_1"]');
      row.querySelector('.cell-module').textContent = 'Test Module';
      row.querySelector('.cell-curriculum').textContent = 'I.1.2';
      row.querySelector('.cell-objectives').textContent = 'Test Objective';
      row.querySelector('.cell-activity').textContent = 'Test Activity';
    });

    test('should return row data with all fields', () => {
      const data = TableManager.getRowData('row_1');

      expect(data).toEqual({
        id: 'row_1',
        module: 'Test Module',
        curriculum: 'I.1.2',
        objectives: 'Test Objective',
        activity: 'Test Activity',
        aiGenerated: false,
        userEdited: false,
      });
    });

    test('should return null for non-existent row', () => {
      const data = TableManager.getRowData('row_999');
      expect(data).toBeNull();
    });

    test('should trim whitespace from cell values', () => {
      const row = document.querySelector('[data-row-id="row_1"]');
      row.querySelector('.cell-module').textContent = '  Spaced  ';

      const data = TableManager.getRowData('row_1');
      expect(data.module).toBe('Spaced');
    });
  });

  describe('setRowData', () => {
    beforeEach(() => {
      TableManager.addRows(1);
    });

    test('should update row content', () => {
      TableManager.setRowData('row_1', {
        module: 'New Module',
        curriculum: 'II.3.1',
        objectives: 'New Objective',
        activity: 'New Activity',
      });

      const row = document.querySelector('[data-row-id="row_1"]');
      expect(row.querySelector('.cell-module').textContent).toBe('New Module');
      expect(row.querySelector('.cell-curriculum').textContent).toBe('II.3.1');
      expect(row.querySelector('.cell-objectives').textContent).toBe('New Objective');
      expect(row.querySelector('.cell-activity').textContent).toBe('New Activity');
    });

    test('should handle array of curriculum refs', () => {
      TableManager.setRowData('row_1', {
        curriculum: ['I.1.1', 'I.1.2', 'II.2.3'],
      });

      const row = document.querySelector('[data-row-id="row_1"]');
      expect(row.querySelector('.cell-curriculum').textContent).toBe('I.1.1, I.1.2, II.2.3');
    });

    test('should handle array of objectives with newlines', () => {
      TableManager.setRowData('row_1', {
        objectives: ['Objective 1', 'Objective 2', 'Objective 3'],
      });

      const row = document.querySelector('[data-row-id="row_1"]');
      expect(row.querySelector('.cell-objectives').textContent).toBe('Objective 1\nObjective 2\nObjective 3');
    });

    test('should update aiGenerated state', () => {
      TableManager.setRowData('row_1', {
        aiGenerated: true,
      });

      const state = TableManager.rows.get('row_1');
      expect(state.aiGenerated).toBe(true);
    });

    test('should update userEdited state', () => {
      TableManager.setRowData('row_1', {
        userEdited: true,
      });

      const state = TableManager.rows.get('row_1');
      expect(state.userEdited).toBe(true);
    });
  });

  describe('setRowLoading', () => {
    beforeEach(() => {
      TableManager.addRows(1);
    });

    test('should add loading class when enabled', () => {
      TableManager.setRowLoading('row_1', true);

      const row = document.querySelector('[data-row-id="row_1"]');
      expect(row.classList.contains('loading')).toBe(true);
    });

    test('should remove loading class when disabled', () => {
      const row = document.querySelector('[data-row-id="row_1"]');
      row.classList.add('loading');

      TableManager.setRowLoading('row_1', false);

      expect(row.classList.contains('loading')).toBe(false);
    });

    test('should disable buttons when loading', () => {
      TableManager.setRowLoading('row_1', true);

      const row = document.querySelector('[data-row-id="row_1"]');
      const buttons = row.querySelectorAll('button');

      buttons.forEach(button => {
        expect(button.disabled).toBe(true);
      });
    });

    test('should enable buttons when not loading', () => {
      TableManager.setRowLoading('row_1', false);

      const row = document.querySelector('[data-row-id="row_1"]');
      const buttons = row.querySelectorAll('button');

      buttons.forEach(button => {
        expect(button.disabled).toBe(false);
      });
    });
  });

  describe('getRowsWithActivities', () => {
    beforeEach(() => {
      TableManager.addRows(3);

      // Set activities for first two rows
      const row1 = document.querySelector('[data-row-id="row_1"]');
      row1.querySelector('.cell-activity').textContent = 'Activity 1';

      const row2 = document.querySelector('[data-row-id="row_2"]');
      row2.querySelector('.cell-activity').textContent = 'Activity 2';

      // Leave row 3 empty
    });

    test('should return only rows with activities', () => {
      const rows = TableManager.getRowsWithActivities();

      expect(rows.length).toBe(2);
      expect(rows[0].activity).toBe('Activity 1');
      expect(rows[1].activity).toBe('Activity 2');
    });

    test('should not include rows with empty activities', () => {
      const rows = TableManager.getRowsWithActivities();

      const row3 = rows.find(r => r.id === 'row_3');
      expect(row3).toBeUndefined();
    });
  });

  describe('getRowsNeedingGeneration', () => {
    beforeEach(() => {
      TableManager.addRows(4);

      // Row 1: has activity, no AI data (should be included)
      const row1 = document.querySelector('[data-row-id="row_1"]');
      row1.querySelector('.cell-activity').textContent = 'Activity 1';

      // Row 2: has activity and AI data (should be excluded)
      const row2 = document.querySelector('[data-row-id="row_2"]');
      row2.querySelector('.cell-activity').textContent = 'Activity 2';
      row2.querySelector('.cell-module').textContent = 'Module 2';
      TableManager.rows.get('row_2').aiGenerated = true;

      // Row 3: has activity and user data (should be excluded)
      const row3 = document.querySelector('[data-row-id="row_3"]');
      row3.querySelector('.cell-activity').textContent = 'Activity 3';
      row3.querySelector('.cell-module').textContent = 'Module 3';

      // Row 4: no activity (should be excluded)
    });

    test('should return only rows needing generation', () => {
      const rows = TableManager.getRowsNeedingGeneration();

      expect(rows.length).toBe(1);
      expect(rows[0].id).toBe('row_1');
    });

    test('should exclude rows with AI-generated data', () => {
      const rows = TableManager.getRowsNeedingGeneration();

      const row2 = rows.find(r => r.id === 'row_2');
      expect(row2).toBeUndefined();
    });

    test('should exclude rows without activities', () => {
      const rows = TableManager.getRowsNeedingGeneration();

      const row4 = rows.find(r => r.id === 'row_4');
      expect(row4).toBeUndefined();
    });
  });

  describe('updateRowButtons', () => {
    beforeEach(() => {
      TableManager.addRows(1);
    });

    test('should show regenerate button for AI-generated rows', () => {
      TableManager.rows.get('row_1').aiGenerated = true;
      TableManager.updateRowButtons('row_1');

      const row = document.querySelector('[data-row-id="row_1"]');
      const generateBtn = row.querySelector('.generate-btn');
      const regenerateBtn = row.querySelector('.regenerate-btn');

      expect(generateBtn.style.display).toBe('none');
      expect(regenerateBtn.style.display).toBe('inline-block');
    });

    test('should show generate button for non-AI-generated rows', () => {
      TableManager.rows.get('row_1').aiGenerated = false;
      TableManager.updateRowButtons('row_1');

      const row = document.querySelector('[data-row-id="row_1"]');
      const generateBtn = row.querySelector('.generate-btn');
      const regenerateBtn = row.querySelector('.regenerate-btn');

      expect(generateBtn.style.display).toBe('inline-block');
      expect(regenerateBtn.style.display).toBe('none');
    });
  });
});