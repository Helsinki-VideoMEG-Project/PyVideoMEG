#!/usr/bin/env zsh

source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate pyvideomeg

# Set your file paths here
VIDEO="public-archivedwl-494/Sadad_Recording/2025-09-19--18-08-56_video_01.vid"
AUDIO="public-archivedwl-494/Sadad_Recording/2025-09-19--18-08-56_audio_00.aud"
MEG="public-archivedwl-494/2025-09-04--14-44-09_test_1/2025_09_04__14_44_09_MEG.fif"

OUTPUT_DIR="/tmp/sync_output"
TIMING_CHANNEL="STI009"
MEG_CHANNEL="STI009"

PYTHON_SCRIPT="examples/sync_test.py"

# Run the Python script
python "$PYTHON_SCRIPT" \
    "$VIDEO" \
    "$AUDIO" \
    "$MEG" \
    -o "$OUTPUT_DIR" \
    -t "$TIMING_CHANNEL" \
    -m "$MEG_CHANNEL"

