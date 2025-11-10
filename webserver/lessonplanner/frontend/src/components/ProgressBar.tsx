import { Progress } from "@/components/ui/progress"

export function ProgressBar({ visible, progress, text }) {
  if (!visible) return null

  return (
    <div className="mb-4 space-y-2">
      <Progress value={progress} className="h-2" />
      <div className="text-center text-sm text-muted-foreground font-medium">
        {text}
      </div>
    </div>
  )
}
