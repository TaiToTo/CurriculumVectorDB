import numpy as np
import pandas as pd
import weaviate
import json

row_list = []
vector_list = []

client = weaviate.connect_to_local()

collection = client.collections.get("CurriculumDemo")

for item in collection.iterator(
    include_vector=True
):
    row_list.append(item.properties)
    vector_list.append(item.vector["default"])

client.close()

df = pd.DataFrame(row_list)
df["page_number"] = df["page_number"].astype(int)

vector_array = np.array(vector_list)

print(df)
print(vector_array.shape)
