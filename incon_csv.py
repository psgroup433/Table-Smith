import requests
import json
import os
import csv  # Import the csv module

def list_gemini_models(api_endpoint_list_models, api_key):
    """
    Lists available Gemini models using the Gemini API ListModels endpoint.

    Args:
        api_endpoint_list_models (str): URL of the Gemini API ListModels endpoint.
        api_key (str): Your API key for Gemini API.
    """

    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': api_key
    }


    try:
        response = requests.get(api_endpoint_list_models, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        json_output = response.json()

        print("Available Gemini Models:\n")
        for model in json_output.get('models', []):
            print(f"Model Name: {model.get('name')}")
            print(f"  Description: {model.get('description')}")
            print(f"  Version: {model.get('version')}")
            print(f"  Supported Methods: {model.get('supportedGenerationMethods')}")
            print("-" * 30)


    except requests.exceptions.RequestException as e:
        print(f"API Request Error (ListModels): {e}")
        if response is not None:
            print("Raw API Response (ListModels):", response.text)


def generate_inconsistent_csv(csv_file_path, api_endpoint, api_key, prompt_template, output_csv_path="output.csv"):
    """
    Calls the Gemini 2.0 Flash API to transform CSV data from a text file into inconsistent CSV format.

    Args:
        csv_file_path (str): Path to the text file containing CSV data.
        api_endpoint (str): URL of the Gemini API endpoint.
        api_key (str): Your API key for Gemini API.
        prompt_template (str): The prompt template string.
        output_csv_path (str, optional): Path to save the generated CSV output. Defaults to "output.csv".
    """

    
    try:
        # *** MODIFIED LINE: Specify encoding='utf-8' ***
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_data = file.read()
    except FileNotFoundError:
        print(f"Error: CSV file not found at path: {csv_file_path}")
        return None
    # Add specific error handling for encoding if needed, but UTF-8 is most likely
    except UnicodeDecodeError:
         print(f"Error: Could not decode CSV file at path: {csv_file_path}. Try specifying a different encoding.")
         return None

    prompt = prompt_template.replace("[CSV_DATA_HERE]", csv_data)


    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': api_key  # Gemini API Key in header
    }

    payload = {
        "contents": [{
            "parts": [{"text": prompt}] # Gemini uses 'contents' and 'parts' for prompt
        }]
    }


    try:
        response = requests.post(api_endpoint, headers=headers, json=payload)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        api_response_text = response.text # Get raw text response

        generated_csv_content = response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text')


        if generated_csv_content:
            try:
                # Attempt to parse the generated content as CSV
                csv_reader = csv.reader(generated_csv_content.splitlines())
                csv_data_rows = list(csv_reader) # Convert to list of lists

                if csv_data_rows:
                    # Write the generated CSV to a file
                    with open(output_csv_path, 'w', newline='') as csvfile:
                        csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL) # Quote all fields for robustness
                        csv_writer.writerows(csv_data_rows)

                    print(f"Successfully generated and saved inconsistent CSV to: {output_csv_path}")
                    return csv_data_rows # Return the CSV data as list of lists

                else:
                    print("Error: No data rows found in generated CSV content.")
                    print("Raw API Response (for debugging):", api_response_text)
                    return None


            except Exception as e: # Catch generic CSV parsing errors
                print(f"Error: Could not parse API response content as CSV:\n{e}")
                print("Raw API Response (for debugging):", api_response_text)
                return None

        else:
            print("Error: No CSV content found in API response.")
            print("Raw API Response (for debugging):", api_response_text)
            return None


    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        if response is not None: # Print API response text if available for more details
            print("Raw API Response (for debugging):", response.text)
        return None

def generate_csvs(folder_path):

    API_ENDPOINT_GENERATE_CONTENT = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-001:generateContent'  # **<-- UPDATED to Gemini Flash Model**
    API_ENDPOINT_LIST_MODELS = 'https://generativelanguage.googleapis.com/v1beta/models' # ListModels Endpoint
    API_KEY = 'AIzaSyDKkmBUPA5_2fFm9QNVOlLEdY8JPd1oxVw'  # **Replace with your actual Gemini API key**
    CSV_FILE_PATH = r"D:\Tabula_X_NGIT\datasets\Ani Files 2\Employees and Sales_Employee.csv"  # **Replace with the actual path to your CSV text file**
    OUTPUT_CSV_FILE = 'data_inconsistent.csv' # Output CSV filename
    
    for filename in os.listdir(folder_path):

        
        if filename.endswith(".csv"): 
            CSV_FILE_PATH = os.path.join(folder_path, filename)
            OUTPUT_CSV_FILE = CSV_FILE_PATH.removesuffix(".csv") + "_inconsistent.csv"

            generated_csv = generate_inconsistent_csv(
            csv_file_path=CSV_FILE_PATH,
            api_endpoint=API_ENDPOINT_GENERATE_CONTENT,
            api_key=API_KEY,
            prompt_template=PROMPT_TEMPLATE,
            output_csv_path=OUTPUT_CSV_FILE
            )

            if generated_csv:
                print(f"csv generated for {CSV_FILE_PATH}")
            else:
                print(f"error generating for {CSV_FILE_PATH}")
            



