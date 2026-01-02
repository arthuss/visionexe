import os
import csv

def collect_analysis_files(start_dir, output_csv):
    # Prepare the list to hold the data
    data = []

    # Walk through the directory tree
    for root, dirs, files in os.walk(start_dir):
        if 'analysis_llm.txt' in files:
            file_path = os.path.join(root, 'analysis_llm.txt')
            
            try:
                # Read the content of the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Append to data list: [Absolute Path, Content]
                # Using abspath to give the full link "from where it comes"
                data.append([os.path.abspath(file_path), content])
                
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    # Write to CSV
    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(['Source Path', 'Content'])
            # Write data rows
            writer.writerows(data)
        print(f"Successfully processed {len(data)} files. Output saved to {output_csv}")
    except Exception as e:
        print(f"Error writing CSV: {e}")

if __name__ == "__main__":
    # Define start directory and output file
    # Assuming the script is run from the project root C:\Users\sasch\henoch
    start_directory = os.path.join(os.getcwd(), 'filmsets')
    output_filename = 'analysis_summary.csv'
    
    if os.path.exists(start_directory):
        collect_analysis_files(start_directory, output_filename)
    else:
        print(f"Directory not found: {start_directory}")
