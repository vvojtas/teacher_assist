# UI Interaction Scenarios
## Teacher Assist - Lesson Planner Interface

**Version:** 1.0
**Date:** 2025-11-09
**Purpose:** Complete reference for all user interaction scenarios in the Teacher Assist UI

---

## Table of Contents

1. [Initial Load & Setup](#1-initial-load--setup)
2. [Theme Input](#2-theme-input)
3. [Manual Data Entry](#3-manual-data-entry)
4. [Single Row AI Generation](#4-single-row-ai-generation)
5. [Single Row AI Regeneration](#5-single-row-ai-regeneration)
6. [Bulk AI Generation](#6-bulk-ai-generation)
7. [Row Management](#7-row-management)
8. [Table Copying](#8-table-copying)
9. [Curriculum Reference Tooltips](#9-curriculum-reference-tooltips)
10. [Error Handling](#10-error-handling)
11. [Loading States](#11-loading-states)
12. [State Tracking & Persistence](#12-state-tracking--persistence)

---

## 1. Initial Load & Setup

### Scenario 1.1: Page First Load

**Trigger:** User opens the Teacher Assist application

**Steps:**
1. Browser loads HTML page
2. JavaScript executes on `DOMContentLoaded`
3. TableManager initializes
4. System automatically creates 5 empty rows
5. Event listeners attach to buttons and table

**Result:**
- Header displays: "Teacher Assist - Planowanie Lekcji"
- Theme input field shown (empty)
- Table with headers: Moduł, Podstawa Programowa, Cele, Aktywność
- 5 empty rows displayed
- Action buttons visible:
  - "Wypełnij wszystko AI" (Bulk Generate)
  - "Dodaj wiersz" (Add Row)
  - "Wyczyść wszystko" (Clear All)
  - "Skopiuj tabelę" (Copy Table)
- Curriculum tooltip container initialized (hidden)
- Modals initialized (hidden)

**UI State:**
- All table cells are editable (contenteditable=true)
- All rows show "Wypełnij AI" button (generate)
- All rows show delete button (X icon)
- All rows show unchecked checkbox
- Regenerate buttons are hidden
- No loading states active

---

## 2. Theme Input

### Scenario 2.1: Enter Weekly Theme

**Trigger:** User clicks in theme input field and types

**Steps:**
1. User focuses on "Temat tygodnia:" input field
2. User types theme text (e.g., "Jesień - zbiory")
3. Input limited to 200 characters (HTML maxlength)

**Result:**
- Theme text stored in input field
- Available to all AI generation requests
- Optional field - can remain empty

**UI State:**
- Theme persists until cleared or page reloaded
- Used as context for all AI generation calls

### Scenario 2.2: Clear Theme

**Trigger:** User clicks "Wyczyść wszystko" button (clears entire form including theme)

**Steps:**
1. Confirmation modal appears
2. If confirmed, theme input field cleared
3. All rows reset

**Result:**
- Theme input becomes empty

---

## 3. Manual Data Entry

### Scenario 3.1: Enter Activity Text

**Trigger:** User clicks in Activity cell and types

**Steps:**
1. User clicks on "Aktywność" cell in any row
2. Cursor appears (contenteditable active)
3. User types activity description
4. Text saved in cell on blur/focus change

**Result:**
- Activity text stored in row
- Generate AI button becomes functional for this row
- No visual state change (no tracking of manual entry)

**UI State:**
- Row ready for AI generation
- No "userEdited" flag set (only metadata edits set this)

### Scenario 3.2: Manually Enter Metadata (Module, Curriculum, Objectives)

**Trigger:** User clicks in Module, Podstawa Programowa, or Cele cell and types

**Steps:**
1. User clicks on metadata cell (Moduł, Podstawa Programowa, or Cele)
2. Cursor appears
3. User types content
4. Input event fires on each character
5. If row has `aiGenerated=true`, sets `userEdited=true`

**Result:**
- Metadata stored in cell
- If AI-generated previously, row marked as user-edited
- User-edited flag used for regenerate confirmation

**UI State:**
- Cell contains user-entered text
- If editing AI data, internal flag `userEdited=true` set

### Scenario 3.3: Edit Existing Content

**Trigger:** User clicks in any cell with existing content

**Steps:**
1. User clicks cell
2. Content becomes editable
3. User modifies text
4. Input event fires
5. Content saved

**Result:**
- Updated content in cell
- If AI-generated row, marked as user-edited

---

## 4. Single Row AI Generation

### Scenario 4.1: Generate AI for Row (Empty Metadata)

**Trigger:** User clicks "Wypełnij AI" button (magic wand icon) on a row

**Preconditions:**
- Activity field has text
- Metadata fields (Moduł, Podstawa, Cele) are empty

**Steps:**
1. User enters activity text in row
2. User clicks "Wypełnij AI" button
3. System validates activity field is not empty
4. No confirmation needed (metadata empty)
5. System triggers `generateMetadata` event
6. AIService.generateSingle() called
7. Row enters loading state:
   - Row gets "loading" CSS class
   - All buttons in row disabled
   - Loading overlay shown
8. Fetch request sent to `/api/fill-work-plan/`
9. Request includes:
   - Activity text
   - Theme (if provided)
   - CSRF token
10. Request timeout: 120 seconds
11. Response received (JSON)
12. TableManager updates row with:
    - module → Moduł cell
    - curriculum_refs (array) → Podstawa Programowa cell (joined with ", ")
    - objectives (array) → Cele cell (joined with "\n")
13. Row state updated:
    - `aiGenerated = true`
    - `userEdited = false`
14. Button visibility updated:
    - "Wypełnij AI" hidden
    - "Generuj ponownie" shown
15. Loading state removed

**Result:**
- Moduł cell populated with module name
- Podstawa Programowa cell populated with curriculum codes
- Cele cell populated with objectives (multi-line)
- Aktywność unchanged
- Row shows "Generuj ponownie" instead of "Wypełnij AI"

**UI State:**
- Row marked as AI-generated internally
- Row not marked as user-edited
- Regenerate button visible

### Scenario 4.2: Generate AI for Row (Has Manual Metadata)

**Trigger:** User clicks "Wypełnij AI" button on row that already has some metadata

**Preconditions:**
- Activity field has text
- At least one metadata field (Moduł, Podstawa, or Cele) has manual content
- Row not AI-generated yet

**Steps:**
1. User clicks "Wypełnij AI"
2. System detects existing metadata
3. Confirmation modal appears:
   - Title: "Potwierdzenie"
   - Message: "Wiersz zawiera dane wprowadzone ręcznie. Nadpisać dane AI?"
   - Buttons: "Anuluj" / "Potwierdź"
4. If user clicks "Anuluj":
   - Modal closes
   - No changes made
   - Process ends
5. If user clicks "Potwierdź":
   - Modal closes
   - Continue with generation (same as Scenario 4.1 from step 5)

**Result:**
- If confirmed: Metadata overwritten with AI data
- If cancelled: No changes

**UI State:**
- Depends on user choice

### Scenario 4.3: Generate AI with Empty Activity

**Trigger:** User clicks "Wypełnij AI" on row with empty Activity field

**Steps:**
1. User clicks "Wypełnij AI"
2. System validates activity field
3. Alert modal appears:
   - Title: "Informacja"
   - Message: "Pole 'Aktywność' nie może być puste."
   - Button: "OK"
4. User clicks OK
5. Modal closes

**Result:**
- No AI generation occurs
- User must enter activity first

---

## 5. Single Row AI Regeneration

### Scenario 5.1: Regenerate AI (Not Edited by User)

**Trigger:** User clicks "Generuj ponownie" button (circular arrow icon)

**Preconditions:**
- Row was previously AI-generated
- User has not edited the metadata
- `userEdited = false`

**Steps:**
1. User clicks "Generuj ponownie"
2. No confirmation needed (not edited)
3. System validates activity field not empty
4. Same generation process as Scenario 4.1 (steps 5-15)
5. New AI data replaces old AI data

**Result:**
- Fresh AI-generated metadata
- May be different from previous generation
- Row remains AI-generated, not user-edited

**UI State:**
- `aiGenerated = true`
- `userEdited = false`

### Scenario 5.2: Regenerate AI (Edited by User)

**Trigger:** User clicks "Generuj ponownie" after editing AI-generated metadata

**Preconditions:**
- Row was previously AI-generated
- User has edited one or more metadata fields
- `userEdited = true`

**Steps:**
1. User clicks "Generuj ponownie"
2. System detects user edits
3. Confirmation modal appears:
   - Title: "Potwierdzenie"
   - Message: "Wiersz był zmodyfikowany. Nadpisać dane wprowadzone przez użytkownika?"
   - Buttons: "Anuluj" / "Potwierdź"
4. If user clicks "Anuluj":
   - Modal closes
   - No changes
   - Process ends
5. If user clicks "Potwierdź":
   - Modal closes
   - Generation proceeds (same as Scenario 4.1 from step 5)
6. User edits overwritten with new AI data
7. `userEdited` reset to false

**Result:**
- If confirmed: User edits lost, replaced with fresh AI data
- If cancelled: User edits preserved

**UI State:**
- If regenerated: `aiGenerated = true`, `userEdited = false`
- If cancelled: `aiGenerated = true`, `userEdited = true`

### Scenario 5.3: Regenerate with Empty Activity

**Trigger:** User clicks "Generuj ponownie" but activity field is empty

**Steps:**
1. User clicks "Generuj ponownie"
2. System validates activity field
3. Alert modal appears:
   - Message: "Pole 'Aktywność' nie może być puste."
4. User clicks OK

**Result:**
- No regeneration occurs

---

## 6. Bulk AI Generation

### Scenario 6.1: Bulk Generate (All Rows Ready)

**Trigger:** User clicks "Wypełnij wszystko AI" button

**Preconditions:**
- Multiple rows have activity text
- Those rows have empty metadata (no AI data, no manual data)

**Steps:**
1. User clicks "Wypełnij wszystko AI"
2. System calls TableManager.getRowsNeedingGeneration()
3. System filters rows:
   - Include: has activity AND no AI-generated data AND no user edits AND empty metadata
   - Exclude: rows without activity, or with existing AI/manual data
4. System counts eligible rows (e.g., 3 rows)
5. Progress container becomes visible
6. Progress bar set to 0%
7. Progress text: "Przetwarzanie... (0/3)"
8. Bulk generate button disabled and shows spinner
9. Button text: "Przetwarzanie..."
10. All eligible rows enter loading state simultaneously
11. For each row sequentially:
    - Make individual POST request to `/api/fill-work-plan/`
    - Timeout: 120 seconds per request
    - Wait for response
    - If success:
      - Update row with metadata
      - Mark as AI-generated
      - Increment success count
    - If error:
      - Log error
      - Add to failed list
      - Continue to next row
    - Clear loading state for this row
    - Update progress:
      - Progress bar: `(completed / total) * 100`%
      - Progress text: "Przetwarzanie... (X/Y)"
12. After all rows processed:
    - If all successful:
      - Progress text: "Ukończono: X/Y"
      - Alert modal: Success message
    - If some failed:
      - Progress text: "Ukończono: X/Y. Nieudane: Z"
      - Error modal with details:
        - Message: "Przetworzono pomyślnie: X/Y"
        - List of failures with activity text and error
13. Progress bar hidden after 2 seconds
14. Bulk button re-enabled
15. Button text restored: "Wypełnij wszystko AI"

**Result:**
- All eligible rows processed
- Successful rows have AI metadata
- Failed rows remain unchanged
- User informed of results

**UI State:**
- Successful rows: `aiGenerated = true`, show "Generuj ponownie"
- Failed rows: unchanged
- All rows unlocked

### Scenario 6.2: Bulk Generate (No Eligible Rows)

**Trigger:** User clicks "Wypełnij wszystko AI" when no rows need generation

**Preconditions:**
- All rows either have no activity, or already have AI/manual data

**Steps:**
1. User clicks "Wypełnij wszystko AI"
2. System calls getRowsNeedingGeneration()
3. Returns empty array
4. Alert modal appears:
   - Message: "Brak nowych aktywności do przetworzenia. Wszystkie wiersze są już wypełnione lub puste."
   - Button: "OK"
5. User clicks OK
6. Modal closes

**Result:**
- No processing occurs
- No changes to table

### Scenario 6.3: Bulk Generate with Partial Failures

**Trigger:** Some API calls succeed, others fail

**Steps:**
1. Bulk generation starts (Scenario 6.1, steps 1-11)
2. During processing:
   - Row 1: Success
   - Row 2: Timeout (120s)
   - Row 3: Network error
   - Row 4: Success
3. After completion:
   - Progress text: "Ukończono: 2/4. Nieudane: 2"
   - Error modal shows:
     ```
     Przetworzono pomyślnie: 2/4

     Nieudane wiersze (2):

     • Malowanie liści farbami...
       Błąd: Przekroczono limit czasu

     • Sortowanie kasztanów według wielkości...
       Błąd: Nie można połączyć z usługą AI
     ```
4. User clicks "Zamknij"
5. Progress hidden after 2s

**Result:**
- Partial success
- Successful rows populated
- Failed rows unchanged
- User can retry failed rows individually

---

## 7. Row Management

### Scenario 7.1: Add New Row

**Trigger:** User clicks "Dodaj wiersz" button

**Steps:**
1. User clicks "Dodaj wiersz"
2. TableManager.addRows(1) called
3. System increments nextRowId counter
4. New row created from template
5. Row assigned unique ID (e.g., "row_6")
6. Row appended to table bottom
7. Row state initialized:
   - All fields empty
   - `aiGenerated = false`
   - `userEdited = false`
8. Event listeners attached

**Result:**
- New empty row appears at table bottom
- Row fully functional (editable, has buttons)
- Shows "Wypełnij AI" button
- Has delete button and checkbox

**UI State:**
- Table now has N+1 rows
- New row ready for data entry

### Scenario 7.2: Delete Row

**Trigger:** User clicks delete button (X icon) on a row

**Steps:**
1. User clicks delete button
2. No confirmation dialog (immediate delete)
3. TableManager.deleteRow(rowId) called
4. DOM row element removed
5. Row state removed from Map

**Result:**
- Row permanently removed from table
- Other rows remain
- No way to undo

**UI State:**
- Table now has N-1 rows
- Row data lost (no persistence in MVP)

**Note:** This is intentional immediate deletion with no confirmation. If a user accidentally deletes a row with valuable data, they cannot recover it.

### Scenario 7.3: Clear All Rows

**Trigger:** User clicks "Wyczyść wszystko" button

**Steps:**
1. User clicks "Wyczyść wszystko"
2. Confirmation modal appears:
   - Title: "Potwierdzenie"
   - Message: "Czy na pewno chcesz wyczyść wszystkie wiersze?"
   - Buttons: "Anuluj" / "Potwierdź"
3. If "Anuluj":
   - Modal closes
   - No changes
4. If "Potwierdź":
   - Modal closes
   - All rows removed from table
   - Row state Map cleared
   - nextRowId reset to 1
   - Theme input cleared
   - 5 new empty rows created
   - Event listeners reattached

**Result:**
- If confirmed: Complete reset to initial state
- If cancelled: No changes

**UI State:**
- Fresh start with 5 empty rows
- All previous data lost

---

## 8. Table Copying

### Scenario 8.1: Copy Entire Table (No Selection)

**Trigger:** User clicks "Skopiuj tabelę" when no checkboxes are checked

**Preconditions:**
- Table has at least one row
- No row checkboxes are checked

**Steps:**
1. User clicks "Skopiuj tabelę"
2. System queries all rows
3. No checked checkboxes found
4. System decides to copy entire table
5. HTML table built:
   - Includes headers: Moduł, Podstawa Programowa, Cele, Aktywność
   - Includes all rows
   - Styled with borders and padding
   - Objectives preserve newlines (white-space: pre-wrap)
6. Plain text (TSV) version built:
   - Tab-separated values
   - Headers included
   - Each row on new line
7. Both formats copied to clipboard using ClipboardItem API
8. Alert modal appears:
   - Message: "Skopiowano całą tabelę (N wierszy) do schowka."
9. User clicks OK

**Result:**
- Table copied to clipboard in both HTML and TSV formats
- Can paste into Google Docs (HTML formatting preserved)
- Can paste into Excel/Sheets (TSV interpreted)
- Original table unchanged

**UI State:**
- No changes to UI
- Clipboard contains data

### Scenario 8.2: Copy Selected Rows

**Trigger:** User checks some row checkboxes and clicks copy

**Preconditions:**
- User has checked one or more row checkboxes

**Steps:**
1. User checks checkboxes on rows 2, 4, and 5
2. Copy button label updates to: "Skopiuj zaznaczone (3)"
3. User clicks "Skopiuj zaznaczone (3)"
4. System queries all rows
5. Filters to checked rows only (2, 4, 5)
6. HTML table built:
   - **No headers** (selective copy)
   - Only selected rows
   - Same styling as full table
7. Plain text (TSV) built:
   - **No headers**
   - Only selected rows
8. Both formats copied to clipboard
9. Alert modal:
   - Message: "Skopiowano 3 zaznaczonych wierszy do schowka."
10. User clicks OK
11. All checkboxes automatically unchecked
12. Button label returns to: "Skopiuj tabelę"

**Result:**
- Selected rows copied without headers
- Easy to paste into existing tables
- Checkboxes cleared after copy
- UI returns to default state

**UI State:**
- Checkboxes unchecked
- Button label reset

### Scenario 8.3: Copy with No Rows

**Trigger:** User clicks copy when table is empty (edge case)

**Steps:**
1. User has deleted all rows (or table somehow empty)
2. User clicks "Skopiuj tabelę"
3. System finds 0 rows
4. Alert modal:
   - Message: "Brak wierszy do skopiowania."
5. User clicks OK

**Result:**
- No copy action
- User informed

### Scenario 8.4: Checkbox Selection Updates Button Label

**Trigger:** User checks/unchecks row checkboxes

**Steps:**
1. Initial state: No checkboxes checked
2. Button shows: "Skopiuj tabelę"
3. User checks row 1 checkbox
4. Change event fires
5. updateCopyButtonLabel() called
6. Button updates: "Skopiuj zaznaczone (1)"
7. User checks row 3 checkbox
8. Button updates: "Skopiuj zaznaczone (2)"
9. User unchecks row 1
10. Button updates: "Skopiuj zaznaczone (1)"
11. User unchecks row 3
12. Button updates: "Skopiuj tabelę"

**Result:**
- Button label dynamically reflects selection count
- Real-time feedback

**Implementation Note:**
- MutationObserver watches for row additions/deletions
- Event delegation on tbody for checkbox changes

### Scenario 8.5: Copy Fails (Browser Permission)

**Trigger:** Clipboard API fails (rare - usually permissions or old browser)

**Steps:**
1. User clicks copy
2. System attempts clipboard.write()
3. Browser throws error (permission denied or unsupported)
4. Error caught
5. Error modal appears:
   - Message: "Nie udało się skopiować do schowka. Spróbuj ponownie."
6. User clicks Zamknij

**Result:**
- Copy failed
- User can retry
- May need to manually copy/paste

---

## 9. Curriculum Reference Tooltips

### Scenario 9.1: View Curriculum Tooltip (Single Code)

**Trigger:** User hovers over Podstawa Programowa cell containing curriculum code

**Preconditions:**
- Cell contains curriculum reference code (e.g., "4.15")

**Steps:**
1. User moves mouse over Podstawa Programowa cell
2. Mouseover event fires (event delegation on tbody)
3. System detects cell type
4. System extracts text content
5. Regex pattern matches codes: `/[IVX]+\.\d+\.\d+|\d+\.\d+/g`
6. Code found: "4.15"
7. Current hovered element stored
8. 300ms delay timer starts
9. User keeps mouse over cell (doesn't leave)
10. After 300ms:
    - Check cache for "4.15"
    - If not cached, fetch from `/api/curriculum-refs/4.15/`
    - Request timeout: 10 seconds
    - Response: `{full_text: "Dziecko potrafi..."}`
    - Cache result
11. Tooltip content built:
    - `<strong>4.15:</strong> Dziecko potrafi...`
12. Tooltip positioned:
    - Calculate cell position
    - Try to place above cell
    - If not enough space, place below
    - Center horizontally
    - Keep within viewport bounds
13. Tooltip display set to "block" (becomes visible)

**Result:**
- White tooltip box appears above/below cell
- Shows curriculum code and full text
- Remains visible while hovering

**UI State:**
- Tooltip visible
- Positioned near cell

### Scenario 9.2: View Curriculum Tooltip (Multiple Codes)

**Trigger:** User hovers over cell with multiple codes (e.g., "4.15, 4.18, I.1.2")

**Steps:**
1. Mouseover on cell
2. Regex matches: ["4.15", "4.18", "I.1.2"]
3. 300ms delay
4. For each code:
   - Check cache
   - If not cached, fetch from API
   - All fetches done in parallel (Promise.all)
5. All responses received
6. Tooltip content built:
   ```
   <strong>4.15:</strong> Dziecko potrafi przeliczać...

   <strong>4.18:</strong> Dziecko rozpoznaje cyfry...

   <strong>I.1.2:</strong> Dziecko rozumie polecenia...
   ```
7. Tooltip positioned and shown

**Result:**
- Tooltip shows all curriculum codes with descriptions
- Separated by double line breaks
- All codes explained in one tooltip

### Scenario 9.3: Hide Tooltip on Mouse Leave

**Trigger:** User moves mouse away from curriculum cell

**Steps:**
1. Tooltip currently visible
2. User moves mouse off cell
3. Mouseout event fires
4. Delay timer cleared (if still waiting)
5. currentHoveredElement cleared
6. Tooltip display set to "none"

**Result:**
- Tooltip disappears
- No delay for hiding (immediate)

### Scenario 9.4: Tooltip API Timeout

**Trigger:** Curriculum API slow or unavailable

**Steps:**
1. User hovers over cell with code "4.15"
2. 300ms delay passes
3. Fetch request sent
4. 10 seconds pass with no response
5. AbortController aborts request
6. Error caught
7. Fallback text returned: "Przekroczono limit czasu pobierania opisu"
8. Tooltip shows with error message

**Result:**
- Tooltip still appears
- Shows timeout message instead of full text

### Scenario 9.5: Curriculum Code Not Found

**Trigger:** Cell contains invalid or unknown code

**Steps:**
1. User hovers over cell with "99.99" (not in database)
2. Fetch request to `/api/curriculum-refs/99.99/`
3. API returns 404 error
4. Error caught
5. Fallback text: "Nie znaleziono opisu dla kodu: 99.99"
6. Tooltip shows with error message

**Result:**
- Tooltip appears with "not found" message
- User knows code is invalid

### Scenario 9.6: Hover Over Tooltip Itself

**Trigger:** User moves mouse from cell onto tooltip

**Steps:**
1. Tooltip visible
2. User moves mouse onto tooltip element
3. Mouseenter event on tooltip (optional feature)
4. Tooltip remains visible

**Result:**
- Tooltip stays visible
- User can read long text or select text if needed

**Steps to dismiss:**
1. User moves mouse away from tooltip
2. Mouseleave event fires
3. Tooltip hidden

### Scenario 9.7: Quick Hover (Under 300ms)

**Trigger:** User quickly moves mouse across cells

**Steps:**
1. User hovers over Podstawa cell
2. Delay timer starts (300ms)
3. After 100ms, user moves mouse away
4. Mouseout fires
5. Timer cleared
6. Tooltip never appears

**Result:**
- No tooltip shown
- Prevents flickering/annoying tooltips during mouse movement

---

## 10. Error Handling

### Scenario 10.1: Network Error During Generation

**Trigger:** Network connection lost or API unreachable

**Steps:**
1. User clicks "Wypełnij AI"
2. Fetch request sent
3. Network error occurs (cannot connect)
4. Error caught in catch block
5. Error type checked
6. User-friendly message determined: "Nie można połączyć z usługą AI. Sprawdź połączenie internetowe."
7. Error modal appears (red header, exclamation icon)
8. Modal body shows error message
9. User clicks "Zamknij"

**Result:**
- Row unchanged
- User can retry when connection restored
- Loading state cleared

### Scenario 10.2: Request Timeout (120s)

**Trigger:** AI service takes too long to respond

**Steps:**
1. User clicks "Wypełnij AI"
2. Fetch request sent with AbortController
3. Timeout timer set for 120 seconds
4. 120 seconds pass without response
5. AbortController.abort() called
6. Fetch aborts with AbortError
7. Error caught
8. Error name === 'AbortError'
9. User-friendly message: "Żądanie przekroczyło limit czasu (120s). Spróbuj ponownie."
10. Error modal shown

**Result:**
- Row unchanged
- User can retry
- Suggests trying again

### Scenario 10.3: Server Error (500)

**Trigger:** Backend API returns error response

**Steps:**
1. User clicks "Wypełnij AI"
2. Request sent
3. Server returns status 500
4. Response JSON: `{error: "Internal server error"}`
5. Response not OK (status >= 400)
6. Error thrown with server error message
7. Error modal shows server error

**Result:**
- Row unchanged
- User sees specific error from server

### Scenario 10.4: Invalid API Response

**Trigger:** API returns unexpected data format

**Steps:**
1. User clicks "Wypełnij AI"
2. Request sent
3. Response JSON missing required fields
4. JavaScript error occurs when accessing data.module
5. Error caught
6. Generic message: "Wystąpił nieoczekiwany błąd."
7. Error modal shown

**Result:**
- Row unchanged
- User informed of issue

### Scenario 10.5: Bulk Generation with All Failures

**Trigger:** All rows fail during bulk generation

**Steps:**
1. User clicks "Wypełnij wszystko AI" for 5 rows
2. All 5 requests fail (e.g., service down)
3. Progress updates: 0/5, 1/5, 2/5, 3/5, 4/5, 5/5
4. succeeded = 0, failed.length = 5
5. Progress text: "Ukończono: 0/5. Nieudane: 5"
6. Error modal shows full failure list
7. User clicks Zamknij

**Result:**
- No rows changed
- All rows remain unchanged
- User can check connection and retry

---

## 11. Loading States

### Scenario 11.1: Single Row Loading

**Trigger:** AI generation in progress for one row

**Visual Changes:**
- Row gets CSS class "loading"
- Row overlay appears (semi-transparent gray)
- Spinner shown over row
- All buttons in row disabled

**Duration:**
- From fetch start to response received
- Maximum 120 seconds (timeout)

**User Restrictions:**
- Cannot click row buttons
- Can still edit cells (not recommended during loading)
- Can interact with other rows

### Scenario 11.2: Bulk Generation Loading

**Trigger:** Bulk AI generation in progress

**Visual Changes:**
- Progress container appears below table
- Progress bar animates from 0% to 100%
- Progress text shows count: "Przetwarzanie... (X/Y)"
- Bulk generate button disabled
- Button shows spinner and "Przetwarzanie..." text
- All processing rows show row loading overlays

**Duration:**
- From start to all rows processed
- Can take several minutes for many rows

**User Restrictions:**
- Cannot click bulk generate again
- Can interact with other buttons (Add Row, Clear All, etc.)
- Can edit cells (not recommended)

### Scenario 11.3: Tooltip Loading

**Trigger:** Curriculum tooltip fetching from API

**Visual Changes:**
- No visible loading indicator (design choice)
- Tooltip appears when data ready

**Duration:**
- Up to 10 seconds timeout
- Usually < 1 second

**Note:** Could add loading spinner in tooltip for long fetches, but current implementation waits until data ready.

---

## 12. State Tracking & Persistence

### Scenario 12.1: Row State Tracking

**Internal State (per row in TableManager.rows Map):**

```javascript
{
  module: '',           // Current text in Moduł cell
  curriculum: '',       // Current text in Podstawa cell
  objectives: '',       // Current text in Cele cell
  activity: '',         // Current text in Aktywność cell
  aiGenerated: false,   // True if AI has generated metadata
  userEdited: false     // True if user edited AI-generated metadata
}
```

**State Transitions:**

1. **Initial:** `aiGenerated=false, userEdited=false`
2. **After AI generation:** `aiGenerated=true, userEdited=false`
3. **After user edits AI data:** `aiGenerated=true, userEdited=true`
4. **After regenerate:** `aiGenerated=true, userEdited=false` (reset)

**Usage:**
- `aiGenerated` controls button visibility (Generate vs Regenerate)
- `userEdited` controls regenerate confirmation
- Used in getRowsNeedingGeneration() to filter bulk operations

### Scenario 12.2: Session Persistence (MVP Limitation)

**What Persists:**
- Nothing (all data in memory only)

**What Doesn't Persist:**
- Table data (rows, content)
- Theme input
- Row states

**On Page Reload:**
- Complete reset
- 5 empty rows
- Empty theme
- All data lost

**Future Enhancement:**
- Add localStorage or backend persistence
- Save/load functionality
- Session recovery

### Scenario 12.3: Tooltip Cache

**Cache Storage:**
- AIService.tooltipCache Map
- Key: curriculum code (e.g., "4.15")
- Value: full text string

**Lifetime:**
- Persists for page session
- Cleared on page reload
- No size limit (grows with usage)

**Benefit:**
- Hovering over same code twice: instant tooltip
- Reduces API calls
- Better UX (no delay)

---

## UI Component Reference

### Buttons

| Button | Icon | Location | Purpose |
|--------|------|----------|---------|
| Wypełnij wszystko AI | Magic wand | Top bar | Bulk generate AI for all eligible rows |
| Dodaj wiersz | Plus circle | Top bar | Add one empty row to table |
| Wyczyść wszystko | Trash | Top bar | Clear all rows (with confirmation) |
| Skopiuj tabelę | Clipboard | Top bar | Copy table to clipboard |
| Wypełnij AI | Magic wand | Per row | Generate AI for single row |
| Generuj ponownie | Circular arrow | Per row | Regenerate AI for row (shown after first generation) |
| Delete Row | X circle | Per row | Delete specific row |
| Row Checkbox | Checkbox | Per row | Select row for copying |

### Modals

| Modal | Color | Purpose | Buttons |
|-------|-------|---------|---------|
| Confirmation Modal | Yellow | Ask user to confirm action | Anuluj, Potwierdź |
| Alert Modal | Blue | Show information | OK |
| Error Modal | Red | Show error message | Zamknij |

### Visual Elements

| Element | Purpose |
|---------|---------|
| Curriculum Tooltip | Show full text for curriculum codes on hover |
| Progress Bar | Show bulk generation progress |
| Row Loading Overlay | Indicate row is processing |
| Spinner | Show button is busy |

---

## Edge Cases & Special Scenarios

### Edge Case 1: Delete All Rows Manually

**Scenario:** User deletes all rows one by one

**Result:**
- Table becomes empty (0 rows)
- User can still click "Dodaj wiersz" to add new ones
- "Wyczyść wszystko" does nothing (no rows to clear)

### Edge Case 2: Very Long Text in Cells

**Scenario:** User enters or AI generates very long text

**Behavior:**
- Cells expand vertically (no horizontal scroll)
- Table remains responsive
- Copy preserves all text

### Edge Case 3: Special Characters in Data

**Scenario:** Text contains HTML special characters (<, >, &, quotes)

**Behavior:**
- Display: Shown correctly (contenteditable handles it)
- Copy: HTML-escaped in escapeHtml() function
- Safe from XSS

### Edge Case 4: Rapid Button Clicking

**Scenario:** User clicks "Wypełnij AI" multiple times quickly

**Behavior:**
- First click: Button disabled, loading starts
- Subsequent clicks: Ignored (button disabled)
- Prevents duplicate requests

### Edge Case 5: Navigate Away During Generation

**Scenario:** User closes tab or navigates away during AI generation

**Behavior:**
- Fetch aborted by browser
- No data saved (MVP has no persistence)
- Data lost

**Future Enhancement:** Add beforeunload warning

### Edge Case 6: Paste Data Into Cells

**Scenario:** User pastes multi-line or formatted text into cell

**Behavior:**
- Contenteditable accepts paste
- Formatting may be preserved (depends on source)
- Works but may have unexpected formatting

**Note:** Plain text paste recommended

### Edge Case 7: Empty Table Copy

**Scenario:** All rows are empty (no content)

**Behavior:**
- Copy still works
- Creates table with empty cells
- User notified: "Skopiowano całą tabelę (N wierszy)"

### Edge Case 8: Curriculum Code Partial Match

**Scenario:** Cell contains text like "Zobacz 4.15 oraz coś więcej"

**Behavior:**
- Regex matches "4.15"
- Tooltip shows for that code
- Other text ignored

---

## Keyboard Accessibility

### Tab Navigation

**Current Implementation:**
- Tab through cells (contenteditable)
- Tab through buttons
- Tab through top action buttons
- Tab through modal buttons when modal open

**Note:** Full keyboard accessibility not fully implemented in MVP. Future enhancement could add:
- Keyboard shortcuts (e.g., Ctrl+S to save)
- Enter to submit form
- Escape to close modals
- Arrow keys for table navigation

---

## Mobile/Touch Support

**Current State:**
- Desktop-first design (per PRD)
- Touch works but not optimized
- Small buttons on mobile
- Tooltips may not work well (hover-based)

**Future Enhancement:**
- Responsive design
- Touch-friendly buttons
- Tap instead of hover for tooltips

---

## Browser Compatibility

### Required Features

- **Clipboard API:** For copying table (navigator.clipboard.write)
- **Fetch API:** For AJAX requests
- **ContentEditable:** For editable cells
- **Template Element:** For row cloning
- **Modern JavaScript:** ES6+ (const, let, arrow functions, async/await, Maps)
- **Bootstrap 5:** Modals and styling

### Supported Browsers

- Chrome/Edge 90+
- Firefox 90+
- Safari 14+

### Potential Issues

- **Older browsers:** No Clipboard API (copy fails)
- **Safari quirks:** Clipboard API may require user gesture
- **Mobile Safari:** ContentEditable quirks

---

## Performance Considerations

### Optimization Strategies

1. **Event Delegation:** tbody listener instead of per-row listeners
2. **Tooltip Caching:** Avoid redundant API calls
3. **Sequential Bulk Processing:** Prevents overwhelming server
4. **AbortController:** Proper timeout handling

### Known Limitations

1. **No Pagination:** Large tables (100+ rows) may slow down
2. **No Virtual Scrolling:** All rows in DOM
3. **Tooltip Regex:** Runs on every hover (acceptable for small cells)

### Future Optimizations

- Virtualize table for 1000+ rows
- Debounce input events
- Web Worker for bulk processing coordination

---

## Summary of All User Interaction Paths

1. **Happy Path - Basic Usage:**
   - Load page → Enter theme → Enter 5 activities → Click "Wypełnij wszystko AI" → Wait for generation → Copy table → Done

2. **Power User Path:**
   - Load page → Enter activities → Generate individual rows → Edit some results → Regenerate specific rows → Add more rows → Selective copy → Done

3. **Manual Entry Path:**
   - Load page → Manually fill all metadata → No AI used → Copy table → Done

4. **Mixed Approach:**
   - Enter activities → Generate AI → Edit results → Add manual rows → Delete unwanted rows → Copy selected rows → Done

5. **Error Recovery:**
   - Start generation → Network error → Retry → Timeout → Switch to manual entry → Complete manually → Copy → Done

---

## Quick Reference: Button State Logic

| Row State | Generate Button | Regenerate Button |
|-----------|----------------|------------------|
| Empty row, no AI | Shown | Hidden |
| Has activity, no AI | Shown (enabled) | Hidden |
| Has activity, AI generated | Hidden | Shown |
| Has activity + AI, user edited | Hidden | Shown (confirms on click) |
| Loading | Disabled | Disabled |

## Quick Reference: Bulk Generate Filter Logic

**Row is eligible for bulk generation IF:**
- ✅ Has activity text
- ✅ aiGenerated = false
- ✅ userEdited = false
- ✅ All metadata fields empty (module, curriculum, objectives)

**Row is excluded from bulk generation IF:**
- ❌ No activity
- ❌ Already AI-generated
- ❌ Has user edits
- ❌ Has any manual metadata

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-09 | Initial comprehensive UI scenarios documentation |

---

**End of Document**
