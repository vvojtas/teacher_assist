import React, { useRef, useEffect, useState } from 'react'
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card"
import { useCurriculumTooltip } from "@/hooks/useCurriculumTooltip"
import { cn } from "@/lib/utils"

export function EditableCell({ field, value, onValueChange, onBlur, className }) {
  const contentRef = useRef(null)
  const { parseCurriculumCodes, fetchMultipleCodes } = useCurriculumTooltip()
  const [tooltipData, setTooltipData] = useState(null)

  // Update contenteditable when value changes externally
  useEffect(() => {
    if (contentRef.current && contentRef.current.textContent !== value) {
      contentRef.current.textContent = value
    }
  }, [value])

  const handleInput = (e) => {
    const newValue = e.target.textContent
    onValueChange(newValue)
  }

  const handleBlur = () => {
    if (onBlur) {
      onBlur()
    }
  }

  // Handle paste to strip formatting
  const handlePaste = (e) => {
    e.preventDefault()
    const text = e.clipboardData.getData('text/plain')
    document.execCommand('insertText', false, text)
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
