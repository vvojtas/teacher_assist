import { TableRow, TableCell } from "@/components/ui/table"
import { EditableCell } from "./EditableCell"
import { RowActions } from "./RowActions"
import { cn } from "@/lib/utils"

export function PlanTableRow({
  row,
  selected,
  onRowUpdate,
  onGenerate,
  onRegenerate,
  onDelete,
  onSelectChange,
  onMarkUserEdited
}) {
  const handleCellChange = (field, value) => {
    onRowUpdate(row.id, { [field]: value })
  }

  const handleCellBlur = () => {
    // Mark as user edited if AI had generated content
    if (row.aiGenerated) {
      onMarkUserEdited(row.id)
    }
  }

  return (
    <TableRow
      className={cn(
        row.loading && 'row-loading',
        "hover:bg-muted/50"
      )}
    >
      <EditableCell
        field="module"
        value={row.module}
        onValueChange={(value) => handleCellChange('module', value)}
        onBlur={handleCellBlur}
        className="w-[20%] p-1"
      />
      <EditableCell
        field="curriculum"
        value={row.curriculum}
        onValueChange={(value) => handleCellChange('curriculum', value)}
        onBlur={handleCellBlur}
        className="w-[20%] p-1"
      />
      <EditableCell
        field="objectives"
        value={row.objectives}
        onValueChange={(value) => handleCellChange('objectives', value)}
        onBlur={handleCellBlur}
        className="w-[30%] p-1"
      />
      <TableCell className="w-[30%] p-0">
        <EditableCell
          field="activity"
          value={row.activity}
          onValueChange={(value) => handleCellChange('activity', value)}
          className="border-0 p-1"
        />
        <RowActions
          rowId={row.id}
          aiGenerated={row.aiGenerated}
          loading={row.loading}
          selected={selected}
          onGenerate={onGenerate}
          onRegenerate={onRegenerate}
          onDelete={onDelete}
          onSelectChange={onSelectChange}
        />
      </TableCell>
    </TableRow>
  )
}
