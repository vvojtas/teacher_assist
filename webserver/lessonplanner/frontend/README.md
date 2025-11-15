# Teacher Assist - React Frontend

This directory contains the React frontend for the Teacher Assist lesson planning application.

## Technology Stack

- **Framework:** React 18
- **Language:** TypeScript 5
- **Build Tool:** Vite
- **Styling:** Tailwind CSS v3
- **Component Library:** shadcn/ui
- **Icons:** Lucide React
- **State Management:** React Hooks (custom hooks)
- **Testing:** Vitest + React Testing Library

## Development

### Install Dependencies
```bash
npm install
```

### Development Server
```bash
npm run dev
```

### Build for Production
```bash
npm run build
```

### Run Tests
```bash
npm test              # Run tests in watch mode
npm run test:run      # Run tests once
npm run test:ui       # Open Vitest UI
npm run test:coverage # Generate coverage report
```

### Auto-Build and Update Django Template

**Linux/macOS:**
```bash
./build-and-update.sh
```

**Windows:**
```cmd
build-and-update.bat
```

See [BUILD_SCRIPTS_README.md](BUILD_SCRIPTS_README.md) for detailed instructions.

## Project Structure

```
src/
├── components/         # React components
│   ├── ui/            # shadcn/ui primitives
│   ├── Modals/        # Dialog components
│   ├── ActionBar.tsx
│   ├── EditableCell.tsx
│   ├── PlanTable.tsx
│   ├── ProgressBar.tsx
│   └── ...
├── hooks/             # Custom React hooks
│   ├── useTableManager.ts
│   ├── useAIService.ts
│   ├── useClipboard.ts
│   └── ...
├── lib/               # Utilities
├── test/              # Test setup
├── App.tsx            # Main application
├── main.tsx           # Entry point
└── index.css          # Global styles
```

## Features

- Editable table cells with contenteditable
- Single & bulk AI generation
- Copy to clipboard (HTML + TSV formats)
- Curriculum reference tooltips with API caching
- Modal confirmations (Polish language)
- Loading states and error handling
- TypeScript type safety
- Comprehensive test coverage
