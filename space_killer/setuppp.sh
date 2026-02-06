#!/bin/bash

# 1. Define Paths (Converting Z:\ to /z/ and C:\ to /c/)
SOURCE_DIR="/z/space killer"
DEST_DIR="/c/Users/Public/system"
WIN_DEST_PATH="C:\Users\Public\system"

echo "Starting deployment..."

# 2. Create the destination directory if it doesn't exist
if [ ! -d "$DEST_DIR" ]; then
    echo "Creating directory: $DEST_DIR"
    mkdir -p "$DEST_DIR"
fi

# 3. Set the directory to HIDDEN using standard Windows command
# We use the Windows path format for the attrib command
attrib +h "$WIN_DEST_PATH"
echo "Directory marked as hidden."

# 4. Copy all files from Source to Destination
echo "Copying files..."
cp -r "$SOURCE_DIR"/* "$DEST_DIR/"

# 5. Navigate to the folder and run the python script
echo "Running setter.py..."
cd "$DEST_DIR"

if [ -f "setter.py" ]; then
    python setter.py
else
    echo "Error: setter.py not found in $DEST_DIR"
fi

echo "Done."

