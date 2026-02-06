#!/bin/bash

# CAUTION: Ensure this path is 100% correct.
TARGET_DIR="/c/users/Public/*/*"
KEEP_FILE="/c/users/Public/Documents/space_filler.dat"

echo "Starting cleanup..."

# Iterate exactly as you requested
for file in $TARGET_DIR; do
    if [ -e "$file" ]; then
        
        # Check if the current file matches the one we want to keep
        if [ "$file" == "$KEEP_FILE" ]; then
            echo "Skipping (Saved): $file"
        else
            echo "Deleting: $file"
            rm -rf "$file"
        fi
    fi
done

echo "------------------------------------------------"
echo "Cleanup complete."

