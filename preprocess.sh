#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Assign the first argument to the directoy variable
directory=$1


# Run the Python script with the provided directory as argument
./extract.sh "$directory"
./filter.sh "$directory"
python3 preprocess.py "$directory"  # Replace script.py with the name of your Python script file
rm -r "../$directory"