#!/bin/bash

for year in {2000..2005}; do
    for month in {1..12}; do
        formatted_month=$(printf "%02d" $month)
        ./preprocess.sh "$year$formatted_month"
    # Add your desired commands or operations for each year here
    done
done

./check.sh
