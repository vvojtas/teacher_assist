import { Button } from "@/components/ui/button"
import { Wand2, Plus, Trash2, Clipboard, Loader2 } from "lucide-react"

export function ActionBar({
  bulkGenerating,
  selectedRowCount,
  onBulkGenerate,
  onAddRow,
  onClearAll,
  onCopyTable
}) {
  return (
    <div className="flex flex-wrap gap-2 mb-4">
      <Button
        onClick={onBulkGenerate}
        disabled={bulkGenerating}
      >
        {bulkGenerating ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Przetwarzanie...
          </>
        ) : (
          <>
            <Wand2 className="h-4 w-4" />
            Wypełnij wszystko AI
          </>
        )}
      </Button>

      <Button
        variant="secondary"
        onClick={onAddRow}
        disabled={bulkGenerating}
      >
        <Plus className="h-4 w-4" />
        Dodaj wiersz
      </Button>

      <Button
        variant="destructive"
        onClick={onClearAll}
        disabled={bulkGenerating}
      >
        <Trash2 className="h-4 w-4" />
        Wyczyść wszystko
      </Button>

      <Button
        variant="outline"
        onClick={onCopyTable}
        disabled={bulkGenerating}
      >
        <Clipboard className="h-4 w-4" />
        {selectedRowCount > 0
          ? `Skopiuj zaznaczone (${selectedRowCount})`
          : 'Skopiuj tabelę'}
      </Button>
    </div>
  )
}
