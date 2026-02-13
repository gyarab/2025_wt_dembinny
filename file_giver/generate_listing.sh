#!/bin/bash
# Minimalistic file listing generator for GitHub Pages
# This script generates an HTML file that lists all files in subdirectories

OUTPUT_FILE="file_giver/index.html"
SCAN_DIR="."

# Start HTML
cat > "$OUTPUT_FILE" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Browser</title>
    <style>
        body {
            font-family: monospace;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        .directory {
            background: white;
            margin: 10px 0;
            padding: 15px;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .directory h2 {
            color: #007bff;
            margin-top: 0;
            font-size: 1.2em;
        }
        .file-list {
            list-style: none;
            padding-left: 0;
        }
        .file-list li {
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }
        .file-list li:last-child {
            border-bottom: none;
        }
        a {
            color: #007bff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .icon {
            margin-right: 5px;
        }
        .back-link {
            display: inline-block;
            margin-bottom: 20px;
            padding: 8px 15px;
            background: #007bff;
            color: white;
            border-radius: 4px;
        }
        .back-link:hover {
            background: #0056b3;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <a href="../index.html" class="back-link">← Back to Home</a>
    <h1>📁 Repository File Browser</h1>
EOF

# Function to get file icon based on extension
get_icon() {
    case "$1" in
        *.html) echo "📄" ;;
        *.css) echo "🎨" ;;
        *.js) echo "📜" ;;
        *.md) echo "📝" ;;
        *.json) echo "🔧" ;;
        *.png|*.jpg|*.jpeg|*.gif|*.svg) echo "🖼️" ;;
        *) echo "📄" ;;
    esac
}

# Scan directories and files
find "$SCAN_DIR" -mindepth 1 -maxdepth 1 -type d | grep -v "^\./\." | grep -v "^\.\/main$" | grep -v "^\.\/file_giver$" | sort | while IFS= read -r dir; do
    dirname=$(basename "$dir")
    
    # Map directory names to their deployed names
    deployed_dirname="$dirname"
    if [ "$dirname" = "prvni_web" ]; then
        deployed_dirname="prvni-web"
    fi
    
    echo "    <div class=\"directory\">" >> "$OUTPUT_FILE"
    echo "        <h2>📁 $dirname/</h2>" >> "$OUTPUT_FILE"
    echo "        <ul class=\"file-list\">" >> "$OUTPUT_FILE"
    
    # List files in directory
    if [ -d "$dir" ]; then
        find "$dir" -maxdepth 1 -type f | sort | while IFS= read -r file; do
            filename=$(basename "$file")
            icon=$(get_icon "$filename")
            echo "            <li><span class=\"icon\">$icon</span><a href=\"../$deployed_dirname/$filename\">$filename</a></li>" >> "$OUTPUT_FILE"
        done
    fi
    
    echo "        </ul>" >> "$OUTPUT_FILE"
    echo "    </div>" >> "$OUTPUT_FILE"
done

# End HTML
cat >> "$OUTPUT_FILE" << 'EOF'
    <footer style="text-align: center; margin-top: 40px; color: #666;">
        <p>Generated automatically by file_giver script</p>
    </footer>
</body>
</html>
EOF

echo "File listing generated at $OUTPUT_FILE"
