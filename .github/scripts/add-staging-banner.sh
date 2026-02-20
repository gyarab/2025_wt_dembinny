#!/bin/bash
# Add staging banner to all HTML files in the main directory
# This visually identifies the staging environment

MAIN_DIR="main"
BANNER='<div style="position:fixed;top:0;left:0;right:0;background:#ff6b00;color:white;padding:10px;text-align:center;z-index:9999;font-weight:bold;box-shadow:0 2px 5px rgba(0,0,0,0.2);">⚠️ STAGING ENVIRONMENT - This is a preview, not production</div>'

echo "Adding staging banner to HTML files in $MAIN_DIR..."

# Find all HTML files and add the banner after <body> tag
find "$MAIN_DIR" -type f -name "*.html" | while read -r file; do
    # Check if file contains <body> tag
    if grep -q "<body" "$file"; then
        # Add banner right after the opening body tag
        sed -i "/<body/a\\
$BANNER" "$file"
        echo "  ✓ Added banner to: $file"
    else
        echo "  ⚠ Skipped (no <body> tag): $file"
    fi
done

echo "Staging banners added successfully!"
