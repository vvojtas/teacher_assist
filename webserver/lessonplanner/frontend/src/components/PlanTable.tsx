import { Table, TableBody, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { PlanTableRow } from "./PlanTableRow"

export function PlanTable({
  rows,
  selectedRows,
  onRowUpdate,
  onGenerate,
  onRegenerate,
  onDelete,
  onSelectChange,
  onMarkUserEdited
}) {
  return (
    <div className="border rounded-lg overflow-hidden mb-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[20%]">Moduł</TableHead>
            <TableHead className="w-[20%]">Podstawa Programowa</TableHead>
            <TableHead className="w-[30%]">Cele</TableHead>
            <TableHead className="w-[30%]">Aktywność</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row) => (
            <PlanTableRow
              key={row.id}
              row={row}
              selected={selectedRows.has(row.id)}
              onRowUpdate={onRowUpdate}
              onGenerate={onGenerate}
              onRegenerate={onRegenerate}
              onDelete={onDelete}
              onSelectChange={(checked) => onSelectChange(row.id, checked)}
              onMarkUserEdited={onMarkUserEdited}
            />
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
