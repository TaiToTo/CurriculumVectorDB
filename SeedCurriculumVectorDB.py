import os

import PyPDF2
import weaviate
from weaviate.classes.config import Configure

if __name__=="__main__":
    pdf_file_path_list = [
        "curriculum_corpus/mathematics.pdf", 
        "curriculum_corpus/science.pdf", 
        "curriculum_corpus/social_studies.pdf"
    ]

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

    
    for pdf_file_path in pdf_file_path_list:

        print("Seeding: " + pdf_file_path)

        with open(pdf_file_path, 'rb') as file:

            subject = os.path.split(pdf_file_path)[-1].replace(".pdf", "")

            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)

            with curriculum_demo.batch.dynamic() as batch:
                # Loop through each page and extract text
                for page_number, page in enumerate(pdf_reader.pages):
                    batch.add_object({
                        "page_number": int(page_number),
                        "text": page.extract_text(),
                        "subject": subject,
                    })

    client.close()  # Free up resources

        
