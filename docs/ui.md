# UI Interaction Reference
## Teacher Assist - Lesson Planner

**Version:** 2.0
**Date:** 2025-11-21
**Purpose:** Quick reference for UI behavior and interaction scenarios
**Technology:** React 18 + TypeScript + Tailwind CSS

---

## Table of Contents

1. [Page Structure](#page-structure)
2. [User Interactions](#user-interactions)
3. [AI Generation](#ai-generation)
4. [Row Management](#row-management)
5. [Table Copying](#table-copying)
6. [Tooltips](#tooltips)
7. [State Management](#state-management)
8. [Error Handling](#error-handling)
9. [Technology Stack](#technology-stack)

---

## Page Structure

### Initial Load
- **Automatic setup:** 5 empty rows created
- **Components visible:**
  - Theme input field (200 char max)
  - Table with 4 columns: Moduł, Podstawa Programowa, Cele, Aktywność
  - Action buttons: Wypełnij wszystko AI, Dodaj wiersz, Wyczyść wszystko, Skopiuj tabelę
  - 3 modals (hidden): Confirmation, Info, Error

### Table Columns
| Column | Width | Editable | Purpose |
|--------|-------|----------|---------|
| Moduł | 20% | Yes | Educational module name |
| Podstawa Programowa | 20% | Yes | Curriculum reference codes |
| Cele | 30% | Yes | Educational objectives (multi-line) |
| Aktywność | 30% | Yes | Activity description |

---

## User Interactions

### Theme Input
- **Component:** `ThemeInput.tsx`
- **Location:** Top of page
- **Optional:** Can be empty
- **Usage:** Provides context to AI generation
- **Cleared by:** "Wyczyść wszystko" button only
- **State:** Managed by `useState` in `App.tsx`

### Manual Data Entry
All table cells use `EditableCell.tsx` component:
1. Click any cell to edit (contenteditable div)
2. Type content directly
3. Content auto-saves on blur
4. Editing AI-generated metadata sets `userEdited=true` flag via `markUserEdited` callback
5. React state updates trigger re-renders

---

## AI Generation

### Single Row Generation

**Trigger:** Click "Wypełnij AI" button (magic wand icon) on row

**Component Flow:**
```
App.tsx handleGenerate()
  → useAIService.generateSingle()
  → fetch('/api/fill-work-plan/')
  → useTableManager.updateRow()
```

**Process:**
1. Validates activity field not empty
2. Checks for existing manual data entries → confirmation modal if present
3. Makes POST request to `/api/fill-work-plan/`
4. Shows loading overlay on row (120s timeout)
5. Populates: module, curriculum_refs, objectives
6. Switches button to "Generuj ponownie"

**API Request:**
```json
{
  "activity": "Zabawa w sklep z owocami",
  "theme": "Jesień - zbiory"  // optional
}
```

**API Response:**
```json
{
  "module": "MATEMATYKA",
  "curriculum_refs": ["4.15", "4.18"],
  "objectives": ["Dziecko potrafi przeliczać...", "Rozpoznaje cyfry..."]
}
```

### Regeneration

**Trigger:** Click "Generuj ponownie" button (circular arrow icon)

**Component:** `handleRegenerate()` in `App.tsx`

**Behavior:**
- If `userEdited=true` → confirmation modal: "Wiersz był zmodyfikowany. Nadpisać dane wprowadzone przez użytkownika?"
- If `userEdited=false` → regenerate immediately
- Resets `userEdited` flag to false after regeneration

### Bulk Generation

**Trigger:** Click "Wypełnij wszystko AI" button

**Component:** `handleBulkGenerate()` in `App.tsx`

**Row Selection Criteria (ALL must be true):**
- ✅ Has activity text
- ✅ `aiGenerated = false`
- ✅ `userEdited = false`
- ✅ All metadata fields empty

**Process:**
1. Calls `getRowsNeedingGeneration()` from `useTableManager`
2. If none → alert: "Brak nowych aktywności do przetworzenia..."
3. Shows progress bar: "Przetwarzanie... (X/Y)"
4. Processes rows sequentially via `useAIService.generateBulk()`
5. Updates progress in real-time with callbacks
6. Shows summary on completion

**Error Handling:**
- Continues on individual failures
- Displays summary modal with failed rows
- Format: "Przetworzono pomyślnie: X/Y\n\nNieudane wiersze (Z): ..."

---

## Row Management

### Add Row
- **Button:** "Dodaj wiersz" in `ActionBar.tsx`
- **Action:** Calls `addRows(1)` from `useTableManager`
- **No limit** on row count
- **Implementation:** Appends new row object to state array

### Delete Row
- **Button:** X icon in `RowActions.tsx`
- **Action:** Immediate deletion (no confirmation)
- **Implementation:** Calls `deleteRow(rowId)` from `useTableManager`
- **Warning:** Cannot be undone

### Clear All
- **Button:** "Wyczyść wszystko" in `ActionBar.tsx`
- **Action:** Confirmation → removes all rows, resets to 5 empty rows, clears theme
- **Confirmation:** "Czy na pewno chcesz wyczyść wszystkie wiersze?"
- **Implementation:** `handleClearAll()` → `ConfirmDialog` → `clearAll()` + `setTheme('')`

---

## Table Copying

### Copy Entire Table
**Trigger:** Click "Skopiuj tabelę" with no rows selected

**Component:** `useClipboard.ts` hook

**Format:**
- **HTML:** Styled table with borders (for Google Docs)
- **TSV:** Tab-separated values (for Excel/Sheets)
- **Includes:** Column headers + all rows

**Implementation:**
```typescript
await navigator.clipboard.write([
  new ClipboardItem({
    'text/html': new Blob([htmlTable], { type: 'text/html' }),
    'text/plain': new Blob([tsvTable], { type: 'text/plain' })
  })
])
```

**Message:** "Skopiowano całą tabelę (N wierszy) do schowka."

### Copy Selected Rows
**Trigger:** Check row checkboxes → button shows "Skopiuj zaznaczone (N)"

**Format:**
- **HTML + TSV:** Both formats
- **Excludes:** Headers (for pasting into existing tables)

**Post-copy:** All checkboxes automatically unchecked via `setSelectedRows(new Set())`

### Checkbox Behavior
- **Location:** In `PlanTableRow.tsx` component
- **State:** Managed by `selectedRows` Set in `App.tsx`
- **Effect:** Updates copy button label dynamically in `ActionBar.tsx`
- **Count:** "Skopiuj zaznaczone (N)" or "Skopiuj tabelę"

---

## Tooltips

### Curriculum Reference Tooltips
**Trigger:** Hover over Podstawa Programowa cell

**Component:** `useCurriculumTooltip.ts` hook

**Pattern Match:** `\d+\.\d+` (e.g., "4.15", "12.3")

**Behavior:**
1. 300ms hover delay before showing (implemented via setTimeout)
2. Fetches from `/api/curriculum-refs/{code}/`
3. Caches result in React state Map (per session)
4. Displays using shadcn/ui Tooltip component
5. Hides on mouse leave (immediate)

**Multiple Codes:**
- Extracts all codes from cell (e.g., "4.15, 4.18")
- Fetches all in parallel using `Promise.all()`
- Displays all in one tooltip:
  ```
  4.15: Dziecko potrafi przeliczać...

  4.18: Dziecko rozpoznaje cyfry...
  ```

**Timeout:** 10 seconds per fetch
**Fallback:** "Nie znaleziono opisu dla kodu: X"

---

## State Management

### Row State (TypeScript Interface)
```typescript
interface WorkPlanRow {
  id: string                // UUID v4
  module: string
  curriculum: string
  objectives: string
  activity: string
  aiGenerated: boolean      // Controls button visibility
  userEdited: boolean       // Controls regenerate confirmation
  loading: boolean          // Row-level loading state
}
```

### React State Architecture

**App.tsx (Main State):**
- `theme: string` - Weekly theme input
- `selectedRows: Set<string>` - Row IDs for copy selection
- `bulkGenerating: boolean` - Bulk operation in progress
- `progress: {visible, value, text}` - Progress bar state

**useTableManager Hook:**
- `rows: WorkPlanRow[]` - Array of all table rows
- Methods: `addRows`, `deleteRow`, `clearAll`, `updateRow`, `setRowLoading`, `markUserEdited`

**useAIService Hook:**
- API communication methods
- `generateSingle(activity, theme)` - Single row generation
- `generateBulk(rows, theme, progressCallback)` - Bulk generation

**useModal Hook:**
- Modal dialog state management
- `showConfirm(message)` - Returns Promise<boolean>
- `showAlert(message)` - Returns Promise<void>
- `showError(message)` - Returns Promise<void>

### State Transitions
| Initial | After AI Gen | After User Edit (Post AI gen) | After Regenerate |
|---------|--------------|-------------------------------|------------------|
| `ai=false, edit=false` | `ai=true, edit=false` | `ai=true, edit=true` | `ai=true, edit=false` |

### Button Display Logic
| State | Generate Button | Regenerate Button |
|-------|----------------|-------------------|
| `aiGenerated=false` | ✅ Shown | ❌ Hidden |
| `aiGenerated=true` | ❌ Hidden | ✅ Shown |

**Implementation:** Conditional rendering in `RowActions.tsx`

### Session Persistence
**MVP Limitation:** No persistence
- All data lost on page reload
- No localStorage or backend save
- Theme, rows, and states all in React memory only
- Future: Will use Django backend `WorkPlan` and `WorkPlanEntry` models

---

## Error Handling

### Error Types & Messages

| Error Type | User Message (Polish) | Component |
|------------|----------------------|-----------|
| Network error | "Nie można połączyć z usługą AI. Sprawdź połączenie internetowe." | `useAIService.ts` |
| Timeout (120s) | "Żądanie przekroczyło limit czasu (120s). Spróbuj ponownie." | `useAIService.ts` |
| Server error (500) | Server's error message from JSON response | `useAIService.ts` |
| Empty activity | "Pole 'Aktywność' nie może być puste." | `App.tsx` handleGenerate |
| Clipboard failure | "Nie udało się skopiować do schowka. Spróbuj ponownie." | `useClipboard.ts` |

### Loading States

**Single Row:**
- Row overlay + spinner (via `loading` property on row)
- Rendered in `PlanTableRow.tsx` with opacity overlay
- All row buttons disabled
- Max duration: 120s

**Bulk Operation:**
- Progress bar (0-100%) in `ProgressBar.tsx`
- Progress text: "Przetwarzanie... (X/Y)"
- Bulk button disabled + spinner
- Individual row overlays

### Confirmation Dialogs

**Component:** `ConfirmDialog.tsx` (shadcn/ui AlertDialog)

| Situation | Message |
|-----------|---------|
| Clear all | "Czy na pewno chcesz wyczyść wszystkie wiersze?" |
| Generate over manual data | "Wiersz zawiera dane wprowadzone ręcznie. Nadpisać dane AI?" |
| Regenerate edited row | "Wiersz był zmodyfikowany. Nadpisać dane wprowadzone przez użytkownika?" |

**Pattern:** All confirmations use async/await Promise-based pattern via `useModal` hook

---

## Technology Stack

### Frontend Framework
- **React:** 18.x with function components and hooks
- **TypeScript:** 5.x for type safety
- **Build Tool:** Vite for fast development and optimized builds
- **Styling:** Tailwind CSS v3 for utility-first styling
- **Component Library:** shadcn/ui for accessible UI primitives

### Key Dependencies
```json
{
  "react": "^18.3.1",
  "typescript": "~5.6.2",
  "vite": "^6.0.1",
  "tailwindcss": "^3.4.17",
  "@radix-ui/react-*": "Various (shadcn/ui base)",
  "lucide-react": "^0.468.0"
}
```

### Component Architecture

```
src/
├── App.tsx                    # Main application component
├── components/
│   ├── ThemeInput.tsx         # Weekly theme input
│   ├── ActionBar.tsx          # Top action buttons
│   ├── ProgressBar.tsx        # Bulk operation progress
│   ├── PlanTable.tsx          # Main table wrapper
│   ├── PlanTableRow.tsx       # Individual table row
│   ├── EditableCell.tsx       # Contenteditable cell component
│   ├── RowActions.tsx         # Row action buttons
│   ├── Modals/
│   │   ├── ConfirmDialog.tsx  # Confirmation modal
│   │   ├── InfoDialog.tsx     # Alert/info modal
│   │   └── ErrorDialog.tsx    # Error modal
│   └── ui/                    # shadcn/ui primitives
├── hooks/
│   ├── useTableManager.ts     # Table state management
│   ├── useAIService.ts        # AI API communication
│   ├── useClipboard.ts        # Clipboard operations
│   ├── useModal.ts            # Modal state management
│   └── useCurriculumTooltip.ts # Tooltip logic
└── lib/
    └── utils.ts               # Utility functions (cn, etc.)
```

### Build Process

**Development:**
```bash
cd webserver/lessonplanner/frontend
npm run dev  # Vite dev server on port 5173
```

**Production Build:**
```bash
npm run build
# Outputs to: frontend/dist/
# - dist/assets/index-[hash].js
# - dist/assets/index-[hash].css
```

**Django Integration:**
```bash
./build-and-update.sh  # Auto-builds and updates Django template
```

The build process:
1. Vite bundles React app with code splitting and minification
2. Outputs to `frontend/dist/` with hashed filenames
3. Django template at `templates/lessonplanner/index.html` loads static assets
4. Assets served via Django's static files system

### Browser Requirements

- **Modern Browsers:** Chrome/Edge 90+, Firefox 90+, Safari 14+
- **Required APIs:**
  - Clipboard API (`navigator.clipboard.write()`)
  - Fetch API (for AJAX requests)
  - ES6+ JavaScript (const, let, async/await, Maps, Sets)
  - CSS Grid and Flexbox
- **Not Required:**
  - No polyfills needed for target browsers
  - Progressive enhancement not implemented

---

## Quick Reference: API Endpoints

| Endpoint | Method | Purpose | Timeout | Called From |
|----------|--------|---------|---------|-------------|
| `/api/fill-work-plan/` | POST | Generate metadata for activity | 120s | `useAIService.ts` |
| `/api/curriculum-refs/{code}/` | GET | Get curriculum full text | 10s | `useCurriculumTooltip.ts` |
| `/api/curriculum-refs/` | GET | Get all curriculum references | 10s | (Future use) |
| `/api/modules/` | GET | Get educational modules | 10s | (Future use) |

---

## Quick Reference: All User Actions

| Action | Trigger | Component | Result |
|--------|---------|-----------|--------|
| Enter theme | Type in theme input | `ThemeInput` | Context for AI |
| Edit cell | Click + type | `EditableCell` | Content saved, userEdited flag set |
| Generate AI | Click "Wypełnij AI" | `RowActions` → `App` | Metadata populated |
| Regenerate | Click "Generuj ponownie" | `RowActions` → `App` | Fresh AI metadata |
| Bulk generate | Click "Wypełnij wszystko AI" | `ActionBar` → `App` | Process all eligible rows |
| Add row | Click "Dodaj wiersz" | `ActionBar` → `App` | New empty row |
| Delete row | Click X icon | `RowActions` → `App` | Row removed |
| Clear all | Click "Wyczyść wszystko" | `ActionBar` → `App` | Reset to 5 empty rows |
| Copy table | Click "Skopiuj tabelę" | `ActionBar` → `App` | Table → clipboard |
| Select rows | Check checkboxes | `PlanTableRow` | Mark for selective copy |
| View tooltip | Hover curriculum cell 300ms | `EditableCell` + `useCurriculumTooltip` | Show curriculum text |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-09 | Initial comprehensive documentation (vanilla JS) |
| 1.1 | 2025-11-09 | Condensed to quick reference format |
| 2.0 | 2025-11-21 | Complete rewrite for React + TypeScript implementation |

---

**End of Document**
