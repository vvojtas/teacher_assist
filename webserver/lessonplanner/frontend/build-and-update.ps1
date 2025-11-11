# Build React app and update Django template with correct asset filenames

Write-Host "Building React app..." -ForegroundColor Cyan
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`nFinding generated asset files..." -ForegroundColor Cyan

# Find CSS and JS files
$cssFile = Get-ChildItem -Path "..\static\lessonplanner\dist\assets\*.css" | Select-Object -First 1 -ExpandProperty Name
$jsFile = Get-ChildItem -Path "..\static\lessonplanner\dist\assets\*.js" | Select-Object -First 1 -ExpandProperty Name

Write-Host "CSS file: $cssFile" -ForegroundColor Green
Write-Host "JS file: $jsFile" -ForegroundColor Green

# Update Django template
$templateFile = "..\templates\lessonplanner\index.html"

Write-Host "`nUpdating Django template..." -ForegroundColor Cyan

$templateContent = @"
{% load static %}
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token }}">
    <title>Teacher Assist - Planowanie Lekcji</title>

    <!-- React App CSS -->
    <link rel="stylesheet" href="{% static 'lessonplanner/dist/assets/$cssFile' %}">
</head>
<body>
    <!-- React App Root -->
    <div id="root"></div>

    <!-- React App JS -->
    <script type="module" src="{% static 'lessonplanner/dist/assets/$jsFile' %}"></script>
</body>
</html>
"@

$templateContent | Out-File -FilePath $templateFile -Encoding UTF8 -NoNewline

Write-Host "`nDjango template updated with:" -ForegroundColor Cyan
Write-Host "  CSS: $cssFile" -ForegroundColor Yellow
Write-Host "  JS: $jsFile" -ForegroundColor Yellow
Write-Host "`nBuild complete! [OK]" -ForegroundColor Green
