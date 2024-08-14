#!/bin/bash

# Function to check if content contains the specified pattern
contains_pattern() {
    if grep -qE '"JFULL"[[:space:]]*:[[:space:]]*".{1,30}判決' "$1"; then
        return 0
    else
        return 1
    fi
}

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Assign the argument to the directory variable
dir="../$1"

# Check if the directory exists
if [ ! -d "$dir" ]; then
    echo "Error: Directory '$dir' not found."
    exit 1
fi

# Loop through each directory in the specified directory
for d in "$dir"/*; do
    # Check if the directory name contains "民事" as a separate word
    if [[ ! "$d" =~ .*民事.* ]]; then
        # If not, remove the directory and its contents
        rm -r "$d"
        echo "Removed directory: $d"
    else
        # If the directory contains "民事", proceed to check and delete JSON files
        # Loop through each JSON file in the directory
        for json_file in "$d"/*.json; do
            # Check if the JSON file name contains "上", if so, delete it
            if [[ "$json_file" =~ .*上.* ]]; then
                rm "$json_file"
                echo "Removed: $json_file"
            else
                # Check if the JSON content contains the specified pattern
                if ! contains_pattern "$json_file"; then
                    rm "$json_file"
                    echo "Removed: $json_file"
                fi
            fi
        done
    fi
done
