import csv

def convert_csv(input_file, output_file):
    with open(input_file, 'r') as infile:
        reader = csv.DictReader(infile)
        
        # Define the output fieldnames
        fieldnames = [
            '#timestamp [ns]',
            'w_RS_S_x [rad s^-1]',
            'w_RS_S_y [rad s^-1]',
            'w_RS_S_z [rad s^-1]',
            'a_RS_S_x [m s^-2]',
            'a_RS_S_y [m s^-2]',
            'a_RS_S_z [m s^-2]'
        ]

        with open(output_file, 'w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                try:
                    time_ns = int(float(row['Time']) * 1e9)
                    writer.writerow({
                        '#timestamp [ns]': time_ns,
                        'w_RS_S_x [rad s^-1]': row['Angular_VelX'],
                        'w_RS_S_y [rad s^-1]': row['Angular_VelY'],
                        'w_RS_S_z [rad s^-1]': row['Angular_VelZ'],
                        'a_RS_S_x [m s^-2]': row['Linear_AccX'],
                        'a_RS_S_y [m s^-2]': row['Linear_AccY'],
                        'a_RS_S_z [m s^-2]': row['Linear_AccZ']
                    })
                except ValueError as e:
                    print(f"Skipping row due to error: {e}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python convert_csv.py input.csv output.csv")
    else:
        convert_csv(sys.argv[1], sys.argv[2])
