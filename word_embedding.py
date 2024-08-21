import os
import pandas as pd
import requests
import datetime
from concurrent.futures import ThreadPoolExecutor

# Load API key from a secure file
with open('API_keys.txt', 'r') as file:
    API_KEY = file.read().strip()

def embedding_generate(row):
    result = dict()
    result['embedding'] = ''
    result['label'] = row['label']
    result['判決字號'] = row['判決字號']  # Include the '判決字號' column in the result
    try:
        result['acts'] = row['acts']
    except:
        pass

    data = {
        "input": row['text'],
        "model": "text-embedding-3-large"
    }

    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        data = response.json()
        embedding = data["data"][0]["embedding"]
        result['embedding'] = embedding
        print(datetime.datetime.now())
    else:
        print(f"Error: {response.status_code}")
        print(response.text)  # This might contain error details

    return result, response.status_code == 200

def embedding_df(df):
    # Shuffle the DataFrame
    df = df.sample(frac=1).reset_index(drop=True)
    
    result_list = []
    success_count = 0
    for index, row in df.iterrows():
        if len(row['text']) < 60 or "一造辯論" in row['text']:
            continue
        result, success = embedding_generate(row)
        if success:
            result_list.append(result)
            success_count += 1
            if success_count >= 500:
                break
    result_df = pd.DataFrame(result_list)
    return result_df, result_df['label'][0] if not result_df.empty else None

def process_file(file_path):
    input_df = pd.read_csv(file_path)
    output_df, df_label = embedding_df(input_df)
    if df_label:
        output_path = f"../combined/{df_label}.csv"
        output_df.to_csv(output_path, index=False)
    os.rename(file_path, os.path.join(os.path.dirname(file_path), f"@{os.path.basename(file_path)}"))

def main():
    src_directory = "../output_acts"
    
    files = [file for file in os.listdir(src_directory) if file.endswith('.csv') and not file.startswith('@')]
    files = sorted(files, key=lambda file: os.path.getsize(os.path.join(src_directory, file)), reverse=True)
    csv_files = [os.path.join(src_directory, file) for file in files]
    
    # Process files in parallel using a ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=16) as executor:
        executor.map(process_file, csv_files)
            
if __name__ == "__main__":
    main()
