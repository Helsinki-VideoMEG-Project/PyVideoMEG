# -*- coding: utf-8 -*-
"""An example: code for assessing video/audio/MEG synchronization.

This script takes a triplet (fiff, audio, and video) of files and generates
a bunch of pictures. Each picture describes a short piece of the
recordings. The upper pane shows 3 consecutive video frames. The lower pane
shows the corresponding pieces of audio and a single MEG channel. The black
vertical lines mark the frame locations.

---------------------------------------------------------------------------
Author: Andrey Zhdanov
Copyright (C) 2014 BioMag Laboratory, Helsinki University Central Hospital

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import argparse
import io
import os
import sys

import numpy as np
import PIL

import pyvideomeg

# Check for optional dependencies
try:
    import matplotlib.pyplot as plt
except ImportError:
    print("Error: matplotlib is required but not installed.", file=sys.stderr)
    print("Please install it with: pip install matplotlib", file=sys.stderr)
    print(
        "Or install all analysis dependencies: pip install pyvideomeg[analysis]",
        file=sys.stderr,
    )
    sys.exit(1)

try:
    import mne
except ImportError:
    print("Error: mne is required but not installed.", file=sys.stderr)
    print("Please install it with: pip install mne", file=sys.stderr)
    print(
        "Or install all analysis dependencies: pip install pyvideomeg[analysis]",
        file=sys.stderr,
    )
    sys.exit(1)

# Default values
FRAME_SZ = (640, 480)
WIND_WIDTH = 3  # in frames

# Percentiles to be used for vertical scaling (to avoid problems caused by
# outlers). Should be a float between 0 and 100
SCALE_PRCTILE_AUDIO = 99.99
SCALE_PRCTILE_MEG = 99.99


def find_sti_channel(raw):
    """Find the STI channel with the most trigger activity."""
    sti_channels = [ch for ch in raw.info["ch_names"] if ch.startswith("STI")]
    if not sti_channels:
        return None

    max_activity = 0
    best_channel = sti_channels[0]

    for ch in sti_channels:
        try:
            picks = mne.pick_types(raw.info, meg=False, include=[ch])
            if len(picks) > 0:
                data = raw[picks, :][0].squeeze()
                activity = np.sum(np.abs(np.diff(data > 0)))  # Count trigger edges
                if activity > max_activity:
                    max_activity = activity
                    best_channel = ch
        except:
            continue

    return best_channel


def main():
    parser = argparse.ArgumentParser(
        description="Assess video/audio/MEG synchronization by generating visualization frames"
    )
    parser.add_argument("video", help="Path to video file (.vid)")
    parser.add_argument("audio", help="Path to audio file (.aud)")
    parser.add_argument("meg", help="Path to MEG file (.fif)")
    parser.add_argument(
        "-o",
        "--output",
        default="/tmp",
        help="Output directory for generated frames (default: /tmp)",
    )
    parser.add_argument(
        "-t",
        "--timing-channel",
        default=None,
        help="MEG timing channel name (e.g., STI006). If not specified, will auto-detect.",
    )
    parser.add_argument(
        "-m",
        "--meg-channel",
        default=None,
        help="MEG channel name to display (e.g., STI006). If not specified, will use timing channel.",
    )

    args = parser.parse_args()

    # Validate input files
    for file_path, name in [
        (args.video, "video"),
        (args.audio, "audio"),
        (args.meg, "meg"),
    ]:
        if not os.path.isfile(file_path):
            print(f"Error: {name} file not found: {file_path}")
            return 1

    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)

    # --------------------------------------------------------------------------
    # Load the data
    #
    raw = mne.io.Raw(args.meg, allow_maxshield=True)

    # Determine timing channel
    if args.timing_channel:
        TIMING_CH = args.timing_channel
    else:
        print("No timing channel specified. Auto-detecting...")
        TIMING_CH = find_sti_channel(raw)
        if TIMING_CH:
            print(f"Using timing channel: {TIMING_CH}")
        else:
            print("Error: Could not find any STI channels in MEG file.")
            return 1

    # Determine MEG channel (default to timing channel if not specified)
    if args.meg_channel:
        MEG_CH = args.meg_channel
    else:
        MEG_CH = TIMING_CH

    # Try to load the timing channel
    try:
        picks_timing = mne.pick_types(raw.info, meg=False, include=[TIMING_CH])
        if len(picks_timing) == 0:
            print(f'Error: Timing channel "{TIMING_CH}" not found in MEG file.')
            print(
                f"Available STI channels: {[ch for ch in raw.info['ch_names'] if ch.startswith('STI')]}"
            )
            return 1
        dt_timing = raw[picks_timing, :][0].squeeze()
    except Exception as e:
        print(f'Error loading timing channel "{TIMING_CH}": {e}')
        print(
            f"Available STI channels: {[ch for ch in raw.info['ch_names'] if ch.startswith('STI')]}"
        )
        return 1

    # Try to load the MEG channel
    try:
        picks_meg = mne.pick_types(raw.info, meg=False, include=[MEG_CH])
        if len(picks_meg) == 0:
            print(f'Error: MEG channel "{MEG_CH}" not found in MEG file.')
            print(
                f"Available STI channels: {[ch for ch in raw.info['ch_names'] if ch.startswith('STI')]}"
            )
            return 1
        meg = raw[picks_meg, :][0].squeeze()
    except Exception as e:
        print(f'Error loading MEG channel "{MEG_CH}": {e}')
        print(
            f"Available STI channels: {[ch for ch in raw.info['ch_names'] if ch.startswith('STI')]}"
        )
        return 1

    # compute the timestamps for the MEG channel
    meg_ts = pyvideomeg.comp_tstamps(dt_timing, raw.info["sfreq"])

    vid_file = pyvideomeg.VideoData(args.video)
    aud_file = pyvideomeg.AudioData(args.audio)

    audio, audio_ts = aud_file.format_audio()
    audio = audio[0, :].squeeze()  # use only the first audio channel

    # --------------------------------------------------------------------------
    # Make the pics
    #
    plt.ioff()  # don't pop up the figure windows

    ts_scale = np.diff(vid_file.ts).max() * (WIND_WIDTH + 0.1)
    meg_scale = np.percentile(np.abs(meg), SCALE_PRCTILE_MEG) * 1.1
    aud_scale = np.percentile(np.abs(audio), SCALE_PRCTILE_AUDIO) * 1.1

    num_frames = len(vid_file.ts) - 2 * (1 + WIND_WIDTH)
    print(f"Generating {num_frames} frames...")

    for i in range(1 + WIND_WIDTH, len(vid_file.ts) - (1 + WIND_WIDTH)):
        # combine 3 frames
        im0 = PIL.Image.open(io.BytesIO(vid_file.get_frame(i - 1)))
        im1 = PIL.Image.open(io.BytesIO(vid_file.get_frame(i)))
        im2 = PIL.Image.open(io.BytesIO(vid_file.get_frame(i + 1)))

        res = PIL.Image.new("RGB", (FRAME_SZ[0] * 3, FRAME_SZ[1]))
        res.paste(im0, (0, 0))
        res.paste(im1, (FRAME_SZ[0], 0))
        res.paste(im2, (FRAME_SZ[0] * 2, 0))

        plt.figure()

        # plot the frames
        plt.subplot(2, 1, 1)
        plt.imshow(np.asarray(res))
        plt.xticks(())
        plt.yticks(())

        # plot the traces
        min_ts = vid_file.ts[i] - ts_scale
        max_ts = vid_file.ts[i] + ts_scale

        plt.subplot(2, 1, 2)
        meg_indx = np.where((meg_ts > min_ts) & (meg_ts < max_ts))
        plt.plot(meg_ts[meg_indx], meg[meg_indx] / meg_scale, "b")

        audio_indx = np.where((audio_ts > min_ts) & (audio_ts < max_ts))
        plt.plot(audio_ts[audio_indx], audio[audio_indx] / aud_scale, "g")

        # mark the frame positions
        plt.plot(vid_file.ts[i - 1] * np.ones(2), (-1, 1), "k")
        plt.plot(vid_file.ts[i] * np.ones(2), (-1, 1), "k")
        plt.plot(vid_file.ts[i + 1] * np.ones(2), (-1, 1), "k")

        plt.xticks(())
        plt.yticks(())
        plt.xlim((min_ts, max_ts))
        plt.ylim((-1, 1))

        plt.savefig("%s/frame-%07d.png" % (args.output, i))
        plt.close("all")

        if (i - WIND_WIDTH) % 100 == 0:
            print(f"Processed {i - WIND_WIDTH} / {num_frames} frames...")

    print(f"Done! Generated frames saved to: {args.output}")
    return 0


if __name__ == "__main__":
    exit(main())
