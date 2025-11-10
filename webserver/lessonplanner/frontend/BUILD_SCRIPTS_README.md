# Build Scripts

This directory contains build scripts for both Unix-like systems (Linux/macOS) and Windows.

## Usage

### Linux / macOS / WSL

```bash
./build-and-update.sh
```

### Windows (Command Prompt)

```cmd
build-and-update.bat
```

### Windows (PowerShell)

```powershell
.\build-and-update.ps1
```

Or if you need to enable script execution first:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\build-and-update.ps1
```

## What These Scripts Do

All three scripts perform the same operations:

1. **Build the React app** using `npm run build`
2. **Find the generated asset files** with hashed names (e.g., `index-XsL2Kv9u.js`)
3. **Update the Django template** at `../templates/lessonplanner/index.html` with the correct filenames

## Why Do We Need This?

Vite generates files with content-based hashes in their names for cache busting:
- `index-DOt_LElg.css` (changes when CSS changes)
- `index-XsL2Kv9u.js` (changes when JS changes)

These scripts automatically detect the new filenames and update the Django template, so you don't have to manually edit it after every build.

## Manual Build (if scripts don't work)

If the scripts fail, you can build and update manually:

1. Build the app:
   ```bash
   npm run build
   ```

2. Check the generated files:
   ```bash
   ls ../static/lessonplanner/dist/assets/
   ```

3. Manually edit `../templates/lessonplanner/index.html` and update the filenames in the `<link>` and `<script>` tags.

## Troubleshooting

### Linux/macOS: "Permission denied"

Make the script executable:
```bash
chmod +x build-and-update.sh
```

### Windows PowerShell: "Execution Policy"

PowerShell may block script execution by default. Run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then run the script:
```powershell
.\build-and-update.ps1
```

### Windows: "npm not found"

Ensure Node.js is installed and added to your PATH. Restart your terminal after installing Node.js.

## Development Workflow

For development, you don't need these scripts. Just run:

```bash
npm run dev
```

This starts the Vite dev server with hot module replacement. The build scripts are only needed when you want to test the production build with Django.
