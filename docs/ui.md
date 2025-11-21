# UI Interaction Reference
## Teacher Assist - Lesson Planner

**Version:** 1.1
**Date:** 2025-11-09
**Purpose:** Quick reference for UI behavior and interaction scenarios

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

---

## Page Structure

### Initial Load
- **Automatic setup:** 5 empty rows created
- **Components visible:**
  - Theme input field (200 char max)
  - Table with 4 columns: Moduł, Podstawa Programowa, Cele, Aktywność
  - Action buttons: Wypełnij wszystko AI, Dodaj wiersz, Wyczyść wszystko, Skopiuj tabelę
  - 3 modals (hidden): Confirmation, Alert, Error

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
- **Location:** Top of page
- **Optional:** Can be empty
- **Usage:** Provides context to AI generation
- **Cleared by:** "Wyczyść wszystko" button only

### Manual Data Entry
All table cells are editable (React EditableCell components):
1. Click any cell to edit
2. Type content directly
3. Content auto-saves on blur
4. Editing AI-generated metadata sets `userEdited=true` flag

---

## AI Generation

### Single Row Generation

**Trigger:** Click "Wypełnij AI" button (magic wand icon) on row

**Process:**
1. Validates activity field not empty
2. Checks for existing manual data entries → confirmation if present
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

**Behavior:**
- If `userEdited=true` → confirmation modal: "Wiersz był zmodyfikowany. Nadpisać dane wprowadzone przez użytkownika?"
- If `userEdited=false` → regenerate immediately
- Resets `userEdited` flag to false after regeneration

### Bulk Generation

**Trigger:** Click "Wypełnij wszystko AI" button

**Row Selection Criteria (ALL must be true):**
- ✅ Has activity text
- ✅ `aiGenerated = false`
- ✅ `userEdited = false`
- ✅ All metadata fields empty

**Process:**
1. Filters eligible rows
2. If none → alert: "Brak nowych aktywności do przetworzenia..."
3. Shows progress bar: "Przetwarzanie... (X/Y)"
4. Processes rows sequentially
5. Updates progress in real-time
6. Shows summary on completion

**Error Handling:**
- Continues on individual failures
- Displays summary modal with failed rows
- Format: "Przetworzono pomyślnie: X/Y\n\nNieudane wiersze (Z): ..."

---

## Row Management

### Add Row
- **Button:** "Dodaj wiersz"
- **Action:** Appends 1 empty row to table bottom
- **No limit** on row count

### Delete Row
- **Button:** X icon on each row
- **Action:** Immediate deletion (no confirmation)
- **Warning:** Cannot be undone

### Clear All
- **Button:** "Wyczyść wszystko"
- **Action:** Confirmation → removes all rows, resets to 5 empty rows, clears theme
- **Confirmation:** "Czy na pewno chcesz wyczyść wszystkie wiersze?"

---

## Table Copying

### Copy Entire Table
**Trigger:** Click "Skopiuj tabelę" with no rows selected

**Format:**
- **HTML:** Styled table with borders (for Google Docs)
- **TSV:** Tab-separated values (for Excel/Sheets)
- **Includes:** Column headers + all rows

**Message:** "Skopiowano całą tabelę (N wierszy) do schowka."

### Copy Selected Rows
**Trigger:** Check row checkboxes → button shows "Skopiuj zaznaczone (N)"

**Format:**
- **HTML + TSV:** Both formats
- **Excludes:** Headers (for pasting into existing tables)

**Post-copy:** All checkboxes automatically unchecked

### Checkbox Behavior
- **Location:** Next to each row's buttons
- **Effect:** Updates copy button label dynamically
- **Count:** "Skopiuj zaznaczone (N)" or "Skopiuj tabelę"

---

## Tooltips

### Curriculum Reference Tooltips
**Trigger:** Hover over Podstawa Programowa cell

**Pattern Match:** `\d+\.\d+` (e.g., "4.15", "12.3")

**Behavior:**
1. 300ms hover delay before showing
2. Fetches from `/api/curriculum-refs/{code}/`
3. Caches result (per session)
4. Displays above/below cell (auto-positioned)
5. Hides on mouse leave (immediate)

