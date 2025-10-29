# Product Requirements Document (PRD)
## Teacher Assist - AI-Powered Lesson Planning Tool

**Version:** 1.0
**Date:** 2025-10-28
**Status:** MVP Definition
**Project Type:** Training/Learning Project

---

## Executive Summary

Teacher Assist is a web-based tool designed to help Polish kindergarten teachers efficiently plan their monthly lessons by automatically generating educational metadata (modules, curriculum references, and objectives) based on planned activities. The MVP focuses on a single-session, local deployment with AI-powered autofill capabilities.

---

## 1. Problem Statement

### Current Situation
Polish kindergarten teachers are required to document their lesson plans with:
- Educational module categorizations
- Core curriculum (Podstawa Programowa) paragraph references
- Educational objectives aligned with activities

This documentation is time-consuming and repetitive, taking valuable time away from actual teaching preparation.

### User Pain Points
- Manual lookup of curriculum paragraph numbers
- Repetitive writing of educational objectives
- Difficulty mapping creative activities to standardized educational modules
- Time spent on administrative documentation vs. creative lesson planning

### Proposed Solution
An AI-powered web application that:
- Accepts simple activity descriptions in Polish
- Automatically generates appropriate educational metadata
- Provides interactive curriculum reference information
- Optimizes output for easy transfer to Google Docs

---

## 2. Goals and Objectives

### Primary Goal
Reduce time spent on lesson plan documentation by 60-70% through AI-assisted metadata generation.

### Secondary Goals
- Provide accurate curriculum references aligned with Polish educational standards
- Maintain teacher autonomy through manual override capabilities
- Create an intuitive interface requiring minimal training

### Learning Objectives (Training Project)
- Explore Claude Code workflows and capabilities
- Gain practical experience with Django web framework
- Implement LangGraph for multi-step AI workflows
- Understand REST API architecture between separate services

---

## 3. Target Users

### Primary User Persona: "Ania - The Experienced Teacher"
- **Role:** Kindergarten teacher with 5+ years experience
- **Technical Skill:** Moderate (comfortable with Google Docs, basic web apps)
- **Environment:** Uses laptop for lesson planning at home
- **Goals:** Spend less time on paperwork, more time on creative activities
- **Pain Point:** Knows what activities work but struggles with formal documentation

### Usage Context
- Local deployment on personal computer
- Used weekly/monthly during lesson planning sessions
- Single user (no collaboration features needed for MVP)
- Session-based workflow (plan, generate, copy to Google Docs, close)

---

## 4. MVP Scope

### In Scope
✅ Single-page web interface with data table

✅ AI-powered metadata generation (modules, curriculum refs, objectives)

✅ Manual activity entry and AI content override

✅ Per-row and bulk autofill options

✅ Interactive curriculum reference tooltips

✅ Polish language interface and AI responses

✅ Basic error handling and loading states

✅ Browser copy-paste optimization


### Out of Scope (Future Phases)
❌ Data persistence between sessions

❌ User authentication

❌ Multiple teacher accounts

❌ Export functionality (CSV, PDF, etc.)

❌ Activity templates or libraries

❌ Collaboration features

❌ Mobile responsive design

❌ Print formatting

---

## 5. User Stories

### Core Workflow
**As a kindergarten teacher,**
**I want to** enter my planned activities for the week,
**So that** I can quickly generate the required documentation metadata.

### Detailed User Stories

#### Story 1: Initial Setup
```
Given I open the Teacher Assist application
When the page loads
Then I see:
  - A text field for entering weekly theme
  - A table with 5 empty rows
  - Columns: Moduł, Podstawa Programowa, Cele, Aktywność
  - Autofill buttons (single and bulk)
```

#### Story 2: Enter Activities
```
Given I have a weekly theme "Jesień - zbiory"
When I enter the theme and fill activity descriptions:
  - Row 1: "Zabawa w sklep z owocami"
  - Row 2: "Malowanie liści farbami"
  - Row 3: "Sortowanie kasztanów według wielkości"
Then I can trigger AI autofill for each row
```

