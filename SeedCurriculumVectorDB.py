import os
from dotenv import load_dotenv

import PyPDF2
from PDFExtraction import extract_paragraphs_est_basic_school

import weaviate
from weaviate.classes.config import Configure
from weaviate.classes.init import Auth

load_dotenv()

if __name__=="__main__":



    pdf_path_dict = {
        
        # "est_upper_secondary_nat_cur_2014_appendix_1_final.pdf": "language_and_literature", 
        # "est_upper_secondary_nat_cur_2014_appendix_2_final.pdf": "foreign_languages", 
        # "est_upper_secondary_nat_cur_2014_appendix_3_final.pdf": "mathematics", 
        # "est_upper_secondary_nat_cur_2014_appendix_4_final.pdf": "natural_science", 
        # "est_upper_secondary_nat_cur_2014_appendix_5_final.pdf": "social_studies", 
        # "est_upper_secondary_nat_cur_2014_appendix_6_final.pdf": "art", 
        # "est_upper_secondary_nat_cur_2014_appendix_7_final.pdf": "physical_education", 
        # "est_upper_secondary_nat_cur_2014_appendix_8_final.pdf": "religious_studies", 
        # "est_upper_secondary_nat_cur_2014_appendix_9_final.pdf": "national_defence", 
        # "est_upper_secondary_nat_cur_2014_appendix_10_final.pdf": "economic_and_business_studies", 
        # "est_upper_secondary_nat_cur_2014_appendix_11_final.pdf": "philosophy", 
        # "est_upper_secondary_nat_cur_2014_appendix_12_final.pdf": "career_education", 

        "est_basic_school_nat_cur_2014_appendix_1_final.pdf": "language_and_literature", 
        "est_basic_school_nat_cur_2014_appendix_2_final.pdf": "foreign_languages", 
        "est_basic_school_nat_cur_2014_appendix_3_final.pdf": "mathematics", 
        "est_basic_school_nat_cur_2014_appendix_4_final.pdf": "natural_science", 
        "est_basic_school_nat_cur_2014_appendix_5_final.pdf": "social_studies", 
        "est_basic_school_nat_cur_2014_appendix_6_final.pdf": "art", 
        "est_basic_school_nat_cur_2014_appendix_7_final.pdf": "technology", 
        "est_basic_school_nat_cur_2014_appendix_8_final.pdf": "physical_education", 
        "est_basic_school_nat_cur_2014_appendix_9_final.pdf": "religious_studies", 
        "est_basic_school_nat_cur_2014_appendix_10_final.pdf": "informatics", 
        "est_basic_school_nat_cur_2014_appendix_11_final.pdf": "career_education", 
        "est_basic_school_nat_cur_2014_appendix_12_final.pdf": "entrepreneurship_studies", 

    }

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

    if client.collections.exists(class_name):
        # Delete the class
        client.collections.delete(class_name)
        print(f"Class '{class_name}' deleted successfully.")
    
    curriculum_demo = client.collections.create(
        name=class_name,
        vectorizer_config=Configure.Vectorizer.text2vec_cohere(),   # Configure the Cohere embedding integration
        generative_config=Configure.Generative.cohere()             # Configure the Cohere generative AI integration
    )

    base_dir_path = "curriculum_corpus/EstonianCurriculum"

    for file_name, subject in pdf_path_dict.items():
        pdf_file_path  =  os.path.join(base_dir_path, file_name)
        print("Seeding: " + pdf_file_path)

        with open(pdf_file_path, 'rb') as file:
            subject = pdf_path_dict[os.path.split(pdf_file_path)[-1]]

            paragraph_list = extract_paragraphs_est_basic_school(file)

            with curriculum_demo.batch.dynamic() as batch:
                # Loop through each page and extract text
                for idx, paragraph_text in enumerate(paragraph_list):
                    batch.add_object({
                        "paragraph_idx": int(idx),
                        "text": paragraph_text,
                        "subject": subject,
                    })

            # print(client.batch.failed_objects)
            # print(curriculum_demo.batch.failed_objects)

    client.close()  # Free up resources

        