**Multiple Codes:**
- Extracts all codes from cell (e.g., "4.15, 4.18")
- Fetches all in parallel
- Displays all in one tooltip:
  ```
  4.15: Dziecko potrafi przeliczać...

  4.18: Dziecko rozpoznaje cyfry...
  ```

**Timeout:** 10 seconds per fetch
**Fallback:** "Nie znaleziono opisu dla kodu: X"

---

## State Management

### Row State (per row)
Managed by React hooks (useTableManager):
```javascript
{
  module: '',
  curriculum: '',
  objectives: '',
  activity: '',
  aiGenerated: false,    // Controls button visibility
  userEdited: false      // Controls regenerate confirmation
}
```

### State Transitions
| Initial | After AI Gen | After User Edit (Post AI gen) | After Regenerate |
|---------|--------------|-------------------------------|------------------|
| `ai=false, edit=false` | `ai=true, edit=false` | `ai=true, edit=true` | `ai=true, edit=false` |

### Button Display Logic
| State | Generate Button | Regenerate Button |
|-------|----------------|-------------------|
| `aiGenerated=false` | ✅ Shown | ❌ Hidden |
| `aiGenerated=true` | ❌ Hidden | ✅ Shown |

### Session Persistence
**MVP Limitation:** No persistence
- All data lost on page reload
- No localStorage or backend save
- Theme, rows, and states all in memory only

---

## Error Handling

### Error Types & Messages

| Error Type | User Message (Polish) |
|------------|----------------------|
| Network error | "Nie można połączyć z usługą AI. Sprawdź połączenie internetowe." |
| Timeout (120s) | "Żądanie przekroczyło limit czasu (120s). Spróbuj ponownie." |
| Server error (500) | Server's error message from JSON response |
| Empty activity | "Pole 'Aktywność' nie może być puste." |
| Clipboard failure | "Nie udało się skopiować do schowka. Spróbuj ponownie." |

### Loading States

**Single Row:**
- Row overlay + spinner
- All row buttons disabled
- Max duration: 120s

**Bulk Operation:**
- Progress bar (0-100%)
- Progress text: "Przetwarzanie... (X/Y)"
- Bulk button disabled + spinner
- Individual row overlays

### Confirmation Dialogs

| Situation | Message |
|-----------|---------|
| Clear all | "Czy na pewno chcesz wyczyść wszystkie wiersze?" |
| Generate over manual data | "Wiersz zawiera dane wprowadzone ręcznie. Nadpisać dane AI?" |
| Regenerate edited row | "Wiersz był zmodyfikowany. Nadpisać dane wprowadzone przez użytkownika?" |

---

## Quick Reference: API Endpoints

| Endpoint | Method | Purpose | Timeout |
|----------|--------|---------|---------|
| `/api/fill-work-plan/` | POST | Generate metadata for activity | 120s |
| `/api/curriculum-refs/{code}/` | GET | Get curriculum full text | 10s |

---

## Quick Reference: All User Actions

| Action | Trigger | Result |
|--------|---------|--------|
| Enter theme | Type in theme input | Context for AI |
| Edit cell | Click + type | Content saved |
| Generate AI | Click "Wypełnij AI" | Metadata populated |
| Regenerate | Click "Generuj ponownie" | Fresh AI metadata |
| Bulk generate | Click "Wypełnij wszystko AI" | Process all eligible rows |
| Add row | Click "Dodaj wiersz" | New empty row |
| Delete row | Click X icon | Row removed |
| Clear all | Click "Wyczyść wszystko" | Reset to 5 empty rows |
| Copy table | Click "Skopiuj tabelę" | Table → clipboard |
| Select rows | Check checkboxes | Mark for selective copy |
| View tooltip | Hover curriculum cell 300ms | Show curriculum text |

---

## Browser Requirements

- **React 18:** Single-page application framework
- **Clipboard API:** `navigator.clipboard.write()`
- **Fetch API:** AJAX requests
- **ContentEditable:** Editable cells
- **Modern JS:** ES6+ (const, let, async/await)

**Supported:** Chrome/Edge 90+, Firefox 90+, Safari 14+

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-09 | Initial comprehensive documentation |
| 1.1 | 2025-11-09 | Condensed to quick reference format |
| 1.2 | 2025-11-21 | Updated to reflect React implementation |

---

**End of Document**