#### Story 3: Single Row Autofill
```
Given I have entered an activity in row 1
When I click the autofill button for that row
Then the system:
  1. Shows loading indicator
  2. Calls AI service with activity + theme
  3. Populates Moduł, Podstawa Programowa, Cele
  4. Allows me to edit any generated content
```

#### Story 4: Bulk Autofill
```
Given I have entered activities in rows 1-3
When I click "Autofill All" button
Then the system:
  1. Shows loading indicator
  2. Processes each row sequentially
  3. Populates all metadata fields
  4. Handles individual failures gracefully
```

#### Story 5: Manual Override
```
Given AI has generated metadata for a row
When I click on any metadata field
Then I can edit the content manually
And my changes are preserved
```

#### Story 6: Curriculum Reference Lookup
```
Given a Podstawa Programowa field shows "I.1.2, II.3.1"
When I hover over the reference numbers
Then a tooltip displays the full curriculum text
```

#### Story 7: Add More Rows
```
Given I have filled all 5 initial rows
When I need to add more activities
Then I can click "Add Row" button
And a new empty row appears at the bottom
```

#### Story 8: Clear and Restart
```
Given I have completed a lesson plan
When I want to start a new plan
Then I click "Clear All" button
And the table resets to 5 empty rows
```

#### Story 9: Error Handling
```
Given the AI service is unavailable
When I trigger autofill
Then the system:
  1. Shows loading indicator for max 120 seconds
  2. Displays error message in Polish
  3. Allows me to enter data manually
```

#### Story 10: Regenerate Content
```
Given AI has generated metadata I'm not satisfied with
When I click "Regenerate" for that row
Then the system calls AI again with the same input
And updates the metadata with new suggestions
```

---

## 6. Functional Requirements

### 6.1 User Interface Components

#### Theme Input Field
- **Type:** Single-line text input
- **Label:** "Temat tygodnia:" (Weekly theme)
- **Placeholder:** "np. Jesień - zbiory"
- **Required:** No (optional context for AI)
- **Max Length:** 200 characters

#### Data Table
- **Initial Rows:** 5
- **Expandable:** Yes (via "Add Row" button)
- **Removable:** Individual rows can be deleted
- **Columns:**
  1. **Moduł** (Educational Module)
     - Width: ~20%
     - Editable: Yes
     - Free text input
  2. **Podstawa Programowa** (Curriculum References)
     - Width: ~20%
     - Editable: Yes
     - Format: Comma-separated refs (e.g., "I.1.2, II.3.1")
     - Interactive: Hover shows tooltip with full text
  3. **Cele** (Educational Objectives)
     - Width: ~30%
     - Editable: Yes
     - Multi-line text (2-3 bullet points)
  4. **Aktywność** (Planned Activity)
     - Width: ~30%
     - Editable: Yes
     - User input (required for AI generation)

#### Autofill Buttons
- **Per-row Button:** "Wypełnij AI" on each row
  - Enabled when activity field has content
  - Disabled during loading
- **Bulk Button:** "Wypełnij wszystko AI"
  - Processes all rows with activities
  - Shows progress indicator
- **Regenerate Button:** "Generuj ponownie" on each row
  - Appears after AI has generated content
  - Calls AI again with same input

#### Action Buttons
- **Add Row:** "Dodaj wiersz"
- **Clear All:** "Wyczyść wszystko"
  - Requires confirmation dialog
- **Delete Row:** Icon/button on each row

#### Loading Indicators
- **Per-row Spinner:** Shows during individual autofill
- **Global Loading Bar:** Shows during bulk operations
- **Status Text:** "Przetwarzanie... (3/5)" for bulk operations

#### Error Messages
- **AI Service Timeout:** "Nie można połączyć z usługą AI. Wypełnij dane ręcznie."
- **Invalid Response:** "Otrzymano nieprawidłową odpowiedź. Spróbuj ponownie."
- **Network Error:** "Błąd połączenia. Sprawdź połączenie internetowe."

### 6.2 AI Integration Requirements

#### Input to AI Service
```json
{
  "activity": "Zabawa w sklep z owocami",
  "theme": "Jesień - zbiory"
}
```

#### Expected Output from AI Service
```json
{
  "modul": "Zabawy matematyczne",
  "podstawa_programowa": ["I.1.2", "II.3.1"],
  "cele": [
    "Rozwijanie umiejętności liczenia",
    "Poznawanie nazw owoców sezonowych"
  ]
}
```

