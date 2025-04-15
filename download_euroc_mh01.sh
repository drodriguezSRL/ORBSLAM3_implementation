#!/bin/bash

set -e  # Exit on error

# === Configuration ===
DATASET_DIR=~/Datasets/EuRoc
ZIP_URL="http://robotics.ethz.ch/~asl-datasets/ijrr_euroc_mav_dataset/machine_hall/MH_01_easy/MH_01_easy.zip"
ZIP_NAME="MH_01_easy.zip"
TARGET_DIR="${DATASET_DIR}/MH01"

# === Create directory ===
mkdir -p "$DATASET_DIR"
cd "$DATASET_DIR"

# === Download the dataset ===
echo "📥 Downloading MH_01_easy dataset..."
wget -c "$ZIP_URL" -O "$ZIP_NAME"

# === Unzip ===
echo "📦 Unzipping dataset..."
mkdir -p "$TARGET_DIR"
unzip -o "$ZIP_NAME" -d "$TARGET_DIR"

# === Fix corrupted images (if necessary) ===
echo "🩹 Checking and fixing known corrupt images..."
cd "$TARGET_DIR/mav0/cam0/data"

# Define known corrupt/fix pairs
declare -A CORRUPT_IMAGES=(
  ["1403636689613555456.png"]="1403636689663555584.png"
  ["1403636722213555456.png"]="1403636722263555584.png"
)

for bad_img in "${!CORRUPT_IMAGES[@]}"; do
  if [ -f "$bad_img" ]; then
    echo "✅ $bad_img exists, skipping fix."
  else
    good_img="${CORRUPT_IMAGES[$bad_img]}"
    if [ -f "$good_img" ]; then
      echo "🔧 Replacing missing/corrupt $bad_img with $good_img"
      cp "$good_img" "$bad_img"
    else
      echo "⚠️  Warning: Replacement image $good_img not found!"
    fi
  fi
done

echo "✅ EuRoC MH_01_easy dataset setup complete at: $TARGET_DIR"
