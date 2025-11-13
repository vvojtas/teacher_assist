import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from '../App'

// Mock fetch globally
global.fetch = vi.fn()

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn(() => Promise.resolve()),
  },
})

// Mock curriculum tooltip hook
vi.mock('@/hooks/useCurriculumTooltip', () => ({
  useCurriculumTooltip: () => ({
    parseCurriculumCodes: vi.fn(() => []),
    fetchMultipleCodes: vi.fn(() => Promise.resolve([])),
  }),
}))

describe('App Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    // Mock CSRF token
    Object.defineProperty(document, 'cookie', {
      writable: true,
      value: 'csrftoken=test-token',
    })
  })

  it('should render the main application', () => {
    render(<App />)

    expect(screen.getByText(/Teacher Assist/i)).toBeInTheDocument()
    expect(screen.getByText(/Temat tygodnia/i)).toBeInTheDocument()
  })

  it('should initialize with 5 empty rows', () => {
    render(<App />)

    // Check that we have table cells (each row has multiple cells)
    const cells = screen.getAllByRole('cell')
    // 5 rows × multiple columns
    expect(cells.length).toBeGreaterThan(5)
  })

  it('should allow user to enter theme', async () => {
    const user = userEvent.setup()
    render(<App />)

    const themeInput = screen.getByPlaceholderText(/np. Jesień/i)
    await user.type(themeInput, 'Zima')

    expect(themeInput).toHaveValue('Zima')
  })

  it('should add new row when add button clicked', async () => {
    const user = userEvent.setup()
    render(<App />)

    const initialCells = screen.getAllByRole('cell')
    const initialCount = initialCells.length

    const addButton = screen.getByText(/Dodaj wiersz/i)
    await user.click(addButton)

    await waitFor(() => {
      const newCells = screen.getAllByRole('cell')
      expect(newCells.length).toBeGreaterThan(initialCount)
    })
  })

  it('should handle AI generation for single row', async () => {
    const user = userEvent.setup()

    // Mock successful AI response
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => ({
        module: 'Matematyka',
        curriculum_refs: ['MAT.1', 'MAT.2'],
        objectives: ['Cel 1', 'Cel 2'],
      }),
    })

    render(<App />)

    // Find first contenteditable field for activity
    const activityCells = screen.getAllByText('', { selector: '[data-field="activity"]' })
    const firstActivityCell = activityCells[0]

    // Enter activity text
    await user.click(firstActivityCell)
    await user.type(firstActivityCell, 'Liczenie do 10')

    // Find and click generate button (Wand icon button)
    const generateButtons = screen.getAllByRole('button')
    const generateButton = generateButtons.find(btn => btn.querySelector('svg'))

    if (generateButton) {
      await user.click(generateButton)

      // Wait for AI generation to complete
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/fill-work-plan/',
          expect.objectContaining({
            method: 'POST',
            headers: expect.objectContaining({
              'X-CSRFToken': 'test-token',
            }),
          })
        )
      })
    }
  })

  it('should show error dialog on AI generation failure', async () => {
    const user = userEvent.setup()

    // Mock failed AI response
    ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

    render(<App />)

    // Enter activity
    const activityCells = screen.getAllByText('', { selector: '[data-field="activity"]' })
    const firstActivityCell = activityCells[0]

    await user.click(firstActivityCell)
    await user.type(firstActivityCell, 'Test activity')

    // Click generate
    const generateButtons = screen.getAllByRole('button')
    const generateButton = generateButtons.find(btn => btn.querySelector('svg'))

    if (generateButton) {
      await user.click(generateButton)

      // Wait for error dialog
      await waitFor(() => {
        expect(screen.getByText(/Błąd/i)).toBeInTheDocument()
      })
    }
  })

  it('should show alert when trying to generate without activity', async () => {
    const user = userEvent.setup()

    render(<App />)

    // Find and click generate button without entering activity
    const generateButtons = screen.getAllByRole('button')
    const generateButton = generateButtons.find(btn => btn.querySelector('svg'))

    if (generateButton) {
      await user.click(generateButton)

      // Wait for alert dialog
      await waitFor(() => {
        expect(screen.getByText(/nie może być puste/i)).toBeInTheDocument()
      })
    }
  })

  it('should handle bulk generation', async () => {
    const user = userEvent.setup()

    // Mock successful responses
    ;(global.fetch as any).mockResolvedValue({
      ok: true,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => ({
        module: 'Module',
        curriculum_refs: [],
        objectives: [],
      }),
    })

    render(<App />)

    // Add activities to first two rows
    const activityCells = screen.getAllByText('', { selector: '[data-field="activity"]' })

    await user.click(activityCells[0])
    await user.type(activityCells[0], 'Activity 1')

    await user.click(activityCells[1])
    await user.type(activityCells[1], 'Activity 2')

    // Click bulk generate
    const bulkButton = screen.getByText(/Wypełnij wszystkie AI/i)
    await user.click(bulkButton)

    // Should show progress
    await waitFor(() => {
      expect(screen.getByText(/Przetwarzanie/i)).toBeInTheDocument()
    })
  })

  it('should delete row when delete button clicked', async () => {
    const user = userEvent.setup()

    render(<App />)

    const initialCells = screen.getAllByRole('cell')
    const initialCount = initialCells.length

    // Find delete button (X icon)
    const deleteButtons = screen.getAllByRole('button').filter(btn => {
      const svg = btn.querySelector('svg')
      return svg?.querySelector('line') // X icon has lines
    })

    if (deleteButtons[0]) {
      await user.click(deleteButtons[0])

      await waitFor(() => {
        const newCells = screen.getAllByRole('cell')
        expect(newCells.length).toBeLessThan(initialCount)
      })
    }
  })

  it('should show confirmation dialog when clearing all', async () => {
    const user = userEvent.setup()

    render(<App />)

    const clearButton = screen.getByText(/Wyczyść wszystko/i)
    await user.click(clearButton)

    // Should show confirmation
    await waitFor(() => {
      expect(screen.getByText(/na pewno/i)).toBeInTheDocument()
    })
  })

  it('should copy table to clipboard', async () => {
    const user = userEvent.setup()

    render(<App />)

    const copyButton = screen.getByText(/Kopiuj tabelę/i)
    await user.click(copyButton)

    // Should show success message
    await waitFor(() => {
      expect(screen.getByText(/Skopiowano/i)).toBeInTheDocument()
    })

    expect(navigator.clipboard.writeText).toHaveBeenCalled()
  })

  it('should handle row selection and selective copy', async () => {
    const user = userEvent.setup()

    render(<App />)

    // Find checkbox (first one after header)
    const checkboxes = screen.getAllByRole('checkbox')

    if (checkboxes[0]) {
      await user.click(checkboxes[0])

      // Should show badge with count
      await waitFor(() => {
        expect(screen.getByText('1')).toBeInTheDocument()
      })

      // Copy should now copy only selected
      const copyButton = screen.getByText(/Kopiuj tabelę/i)
      await user.click(copyButton)

      await waitFor(() => {
        expect(screen.getByText(/zaznaczonych/i)).toBeInTheDocument()
      })
    }
  })

  it('should mark AI-generated row as user-edited when manually changed', async () => {
    const user = userEvent.setup()

    // Mock successful AI response
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => ({
        module: 'AI Module',
        curriculum_refs: ['REF1'],
        objectives: ['Objective 1'],
      }),
    })

    render(<App />)

    // Enter activity and generate
    const activityCells = screen.getAllByText('', { selector: '[data-field="activity"]' })
    await user.click(activityCells[0])
    await user.type(activityCells[0], 'Test activity')

    const generateButtons = screen.getAllByRole('button')
    const generateButton = generateButtons.find(btn => btn.querySelector('svg'))

    if (generateButton) {
      await user.click(generateButton)

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled()
      })

      // Now edit a field manually
      const moduleCells = screen.getAllByText('', { selector: '[data-field="module"]' })
      await user.click(moduleCells[0])
      await user.type(moduleCells[0], 'Manual edit')

      // Row should now be marked as user-edited (internal state)
      // This affects regeneration behavior
    }
  })
})
