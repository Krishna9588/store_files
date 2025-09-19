import pandas as pd
import os
from pathlib import Path
from main_new_id import CHECKPOINT_FILE as new_file
from main_io_id import CHECKPOINT_FILE as io_file

""" *** Note ***
To use this Script efficiently 
1. Make sure you have Company ID in place - without this it won't work
2. input_1 and input_2: Put your paths to 2 files with common output from main_io and main_new
3. final_output: Name your output file *** Do not put `.csv` in the end *** 
"""

""" basic input - output
input_1 = "checkpoint/AWS_Korea_io_n3_03_checkpoint.csv"
input_2 = "result/AWS_Korea_new_n3_03_result.csv"
final_output = "combined_output_009"
"""

# input_1 = new_file
input_1 = io_file
# input_2 = io_file
input_2 = new_file
if os.path.exists(input_1) and os.path.exists(input_2):
    print("File Exist\n"
          f"input_1: {input_1}\n"
          f"input_2: {input_2}")
    final_output = input("Enter final file name: ")
else:
    print("Files do not exist")
    input_1 = input("Enter new_id output file from root file")
    input_2 = input("Enter io_id output file from root file")
    final_output = input("Enter final file name:")

def combine_csv_files(file_path_1: str, file_path_2: str, final_output_path: str) -> None:
    try:
        df1 = pd.read_csv(file_path_1)
        df2 = pd.read_csv(file_path_2)

        df1 = df1.rename(columns={"Usage Indicated": "Usage Indicated_f1", "Explanation": "Explanation_f1"})
        df2 = df2.rename(columns={"Usage Indicated": "Usage Indicated_f2", "Explanation": "Explanation_f2"})

        if "Company ID" in df1.columns and "Company ID" in df2.columns and \
                not df1['Company ID'].isnull().all() and not df2['Company ID'].isnull().all():
            merge_keys = ["Company ID"]
            print("Using 'Company ID' as the merge key.")
            combined_df = pd.merge(df1, df2, on=merge_keys, how='inner', suffixes=("_x", "_y"))
            combined_df = combined_df.drop(columns=["Company Name_y", "Domain_y", "Page URL_y", "Keyword_y"])
            combined_df = combined_df.rename(columns={"Company Name_x": "Company Name",
                                                      "Domain_x": "Domain",
                                                      "Page URL_x": "Page URL",
                                                      "Keyword_x": "Keyword"})

        else:
            merge_keys = ["Company Name", "Domain", "Page URL", "Keyword"]
            print("Falling back to composite key as 'Company ID' is not a suitable merge key.")
            combined_df = pd.merge(df1, df2, on=merge_keys, how='inner', suffixes=("_x", "_y"))

        if "Company ID_x" in combined_df.columns:
            combined_df = combined_df.rename(columns={"Company ID_x": "Company ID"})
        if "Date_x" in combined_df.columns:
            combined_df = combined_df.rename(columns={"Date_x": "Date"})

        if "Company ID_y" in combined_df.columns:
            combined_df = combined_df.drop(columns=["Company ID_y"])
        if "Date_y" in combined_df.columns:
            combined_df = combined_df.drop(columns=["Date_y"])

        combined_df['Final_output'] = combined_df['Usage Indicated_f1'].astype(str) + combined_df[
            'Usage Indicated_f2'].astype(str)

        print("\n--- Summary of Final Output Combinations ---")
        final_output_counts = combined_df['Final_output'].value_counts()
        print(final_output_counts.to_string())
        print(f"{"-"*46}")

        final_columns = [
            "Company ID",
            "Company Name",
            "Domain",
            "Page URL",
            "Keyword",
            "Date",
            "Usage Indicated_f1",
            "Explanation_f1",
            "Usage Indicated_f2",
            "Explanation_f2",
            "Final_output"
        ]

        columns_to_select = [col for col in final_columns if col in combined_df.columns]
        combined_df = combined_df[columns_to_select]

        if not os.path.exists("result_concat"):
            os.makedirs("result_concat")
        output_file_path = f"result_concat/{final_output_path}.csv"
        output_path = Path(output_file_path).resolve().as_uri()
        combined_df.to_csv(output_file_path, index=False)

        print(f"Successfully combined the files: '{final_output_path}.csv'\n"
              f"»» {output_path}")

    except FileNotFoundError:
        print("Error: One of the input files was not found. Please check the file paths.")
    except KeyError as ke:
        print(
            f"Error: A required column was not found. Please ensure all headers are present in your CSV files. Missing key: {ke}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    combine_csv_files(input_1, input_2, final_output)