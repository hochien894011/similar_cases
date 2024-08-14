import os
import pandas as pd
import re
import random

def load_data_from_directory(src, dst):
    
    all_data = dict()
    
    # List all files in the directory
    files = os.listdir(src)
    
    # Iterate over each file
    for file in files:
        # Check if the file is a CSV file
        if file.endswith(".csv"):
            # Construct the full path to the file
            file_path = os.path.join(src, file)
            # Load the CSV file into a DataFrame
            df = pd.read_csv(file_path)
    
        # Iterate over each row in the dataframe
        for index, row in df.iterrows():
            title = re.sub("\s*|\u3000*", "", row['案由'])
            if title not in all_data:
                all_data[title] = []
            if title == "0給付工程款":
                all_data["給付工程款"].append((row['原告主張'], row['判決字號']))
            elif title == "3":
                all_data["返還借款"].append((row['原告主張'], row['判決字號']))
            else:
                # Update the count in the dictionary
                all_data[title].append((row['原告主張'], row['判決字號']))
    
    # Iterate over the dictionary keys and values
    for key, value in all_data.items():
        if "等" not in key:
            # Create a DataFrame from the list
            df = pd.DataFrame(value, columns=['text', '判決字號'])
            df['label'] = key
            
            # Define the file path
            file_path = os.path.join(dst, f"{key}.csv")
            
            # Check if the directory exists, if not, create it
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # Save the DataFrame as a CSV file
            df.to_csv(file_path, index=False)

    print("DataFrames saved as CSV files.")

# Directory containing the CSV files
src = "../preprocess_data"
dst = "../data_by_label"
# Load data from all CSV files in the directory
load_data_from_directory(src, dst)
