import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ActionBar } from '../ActionBar'

describe('ActionBar', () => {
  const defaultProps = {
    bulkGenerating: false,
    selectedRowCount: 0,
    onBulkGenerate: vi.fn(),
    onAddRow: vi.fn(),
    onClearAll: vi.fn(),
    onCopyTable: vi.fn(),
  }

  it('should render all action buttons', () => {
    render(<ActionBar {...defaultProps} />)

    expect(screen.getByText(/Wypełnij wszystkie AI/i)).toBeInTheDocument()
    expect(screen.getByText(/Dodaj wiersz/i)).toBeInTheDocument()
    expect(screen.getByText(/Wyczyść wszystko/i)).toBeInTheDocument()
    expect(screen.getByText(/Kopiuj tabelę/i)).toBeInTheDocument()
  })

  it('should call onBulkGenerate when bulk generate button clicked', async () => {
    const onBulkGenerate = vi.fn()
    const user = userEvent.setup()

    render(<ActionBar {...defaultProps} onBulkGenerate={onBulkGenerate} />)

    await user.click(screen.getByText(/Wypełnij wszystkie AI/i))

    expect(onBulkGenerate).toHaveBeenCalledTimes(1)
  })

  it('should call onAddRow when add row button clicked', async () => {
    const onAddRow = vi.fn()
    const user = userEvent.setup()

    render(<ActionBar {...defaultProps} onAddRow={onAddRow} />)

    await user.click(screen.getByText(/Dodaj wiersz/i))

    expect(onAddRow).toHaveBeenCalledTimes(1)
  })

  it('should call onClearAll when clear button clicked', async () => {
    const onClearAll = vi.fn()
    const user = userEvent.setup()

    render(<ActionBar {...defaultProps} onClearAll={onClearAll} />)

    await user.click(screen.getByText(/Wyczyść wszystko/i))

    expect(onClearAll).toHaveBeenCalledTimes(1)
  })

  it('should call onCopyTable when copy button clicked', async () => {
    const onCopyTable = vi.fn()
    const user = userEvent.setup()

    render(<ActionBar {...defaultProps} onCopyTable={onCopyTable} />)

    await user.click(screen.getByText(/Kopiuj tabelę/i))

    expect(onCopyTable).toHaveBeenCalledTimes(1)
  })

  it('should disable bulk generate button when generating', () => {
    render(<ActionBar {...defaultProps} bulkGenerating={true} />)

    const button = screen.getByText(/Wypełnij wszystkie AI/i).closest('button')
    expect(button).toBeDisabled()
  })

  it('should show spinner when bulk generating', () => {
    const { container } = render(<ActionBar {...defaultProps} bulkGenerating={true} />)

    // Look for spinner animation class
    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })

  it('should display selected row count badge when rows selected', () => {
    render(<ActionBar {...defaultProps} selectedRowCount={3} />)

    expect(screen.getByText('3')).toBeInTheDocument()
  })

  it('should not display badge when no rows selected', () => {
    render(<ActionBar {...defaultProps} selectedRowCount={0} />)

    // Badge should not be visible
    const copyButton = screen.getByText(/Kopiuj tabelę/i).closest('button')
    const badge = copyButton?.querySelector('.absolute')
    expect(badge).not.toBeInTheDocument()
  })

  it('should have correct button variants', () => {
    render(<ActionBar {...defaultProps} />)

    // Primary action (bulk generate) should be default variant
    const bulkButton = screen.getByText(/Wypełnij wszystkie AI/i).closest('button')
    expect(bulkButton).toHaveClass('bg-primary')

    // Secondary actions should be outline variant
    const addButton = screen.getByText(/Dodaj wiersz/i).closest('button')
    expect(addButton).toHaveClass('border')
  })

  it('should disable all buttons when bulk generating', () => {
    render(<ActionBar {...defaultProps} bulkGenerating={true} />)

    const buttons = screen.getAllByRole('button')
    buttons.forEach(button => {
      expect(button).toBeDisabled()
    })
  })
})
