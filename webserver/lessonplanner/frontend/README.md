# Teacher Assist - React Frontend

This directory contains the React frontend for the Teacher Assist lesson planning application, migrated from vanilla JavaScript + Bootstrap to React + Tailwind CSS + shadcn/ui.

## Technology Stack

- **Framework:** React 18
- **Language:** TypeScript 5
- **Build Tool:** Vite
- **Styling:** Tailwind CSS v3
- **Component Library:** shadcn/ui
- **Icons:** Lucide React
- **State Management:** React Hooks (custom hooks)

## Development

### Install Dependencies
\`\`\`bash
npm install
\`\`\`

### Development Server
\`\`\`bash
npm run dev
\`\`\`

### Build for Production
\`\`\`bash
npm run build
\`\`\`

### Auto-Build and Update Django Template

**Linux/macOS:**
\`\`\`bash
./build-and-update.sh
\`\`\`

**Windows (Command Prompt):**
\`\`\`cmd
build-and-update.bat
\`\`\`

**Windows (PowerShell):**
\`\`\`powershell
.\build-and-update.ps1
\`\`\`

See [BUILD_SCRIPTS_README.md](BUILD_SCRIPTS_README.md) for detailed instructions.

## Migration Summary

Successfully migrated from Bootstrap 5 + Vanilla JS to React + TypeScript + Tailwind CSS + shadcn/ui with full feature parity.

All original features preserved:
- Theme input, editable table cells
- Single & bulk AI generation
- Copy to clipboard (HTML + TSV)
- Curriculum tooltips with caching
- Modal confirmations in Polish
- Loading states and error handling
