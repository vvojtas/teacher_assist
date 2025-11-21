# UI Reference - Visual Design and User Experience
## Teacher Assist - Lesson Planner

**Version:** 2.0
**Date:** 2025-11-21
**Purpose:** Visual and interaction reference for the lesson planning interface

---

## Table of Contents

1. [Visual Layout](#visual-layout)
2. [Table Interface](#table-interface)
3. [User Actions](#user-actions)
4. [AI Generation](#ai-generation)
5. [Feedback and Messages](#feedback-and-messages)

---

## Visual Layout

### Application Header
- **Color:** Green gradient header bar (primary green to lighter green)
- **Title:** "🍎 Teacher Assist - Planowanie Lekcji"
- **Subtitle:** "Asystent planowania zajęć przedszkolnych z AI"
- **Background:** Light green gradient background (green-50 via white to green-50)

### Main Content Area
**Container:** Centered, maximum width 1280px with padding

**Top Section - Theme Input:**
- Large text input field
- Label: "Motyw tygodnia (opcjonalnie)"
- Placeholder: "np. Jesień - zbiory, Zwierzęta domowe"
- Maximum 200 characters
- Full width, rounded corners
- Light border, focus highlight

**Action Bar:**
Row of buttons aligned to the right:
1. **"Wypełnij wszystko AI"** - Primary action button (green)
2. **"Dodaj wiersz"** - Secondary button
3. **"Wyczyść wszystko"** - Danger button (red)
4. **"Skopiuj tabelę"** - Secondary button
   - Changes to **"Skopiuj zaznaczone (N)"** when rows are selected

**Progress Bar** (shown during bulk AI generation):
- Full width bar beneath action buttons
- Green fill showing percentage (0-100%)
- Text: "Przetwarzanie... (X/Y)" centered on bar
- Animated progress fill
- Auto-hides 2 seconds after completion

---

## Table Interface

### Table Structure

**Full-width table with 5 columns:**

| Column | Width | Content |
|--------|-------|---------|
| ☐ | 40px | Checkbox for selection |
| **Moduł** | 20% | Educational module name |
| **Podstawa Programowa** | 20% | Curriculum reference codes |
| **Cele** | 30% | Educational objectives |
| **Aktywność** | 30% | Activity description |

### Visual Styling

**Table Appearance:**
- White background
- Light gray borders between cells
- Rounded corners on table container
- Shadow for depth

**Table Header:**
- Bold text
- Gray background (lighter than borders)
- Sticky header (stays visible when scrolling)

**Table Rows:**
- Alternating white and very light gray backgrounds (zebra striping)
- Hover effect: Light green highlight on row hover
- Minimum height: ~60px per row

### Cell Editing

**Editable Cells (all except checkbox column):**
- **Visual Cue:** Dashed border appears on focus
- **Cursor:** Text cursor changes on hover
- **Behavior:** Click anywhere in cell to edit
- **Multi-line:** Cells expand vertically as content grows (especially "Cele" and "Aktywność")
- **Save:** Auto-saves when clicking outside cell (on blur)

**Cell States:**
- **Empty:** Light gray placeholder text
- **Filled (manual):** Black text on white background
- **Filled (AI-generated):** Slightly green-tinted background
- **Edited after AI:** Returns to white background with subtle indicator

### Row Actions

**Right side of each row shows action buttons:**

**When row is empty or manually filled:**
- **"Wypełnij AI"** button (magic wand icon ✨)
  - Green button
  - Tooltip: "Wygeneruj metadane AI"

**After AI generation:**
- **"Generuj ponownie"** button (circular arrow icon 🔄)
  - Blue button
  - Tooltip: "Generuj ponownie"

**Always visible:**
- **Delete button** (X icon)
  - Small, red, on far right
  - Tooltip: "Usuń wiersz"

**Loading State:**
- Semi-transparent white overlay on entire row
- Spinning loader icon in center
- All buttons disabled
- Duration: Up to 120 seconds

---

## User Actions

### Theme Input
**What user sees:**
- Text input at top of page
- Optional field for weekly theme context
- Helps AI understand the educational context
- Cleared only when clicking "Wyczyść wszystko"

**Example themes:**
- "Jesień - zbiory"
- "Zwierzęta domowe"
- "Kolory i kształty"

### Manual Data Entry

**Direct Editing:**
1. Click any cell (except checkbox)
2. Cell border changes to dashed line
3. Type or paste content
4. Click outside cell or press Tab to save
5. Content persists until changed or cleared

**Copy-Paste Friendly:**
- Can paste multi-line text into "Cele" and "Aktywność"
- Text wraps naturally
- Cell height adjusts automatically

### Row Selection

**Checkbox Column:**
- Checkbox at the start of each row
- **Unchecked:** Default state
- **Checked:** Row marked for selective copying
- **Visual:** Selected rows have light blue background tint
- **Counter:** Copy button updates to show "Skopiuj zaznaczone (3)"

**Selection Behavior:**
- Can select any number of rows
- Selection persists across page (until copy or clear)
- Auto-uncheck after successful copy

### Bulk Actions

**"Wypełnij wszystko AI":**
- Finds all rows with:
  - Activity text entered
  - No AI-generated metadata yet
  - No manual edits to metadata
- Shows progress bar during processing
- Processes rows sequentially
- Shows summary when complete

**"Dodaj wiersz":**
- Adds one blank row at bottom of table
- No limit on row count
- Row appears immediately

**"Wyczyść wszystko":**
- Shows confirmation dialog (see Modals below)
- If confirmed: Removes all rows, adds 5 empty rows, clears theme
- Cannot be undone

**"Skopiuj tabelę" / "Skopiuj zaznaczone (N)":**
- Copies table to clipboard in two formats:
  - HTML (for pasting into Google Docs with formatting)
  - TSV (for pasting into Excel/Sheets)
- If no selection: Copies entire table with headers
- If rows selected: Copies only selected rows without headers
- Shows success message
- Auto-uncheck selected rows after copy

---

## AI Generation

### Single Row Generation

**Visual Flow:**
1. User clicks **"Wypełnij AI"** button on a row
2. If manual data exists → Confirmation modal appears
3. Row shows loading overlay (white semi-transparent with spinner)
4. AI fills three columns:
   - **Moduł:** e.g., "MATEMATYKA"
   - **Podstawa Programowa:** e.g., "4.15, 4.18"
   - **Cele:** Multi-line objectives (2-3 items)
5. Loading overlay disappears
6. Button changes to **"Generuj ponownie"**
7. Filled cells show subtle green tint

**Time:** Usually 2-5 seconds per row, maximum 120 seconds

### Bulk Generation

**Visual Flow:**
1. User clicks **"Wypełnij wszystko AI"**
2. If no eligible rows → Alert: "Brak nowych aktywności do przetworzenia..."
3. Progress bar appears: "Przetwarzanie... (0/5)"
4. Each eligible row gets loading overlay
5. Progress bar updates: "Przetwarzanie... (1/5)", "Przetwarzanie... (2/5)"
6. Loading overlay disappears from each row as completed
7. Final progress: "Ukończono: 5/5"
8. Progress bar auto-hides after 2 seconds
9. If any failures → Error modal with summary

**Eligible Rows:**
- Has activity text
- No AI-generated metadata yet
- No manual edits to metadata fields

### Regeneration

**Visual Flow:**
1. User clicks **"Generuj ponownie"**
2. If user edited the row → Confirmation modal
3. Same loading and generation process as initial generation
4. New AI content replaces old content

**Use Case:** When user wants different AI suggestions

---

## Feedback and Messages

### Tooltips

**Curriculum Reference Tooltips:**
- **Trigger:** Hover mouse over "Podstawa Programowa" cell for 300ms
- **Appearance:**
  - Floating box above or below cell
  - Dark background, white text
  - Rounded corners, subtle shadow
  - Maximum width 400px
- **Content:** Full Polish text for each curriculum code
  - Example: "4.15: przelicza elementy zbiorów w czasie zabawy..."
  - Multiple codes shown in one tooltip with line breaks
- **Hide:** Mouse leaves cell (immediate)

**Button Tooltips:**
- **Trigger:** Hover mouse over button for 500ms
- **Appearance:** Small dark tooltip below button
- **Examples:**
  - "Wygeneruj metadane AI"
  - "Generuj ponownie"
  - "Usuń wiersz"

### Modals (Dialog Boxes)

**Visual Style:**
- Centered on screen
- White background
- Rounded corners
- Semi-transparent dark overlay behind
- Cannot click outside to close (must use buttons)

**Confirmation Modal:**
- **Icon:** ⚠️ (warning triangle)
- **Title:** "Potwierdzenie"
- **Message:** Specific to action (see messages below)
- **Buttons:**
  - "Anuluj" (gray, left)
  - "Potwierdź" (blue, right)

**Alert/Info Modal:**
- **Icon:** ℹ️ (info circle)
- **Title:** "Informacja"
- **Message:** Success or informational message
- **Button:** "OK" (blue, centered)

**Error Modal:**
- **Icon:** ❌ (red X)
- **Title:** "Błąd"
- **Message:** Error description in Polish
- **Button:** "OK" (blue, centered)
- **Content:** Can be multi-line for bulk error summaries

### Modal Messages

**Confirmation Messages:**
| Situation | Message |
|-----------|---------|
| Clear all | "Czy na pewno chcesz wyczyść wszystkie wiersze?" |
| Overwrite manual data | "Wiersz zawiera dane wprowadzone ręcznie. Nadpisać dane AI?" |
| Regenerate edited row | "Wiersz był zmodyfikowany. Nadpisać dane wprowadzone przez użytkownika?" |

**Success Messages:**
| Situation | Message |
|-----------|---------|
| Copied all rows | "Skopiowano całą tabelę (5 wierszy) do schowka." |
| Copied selected rows | "Skopiowano 3 zaznaczone wiersze do schowka." |
| No rows to process | "Brak nowych aktywności do przetworzenia. Wszystkie wiersze są już wypełnione lub puste." |

**Error Messages:**
| Error Type | Message |
|------------|---------|
| Empty activity field | "Pole 'Aktywność' nie może być puste." |
| Network error | "Nie można połączyć z usługą AI. Sprawdź połączenie internetowe." |
| Timeout | "Żądanie przekroczyło limit czasu (120s). Spróbuj ponownie." |
| Clipboard error | "Nie udało się skopiować do schowka. Spróbuj ponownie." |

**Bulk Error Summary:**
```
Przetworzono pomyślnie: 3/5

Nieudane wiersze (2):

• Zabawa w sklep z owocami...
  Błąd: Nie można połączyć z usługą AI

• Malowanie jesiennych liści...
  Błąd: Żądanie przekroczyło limit czasu
```

### Progress Indicators

**Single Row Loading:**
- White semi-transparent overlay over entire row
- Spinning loader icon in center of row
- All row buttons disabled
- Row height maintained

**Bulk Loading:**
- Green progress bar below action buttons
- Percentage fill (0-100%)
- Text centered: "Przetwarzanie... (3/7)"
- Each row also shows individual loading overlay

**Loading Animation:**
- Smooth, continuous spinning
- Color: Green to match theme
- Size: Medium (32px icon)

---

## Color Palette Reference

**Primary Colors:**
- **Header gradient:** Green (#059669) to light green (#10b981)
- **Background:** Very light green (#f0fdf4) with white
- **Primary buttons:** Green (#16a34a)
- **Hover state:** Darker green (#15803d)

**Secondary Colors:**
- **Secondary buttons:** Gray (#6b7280)
- **Danger button:** Red (#dc2626)
- **Info/blue:** Blue (#3b82f6)

**Table Colors:**
- **Border:** Light gray (#e5e7eb)
- **Zebra striping:** White / very light gray (#f9fafb)
- **Hover:** Very light green (#f0fdf4)
- **AI-generated background:** Light green tint (#ecfdf5)

**Text Colors:**
- **Primary:** Black (#0f172a)
- **Secondary:** Gray (#64748b)
- **Placeholder:** Light gray (#94a3b8)

---

## Responsive Behavior

**Desktop (1280px+):**
- Full table visible
- All columns comfortable width
- Action buttons spread out

**Tablet (768px - 1279px):**
- Table takes full width
- Slightly narrower columns
- Action buttons closer together

**Mobile (< 768px):**
- Table scrolls horizontally
- Fixed action buttons at top
- One row at a time visible (vertical scrolling)

---

## Keyboard Navigation

**Tab Order:**
1. Theme input
2. Action buttons (left to right)
3. Table cells (left to right, top to bottom)
4. Checkboxes and action buttons per row

**Shortcuts:**
- **Tab:** Move to next cell
- **Shift+Tab:** Move to previous cell
- **Enter:** Same as Tab when in cell
- **Escape:** Cancel cell edit (restore original value)

---

## Initial State

**On Page Load:**
- 5 empty rows displayed
- Theme input empty
- No checkboxes selected
- All cells empty with light gray placeholders:
  - Moduł: "np. MATEMATYKA"
  - Podstawa Programowa: "np. 4.15, 4.18"
  - Cele: "np. Dziecko potrafi..."
  - Aktywność: "Wprowadź opis aktywności"
- Copy button shows "Skopiuj tabelę"
- All "Wypełnij AI" buttons visible

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-09 | Initial comprehensive documentation |
| 1.1 | 2025-11-09 | Condensed to quick reference format |
| 2.0 | 2025-11-21 | Refocused on visual design and user experience |

---

**End of Document**
