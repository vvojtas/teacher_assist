/**
 * Tests for aiService.js - API calls and error handling
 * Updated for new API endpoints and sequential bulk processing
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
    fillWorkPlan: '/api/fill-work-plan/',
    curriculumTooltip: '/api/curriculum-refs/'
  },
  tooltipCache: new Map(),
  REQUEST_TIMEOUT: 120000
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

  describe('fill-work-plan endpoint', () => {
    test('should call API with correct endpoint', async () => {
      const mockResponse = {
        module: 'Test Module',
        curriculum_refs: ['4.15'],
        objectives: ['Objective 1']
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const activity = 'Test Activity';
      const theme = 'Test Theme';

      await fetch(AIService.endpoints.fillWorkPlan, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ activity, theme })
      });

      expect(global.fetch).toHaveBeenCalledWith(
        '/api/fill-work-plan/',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ activity, theme })
        })
      );
    });

    test('should set row loading state', () => {
      const rowId = 'row_1';
      TableManager.setRowLoading(rowId, true);
      expect(TableManager.setRowLoading).toHaveBeenCalledWith(rowId, true);
    });

    test('should clear row loading state', async () => {
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
        await fetch('/api/fill-work-plan/', {
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
        curriculum_refs: ['4.15', '4.18'],
        objectives: ['Objective 1', 'Objective 2']
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData
      });

      const response = await fetch('/api/fill-work-plan/', {
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
        curriculum: ['4.15', '4.18'],
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

      const response = await fetch('/api/fill-work-plan/', {
        method: 'POST',
        body: JSON.stringify({ activity: 'test', theme: '' })
      });

      expect(response.ok).toBe(false);
    });
  });

  describe('generateBulk - sequential processing', () => {
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

    test('should set loading state for each row individually', () => {
      mockRows.forEach(row => {
        TableManager.setRowLoading(row.id, true);
        TableManager.setRowLoading(row.id, false);
      });

      // Should be called twice per row (set true, then set false)
      expect(TableManager.setRowLoading).toHaveBeenCalledTimes(4);
      expect(TableManager.setRowLoading).toHaveBeenCalledWith('row_1', true);
      expect(TableManager.setRowLoading).toHaveBeenCalledWith('row_1', false);
    });

    test('should call fill-work-plan endpoint for each row sequentially', async () => {
      const theme = 'Test Theme';

      // Mock successful responses for both rows
      global.fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ module: 'Module 1', curriculum_refs: [], objectives: [] })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ module: 'Module 2', curriculum_refs: [], objectives: [] })
        });

      // Simulate sequential calls
      for (const row of mockRows) {
        await fetch(AIService.endpoints.fillWorkPlan, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ activity: row.activity, theme })
        });
      }

      expect(global.fetch).toHaveBeenCalledTimes(2);
      expect(global.fetch).toHaveBeenNthCalledWith(
        1,
        '/api/fill-work-plan/',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ activity: 'Activity 1', theme })
        })
      );
      expect(global.fetch).toHaveBeenNthCalledWith(
        2,
        '/api/fill-work-plan/',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ activity: 'Activity 2', theme })
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

    test('should re-enable bulk generate button when complete', () => {
      const bulkBtn = document.getElementById('bulkGenerateBtn');
      bulkBtn.disabled = false;
      bulkBtn.innerHTML = '<i class="bi bi-magic"></i> Wypełnij wszystko AI';

      expect(bulkBtn.disabled).toBe(false);
      expect(bulkBtn.innerHTML).toContain('Wypełnij wszystko AI');
    });
  });

  describe('getCurriculumTooltip', () => {
    test('should return cached value if available', () => {
      const code = '4.15';
      const cachedText = 'Cached curriculum text';

      AIService.tooltipCache.set(code, cachedText);
      const result = AIService.tooltipCache.get(code);

      expect(result).toBe(cachedText);
    });

    test('should fetch from API if not in cache', async () => {
      const code = '3.8';
      const responseText = 'Fetched curriculum text';

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          reference_code: code,
          full_text: responseText,
          created_at: '2025-10-28T10:30:00Z'
        })
      });

      const response = await fetch(`${AIService.endpoints.curriculumTooltip}${code}/`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();

      expect(global.fetch).toHaveBeenCalledWith(
        '/api/curriculum-refs/3.8/',
        expect.objectContaining({
          method: 'GET'
        })
      );
      expect(data.full_text).toBe(responseText);
    });

    test('should cache fetched value', async () => {
      const code = '2.5';
      const text = 'New curriculum text';

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          reference_code: code,
          full_text: text,
          created_at: '2025-10-28T10:30:00Z'
        })
      });

      const response = await fetch(`${AIService.endpoints.curriculumTooltip}${code}/`);
      const data = await response.json();

      AIService.tooltipCache.set(code, data.full_text);

      expect(AIService.tooltipCache.get(code)).toBe(text);
    });

    test('should handle API errors for missing codes', async () => {
      const code = 'INVALID';

      global.fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          error: 'Nie znaleziono odniesienia dla kodu: INVALID',
          error_code: 'REFERENCE_NOT_FOUND'
        })
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
        await fetch('/api/fill-work-plan/');
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
        const response = await fetch('/api/fill-work-plan/');
        await response.json();
      } catch (error) {
        expect(error.message).toBe('Invalid JSON');
      }
    });
  });
});
