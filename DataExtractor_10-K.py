# import os
# import re
# import pandas as pd
# from PyPDF2 import PdfReader

# base_path = 'SEC-EDGAR'

# financial_metrics = {
#     'Total Revenue': r'Total\s+Revenue\s*\(?\$?([\d,]+)',
#     'Net Income': r'Net\s+Income\s*\(?\$?([\d,]+)',
#     'Total Assets': r'Total\s+Assets\s*\(?\$?([\d,]+)',
#     'Total Liabilities': r'Total\s+Liabilities\s*\(?\$?([\d,]+)',
#     'Cash Flow from Operating Activities': r'Cash\s+Flow\s+from\s+Operating\s+Activities\s*\(?\$?([\d,]+)',
# }

# financial_data = {}

# def extract_financial_data(pdf_path):
#     with open(pdf_path, 'rb') as file:
#         pdf_reader = PdfReader(file)
#         text = ""
#         for page in pdf_reader.pages:
#             text += page.extract_text()
        
#     # Extract financial metrics
#     extracted_data = {}
#     for metric, pattern in financial_metrics.items():
#         match = re.search(pattern, text)
#         extracted_data[metric] = int(match.group(1).replace(',', '')) if match else None
    
#     return extracted_data

# for company_folder in os.listdir(base_path):
#     company_path = os.path.join(base_path, company_folder)
#     if os.path.isdir(company_path):
#         company_data = []  # List to hold yearly data for this company
        
#         for pdf_file in os.listdir(company_path):
#             if pdf_file.endswith('.pdf'):
#                 pdf_path = os.path.join(company_path, pdf_file)
#                 year = re.search(r'Y(\d{2})', pdf_file).group(1)  # Extract year from filename
                
#                 # Extract financial data from PDF
#                 data = extract_financial_data(pdf_path)
#                 data['Year'] = f"20{year}"
#                 company_data.append(data)
        
#         # Create a DataFrame for each company
#         financial_data[company_folder] = pd.DataFrame(company_data)

# for company, df in financial_data.items():
#     print(f"Financial Data for {company}:")
#     print(df)
#     print("\n")

# for company, df in financial_data.items():
#     df.to_csv(f"{company}_financials.csv", index=False)

import os
import re
import pandas as pd
from PyPDF2 import PdfReader

# Define paths
base_path = 'SEC-EDGAR'

# Define search terms and regex patterns for financial metrics
financial_metrics = {
    'Total Revenue': r'Total\s+net\s+sales\s*\(?\$?([\d,]+)',
    'Total Cost of Sales': r'Total\s+cost\s+of\s+sales\s*\(?\$?([\d,]+)',
    'Cash Flow from Operating Activities': r'Total\s+operating\s+expenses\s*\(?\$?([\d,]+)',
    'Net Income': r'Net\s+income\s*\(?\$?([\d,]+)'
    # 'Total Assets': r'Total\s+Assets\s*\(?\$?([\d,]+)',
    # 'Total Liabilities': r'Total\s+Liabilities\s*\(?\$?([\d,]+)',
}

# Initialize a dictionary to hold the financial data for each company
financial_data = {}

# Function to extract text from Item 8 section onward in a PDF
def extract_financial_data(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    
    # Search for Item 8 as the starting point for financial tables
    item_8_start = re.search(r'Item\s+8\.\s+Financial\s+Statements\s+and\s+Supplementary\s+Data', text, re.IGNORECASE)
    if item_8_start:
        text = text[item_8_start.end():]  # Narrow down to content after Item 8

    # Extract financial metrics
    extracted_data = {}
    for metric, pattern in financial_metrics.items():
        match = re.search(pattern, text)
        extracted_data[metric] = int(match.group(1).replace(',', '')) if match else None
    
    return extracted_data

# Main loop to iterate over companies and years
for company_folder in os.listdir(base_path):
    company_path = os.path.join(base_path, company_folder)
    if os.path.isdir(company_path):
        company_data = []  # List to hold yearly data for this company
        
        for pdf_file in os.listdir(company_path):
            if pdf_file.endswith('.pdf'):
                pdf_path = os.path.join(company_path, pdf_file)
                year = re.search(r'Y(\d{2})', pdf_file).group(1)  # Extract year from filename
                
                # Extract financial data from PDF
                data = extract_financial_data(pdf_path)
                data['Year'] = f"20{year}"
                company_data.append(data)
        
        # Create a DataFrame for each company
        financial_data[company_folder] = pd.DataFrame(company_data)

# Display results
for company, df in financial_data.items():
    print(f"Financial Data for {company}:")
    print(df)
    print("\n")

# Save each company's DataFrame to a CSV file
for company, df in financial_data.items():
    df.to_csv(f"{company}_financials.csv", index=False)
