import os
import csv
import time
import statistics

def get_first_column_values(filepath):
    """Read the first column of a CSV file and return its values."""
    with open(filepath, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader, None) # Skip the header row
        rows = [row[0] for row in reader if row]
        print(f"{filepath}: {len(rows)} rows (excluding header)")
        return set(rows), rows

def compute_frame_stats(timestamps, label):
    """Compute and print framerate for the given timestamps."""
    timestamps = sorted(int(ts) for ts in timestamps)
    if len(timestamps) < 2:
        print(f"{label} - Not enough data to compute framerate.")
        return

    deltas = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps) - 1)]
    mean_interval_ns = statistics.mean(deltas)
    std_dev_ns = statistics.stdev(deltas) if len(deltas) > 1 else 0 

    mean_interval_s = mean_interval_ns / 1e9
    std_dev_s = std_dev_ns / 1e9

    framerate = 1 / mean_interval_s if mean_interval_s else 0 

    print(f"\n{label} Stats:")
    print(f"  Avg frame interval: {mean_interval_s:.6f} s")
    print(f"  Frame rate: {framerate:.2f} FPS")
    print(f"  Interval std deviation: {std_dev_s:.6f} s")

def find_closest_timestamp(target, candidates, max_diff=5): # 5ns 
    """Find the closest timestamp in candidates to the target timestamp."""
    target = int(target)
    candidates = sorted(int(c) for c in candidates)
    closest = min(candidates, key=lambda x: abs(x - target))
    return str(closest) if abs(closest - target) <= max_diff else None

def find_missing_frames(file1, file2):
    """Find and return the missing frames from file1 that are not present in file2."""
    frames1, frames1_list = get_first_column_values(file1)
    frames2, frames2_list = get_first_column_values(file2)
    
    missing_frames = set(frames1) - set(frames2)

    closest_count = 0

    print("Missing timestamps in file2:")
    for ts in sorted(missing_frames):

        closest = find_closest_timestamp(ts, frames2)
        if closest:
            print(f"Missing: {ts} → CLOSEST MATCH FOUND!!: {closest}")
            closest_count += 1
            #time.sleep(1)
        else:
             print(f"Missing: {ts} → No close match found (over 5ns difference)")

    print(f"\nTotal missing or mismatched timestamps: {len(missing_frames)}")
    print(f"\nTotal closest timestamps found: {closest_count}")

    # computing and printing framerate stats
    compute_frame_stats(frames1_list, "Cam0")
    compute_frame_stats(frames2_list, "Imu0")

def load_timestamps(filepath):
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        data = [row for row in reader if row]
        return header, data

def save_cleaned_csv(filepath, header, rows):
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        writer.writerows(rows)

def clean_missing_timestamps(target, reference, image_dir):
    # Load timestamps from both CSVs
    _, file1_data = load_timestamps(target)
    _, file2_data = load_timestamps(reference)

    file1_timestamps = {row[0]: row for row in file1_data}
    file2_timestamps = {row[0] for row in file2_data}

    cleaned_rows = []
    removed = 0

    for ts, row in file1_timestamps.items():
        if ts in file2_timestamps:
            cleaned_rows.append(row)
        else:
            # Delete the image file if it exists
            image_path = os.path.join(image_dir, row[1])
            if os.path.isfile(image_path):
                os.remove(image_path)
                print(f"Deleted image: {image_path}")
            else:
                print(f"Image not found (skipped): {image_path}")
            removed += 1

    print(f"\nRemoved {removed} rows with missing timestamps from {target}")

    # Save the cleaned CSV
    header, _ = load_timestamps(target)
    save_cleaned_csv(target, header, cleaned_rows)


file1 = '/mnt/c/users/david/downloads/spice-hl3/mav0/cam0/data.csv'
file2 = '/mnt/c/users/david/downloads/spice-hl3/mav0/cam1/data.csv'
file3 = '/mnt/c/users/david/downloads/spice-hl3/mav0/imu0/data.csv'
img_dir1 = '/mnt/c/users/david/downloads/spice-hl3/mav0/cam0/data/'
img_dir2 = '/mnt/c/users/david/downloads/spice-hl3/mav0/cam1/data/'

find_missing_frames(file1, file3)

#clean_missing_timestamps(file1, file2, img_dir1)