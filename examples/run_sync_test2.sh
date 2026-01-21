#!/usr/bin/env zsh

source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate pyvideomeg

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Set your file paths here
VIDEO1="public-archivedwl-494/2025-09-04--14-44-09_test_1/2025-09-04--14-44-09_video_01.vid"
VIDEO2="public-archivedwl-494/2025-09-04--14-44-09_test_1/2025-09-04--14-44-09_video_02.vid"
AUDIO="public-archivedwl-494/2025-09-04--14-44-09_test_1/2025-09-04--14-44-09_audio_00.aud"
MEG="public-archivedwl-494/2025-09-04--14-44-09_test_1/2025_09_04__14_44_09_MEG.fif"

OUTPUT_DIR="/tmp/sync_output"
TIMING_CHANNEL="STI009"
MEG_CHANNEL="STI009"

PYTHON_SCRIPT="examples/sync_test2.py"

# Run the Python script
python "$PYTHON_SCRIPT" \
    "$VIDEO1" \
    "$VIDEO2" \
    "$AUDIO" \
    "$MEG" \
    -o "$OUTPUT_DIR" \
    -t "$TIMING_CHANNEL" \
    -m "$MEG_CHANNEL"

