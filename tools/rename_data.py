# This script renames files in a specified directory by extracting a timestamp from the filename and converting it to nanoseconds.

import os
import re

data_folder_path = ""

name_pattern = re.compile(r"stereo\_(\w+)\_(\d+\.\d+)\_0")

for filename in os.listdir(data_folder_path):
    match = name_pattern.match(filename)
    if match:
        timestamp_str = match.group(1) # extract timestamp
        try:
            timestamp_ns = int(float(timestamp_str) * 1e9) # convert to nanoseconds
            new_filename = f"{timestamp_ns}.png"

            old_file_path = os.path.join(data_folder_path, filename)
            new_file_path = os.path.join(data_folder_path, new_filename)

            os.rename(old_file_path, new_file_path)

        except ValueError:
            print(f"Error converting timestamp: {timestamp_str} in file {filename}")
    else:
        print(f"Filename {filename} does not match the expected pattern.")

