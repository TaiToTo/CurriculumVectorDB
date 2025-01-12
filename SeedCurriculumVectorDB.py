import os

import PyPDF2
import weaviate
from weaviate.classes.config import Configure

if __name__=="__main__":
    # pdf_file_path_list = [
    #     "curriculum_corpus/mathematics.pdf", 
    #     "curriculum_corpus/science.pdf", 
    #     "curriculum_corpus/social_studies.pdf"
    # ]

    pdf_path_dict = {
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

    class_name = "CurriculumDemo"

    client = weaviate.connect_to_local()

    if client.collections.exists(class_name):
        # Delete the class
        client.collections.delete(class_name)
        print(f"Class '{class_name}' deleted successfully.")

    curriculum_demo = client.collections.create(
            name=class_name,
            vectorizer_config=Configure.Vectorizer.text2vec_ollama(     # Configure the Ollama embedding integration
                api_endpoint="http://host.docker.internal:11434",       # Allow Weaviate from within a Docker container to contact your Ollama instance
                model="nomic-embed-text",                               # The model to use
            ),
            generative_config=Configure.Generative.ollama(              # Configure the Ollama generative integration
                api_endpoint="http://host.docker.internal:11434",       # Allow Weaviate from within a Docker container to contact your Ollama instance
                model="llama3.2",                                       # The model to use
            )
        )

    
    base_dir_path = "curriculum_corpus/EstoniaBasicSchool"

    for file_name, subject in pdf_path_dict.items():
        pdf_file_path  =  os.path.join(base_dir_path, file_name)
        print("Seeding: " + pdf_file_path)

        with open(pdf_file_path, 'rb') as file:

            subject = os.path.split(pdf_file_path)[-1].replace(".pdf", "")

            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)

            with curriculum_demo.batch.dynamic() as batch:
                # Loop through each page and extract text
                for page_number, page in enumerate(pdf_reader.pages):
                    batch.add_object({
                        "page_number": int(page_number + 1),
                        "text": page.extract_text(),
                        "subject": subject,
                    })

    client.close()  # Free up resources

        
