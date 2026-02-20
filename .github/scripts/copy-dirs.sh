#!/bin/bash
# Dynamic directory copier for GitHub Pages deployment
# Reads .deploy-dirs configuration and copies directories to main/

CONFIG_FILE=".deploy-dirs"
TARGET_DIR="main"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file '$CONFIG_FILE' not found"
    exit 1
fi

# Check if target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Target directory '$TARGET_DIR' not found"
    exit 1
fi

echo "Reading deployment configuration from $CONFIG_FILE..."

# Process configuration file
while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines and comments
    if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
        continue
    fi
    
    # Parse source:target format
    if [[ "$line" =~ ^([^:]+):([^:]+)$ ]]; then
        source_dir="${BASH_REMATCH[1]}"
        target_name="${BASH_REMATCH[2]}"
    else
        source_dir="$line"
        target_name="$line"
    fi
    
    # Trim whitespace
    source_dir=$(echo "$source_dir" | xargs)
    target_name=$(echo "$target_name" | xargs)
    
    # Validate source directory exists
    if [ ! -d "$source_dir" ]; then
        echo "Warning: Source directory '$source_dir' not found, skipping..."
        continue
    fi
    
    # Copy directory
    echo "Copying $source_dir -> $TARGET_DIR/$target_name"
    if cp -r "$source_dir" "$TARGET_DIR/$target_name"; then
        echo "  ✓ Successfully copied $source_dir"
    else
        echo "  ✗ Failed to copy $source_dir"
        exit 1
    fi
done < "$CONFIG_FILE"

echo "All directories copied successfully!"
