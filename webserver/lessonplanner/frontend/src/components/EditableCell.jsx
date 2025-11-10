import React, { useRef, useEffect, useState } from 'react'
import { TableCell } from "@/components/ui/table"
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

  const cellContent = (
    <TableCell className={cn("p-2", className)}>
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
          field === 'objectives' && 'cell-objectives'
        )}
        data-field={field}
      >
        {value}
      </div>
    </TableCell>
  )

  if (showTooltip && tooltipData && tooltipData.length > 0) {
    return (
      <HoverCard openDelay={300}>
        <HoverCardTrigger asChild>
          {cellContent}
        </HoverCardTrigger>
        <HoverCardContent className="w-96">
          {tooltipData.map(({ code, text }, index) => (
            <div key={code} className={index > 0 ? 'mt-3' : ''}>
              <strong>{code}:</strong> {text}
            </div>
          ))}
        </HoverCardContent>
      </HoverCard>
    )
  }

  return cellContent
}
