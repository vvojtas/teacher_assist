@echo off
REM Build React app and update Django template with correct asset filenames

echo Building React app...
call npm run build
if %errorlevel% neq 0 (
    echo Build failed!
    exit /b %errorlevel%
)

echo.
echo Finding generated asset files...

REM Find CSS and JS files
for %%f in (..\static\lessonplanner\dist\assets\*.css) do set CSS_FILE=%%~nxf
for %%f in (..\static\lessonplanner\dist\assets\*.js) do set JS_FILE=%%~nxf

echo CSS file: %CSS_FILE%
echo JS file: %JS_FILE%

REM Update Django template
set TEMPLATE_FILE=..\templates\lessonplanner\index.html

echo.
echo Updating Django template...

(
echo {%% load static %%}
echo ^<!DOCTYPE html^>
echo ^<html lang="pl"^>
echo ^<head^>
echo     ^<meta charset="UTF-8"^>
echo     ^<meta name="viewport" content="width=device-width, initial-scale=1.0"^>
echo     ^<title^>Teacher Assist - Planowanie Lekcji^</title^>
echo.
echo     ^<!-- React App CSS --^>
echo     ^<link rel="stylesheet" href="{%% static 'lessonplanner/dist/assets/%CSS_FILE%' %%}"^>
echo ^</head^>
echo ^<body^>
echo     ^<!-- React App Root --^>
echo     ^<div id="root"^>^</div^>
echo.
echo     ^<!-- React App JS --^>
echo     ^<script type="module" src="{%% static 'lessonplanner/dist/assets/%JS_FILE%' %%}"^>^</script^>
echo ^</body^>
echo ^</html^>
) > "%TEMPLATE_FILE%"

echo.
echo Django template updated with:
echo   CSS: %CSS_FILE%
echo   JS: %JS_FILE%
echo.
echo Build complete! ✓
