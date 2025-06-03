import os
import re
import csv
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate a TXT file from a CSV file.")
    parser.add_argument("csv_folder_path", type=str, help="Path to the CSV file.")
    parser.add_argument("output_txt_path", type=str, help="Path to the output TXT file.")
    return parser.parse_args()

def extract_timestamps(input_file, output_file):
    with open(input_file, 'r', newline='') as infile, open(output_file, 'w', newline='') as outfile:
        for line in infile:
            # Skip headers or comments
            if line.startswith('#') or 'timestamp' in line:
                continue

            # Split line by comma and write only the timestamp
            parts = line.strip().split(',')
            if parts:
                outfile.write(parts[0] + '\n')
    

def main():
    args = parse_arguments()

    csv_file = args.csv_folder_path
    txt_file = args.output_txt_path

    if not os.path.isfile(csv_file):
        print(f"Error: The path {csv_file} is not a valid file.")
        return

    extract_timestamps(csv_file, txt_file)  
    print(f"Timestamps txt file saved to: {txt_file}")  


if __name__ == "__main__":
    main()

