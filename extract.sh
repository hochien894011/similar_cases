#!/bin/bash

# Define the master directory
master_directory=".."

# Check if argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <partial_file_name>"
    exit 1
fi

# Get the partial file name provided as argument
partial_file_name="$1"

# Check if any file starts with the provided partial name
found_file=$(find "$master_directory" -maxdepth 1 -type f -name "$partial_file_name*" -print -quit)

# Check if a file is found
if [ -z "$found_file" ]; then
    echo "Error: No file found in the master directory starting with '$partial_file_name'."
    exit 1
fi

# Extract the file and store it in the master directory
unrar x "$found_file" "$master_directory/"

echo "File starting with '$partial_file_name' extracted and stored in the master directory."
