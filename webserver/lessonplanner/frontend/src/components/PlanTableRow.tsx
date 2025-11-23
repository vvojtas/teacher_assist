import { useCallback } from "react"
import { TableRow, TableCell } from "@/components/ui/table"
import { EditableCell } from "./EditableCell"
import { RowActions } from "./RowActions"
import { cn } from "@/lib/utils"
import type { Row, RowUpdate } from "@/hooks/useTableManager"

interface PlanTableRowProps {
  row: Row
  selected: boolean
  onRowUpdate: (rowId: string, update: RowUpdate) => void
  onGenerate: (rowId: string) => void
  onRegenerate: (rowId: string) => void
  onDelete: (rowId: string) => void
  onSelectChange: (rowId: string, checked: boolean) => void
  onMarkUserEdited: (rowId: string) => void
}

export function PlanTableRow({
  row,
  selected,
  onRowUpdate,
  onGenerate,
  onRegenerate,
  onDelete,
  onSelectChange,
  onMarkUserEdited
}: PlanTableRowProps) {
  const handleCellChange = useCallback((field: string, value: string) => {
    onRowUpdate(row.id, { [field]: value })
  }, [row.id, onRowUpdate])

  const handleCellBlur = useCallback(() => {
    // Mark as user edited if AI had generated content
    if (row.aiGenerated) {
      onMarkUserEdited(row.id)
    }
  }, [row.aiGenerated, row.id, onMarkUserEdited])

  const handleSelectChange = useCallback((checked: boolean) => {
    onSelectChange(row.id, checked)
  }, [row.id, onSelectChange])

  return (
    <TableRow
      className={cn(
        row.loading && 'row-loading',
        "hover:bg-muted/50"
      )}
    >
      <TableCell className="w-[20%] p-1">
        <EditableCell
          field="module"
          value={row.module}
          onValueChange={(value) => handleCellChange('module', value)}
          onBlur={handleCellBlur}
        />
      </TableCell>
      <TableCell className="w-[20%] p-1">
        <EditableCell
          field="curriculum"
          value={row.curriculum}
          onValueChange={(value) => handleCellChange('curriculum', value)}
          onBlur={handleCellBlur}
        />
      </TableCell>
      <TableCell className="w-[30%] p-1">
        <EditableCell
          field="objectives"
          value={row.objectives}
          onValueChange={(value) => handleCellChange('objectives', value)}
          onBlur={handleCellBlur}
        />
      </TableCell>
      <TableCell className="w-[30%] p-1">
        <EditableCell
          field="activity"
          value={row.activity}
          onValueChange={(value) => handleCellChange('activity', value)}
        />
        <RowActions
          rowId={row.id}
          aiGenerated={row.aiGenerated}
          loading={row.loading}
          selected={selected}
          onGenerate={onGenerate}
          onRegenerate={onRegenerate}
          onDelete={onDelete}
          onSelectChange={handleSelectChange}
        />
      </TableCell>
    </TableRow>
  )
}
