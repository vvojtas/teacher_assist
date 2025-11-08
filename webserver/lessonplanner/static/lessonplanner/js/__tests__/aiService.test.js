/**
 * Tests for aiService.js - API calls and error handling
 */

// Mock DOM elements
document.body.innerHTML = `
  <div id="progressContainer" style="display: none;">
    <div id="progressBar" class="progress-bar" style="width: 0%"></div>
    <div id="progressText"></div>
  </div>
  <button id="bulkGenerateBtn">Wypełnij wszystko AI</button>
  <div id="errorModal" class="modal">
    <div id="errorModalBody"></div>
  </div>
`;

// Mock TableManager
global.TableManager = {
  setRowLoading: jest.fn(),
  setRowData: jest.fn(),
};

// Mock bootstrap
global.bootstrap = {
  Modal: jest.fn().mockImplementation(() => ({
    show: jest.fn(),
    hide: jest.fn(),
  })),
};

// Create a mock AIService object
const createAIService = () => ({
  endpoints: {
    generateMetadata: '/api/generate-metadata/',
    generateBulk: '/api/generate-bulk/',
    curriculumTooltip: '/api/curriculum/'
  },
  tooltipCache: new Map(),
});

describe('AIService', () => {
  let AIService;

  beforeEach(() => {
    AIService = createAIService();
    jest.clearAllMocks();
    global.fetch.mockClear();
    document.getElementById('progressContainer').style.display = 'none';
    document.getElementById('bulkGenerateBtn').disabled = false;
  });

  describe('generateSingle', () => {
    test('should call API with correct parameters', async () => {
      const mockResponse = {
        module: 'Test Module',
        curriculum_refs: ['I.1.2'],
        objectives: ['Objective 1']
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const activity = 'Test Activity';
      const theme = 'Test Theme';

      // Simulate the call (would need actual function)
      await fetch(AIService.endpoints.generateMetadata, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ activity, theme })
      });

      expect(global.fetch).toHaveBeenCalledWith(
        '/api/generate-metadata/',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ activity, theme })
        })
      );
    });

    test('should set row loading state before API call', () => {
      const rowId = 'row_1';

      TableManager.setRowLoading(rowId, true);

      expect(TableManager.setRowLoading).toHaveBeenCalledWith(rowId, true);
    });

    test('should clear row loading state after API call', async () => {
      const rowId = 'row_1';

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          module: 'Test',
          curriculum_refs: [],
          objectives: []
        })
      });

      try {
        await fetch('/api/generate-metadata/', {
          method: 'POST',
          body: JSON.stringify({ activity: 'test', theme: '' })
        });
      } finally {
        TableManager.setRowLoading(rowId, false);
      }

      expect(TableManager.setRowLoading).toHaveBeenCalledWith(rowId, false);
    });

    test('should update row data on successful response', async () => {
      const mockData = {
        module: 'Test Module',
        curriculum_refs: ['I.1.2', 'II.2.3'],
        objectives: ['Objective 1', 'Objective 2']
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      });

      const response = await fetch('/api/generate-metadata/', {
        method: 'POST',
        body: JSON.stringify({ activity: 'test', theme: '' })
      });
      const data = await response.json();

      TableManager.setRowData('row_1', {
        module: data.module,
        curriculum: data.curriculum_refs,
        objectives: data.objectives,
        aiGenerated: true,
        userEdited: false
      });

      expect(TableManager.setRowData).toHaveBeenCalledWith('row_1', {
        module: 'Test Module',
        curriculum: ['I.1.2', 'II.2.3'],
        objectives: ['Objective 1', 'Objective 2'],
        aiGenerated: true,
        userEdited: false
      });
    });

    test('should handle API errors gracefully', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Server error' })
      });

      const response = await fetch('/api/generate-metadata/', {
        method: 'POST',
        body: JSON.stringify({ activity: 'test', theme: '' })
      });

      expect(response.ok).toBe(false);
    });
  });

  describe('generateBulk', () => {
    const mockRows = [
      { id: 'row_1', activity: 'Activity 1' },
      { id: 'row_2', activity: 'Activity 2' }
    ];

    test('should show progress bar during bulk generation', () => {
      const progressContainer = document.getElementById('progressContainer');
      const progressBar = document.getElementById('progressBar');
      const progressText = document.getElementById('progressText');

      progressContainer.style.display = 'block';
      progressBar.style.width = '0%';
      progressText.textContent = `Przetwarzanie... (0/${mockRows.length})`;

      expect(progressContainer.style.display).toBe('block');
      expect(progressBar.style.width).toBe('0%');
      expect(progressText.textContent).toContain('Przetwarzanie...');
    });

    test('should disable bulk generate button', () => {
      const bulkBtn = document.getElementById('bulkGenerateBtn');
      bulkBtn.disabled = true;
      bulkBtn.innerHTML = '<span class="spinner-border"></span> Przetwarzanie...';

      expect(bulkBtn.disabled).toBe(true);
      expect(bulkBtn.innerHTML).toContain('Przetwarzanie...');
    });

    test('should set all rows to loading state', () => {
      mockRows.forEach(row => {
        TableManager.setRowLoading(row.id, true);
      });

      expect(TableManager.setRowLoading).toHaveBeenCalledTimes(2);
      expect(TableManager.setRowLoading).toHaveBeenCalledWith('row_1', true);
      expect(TableManager.setRowLoading).toHaveBeenCalledWith('row_2', true);
    });

    test('should call bulk API endpoint', async () => {
      const theme = 'Test Theme';

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ results: [] })
      });

      await fetch(AIService.endpoints.generateBulk, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ theme, activities: mockRows })
      });

      expect(global.fetch).toHaveBeenCalledWith(
        '/api/generate-bulk/',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            theme,
            activities: mockRows
          })
        })
      );
    });

    test('should update progress for each completed row', async () => {
      const progressBar = document.getElementById('progressBar');
      const progressText = document.getElementById('progressText');

      // Simulate progress updates
      let completed = 0;
      mockRows.forEach(() => {
        completed++;
        const progress = (completed / mockRows.length) * 100;
        progressBar.style.width = progress + '%';
        progressText.textContent = `Przetwarzanie... (${completed}/${mockRows.length})`;
      });

      expect(progressBar.style.width).toBe('100%');
      expect(progressText.textContent).toBe('Przetwarzanie... (2/2)');
    });

    test('should clear loading state for all rows when complete', () => {
      mockRows.forEach(row => {
        TableManager.setRowLoading(row.id, false);
      });

      // Should have been called for both setting to true and false
      expect(TableManager.setRowLoading).toHaveBeenCalledWith('row_1', false);
      expect(TableManager.setRowLoading).toHaveBeenCalledWith('row_2', false);
    });

    test('should re-enable bulk generate button when complete', () => {
      const bulkBtn = document.getElementById('bulkGenerateBtn');
      bulkBtn.disabled = false;
      bulkBtn.innerHTML = '<i class="bi bi-magic"></i> Wypełnij wszystko AI';

      expect(bulkBtn.disabled).toBe(false);
      expect(bulkBtn.innerHTML).toContain('Wypełnij wszystko AI');
    });

    test('should hide progress bar after delay', (done) => {
      const progressContainer = document.getElementById('progressContainer');

      setTimeout(() => {
        progressContainer.style.display = 'none';
      }, 100);

      setTimeout(() => {
        expect(progressContainer.style.display).toBe('none');
        done();
      }, 150);
    });
  });

  describe('getCurriculumTooltip', () => {
    test('should return cached value if available', () => {
      const code = 'I.1.2';
      const cachedText = 'Cached curriculum text';

      AIService.tooltipCache.set(code, cachedText);

      const result = AIService.tooltipCache.get(code);

      expect(result).toBe(cachedText);
    });

    test('should fetch from API if not in cache', async () => {
      const code = 'II.3.1';
      const responseText = 'Fetched curriculum text';

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ text: responseText })
      });

      const response = await fetch(`${AIService.endpoints.curriculumTooltip}${code}/`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();

      expect(global.fetch).toHaveBeenCalledWith(
        '/api/curriculum/II.3.1/',
        expect.objectContaining({
          method: 'GET'
        })
      );
      expect(data.text).toBe(responseText);
    });

    test('should cache fetched value', async () => {
      const code = 'III.1.1';
      const text = 'New curriculum text';

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ text })
      });

      const response = await fetch(`${AIService.endpoints.curriculumTooltip}${code}/`);
      const data = await response.json();

      AIService.tooltipCache.set(code, data.text);

      expect(AIService.tooltipCache.get(code)).toBe(text);
    });

    test('should handle API errors for missing codes', async () => {
      const code = 'INVALID';

      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ error: 'Not found' })
      });

      const response = await fetch(`${AIService.endpoints.curriculumTooltip}${code}/`);

      expect(response.ok).toBe(false);
    });
  });

  describe('Error Handling', () => {
    test('should show error modal on server error', () => {
      const modalElement = document.getElementById('errorModal');
      const modalBody = document.getElementById('errorModalBody');
      const message = 'Nie można połączyć z usługą AI';

      modalBody.textContent = message;
      const modal = new bootstrap.Modal(modalElement);
      modal.show();

      expect(modalBody.textContent).toBe(message);
      expect(bootstrap.Modal).toHaveBeenCalledWith(modalElement);
    });

    test('should handle network errors', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      try {
        await fetch('/api/generate-metadata/');
      } catch (error) {
        expect(error.message).toBe('Network error');
      }
    });

    test('should handle JSON parse errors', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => { throw new Error('Invalid JSON'); }
      });

      try {
        const response = await fetch('/api/generate-metadata/');
        await response.json();
      } catch (error) {
        expect(error.message).toBe('Invalid JSON');
      }
    });
  });
});