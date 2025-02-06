import os
import yaml
from dotenv import load_dotenv

import weaviate
from weaviate.classes.config import Configure
from weaviate.classes.init import Auth

load_dotenv()

def run_through_curriculum_tree(parent_node, element_list=[]):
    for child_node in parent_node["children"]:        
        element_list.append({"node_id": child_node["id"], "label": child_node["label"], "text_type": child_node["text_type"]})
        if len(child_node["children"]) > 0:
            element_list = run_through_curriculum_tree(child_node, element_list=element_list)

    return element_list

if __name__=="__main__":

    # Get a list of texts to embed from leaf nodes
    with open("../JapaneseDocumentLayoutAnalysis/structured_data/sample_structured_curriculum.yaml", "r", encoding="utf-8") as file:
        curriculum_tree = yaml.safe_load(file)  # Load YAML content as a dictionary

    node_list = run_through_curriculum_tree(curriculum_tree)

    # Configure weaviate 
    weaviate_url = os.environ["WEAVIATE_URL"]
    weaviate_api_key = os.environ["WEAVIATE_API_KEY"]
    openai_api_key = os.environ["OPENAI_API_KEY"]

    class_name = "JapaneseCurriculumDemo"

    # Connect to Weaviate Cloud
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=weaviate_url,                                    # Replace with your Weaviate Cloud URL
        auth_credentials=Auth.api_key(weaviate_api_key),             # Replace with your Weaviate Cloud key
        headers={"X-OpenAI-Api-Key": openai_api_key},           # Replace with your Cohere API key
    )

    if client.collections.exists(class_name):
        # Delete the class
        client.collections.delete(class_name)
        print(f"Class '{class_name}' deleted successfully.")
    
    jp_curriculum_demo = client.collections.create(
        name=class_name,
        vectorizer_config=Configure.Vectorizer.text2vec_openai(model="text-embedding-3-small"),   # Configure the Cohere embedding integration
        generative_config=Configure.Generative.openai(model="gpt-4o-mini")             # Configure the Cohere generative AI integration
    )

    base_dir_path = "curriculum_corpus/EstonianCurriculum"

    for subject in ["social_studies"]:
        with jp_curriculum_demo.batch.dynamic() as batch:
            for idx, node in enumerate(node_list):
                batch.add_object({
                    "node_id": node["node_id"],
                    "label": node["label"],
                    "subject": subject,
                    "text_type": node["text_type"]
                })

    client.close()  # Free up resources

        
