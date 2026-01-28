#!/usr/bin/env zsh

# Note: The following lines set up a specific Conda environment for the examples.
# Please adjust or comment them out if you use a different environment manager.
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate pyvideomeg

# Set your file paths here
VIDEO1="public-archivedwl-494/Sadad_Recording/2025-09-19--18-08-56_video_01.vid"
VIDEO2="public-archivedwl-494/Sadad_Recording/2025-09-19--18-08-56_video_02.vid"

OUTPUT_FILE="/tmp/merged_video.vid"
FRAME_WIDTH=1280
FRAME_HEIGHT=480

PYTHON_SCRIPT="examples/merge_videos.py"

# Run the Python script
python "$PYTHON_SCRIPT" \
    "$VIDEO1" \
    "$VIDEO2" \
    "$OUTPUT_FILE" \
    --frame-width "$FRAME_WIDTH" \
    --frame-height "$FRAME_HEIGHT"

