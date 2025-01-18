import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
# import umap

import os
from dotenv import load_dotenv
load_dotenv()

import weaviate
from weaviate.classes.config import Configure
from weaviate.classes.init import Auth

def retrieve_weaviate_vector(collection_name="CurriculumDemo"):
    row_list = []
    vector_list = []

    # client = weaviate.connect_to_local()

    weaviate_url = os.environ["WEAVIATE_URL"]
    weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
    cohere_api_key = os.environ["COHERE_API_KEY"]

    class_name = "CurriculumDemo"

    # Connect to Weaviate Cloud
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=weaviate_url,                                    # Replace with your Weaviate Cloud URL
        auth_credentials=Auth.api_key(weaviate_api_key),             # Replace with your Weaviate Cloud key
        headers={"X-Cohere-Api-Key": cohere_api_key},           # Replace with your Cohere API key
    )

    collection = client.collections.get("CurriculumDemo")

    for item in collection.iterator(include_vector=True):
        row_list.append(item.properties)
        vector_list.append(item.vector["default"])

    client.close()

    df = pd.DataFrame(row_list)
    df["paragraph_idx"] = df["paragraph_idx"].astype(int)

    vector_array = np.array(vector_list)

    return df, vector_array

if __name__=="__main__":

    subject_color_map = {
        "language_and_literature": "red",
        "foreign_languages": "purple",
        "mathematics": "blue",
        "natural_science": "green",
        "social_studies": "orange",
        "art": "pink",
        "technology": "cyan",
        "physical_education": "yellow",
        "religious_studies": "brown",
        "informatics": "teal",
        "career_education": "magenta",
        "entrepreneurship_studies": "lime",
    }

    df, vector_array = retrieve_weaviate_vector()

    print(df)
    
    reducer = umap.UMAP(
                    metric='cosine', 
                    n_neighbors=10, 
                    min_dist=0.01
                   )
    embedding_2d = reducer.fit_transform(vector_array)

    df["x"] = pd.Series(embedding_2d[:, 0])
    df["y"] = pd.Series(embedding_2d[:, 1])

    df.to_csv("../CurriculumInterdisciplinarityAnalysis/data/embedding_2d_est_basic_school.csv")

    legend_patches = [mpatches.Patch(color=color, label=subject) for subject, color in subject_color_map.items()]

    color_list = [subject_color_map[row["subject"]] for idx, row in df.iterrows()]


    plt.figure(figsize=(10, 10))
    plt.scatter(embedding_2d[:, 0],
                embedding_2d[:, 1], 
                c=color_list, 
                s=5
            )
    plt.legend(handles=legend_patches, title="Subjects", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()