#### AI Service Requirements
- **Response Time:** Target < 10 seconds per row
- **Timeout:** 120 seconds before showing error
- **Language:** All AI responses in Polish
- **Quality:** Must reference valid curriculum paragraphs
- **Flexibility:** AI can suggest new modules beyond predefined list

### 6.3 Business Rules

#### Validation Rules
- Activity field cannot be empty when triggering autofill
- Curriculum references must match format: Roman.Arabic.Arabic (e.g., "I.1.2")
- At least one row must have content to enable bulk autofill

#### Override Rules
- User edits always take precedence over AI suggestions
- Regenerate overwrites previous AI content (with user confirmation if edited)
- Manual edits are not sent back to AI service

#### Educational Module Rules
- Initial predefined list of common modules (to be defined)
- AI can suggest new modules not in list
- Free text entry allows teacher creativity

---

## 7. Technical Requirements

### 7.1 Architecture

#### Two-Process Design
```
User Browser (Polish UI)
       ↓
Django Web Server (localhost:8000)
   ├── Serves HTML/CSS/JS
   ├── Manages session data
   ├── Stores curriculum references (SQLite)
   └── Makes REST API calls
       ↓
LangGraph AI Service (localhost:8001)
   ├── Receives activity + theme
   ├── Processes via LangGraph workflow
   ├── Calls LLM via OpenRouter
   └── Returns structured JSON
```

### 7.2 Technology Stack

#### Django Web Server
- **Framework:** Django 5.2.7
- **Database:** SQLite (committed to git)
- **HTTP Client:** `requests` library
- **Frontend:** Django templates + vanilla JavaScript
- **Styling:** CSS (Bootstrap or Tailwind optional)

#### LangGraph AI Service
- **Framework:** FastAPI or Flask
- **AI Orchestration:** LangGraph
- **LLM Gateway:** OpenRouter
- **Response Format:** JSON

### 7.3 API Contract

