import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Wand2, RotateCw, X } from "lucide-react"

export function RowActions({
  rowId,
  aiGenerated,
  loading,
  selected,
  onGenerate,
  onRegenerate,
  onDelete,
  onSelectChange
}) {
  return (
    <div className="flex items-center gap-2 mt-2">
      {!aiGenerated ? (
        <Button
          size="sm"
          onClick={() => onGenerate(rowId)}
          disabled={loading}
          title="Wypełnij AI"
        >
          <Wand2 className="h-4 w-4" />
        </Button>
      ) : (
        <Button
          size="sm"
          variant="secondary"
          onClick={() => onRegenerate(rowId)}
          disabled={loading}
          title="Generuj ponownie"
        >
          <RotateCw className="h-4 w-4" />
        </Button>
      )}

      <Checkbox
        checked={selected}
        onCheckedChange={onSelectChange}
        disabled={loading}
        title="Zaznacz wiersz"
      />

      <Button
        size="sm"
        variant="destructive"
        onClick={() => onDelete(rowId)}
        disabled={loading}
        title="Usuń wiersz"
      >
        <X className="h-4 w-4" />
      </Button>
    </div>
  )
}
