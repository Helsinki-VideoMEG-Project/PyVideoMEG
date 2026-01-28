#!/usr/bin/env python

"""
Export a pair of video and audio files to a standard video format. Requires
ffmpeg.

Usage: pvm_export video_file_name audio_file_name output_file_name. The audio
file name is optional.

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

import glob
import os
import shutil
import struct
import sys
import tempfile

import numpy
from PIL import Image, ImageDraw

try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO

import ffmpeg

import pyvideomeg
from pyvideomeg.fonts import DEFAULT_FONT_SIZE, load_font


def get_ffmpeg_format(format_string):
    """
    Convert Python struct format string to ffmpeg audio format string.

    Args:
        format_string: Python struct format code (e.g., 'h', 'i', 'f')

    Returns:
        ffmpeg format string (e.g., 's16le', 's32le', 'f32le')
    """
    format_map = {
        "b": "s8",
        "B": "u8",
        "h": "s16le",
        "H": "u16le",
        "i": "s32le",
        "I": "u32le",
        "l": "s32le",
        "L": "u32le",
        "f": "f32le",
        "d": "f64le",
    }
    clean_format = format_string.strip("<>=@!")
    if clean_format in format_map:
        return format_map[clean_format]
    else:
        raise ValueError(f"Unknown audio format string: {format_string}")


def main():
    tmp_fldr = tempfile.mkdtemp()
    print("Using '%s' for storing temporary files" % tmp_fldr)

    if len(sys.argv) < 3:
        print("Usage: pvm_export video_file_name [audio_file_name] output_file_name")
        print("  If audio_file_name is omitted, only video will be exported")
        sys.exit(1)

    vid_file = pyvideomeg.VideoData(sys.argv[1])
    fnt = load_font(DEFAULT_FONT_SIZE)

    for i in range(len(vid_file.ts)):
        img = Image.open(BytesIO(vid_file.get_frame(i)))
        draw = ImageDraw.Draw(img)
        draw.text(
            (10, 0),
            "%i  :  %s" % (vid_file.ts[i], pyvideomeg.ts2str(vid_file.ts[i])),
            font=fnt,
            fill="black",
        )
        img.save("%s/%08i.jpg" % (tmp_fldr, i))

    if len(sys.argv) == 3:
        print("No audio file is specified, using only the video")
        fps = len(vid_file.ts) / (float(vid_file.ts[-1] - vid_file.ts[0]) / 1000)
        print("FPS: %f" % fps)

        output_file = sys.argv[2]
        pattern = "%s/%%08d.jpg" % tmp_fldr

        output_format = None
        if output_file.lower().endswith(".avi") or output_file.lower().endswith(
            ".avi.tmp"
        ):
            output_format = "avi"
        elif output_file.lower().endswith(".mp4"):
            output_format = "mp4"
        elif output_file.lower().endswith(".mov"):
            output_format = "mov"

        try:
            output_args = {"vcodec": "libx264", "pix_fmt": "yuv420p"}
            if output_format:
                output_args["f"] = output_format

            (
                ffmpeg.input(pattern, framerate=fps)
                .output(output_file, **output_args)
                .overwrite_output()
                .run(quiet=True, capture_stderr=True)
            )
            ret_code = 0
        except ffmpeg.Error as e:
            print("Error running ffmpeg:")
            print(e.stderr.decode() if e.stderr else str(e))
            ret_code = 1
        except Exception as e:
            print("Error running ffmpeg: %s" % e)
            ret_code = 1

        if ret_code != 0:
            print("ERROR: Encoding failed")
            shutil.rmtree(tmp_fldr)
            del vid_file
            sys.exit(1)

        shutil.rmtree(tmp_fldr)
        del vid_file
        sys.exit(0)

    aud_file = pyvideomeg.AudioData(sys.argv[2])

    if aud_file.ts[0] < vid_file.ts[0]:
        first_vid_indx = 0
        first_aud_indx = numpy.argmin(abs(aud_file.ts - vid_file.ts[0]))
    else:
        first_aud_indx = 0
        first_vid_indx = numpy.argmin(abs(vid_file.ts - aud_file.ts[0]))

    if aud_file.ts[-1] > vid_file.ts[-1]:
        last_vid_indx = len(vid_file.ts) - 1
        last_aud_indx = numpy.argmin(abs(aud_file.ts - vid_file.ts[-1]))
    else:
        last_aud_indx = len(aud_file.ts) - 1
        last_vid_indx = numpy.argmin(abs(vid_file.ts - aud_file.ts[-1]))

    # make sure there is an overlap between video and audio
    assert (first_aud_indx != last_aud_indx) & (first_vid_indx != last_vid_indx)

    # delete the video frames for which there is no audio and renumber the remaining ones
    remaining_frames = []
    for i in range(len(vid_file.ts)):
        if (i < first_vid_indx) | (i > last_vid_indx):
            os.remove("%s/%08i.jpg" % (tmp_fldr, i))
        else:
            remaining_frames.append(i)

    # Renumber remaining frames sequentially so ffmpeg can read them
    for new_idx, old_idx in enumerate(remaining_frames):
        old_path = "%s/%08i.jpg" % (tmp_fldr, old_idx)
        new_path = "%s/%08i.jpg" % (tmp_fldr, new_idx)
        if old_idx != new_idx:
            os.rename(old_path, new_path)

    # dump the relevant part of the audio to the file
    out_file = open(tmp_fldr + "/audio.raw", "wb")
    out_file.write(
        aud_file.raw_audio[
            (first_aud_indx * aud_file.buf_sz) : ((last_aud_indx + 1) * aud_file.buf_sz)
        ]
    )
    out_file.close()

    video_frame_cnt = last_vid_indx - first_vid_indx + 1
    audio_frame_cnt = last_aud_indx - first_aud_indx + 1

    print(
        "Discarded %i video frames out of %i"
        % (len(vid_file.ts) - video_frame_cnt, len(vid_file.ts))
    )
    print(
        "Discarded %i audio buffers out of %i"
        % (len(aud_file.ts) - audio_frame_cnt, len(aud_file.ts))
    )

    fps = video_frame_cnt / (
        float(vid_file.ts[last_vid_indx] - vid_file.ts[first_vid_indx]) / 1000
    )
    print("FPS: %f" % fps)

    # Get bytes per sample from the format string
    bytes_per_sample = struct.calcsize(aud_file.format_string)
    wc_srate = (
        audio_frame_cnt * aud_file.buf_sz / bytes_per_sample / aud_file.nchan
    ) / (float(aud_file.ts[last_aud_indx] - aud_file.ts[first_aud_indx]) / 1000)
    fixed_fps = fps * aud_file.srate / wc_srate
    print(
        "nominal sampling rate is %i\nwall clock sampling rate is %f\nnumber of channels: %i\nformat: %s\nfixed FPS: %f"
        % (aud_file.srate, wc_srate, aud_file.nchan, aud_file.format_string, fixed_fps)
    )

    output_file = sys.argv[3]
    audio_file = tmp_fldr + "/audio.raw"
    pattern = "%s/%%08d.jpg" % tmp_fldr

    output_format = None
    if output_file.lower().endswith(".avi") or output_file.lower().endswith(".avi.tmp"):
        output_format = "avi"
    elif output_file.lower().endswith(".mp4"):
        output_format = "mp4"
    elif output_file.lower().endswith(".mov"):
        output_format = "mov"

    img_files = glob.glob("%s/*.jpg" % tmp_fldr)
    print("Found %i image files in temp directory" % len(img_files))
    if len(img_files) == 0:
        print("ERROR: No image files found in temp directory %s" % tmp_fldr)
        ret_code = 1
    else:
        try:
            ffmpeg_audio_format = get_ffmpeg_format(aud_file.format_string)
            print("Using ffmpeg audio format: %s" % ffmpeg_audio_format)

            video_input = ffmpeg.input(pattern, framerate=fixed_fps)
            audio_input = ffmpeg.input(
                audio_file,
                format=ffmpeg_audio_format,
                ar=aud_file.srate,
                ac=aud_file.nchan,
            )

            output_args = {"vcodec": "libx264", "pix_fmt": "yuv420p", "acodec": "aac"}
            if output_format:
                output_args["f"] = output_format

            (
                ffmpeg.output(video_input, audio_input, output_file, **output_args)
                .global_args("-shortest")
                .overwrite_output()
                .run(quiet=True, capture_stderr=True)
            )
            ret_code = 0
        except ffmpeg.Error as e:
            print("Error running ffmpeg:")
            print(e.stderr.decode() if e.stderr else str(e))
            ret_code = 1
        except Exception as e:
            print("Error running ffmpeg: %s" % e)
            ret_code = 1

    if ret_code != 0:
        print("ERROR: Encoding failed with return code %i" % ret_code)
        shutil.rmtree(tmp_fldr)
        sys.exit(1)

    shutil.rmtree(tmp_fldr)


if __name__ == "__main__":
    main()
