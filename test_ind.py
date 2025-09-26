# To run this code, you need the following:
# 1. An environment variable `GEMINI_API_KEY` with your API key.
# 2. A file named `industries.csv` in the same directory.
# 3. Dependencies: pip install google-genai pandas

import os
import json
import pandas as pd
import google.genai as genai

# --- CONFIGURATION ---
# Configure the Gemini API client
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
    print("FATAL: GEMINI_API_KEY environment variable not set.")
    exit(1)

# Input file containing the list of industries
INDUSTRY_LIST_PATH = 'industries.csv'
# The final output file
OUTPUT_CSV_PATH = 'industry_tech_mapping_results.csv'

# The master list of technology categories to guide the model
# This ensures the model's responses are constrained to our desired framework.
TECH_CATEGORIES = [
    "ERP", "CRM", "Supply Chain & Manufacturing Tech", "PLM Systems", "Middleware & Integration",
    "Database & Data Warehousing", "AI / ML", "Digital Twin & IoT", "Low-code / Visualization / BI Tools",
    "Productivity & Collaboration", "Content Management & ECM", "Cybersecurity & Identity Management",
    "Cloud", "Virtualization & Infrastructure", "DevOps & Development Tools", "GIS & Mapping"
]


def get_mapping_for_industry(industry_name: str) -> list | None:
    """
    Generates technology mappings for a single industry using the Gemini API.

    Args:
        industry_name: The name of the industry to process.

    Returns:
        A list of dictionaries containing the mapping data, or None if an error occurs.
    """
    print(f"-> Processing industry: {industry_name}...")

    # This prompt is engineered to get a structured JSON response
    prompt = f"""
    You are an expert market analyst specializing in technology adoption across industries.
    Your task is to identify the most relevant technologies for the '{industry_name}' industry.

    Follow these instructions precisely:
    1.  From the provided list of technology categories, select the 5 to 7 MOST CRITICAL categories for the '{industry_name}' industry's core operations.
    2.  For each category you select, list the top 2-3 most popular and widely adopted software or hardware tools.
    3.  Use your internal knowledge and Google Search grounding to ensure the tool recommendations are current and accurate for the year 2025.

    AVAILABLE TECHNOLOGY CATEGORIES: {", ".join(TECH_CATEGORIES)}

    IMPORTANT: Your response MUST be a valid JSON object. Do not include any text, explanation, or markdown formatting before or after the JSON object.

    The JSON object should be a dictionary where keys are the selected technology categories and values are a list of the preferred tool names.

    Example JSON format:
    {{
      "CRM": ["Salesforce Sales Cloud", "HubSpot CRM"],
      "ERP": ["Oracle NetSuite", "SAP S/4HANA"],
      "Cloud": ["Amazon Web Services (AWS)", "Microsoft Azure"]
    }}
    """

    try:
        # Initialize the model with search grounding enabled
        model = genai.GenerativeModel('gemini-1.5-pro-latest', tools=['grounding'])
        response = model.generate_content(prompt)

        # Clean up the response to ensure it's a pure JSON string
        json_string = response.text.strip().removeprefix("```json").removesuffix("```")

        # Parse the JSON string into a Python dictionary
        data = json.loads(json_string)

        # Convert the dictionary into a flat list for the final CSV
        formatted_results = []
        for category, tools in data.items():
            formatted_results.append({
                "Industry": industry_name,
                "Category": category,
                "Preferred Tools": ", ".join(tools)  # Join tools into a single string
            })
        return formatted_results

    except json.JSONDecodeError:
        print(f"   [ERROR] Failed to decode JSON for industry: {industry_name}")
        return None
    except Exception as e:
        print(f"   [ERROR] An unexpected error occurred for {industry_name}: {e}")
        return None


def main():
    """Main function to run the entire mapping process."""
    print("Starting industry-to-technology mapping process...")

    # Check if the input file exists
    if not os.path.exists(INDUSTRY_LIST_PATH):
        print(f"FATAL: Input file not found at '{INDUSTRY_LIST_PATH}'")
        return

    # Read the list of industries from the CSV
    industries_df = pd.read_csv(INDUSTRY_LIST_PATH)

    if "Industry" not in industries_df.columns:
        print("FATAL: 'Industry' column not found in industries.csv")
        return

    industries = industries_df["Industry"].dropna().unique()

    # This list will store all the results from the API
    all_results = []

    for industry in industries:
        mapping = get_mapping_for_industry(industry)
        if mapping:
            all_results.extend(mapping)

    if not all_results:
        print("Process finished, but no data was generated.")
        return

    # Convert the final list of results into a pandas DataFrame
    final_df = pd.DataFrame(all_results)

    # Save the DataFrame to a CSV file
    final_df.to_csv(OUTPUT_CSV_PATH, index=False)

    print("\n-------------------------------------------------")
    print(f"✅ Success! Mapping complete.")
    print(f"Results have been saved to '{OUTPUT_CSV_PATH}'")
    print("-------------------------------------------------")


if __name__ == "__main__":
    main()