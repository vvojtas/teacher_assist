#!/bin/bash
# Build React app and update Django template with correct asset filenames

set -e

cd "$(dirname "$0")"

# Build the React app
echo "Building React app..."
npm run build

# Find the generated asset filenames
CSS_FILE=$(ls -1 ../static/lessonplanner/dist/assets/*.css | head -1 | xargs basename)
JS_FILE=$(ls -1 ../static/lessonplanner/dist/assets/*.js | head -1 | xargs basename)

echo "CSS file: $CSS_FILE"
echo "JS file: $JS_FILE"

# Update Django template
TEMPLATE_FILE="../templates/lessonplanner/index.html"

# Create template content
cat > "$TEMPLATE_FILE" << EOF
{% load static %}
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token }}">
    <title>Teacher Assist - Planowanie Lekcji</title>

    <!-- React App CSS -->
    <link rel="stylesheet" href="{% static 'lessonplanner/dist/assets/$CSS_FILE' %}">
</head>
<body>
    <!-- React App Root -->
    <div id="root"></div>

    <!-- React App JS -->
    <script type="module" src="{% static 'lessonplanner/dist/assets/$JS_FILE' %}"></script>
</body>
</html>
EOF

echo "Django template updated with:"
echo "  CSS: $CSS_FILE"
echo "  JS: $JS_FILE"
echo ""
echo "Build complete! [OK]"
