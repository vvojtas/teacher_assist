# Path Alias Information

## What is `@/lib/utils`?

The `@` symbol is a **path alias** configured in both `vite.config.ts` and `tsconfig.json`.

- `@` → points to the `src/` directory
- `@/lib/utils` → resolves to `src/lib/utils.ts`
- `@/components/ui/button` → resolves to `src/components/ui/button.tsx`

## File Location

The actual file is located at:
```
webserver/lessonplanner/frontend/src/lib/utils.ts
```

It contains the `cn()` utility function used for merging Tailwind CSS classes.

## Troubleshooting Import Errors on Windows

If you're getting `Failed to resolve import "@/lib/utils"` errors:

### 1. Clear Vite Cache
```bash
# Delete node_modules/.vite directory
rm -rf node_modules/.vite

# Or on Windows (PowerShell)
Remove-Item -Recurse -Force node_modules\.vite
```

### 2. Restart Dev Server
After clearing cache, restart the dev server:
```bash
npm run dev
```

### 3. Clear npm Cache (if issue persists)
```bash
npm cache clean --force
rm -rf node_modules
npm install
```

### 4. Verify Configuration

**vite.config.ts** should have:
```typescript
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),  // Note: 'src' not './src'
    },
  },
})
```

**tsconfig.json** should have:
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

## Why This Happens

- Vite caches module resolution for performance
- Path separators differ between Windows (`\`) and Unix (`/`)
- Using `'src'` instead of `'./src'` in `path.resolve(__dirname, 'src')` is more reliable cross-platform
- After config changes, Vite cache must be cleared

## Key Fix Applied

Changed from:
```typescript
'@': path.resolve(__dirname, './src')  // ❌ Can be problematic on Windows
```

To:
```typescript
'@': path.resolve(__dirname, 'src')  // ✅ Cross-platform compatible
```
