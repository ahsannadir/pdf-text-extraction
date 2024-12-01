# Importing Libraries
import fitz
import os
import cv2
import shutil
from pypdf import PdfReader
import pytesseract
import pdfplumber
import pandas as pd
import json

# Function to Extract Text from PDF
def extract_pdf_text(file_path):
    pdf_texts = ""
    pdf_file = fitz.open(file_path)
    global total_pages
    total_pages = pdf_file.page_count
    for i in range(total_pages):
        pdf_page = pdf_file.load_page(i)
        text = pdf_page.get_text()
        pdf_texts += text

    return pdf_texts

# Function to Extract Tables from PDF
def extract_tables(file_path):
    extracted_tables = {}
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for j, table in enumerate(tables):
                extracted_tables[f'Page{i + 1}_Table{j + 1}'] = pd.DataFrame(table).to_dict()
    return extracted_tables

# Function to Extract Images from PDF (The Images will be stored in 'images' folder)
def extract_images(file_path):
    reader = PdfReader(file_path)

    if os.path.exists('images'):
        shutil.rmtree('images')

    os.makedirs('images')

    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
    
        if hasattr(page, 'images'):
            for image_index, image in enumerate(page.images):

                image_extension = image.name.split('.')[-1] if '.' in image.name else 'jpg'
            
                image_name = f"page{page_num + 1}_image{image_index + 1}.{image_extension}"
                image_path = os.path.join('images', image_name)
            
                with open(image_path, 'wb') as f:
                    f.write(image.data)
                print(f"Saved image {image_name} from page {page_num + 1}")

# Function to Check if Images are extacted from PDF
def check_for_images():
    if os.path.exists('images'):

        if not os.listdir('images'):
            return False
        else:
            return True

# Fuction to Extract text from Images (OCR)
def get_ocr_text():
    image_folder = 'images'

    ocr_results = {}

    for image_file in os.listdir(image_folder):

        image_path = os.path.join(image_folder, image_file)

        if image_file.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            img = cv2.imread(image_path)
        
            if img is not None:
                extracted_text = pytesseract.image_to_string(img, lang = 'eng') # Change the Language based on the Images you have.
            
                ocr_results[image_file] = extracted_text
            else:
                print(f"Could not load image {image_file}")
        else:
            print(f"Skipping non-image file {image_file}")

    return ocr_results

# Main Function
def main():
    pdf_file_path = "table.pdf" # Enter your PDF File location here

    pdf_texts = extract_pdf_text(pdf_file_path)

    tables = extract_tables(pdf_file_path)

    extract_images(pdf_file_path)

    ocr_texts = {}
    if check_for_images():
        ocr_texts = get_ocr_text()

    final_dict = {
        "Extracted Text": pdf_texts,
        "Extracted Tables": tables,
        "OCR Extracted Text": ocr_texts
    }

    with open('JSON_Output.json', 'w') as json_file:
        json.dump(final_dict, json_file)

if __name__ == "__main__":
    main()
