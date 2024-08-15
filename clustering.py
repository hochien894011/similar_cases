import pandas as pd
import os
import random
import json

import numpy as np
from sklearn.cluster import DBSCAN

from collections import defaultdict

def data_processing(numofSample, is_colab=False):
    """ Import files and process to fit in following process

    Args:
        numofSample (int): number of sample, each case title will extract # of samples into data
        is_colab (Boolean): True if this code is execute on the colab

    Returns:
        dataframe (pd.DataFrame): a dataframe that can be use in following process
            - embedding (float[]): embedding data
            - label (string): judgement case title
            - 判決字號 (string): judgement case number
            - acts (template(string, string)[]): related acts
    """
    # Set the directory path
    if is_colab:
        from google.colab import drive # type: ignore
        drive.mount('/content/drive')

        # Define the directory path where your data is stored
        dir_path = "/content/drive/MyDrive/embedding_data"
    else:
        dir_path = "../embedded/"
    
    dataframe = pd.DataFrame()
    SAMPLE_NUM = numofSample
    for file_name in os.listdir(dir_path):
        if file_name.endswith('.csv'):
            df = pd.read_csv(os.path.join(dir_path, file_name))
            df = df.dropna()
            max_index = len(df)
            print(f"{file_name}: {max_index}")
            if max_index < SAMPLE_NUM:
                continue
            if max_index == SAMPLE_NUM:
                sampled_df = df
            else:
                sampled_indices = random.sample(range(max_index-1), SAMPLE_NUM)
                sampled_df = df.iloc[sampled_indices]
            dataframe = pd.concat([dataframe, sampled_df], ignore_index=True)

    dataframe['embedding'] = dataframe['embedding'].apply(json.loads)

    return dataframe

def extract_embeddings_and_labels(dataframe):
    """ Extract embbeddings and labels from dataframe

    Args:
        dataframe (pd.Dataframe): dataframe from data_processing()

    Returns:
        embeddings (float[]): embedding data
        labels (string[]): label data
    """
    
    # Convert embedding column to numpy array
    embeddings = np.array(dataframe['embedding'].tolist())
    # Get labels from dataframe
    labels = dataframe['label']

    return embeddings, labels

def dbscan_cases(embeddings, labels, epsilon):
    """ DBSCAN cases and construct case title relation matrix

    Args:
        embeddings (float[]): list containing embedding data
        labels (string[]): list containing case title labels
        epsilon (float, in the interval [0,1]): the epsilon of DBSCAN

    Returns:
        matrix (int[][]): a matrix represent relationship between two case titles
        label_list (string[]): list containing case title labels
    """
    
    # DBSCAN by correspond epsilon 
    db = DBSCAN(eps=epsilon, min_samples=1).fit(embeddings)
    cluster_labels = db.labels_
    
    # Dictionary to store clusters for each label
    label_clusters = defaultdict(set)
    
    # Populate the dictionary with clusters for each label
    for idx, cluster_id in enumerate(cluster_labels):
        label_clusters[labels[idx]].add(cluster_id)

    # Convert sets to sorted lists for efficient search
    for label in label_clusters:
        label_clusters[label] = sorted(label_clusters[label])

    # Create a matrix to store the counts
    label_count = len(label_clusters)
    matrix = np.zeros((label_count, label_count), dtype=int)
    label_index = {label: idx for idx, label in enumerate(label_clusters)}

    # Populate the matrix
    for idx, cluster_id in enumerate(cluster_labels):
        original_label = labels[idx]
        label_idx = label_index[original_label]
        for other_label, clusters in label_clusters.items():
            other_label_idx = label_index[other_label]
            if cluster_id in clusters:
                matrix[label_idx][other_label_idx] += 1
    
    label_list = list(label_clusters.keys())
    
    return matrix, label_list

def find_similar_case(matrix, label_list, threshold):
    """ According to similar case

    Args:
        matrix (int[][]): a matrix represent relationship between two case titles
        label_list (string[]): list containing case title labels
        threshold (float, in the interval [0, 1]): threshold of similarity

    Returns:
        edges (template(string, string)[]): the relation between two case titles
    """
    # Calculate fractions for threshold comparison
    real_threshold = threshold * matrix[0][0]
    edges = []
    label_count = len(label_list)
    for i in range(label_count):
        for j in range(i + 1, label_count):
            if (matrix[i][j] >= real_threshold and matrix[j][i] >= real_threshold):
                edges.append((label_list[i], label_list[j]))
    return edges
    

df = data_processing(200)
embeddings, labels = extract_embeddings_and_labels(df)
matrix, label_list = dbscan_cases(embeddings, labels, 0.5)
edges = find_similar_case(matrix, label_list, 0.5)
