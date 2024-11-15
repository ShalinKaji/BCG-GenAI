import os
import re
import pdfplumber
import pandas as pd

# Define paths
base_path = 'SEC-EDGAR'

# Define financial terms with multiple possible keywords for flexibility
financial_terms = {
    'Total Revenue': ['Total Revenue', 'Total Net Sales', 'Total Revenues'],
    'Total Cost of Sales': ['Total Cost of Sales', 'Total Cost of Revenue', 'Total Cost of Revenues'],
    'Cash Flow from Operating Activities': ['Cash Flow from Operating Activities', 'Net Cash from Operating Activities'],
    'Net Income': ['Net Income'],
    'Total Assets': ['Total Assets'],
    'Total Liabilities': ['Total Liabilities']
}

# Headers for each company's general financial statement section (to locate starting point for extraction)
item_8_headers = [
    'CONSOLIDATED STATEMENTS OF OPERATIONS',
    'FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA',
    'Consolidated Balance Sheets'
]

# Initialize a dictionary to hold the financial data for each company
financial_data = {}

# Function to extract financial data from tables in a PDF
def extract_financial_data(pdf_path):
    extracted_data = {key: None for key in financial_terms}  # Initialize extracted data dictionary with None values
    found_item_8 = False

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ''

            # Check if we are in the Item 8 section based on provided headers
            if any(header in text for header in item_8_headers):
                found_item_8 = True
                print(f"Located main financial section on page {page_num} - starting table extraction.")

            if found_item_8:
                tables = page.extract_tables()
                print(f"Extracting tables from page {page_num} - Number of tables found: {len(tables)}")
                
                # Process each table
                for table in tables:
                    for row in table:
                        # Clean up row data to avoid NoneType issues
                        row = [cell if cell is not None else '' for cell in row]
                        
                        # Try to match each financial metric term with possible keywords
                        for metric, keywords in financial_terms.items():
                            if any(keyword.lower() in ' '.join(row).lower() for keyword in keywords):
                                # Extract the first numeric cell next to keyword match
                                for cell in row:
                                    if cell and re.search(r'\d', cell):  # Check if cell has digits
                                        try:
                                            extracted_data[metric] = int(cell.replace(',', '').replace('$', ''))
                                            print(f"Extracted {metric}: {extracted_data[metric]} on page {page_num}")
                                            break
                                        except ValueError:
                                            continue
            if all(extracted_data.values()):  # Stop if all terms are found
                break
    return extracted_data

# Main loop to iterate over companies and years
for company_folder in os.listdir(base_path):
    company_path = os.path.join(base_path, company_folder)
    if os.path.isdir(company_path):
        company_data = []  # List to hold yearly data for this company

        for pdf_file in os.listdir(company_path):
            if pdf_file.endswith('.pdf'):
                pdf_path = os.path.join(company_path, pdf_file)
                year_match = re.search(r'Y(\d{2})', pdf_file)
                year = f"20{year_match.group(1)}" if year_match else "Unknown"

                # Extract financial data from PDF
                print(f"\nProcessing file: {pdf_file} for year: {year}")
                data = extract_financial_data(pdf_path)
                data['Year'] = year
                company_data.append(data)

        # Create a DataFrame for each company
        financial_data[company_folder] = pd.DataFrame(company_data)

# Display results
for company, df in financial_data.items():
    print(f"\nFinancial Data for {company}:")
    print(df)
    print("\n")

# Save each company's DataFrame to a CSV file
for company, df in financial_data.items():
    df.to_csv(f"{company}_financials.csv", index=False)
