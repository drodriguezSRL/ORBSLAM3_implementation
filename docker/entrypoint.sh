#! /bin/bash
set -e # immediate exit on error


# === Config ===
VOCAB="./Vocabulary/ORBvoc.txt"
DATASET="/data/EuRoc/MH01"
DATASET_NAME="dataset-MH01"
TIME_BASE="./Examples"
CONFIG_BASE="./Examples"
MODE="$1" #passing on first argument

function print_usage() {
    echo "Usage: docker run ... [mode]" # I may have to change this to the actual instructions
    echo ""
    echo "Available modes:"
    echo " mono     - Monocular"
    echo " monoi    - Monocular inertial"
    echo " stereo   - Stereo"
    echo " stereoi  - Stereo inertial"
    echo ""
    echo "Example:"
    echo " docker run orbslam3_container mono" # to be changed...
}

if [[-z "$MODE"]]; then # if MODE is zero length
    echo "❌ Error: No mode specified."
    print_usage
    exit 1
fi

case "$MODE" in
    mono)
        EXEC="./Examples/Monocular/mono_euroc"
        CONFIG="$CONFIG_BASE/Monocular/EuRoC.yaml"
        TIMESTAMPS="$TIME_BASE/Monocular/EuRoC_TimeStamps/MH01.txt"
        ;;
    monoi)
        EXEC="./Examples/Monocular-Inertial/mono_inertial_euroc"
        CONFIG="$CONFIG_BASE/Monocular-Intertial/EuRoC.yaml"
        TIMESTAMPS="$TIME_BASE/Monocular-Intertial/EuRoC_TimeStamps/MH01.txt"
        ;;
    stereo)
        EXEC="./Examples/Stereo/stereo_euroc"
        CONFIG="$CONFIG_BASE/Stereo/EuRoC.yaml"
        TIMESTAMPS="$TIME_BASE/Stereo/EuRoC_TimeStamps/MH01.txt"
        ;;
    stereoi)
        EXEC="./Examples/Stereo-Inertial/stereo_inertial_euroc"
        CONFIG="$CONFIG_BASE/Stereo-Inertial/EuRoC.yaml"
        TIMESTAMPS="$TIME_BASE/Stereo-Inertial/EuRoC_TimeStamps/MH01.txt"
        ;;
    *)
        echo "❌ Error: Invalid mode '$MODE'"
        print_usage
        exit 1
        ;;
esac

# === sanity checks ===
if [[! -f "$EXEC"]]; then
    echo "❌ Error: Executable $EXEC not found."
    exit 1
fi

if [[ ! -d "$DATASET" ]]; then
    echo "❌ Error: Dataset directory $DATASET not found."
    exit 1
fi

echo "🚀 Launching ORB_SLAM3 in '$MODE' mode..."
"$EXEC" "$VOCAB" "$CONFIG" "$DATASET" "$TIMESTAMPS" "${DATASET_NAME}_$MODE"
