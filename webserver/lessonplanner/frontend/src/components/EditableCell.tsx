import React, { useRef, useEffect, useState } from 'react'
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card"
import { useCurriculumTooltip } from "@/hooks/useCurriculumTooltip"
import { cn } from "@/lib/utils"

// Maximum character length to prevent XSS/DoS attacks
const MAX_INPUT_LENGTH = 10000

interface EditableCellProps {
  field: string
  value: string
  onValueChange: (value: string) => void
  onBlur?: () => void
  className?: string
}

export function EditableCell({ field, value, onValueChange, onBlur, className }: EditableCellProps) {
  const contentRef = useRef<HTMLDivElement>(null)
  const { parseCurriculumCodes, fetchMultipleCodes } = useCurriculumTooltip()
  const [tooltipData, setTooltipData] = useState<Array<{ code: string; text: string }> | null>(null)

  // Update contenteditable when value changes externally
  useEffect(() => {
    if (contentRef.current && contentRef.current.textContent !== value) {
      contentRef.current.textContent = value
    }
  }, [value])

  const handleInput = (e: React.FormEvent<HTMLDivElement>) => {
    const newValue = (e.target as HTMLDivElement).textContent || ''

    // Enforce max length for XSS/DoS protection
    if (newValue.length > MAX_INPUT_LENGTH) {
      const truncated = newValue.substring(0, MAX_INPUT_LENGTH)
      if (contentRef.current) {
        contentRef.current.textContent = truncated
      }
      onValueChange(truncated)
      return
    }

    onValueChange(newValue)
  }

  const handleBlur = () => {
    if (onBlur) {
      onBlur()
    }
  }

  // Handle paste to strip formatting using modern Selection API
  const handlePaste = (e: React.ClipboardEvent<HTMLDivElement>) => {
    e.preventDefault()
    let text = e.clipboardData.getData('text/plain')

    // Calculate remaining space for XSS/DoS protection
    const currentLength = contentRef.current?.textContent?.length || 0
    const selection = window.getSelection()
    if (!selection || selection.rangeCount === 0) return

    // Get selected text length (will be replaced)
    const selectedText = selection.toString()
    const remainingSpace = MAX_INPUT_LENGTH - (currentLength - selectedText.length)

    // Truncate pasted text if needed
    if (text.length > remainingSpace) {
      text = text.substring(0, remainingSpace)
    }

    // Delete current selection
    selection.deleteFromDocument()

    // Insert plain text
    const range = selection.getRangeAt(0)
    const textNode = document.createTextNode(text)
    range.insertNode(textNode)

    // Move cursor to end of inserted text
    range.setStartAfter(textNode)
    range.setEndAfter(textNode)
    selection.removeAllRanges()
    selection.addRange(range)

    // Trigger state update
    if (contentRef.current) {
      const newValue = contentRef.current.textContent
      onValueChange(newValue || '')
    }
  }

  // For curriculum field, show tooltip on hover
  const isCurriculumField = field === 'curriculum'
  const showTooltip = isCurriculumField && value

  const handleMouseEnter = async () => {
    if (isCurriculumField && value) {
      const codes = parseCurriculumCodes(value)
      if (codes.length > 0) {
        const data = await fetchMultipleCodes(codes)
        setTooltipData(data)
      }
    }
  }

  const editableContent = (
    <div
      ref={contentRef}
      contentEditable
      suppressContentEditableWarning
      onInput={handleInput}
      onBlur={handleBlur}
      onPaste={handlePaste}
      onMouseEnter={handleMouseEnter}
      className={cn(
        "outline-none",
        field === 'objectives' && 'cell-objectives',
        className
      )}
      data-field={field}
    >
      {value}
    </div>
  )

  if (showTooltip && tooltipData && tooltipData.length > 0) {
    return (
      <HoverCard openDelay={300}>
        <HoverCardTrigger asChild>
          <div className="cursor-text">
            {editableContent}
          </div>
        </HoverCardTrigger>
        <HoverCardContent className="w-96 max-h-96 overflow-auto">
          {tooltipData.map(({ code, text }, index) => (
            <div key={code} className={index > 0 ? 'mt-3 pt-3 border-t' : ''}>
              <strong className="text-primary">{code}:</strong>{' '}
              <span className="text-sm">{text}</span>
            </div>
          ))}
        </HoverCardContent>
      </HoverCard>
    )
  }

  return editableContent
}
