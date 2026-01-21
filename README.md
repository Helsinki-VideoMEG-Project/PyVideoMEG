# PyVideoMEG

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Python tools for analyzing video-MEG (magnetoencephalography) recordings.

## Installation

### From source (recommended)

```bash
git clone https://github.com/Helsinki-VideoMEG-Project/PyVideoMEG.git
cd PyVideoMEG
pip install .
```

### Development installation

For development with editable install:

```bash
git clone https://github.com/Helsinki-VideoMEG-Project/PyVideoMEG.git
cd PyVideoMEG
pip install -e ".[dev]"
```

### Optional dependencies

Install with analysis tools (matplotlib, plotly, mne):

```bash
cd PyVideoMEG
pip install -e ".[analysis]"
```

Install all optional dependencies:

```bash
cd PyVideoMEG
pip install -e ".[all]"
```

## Quick Start

```python
import pyvideomeg

# Read video data
video = pyvideomeg.VideoData('recording.vid')

# Read audio data  
audio = pyvideomeg.AudioData('recording.aud')

# Get timestamps
print(f"Video frames: {len(video.ts)}")
print(f"First frame: {pyvideomeg.ts2str(video.ts[0])}")
```

## Command Line Tools

PyVideoMEG includes several command-line utilities:

- `pvm_show_info` - Display information about video/audio files (version, frame count, timestamps, etc.)
- `pvm_export` - Export video-MEG recordings to standard video formats (MP4, AVI, etc.). Requires ffmpeg or mencoder.
- `pvm_export_audio` - Export audio data to WAV format
- `pvm_merge` - Merge two video files side-by-side into a single video file
- `pvm_repair` - Repair corrupted video or audio files (assumes damage is at the end of the file)
- `pvm_repack_audio` - Repack audio files by changing the buffer size
- `pvm_data_converter0_1` - Convert video/audio files from format version 0 to version 1
- `pvm_export_dragdrop` - Drag-and-drop converter for batch processing video files

### Usage Examples

```bash
# Display file information
pvm_show_info recording.vid

# Export video with audio to MP4
pvm_export recording.vid recording.aud output.mp4

# Export only video (no audio)
pvm_export recording.vid output.mp4

# Export audio to WAV
pvm_export_audio recording.aud

# Merge two video files side-by-side
pvm_merge video1.vid video2.vid merged_output.mp4

# Repair a corrupted file
pvm_repair corrupted.vid fixed.vid

# Repack audio with new buffer size
pvm_repack_audio input.aud 1024 output.aud
```

## Examples

The `examples/` directory contains example scripts demonstrating advanced usage:

- `sync_test.py` - Assess video/audio/MEG synchronization (requires matplotlib and mne)
- `sync_test2.py` - Assess synchronization with two video files (requires matplotlib and mne)
- `merge_videos.py` - Python script for merging video files programmatically

See the example scripts and their corresponding shell scripts (`run_*.sh`) for usage patterns.

## Requirements

- Python >= 3.11
- NumPy
- Pillow
- SciPy

Optional:
- Matplotlib (for visualization and examples)
- Plotly (for interactive plots)
- MNE (for MEG data analysis in examples)

**External tools** (for video export):
- ffmpeg or mencoder (required for `pvm_export` and `pvm_merge` commands)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