if __name__ == "__main__":
    # --- Configuration ---
    
    # --- Prompt Template (Paste your revised prompt template for CSV output here) ---
    PROMPT_TEMPLATE = """
    Task: Transform the following CSV data into an inconsistent CSV format suitable for data integration testing.

    CSV Data:
    [CSV_DATA_HERE]

    Transformation Instructions:

    MAKE SURE THAT ALL COULUMNS ARE PRESENT IN THE JSON
    dont skip the columns and don't change the column names for every record
    General Instructions:
    - don't add any random extra data to the given input make the json attribute names as similar as possible even better if they are same
    - The output MUST be in CSV format. Use comma (",") as the delimiter and double quotes ("") to enclose string values if they contain commas.
    - Ensure that ALL columns from the input CSV are present in the output CSV. **Do not skip columns**.
    - Maintain consistent column names across all rows in the output CSV.  You can change the column names from the input CSV to different names in the output CSV, but use these *new* column names consistently. Aim to make the output CSV header row contain different column names that are semantically related to the original CSV headers, but ideally, keep them as close as possible to the original names.
    - Introduce inconsistencies in the CSV data compared to the input CSV data. Focus on creating *realistic and common data formatting mismatches* that are often encountered in real-world data integration scenarios.
    - Aim for human-interpretable transformations. The output CSV should represent the same information as the input CSV but in a significantly different and inconsistent format.

    Example Transformation Types to Consider (but not limited to):
    - String formatting variations: case changes (uppercase, lowercase, title case), abbreviations, adding prefixes/suffixes, different separators, typos, slight variations in wording.
    - Numerical formatting variations: different units (e.g., USD to EUR), different precision (decimal places), different scales (e.g., full numbers vs. "K" notation).
    - Date/Time formatting variations: different date formats, presence/absence of time components.
    - Structural variations: Nesting data in JSON, using different key names, restructuring arrays.
    - Algorithmic/Rule-based variations: Introduce simple calculations or logical rules to derive some JSON field values from CSV columns.

    Example Transformations (Crucial for Guidance):
    - **Product Column (String):**  Change the CSV column "Product" to "item" in the output CSV header. Add the prefix "Product-" to each product letter in the "item" column.  Example: CSV Value: "A", Output CSV Value in "item" column: "Product-A".
    - **Sales Columns - Total Sales (Numerical):** Transform CSV column "T.Sales" to output CSV column "totalSales". Format numerical values to "K" notation in the "totalSales" column. Example: CSV Value: "4873", Output CSV Value in "totalSales" column: "4.9K".
    - **Sales Columns - Expected Ranges (Numerical Range):** Create new output CSV columns named "min_expected_range" and "max_expected_range" from the CSV columns "Min.Expected" and "Max.Expected" respectively. Format numbers in both columns to "XK" notation (one decimal place). Example: CSV "3958" in "Min.Expected" becomes Output CSV "3.9K" in "min_expected_range"; CSV "8030" in "Max.Expected" becomes Output CSV "8.0K" in "max_expected_range".
    - **Status Column (Algorithmic):** Create a new output CSV column named "status". Calculate its value based on the "Sales" compared to "Min.Expected" and "Max.Expected" ranges. Example: If Sales is within range, status in "status" column is "Within Range".
    - **Date Column (Date Formatting - Hypothetical Example):**  Assume your CSV had a "Date" column in "YYYY-MM-DD" format.  Transform it to output CSV column "eventDate" and format dates to "Month DD, YYYY". Example: CSV Value: "2024-12-25", Output CSV Value in "eventDate" column: "December 25, 2024".
    - **Price Column (Currency Formatting - Hypothetical Example):** Assume your CSV had a "Price" column with USD values. Transform it to output CSV column "priceEUR" and convert to Euros with currency symbol and 2 decimal places. Example: CSV Value: "1200", Output CSV Value in "priceEUR" column: "€1100.00".

    Desired Output Format: CSV
    """

    EXAMPLE_TRANSFORMATIONS_TEXT = """
    Example Transformations (Crucial for Guidance):
    - For "Product" column: CSV Value: "A", Output CSV Value in "item" column: "Product-A"
    - For "T.Sales" column: CSV Value: "4873", Output CSV Value in "totalSales" column: "4.9K"
    - For "Min.Expected" and "Max.Expected": CSV Values: "3958", "8030", Output CSV Value in "min_expected_range" column: "3.9K", Output CSV Value in "max_expected_range" column: "8.0K"
    - For "Sales" column: CSV Value within "Min.Expected" and "Max.Expected" range, Output CSV Value in "status" column: "Within Range"; CSV Value less than "Min.Expected", Output CSV Value in "status" column: "Below Range"; Otherwise, Output CSV Value in "status" column: "Exceeded".
    - CSV column "Date" (hypothetical) becomes Output CSV column "eventDate" and format dates to "Month DD, YYYY". Example: CSV Value: "2024-12-25", Output CSV Value in "eventDate" column: "December 25, 2024".
    - CSV column "Price" (hypothetical USD) becomes Output CSV column "priceEUR" in Euros with currency symbol. Example: CSV Value: "1200", Output CSV Value in "priceEUR" column: "€1100.00".
    """

    generate_csvs(r"D:\Tabula_X_NGIT\datasets 2\may 8")
    
