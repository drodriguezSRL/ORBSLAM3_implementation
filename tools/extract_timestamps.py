import csv

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

extract_timestamps('/mnt/c/users/david/downloads/spice-hl3/cam0/data.csv', '/mnt/c/users/david/downloads/spice-hl3/spicehl3_timeStamps/trajecory_F.txt')
