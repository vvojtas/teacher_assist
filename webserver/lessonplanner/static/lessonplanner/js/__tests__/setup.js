/**
 * Jest setup file for lesson planner tests
 */

// Setup jsdom environment
global.bootstrap = {
  Modal: class {
    constructor(element) {
      this.element = element;
    }
    show() {}
    hide() {}
  }
};

// Mock navigator.clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: jest.fn(() => Promise.resolve()),
    write: jest.fn(() => Promise.resolve()),
  },
});

// Mock fetch API
global.fetch = jest.fn();

// Helper to reset all mocks between tests
afterEach(() => {
  jest.clearAllMocks();
});