#### Endpoint: `POST http://localhost:8001/api/fill-work-plan`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "activity": "string (required, 1-500 chars)",
  "theme": "string (optional, 0-200 chars)"
}
```

**Success Response (200):**
```json
{
  "modul": "string",
  "podstawa_programowa": ["string", "string"],
  "cele": ["string", "string", "string"]
}
```

**Error Response (500/503):**
```json
{
  "error_code": "string (describing general error category)"
  "error": "string (error details)"
}
```

**Timeout:** 120 seconds

### 7.4 LangGraph Workflow

#### Workflow Steps (High-Level)
1. **Input Validation** - Check activity description quality
2. **Activity Classification** - Determine activity type and domain
3. **Module Mapping** - Select appropriate educational module
4. **Curriculum Lookup** - Find relevant Podstawa Programowa paragraphs
5. **Objective Generation** - Create 2-3 educational objectives in Polish
6. **Output Formatting** - Structure as JSON response

#### LLM Calls
- **Model Selection:** Configurable via OpenRouter (e.g., GPT-3.5-turbo, Claude Haiku for cost)
- **Budget Constraint:** ~$1/month (approximately 1,000,000 tokens at $0.001/1K)
- **Expected Usage:** ~20 lesson planning sessions per month (~50,000 tokens per session budget)
- **Token Optimization:** Use concise prompts, limit output tokens, choose cost-effective models

### 7.5 Database Schema

#### Table: `curriculum_references`
```sql
CREATE TABLE curriculum_references (
    id INTEGER PRIMARY KEY,
    reference_code VARCHAR(20) UNIQUE NOT NULL,  -- e.g., "I.1.2"
    full_text TEXT NOT NULL,                      -- Polish curriculum text
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Table: `educational_modules`
```sql
CREATE TABLE educational_modules (
    id INTEGER PRIMARY KEY,
    module_name VARCHAR(200) UNIQUE NOT NULL,    -- e.g., "Zabawy matematyczne"
    is_ai_suggested BOOLEAN DEFAULT TRUE,             -- True if AI-suggested
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Note:** Session data (themes, activities, generated metadata) is NOT persisted in MVP.

### 7.6 Performance Requirements

- **Page Load:** < 2 seconds
- **Single Row AI Generation:** < 30 seconds target, 120 seconds timeout
- **Bulk Autofill (5 rows):** < 150 seconds
- **Tooltip Display:** Instant (data preloaded)
- **Add/Delete Row:** Instant (client-side)

### 7.7 Security Requirements

**MVP (Local Deployment):**
- No authentication required
- No HTTPS required (localhost only)
- Development SECRET_KEY acceptable


**API Security:**
- OpenRouter API key stored in environment variable
- Not exposed to frontend
- LangGraph service only accepts localhost connections

---

## 8. UI/UX Specifications

### 8.1 Language and Localization
- **UI Language:** Polish
- **AI Responses:** Polish
- **Error Messages:** Polish
- **Placeholders/Labels:** Polish

### 8.2 Visual Design Principles
- **Clean and Simple:** Minimal distractions
- **Table-Centric:** Primary focus on data table
- **Copy-Paste Friendly:** Plain text, no complex formatting
- **Desktop-First:** Optimized for laptop screens (no mobile requirement)

### 8.3 Layout
```
┌─────────────────────────────────────────────────────────────┐
│  Teacher Assist - Planowanie Lekcji                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Temat tygodnia: [_________________________]                │
│                                                              │
│  [Wypełnij wszystko AI] [Dodaj wiersz] [Wyczyść]           │
│                                                              │
│  ┌──────────┬──────────┬──────────┬──────────────────┐    │
│  │ Moduł    │ Podstawa │ Cele     │ Aktywność        │    │
│  │          │ Program. │          │                  │    │
│  ├──────────┼──────────┼──────────┼──────────────────┤    │
│  │[______]  │[_______] │[_______] │[________] [↻][×]│    │
│  │          │          │          │                  │    │
│  ├──────────┼──────────┼──────────┼──────────────────┤    │
│  │[______]  │[_______] │[_______] │[________] [↻][×]│    │
│  │          │          │          │                  │    │
│  └──────────┴──────────┴──────────┴──────────────────┘    │
│                                                              │
│  [↻] = Wypełnij AI / Generuj ponownie                      │
│  [×] = Usuń wiersz                                          │
└─────────────────────────────────────────────────────────────┘
```

### 8.4 Interaction Patterns

#### Hover Tooltip (Curriculum References)
- **Trigger:** Mouse hover over reference code (e.g., "I.1.2")
- **Appearance:** White box with gray border, drops shadow
- **Content:** Full curriculum text
- **Positioning:** Above or below reference, stays on screen
- **Delay:** 300ms before showing
- **Dismiss:** Mouse leave

#### Loading States
- **Button State:** Disabled + spinner icon
- **Row State:** Light gray overlay with spinner
- **Bulk State:** Progress bar showing "X/Y completed"

#### Confirmation Dialogs
- **Clear All:** "Czy na pewno chcesz wyczyść wszystkie wiersze?"
- **Regenerate (if edited):** "Wiersz był zmodyfikowany. Nadpisać dane wprowadzone przez użytkownika?"

---

## 9. Data Requirements

### 9.1 Podstawa Programowa (Core Curriculum) Data
- **Source:** Official Polish kindergarten curriculum document
- **Format:** Reference code + full text
- **Storage:** SQLite database (pre-populated)
- **Quantity:** Estimated 50-100 paragraph references
- **Task:** Manual data entry or import script (separate task)

### 9.2 Educational Modules Initial List
**Suggested Categories:**
- Zabawy matematyczne (Mathematical games)
- Rozwój społeczny (Social development)
- Formy ekspresji artystycznej (Artistic expression)
- Rozwój emocjonalny (Emotional development)
- Aktywność fizyczna (Physical activity)
- Poznawanie przyrody (Nature exploration)
- Rozwój mowy i języka (Language development)
- Zabawy konstrukcyjne (Construction play)

**Note:** This list is not exhaustive; AI can suggest new modules.

---

## 10. Success Metrics

### MVP Validation Criteria
✅ Teacher can fill 5 activities and generate metadata in < 5 minutes

✅ AI-generated curriculum references are accurate ≥80% of the time

✅ AI-generated objectives are relevant and usable ≥80% of the time

✅ No critical bugs prevent core workflow completion

✅ Test teacher reports tool is "easier than manual method"

### Quality Metrics
- **Accuracy:** Curriculum references must be valid codes
- **Relevance:** Generated objectives align with activities
- **Language:** Natural Polish, no translation artifacts
- **Speed:** Perceived as faster than manual lookup

### Usage Metrics (Future - Post-MVP)
- Time saved per lesson plan
- Percentage of AI content kept vs. edited
- Most frequently regenerated fields
- Module suggestion acceptance rate

---

## 11. Development Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Django app with basic UI (table, forms, buttons)
- [ ] SQLite database with curriculum references
- [ ] Mock AI service returning hardcoded JSON
- [ ] Frontend-backend integration (no real AI)

### Phase 2: AI Integration (Week 3-4)
- [ ] LangGraph service setup with FastAPI
- [ ] OpenRouter integration
- [ ] Basic prompt engineering for metadata generation
- [ ] REST API connection between Django and LangGraph

### Phase 3: Polish & Test (Week 5)
- [ ] Error handling and loading states
- [ ] Curriculum reference tooltips
- [ ] Polish language refinement
- [ ] User testing with teacher
- [ ] Bug fixes and adjustments

### Phase 4: Future Enhancements (Post-MVP)
- [ ] Data persistence (save/load plans)
- [ ] Export functionality
- [ ] Activity templates
- [ ] Multi-user support

---

## 12. Risks and Mitigations

### Technical Risks

#### Risk: AI Service Downtime
- **Impact:** High - blocks core functionality
- **Mitigation:** Graceful degradation to manual entry, clear error messages

#### Risk: LLM API Cost Overruns
- **Impact:** Medium - budget constraints
- **Mitigation:** Token usage monitoring, model selection (cheaper options), rate limiting

#### Risk: Poor AI Quality
- **Impact:** High - tool becomes unusable
- **Mitigation:** Iterative prompt engineering, user can always regenerate or edit manually

### User Experience Risks

#### Risk: AI Suggestions Not Relevant
- **Impact:** Medium - user frustration
- **Mitigation:** Manual override always available, regenerate option

#### Risk: Complex UI
- **Impact:** Low - teacher doesn't adopt tool
- **Mitigation:** Single-page design, clear labels, minimal features

### Deployment Risks

#### Risk: Local Setup Complexity
- **Impact:** Medium - teacher can't run application
- **Mitigation:** Clear documentation, simple startup script, pre-configured database

---

## 13. Open Questions

### To Be Determined
1. **Specific LLM Model:** Which OpenRouter model provides best quality/cost ratio?
2. **Prompt Engineering:** Optimal prompts for Polish educational context
3. **Curriculum Data Entry:** Manual or automated import of Podstawa Programowa?
4. **Module Standardization:** Should new AI-suggested modules be saved and reused?
5. **Session Duration:** How long do typical planning sessions last (impacts session timeout)?

---

## 14. Appendices

### Appendix A: Polish Language Examples

**Theme Examples:**
- "Jesień - zbiory"
- "Zima i święta"
- "Wiosna i przyroda"

**Activity Examples:**
- "Zabawa w sklep z owocami"
- "Malowanie liści farbami"
- "Sortowanie kasztanów według wielkości"
- "Czytanie bajki o jeżu"

**Module Examples:**
- "Zabawy matematyczne"
- "Rozwój społeczny"
- "Formy ekspresji artystycznej"

**Objective Examples:**
- "Rozwijanie umiejętności liczenia"
- "Poznawanie nazw owoców sezonowych"
- "Kształtowanie umiejętności współpracy"

### Appendix B: Reference Documents
- CLAUDE.md - Development guidelines and git workflow
- projectPremise.md - Original project concept and UI specifications
- Podstawa Programowa - Official curriculum document (to be added)

---

## Document History

| Version | Date       | Author | Changes                    |
|---------|------------|--------|----------------------------|
| 1.0     | 2025-10-28 | PM     | Initial PRD for MVP        |

---

**Next Steps:**
2. Populate curriculum database
3. Begin Phase 1 development
4. Set up OpenRouter account
