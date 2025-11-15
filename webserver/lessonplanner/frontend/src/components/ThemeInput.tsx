import { Input } from "@/components/ui/input"

interface ThemeInputProps {
  value: string
  onChange: (value: string) => void
}

export function ThemeInput({ value, onChange }: ThemeInputProps) {
  return (
    <div className="mb-4">
      <label htmlFor="themeInput" className="block text-sm font-medium mb-2">
        Temat tygodnia:
      </label>
      <Input
        id="themeInput"
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="np. Jesień - zbiory"
        maxLength={200}
        className="max-w-md"
      />
    </div>
  )
}
