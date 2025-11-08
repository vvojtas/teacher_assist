# JavaScript Tests for Lesson Planner

This directory contains Jest-based tests for the lesson planner JavaScript modules.

## Test Coverage

- **tableManager.test.js**: Tests for row operations and state management
  - Row add/delete operations
  - Data getting/setting
  - Loading states
  - Button visibility updates
  - Rows needing generation

- **planner.test.js**: Tests for copy functionality and button label updates
  - Copy button label updates based on selection
  - HTML table formatting for Google Docs
  - TSV plain text formatting
  - Checkbox selection logic
  - HTML escaping

- **aiService.test.js**: Tests for API calls and error handling
  - Single row generation
  - Bulk generation with progress tracking
  - Curriculum tooltip caching
  - Error handling and network failures
  - Loading state management

## Setup

Install dependencies:
```bash
npm install
```

## Running Tests

Run all tests:
```bash
npm test
```

Run tests in watch mode:
```bash
npm run test:watch
```

Run tests with coverage:
```bash
npm run test:coverage
```

## Test Environment

- **Framework**: Jest 29.7.0
- **Environment**: jsdom (browser-like environment)
- **Mocking**: Bootstrap modals, Clipboard API, Fetch API
- **Coverage**: All main JS modules except test files

## Notes

- Tests use mocked DOM elements and browser APIs
- Bootstrap Modal and Clipboard API are mocked in setup.js
- fetch API is globally mocked for API call testing
- All mocks are cleared between tests for isolation