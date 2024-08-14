for year in {2000..2024}; do
    for month in {1..12}; do
        formatted_month=$(printf "%02d" $month)
        if [ ! -f "../preprocess_data/$year$formatted_month.csv" ]; then
            echo "$year$formatted_month"
        fi
    done
done
