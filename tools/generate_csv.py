import os
import re
import csv
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate a CSV file from a directory of images.")
    parser.add_argument("data_folder_path", type=str, help="Path to the folder containing the images.")
    parser.add_argument("output_csv_path", type=str, help="Path to the output CSV file.")
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    data_folder_path = args.data_folder_path
    output_csv_path = args.output_csv_path

    if not os.path.isdir(data_folder_path):
        print(f"Error: The path {data_folder_path} is not a valid directory.")
        return

    name_pattern = re.compile(r"^(\d+)\.png$")

    entries = []

    for filename in os.listdir(data_folder_path):
        match = name_pattern.match(filename)
        if match:
            timestamp_str = match.group(1)
            entries.append((timestamp_str, filename))
    
    entries.sort(key=lambda x: int(x[0]))  # Sort by timestamp

    with open(output_csv_path, mode='w', newline= '') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["#timestamp [ns]", "filename"])
        writer.writerows(entries)

    print(f"CSV file saved to: {output_csv_path}")


if __name__ == "__main__":
    main()