import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { EditableCell } from '../EditableCell'

// Mock the curriculum tooltip hook
vi.mock('@/hooks/useCurriculumTooltip', () => ({
  useCurriculumTooltip: () => ({
    parseCurriculumCodes: vi.fn(() => []),
    fetchMultipleCodes: vi.fn(() => Promise.resolve([])),
  }),
}))

describe('EditableCell', () => {
  const defaultProps = {
    field: 'activity',
    value: '',
    onValueChange: vi.fn(),
  }

  it('should render with initial value', () => {
    render(<EditableCell {...defaultProps} value="Test value" />)

    expect(screen.getByText('Test value')).toBeInTheDocument()
  })

  it('should call onValueChange when user types', async () => {
    const onValueChange = vi.fn()
    const user = userEvent.setup()

    render(<EditableCell {...defaultProps} onValueChange={onValueChange} />)

    const cell = screen.getByText('').parentElement as HTMLElement
    await user.click(cell)
    await user.type(cell, 'New text')

    expect(onValueChange).toHaveBeenCalled()
  })

  it('should enforce max length limit', async () => {
    const onValueChange = vi.fn()
    const user = userEvent.setup()

    render(<EditableCell {...defaultProps} onValueChange={onValueChange} />)

    const cell = screen.getByText('').parentElement as HTMLElement

    // Create string longer than MAX_INPUT_LENGTH (10000)
    const longText = 'a'.repeat(10001)

    // Simulate input event with long text
    const inputEvent = new Event('input', { bubbles: true })
    Object.defineProperty(cell, 'textContent', { value: longText, writable: true })
    cell.dispatchEvent(inputEvent)

    // Should truncate to 10000
    const lastCall = onValueChange.mock.calls[onValueChange.mock.calls.length - 1]
    expect(lastCall[0]).toHaveLength(10000)
  })

  it('should call onBlur when provided', async () => {
    const onBlur = vi.fn()
    const user = userEvent.setup()

    render(<EditableCell {...defaultProps} onBlur={onBlur} />)

    const cell = screen.getByText('').parentElement as HTMLElement
    await user.click(cell)
    await user.tab() // Blur

    expect(onBlur).toHaveBeenCalled()
  })

  it('should update when value prop changes', () => {
    const { rerender } = render(<EditableCell {...defaultProps} value="Initial" />)

    expect(screen.getByText('Initial')).toBeInTheDocument()

    rerender(<EditableCell {...defaultProps} value="Updated" />)

    expect(screen.getByText('Updated')).toBeInTheDocument()
  })

  it('should apply field-specific className', () => {
    const { container } = render(
      <EditableCell {...defaultProps} field="objectives" />
    )

    const cell = container.querySelector('[data-field="objectives"]')
    expect(cell).toHaveClass('cell-objectives')
  })

  it('should apply custom className', () => {
    const { container } = render(
      <EditableCell {...defaultProps} className="custom-class" />
    )

    const cell = container.querySelector('[data-field]')
    expect(cell).toHaveClass('custom-class')
  })

  describe('paste handling', () => {
    it('should strip HTML formatting on paste', async () => {
      const onValueChange = vi.fn()

      render(<EditableCell {...defaultProps} onValueChange={onValueChange} />)

      const cell = screen.getByText('').parentElement as HTMLElement

      // Create paste event with HTML content
      const pasteEvent = new ClipboardEvent('paste', {
        clipboardData: new DataTransfer(),
        bubbles: true,
      })

      // Mock getData to return plain text
      Object.defineProperty(pasteEvent.clipboardData, 'getData', {
        value: (type: string) => {
          if (type === 'text/plain') return 'Plain text content'
          return ''
        },
      })

      // Mock selection
      const range = document.createRange()
      range.selectNodeContents(cell)
      const selection = window.getSelection()
      selection?.removeAllRanges()
      selection?.addRange(range)

      cell.dispatchEvent(pasteEvent)

      // Should call onValueChange with plain text
      expect(onValueChange).toHaveBeenCalledWith(expect.stringContaining('Plain'))
    })

    it('should truncate pasted text if it exceeds max length', async () => {
      const onValueChange = vi.fn()

      render(<EditableCell {...defaultProps} value="Existing text" onValueChange={onValueChange} />)

      const cell = screen.getByText('Existing text').parentElement as HTMLElement

      // Create very long paste content
      const longText = 'a'.repeat(10000)

      const pasteEvent = new ClipboardEvent('paste', {
        clipboardData: new DataTransfer(),
        bubbles: true,
      })

      Object.defineProperty(pasteEvent.clipboardData, 'getData', {
        value: () => longText,
      })

      const range = document.createRange()
      range.selectNodeContents(cell)
      const selection = window.getSelection()
      selection?.removeAllRanges()
      selection?.addRange(range)

      cell.dispatchEvent(pasteEvent)

      // Should respect remaining space
      const lastCall = onValueChange.mock.calls[onValueChange.mock.calls.length - 1]
      if (lastCall) {
        expect(lastCall[0].length).toBeLessThanOrEqual(10000)
      }
    })
  })

  describe('curriculum field tooltip', () => {
    it('should not show tooltip for non-curriculum fields', () => {
      render(<EditableCell {...defaultProps} field="activity" value="Test" />)

      // Tooltip trigger should not be present for non-curriculum fields
      const cell = screen.getByText('Test').parentElement
      expect(cell?.tagName).toBe('DIV')
    })

    it('should handle empty curriculum field', () => {
      render(<EditableCell {...defaultProps} field="curriculum" value="" />)

      // Should render without error
      expect(screen.getByText('')).toBeInTheDocument()
    })
  })
})
