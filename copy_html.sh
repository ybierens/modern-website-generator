#!/bin/bash

# Copy HTML Script - Get clean HTML output for CodePen
# ====================================================

echo "🚀 Website Optimizer - Copy HTML for CodePen"
echo "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" 

# Check if container is running
if ! docker-compose ps | grep -q "website-optimizer.*Up"; then
    echo "🔥 Starting container..."
    docker-compose up -d
    sleep 3
fi

echo "🎯 Generating optimized HTML..."
docker-compose exec website-optimizer python website_optimizer.py > /dev/null 2>&1

echo ""
echo "📋 COPY THE HTML BELOW FOR CODEPEN:"
echo "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "="
echo ""

# Output clean HTML without container prefixes
docker-compose exec website-optimizer cat optimized_website.html

echo ""
echo "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "="
echo "🎨 Copy the HTML above and paste it directly into CodePen!"
echo "💡 The HTML is also saved as 'optimized_website.html' in the container"
