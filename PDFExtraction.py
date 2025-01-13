import re
import fitz  # PyMuPDF

def extract_paragraphs_est_basic_school(file_path):
    whole_text_list = []
    paragraph_list = []
    try:
        # Open the PDF file
        with fitz.open(file_path) as pdf:
            for page in pdf:
                # Extract the text of the page
                text = page.get_text("text")
                text = re.sub(r" \n\d", "", text, count=1)
                whole_text_list.append(text)

        whole_text = "".join(whole_text_list)
        paragraph_list = whole_text.split("\n \n")
        paragraph_list = [p.strip() for p in paragraph_list if p.strip()]
        return paragraph_list
    
    except Exception as e:
        print(f"Error: {e}")
        return []
    

if __name__=="__main__":
    pdf_file = "curriculum_corpus/EstoniaBasicSchool/est_basic_school_nat_cur_2014_appendix_1_final.pdf"

    paragraph_list = extract_paragraphs_est_basic_school(pdf_file)

    for i, paragraph in enumerate(paragraph_list[:10], start=1):
        print(f"Paragraph {i}:\n{paragraph}\n")