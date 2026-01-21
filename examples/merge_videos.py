# -*- coding: utf-8 -*-
"""An example: merging two video files
    
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
import os
import sys
import numpy as np
from PIL import Image
import io
import struct

import pyvideomeg

# Default frame size
FRAME_SZ = (1280, 480)


def main():
    parser = argparse.ArgumentParser(
        description='Merge two video files side by side into a single video file'
    )
    parser.add_argument('video1', help='Path to first video file (.vid)')
    parser.add_argument('video2', help='Path to second video file (.vid)')
    parser.add_argument('output', help='Path to output merged video file (.vid)')
    parser.add_argument('--frame-width', type=int, default=1280,
                       help='Width of output frames (default: 1280)')
    parser.add_argument('--frame-height', type=int, default=480,
                       help='Height of output frames (default: 480)')
    
    args = parser.parse_args()
    
    # Validate input files
    for file_path, name in [(args.video1, 'video1'), (args.video2, 'video2')]:
        if not os.path.isfile(file_path):
            print(f'Error: {name} file not found: {file_path}', file=sys.stderr)
            return 1
    
    # Check if output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.isdir(output_dir):
        print(f'Error: Output directory does not exist: {output_dir}', file=sys.stderr)
        return 1
    
    # Warn if output file exists
    if os.path.isfile(args.output):
        response = input(f'Output file {args.output} already exists. Overwrite? (y/N): ')
        if response.lower() != 'y':
            print('Aborted.')
            return 1
    
    FRAME_SZ = (args.frame_width, args.frame_height)
    
    print(f'Loading video files...')
    file_1 = pyvideomeg.VideoData(args.video1)
    file_2 = pyvideomeg.VideoData(args.video2)
    
    print(f'Video 1: {len(file_1.ts)} frames')
    print(f'Video 2: {len(file_2.ts)} frames')
    print(f'Merging frames...')
    
    out_file = open(args.output, 'wb')
    out_file.write(b'HELSINKI_VIDEO_MEG_PROJECT_VIDEO_FILE')
    out_file.write(struct.pack('I', 1))  # file format version
    
    for i in range(len(file_1.ts)):
        # find the closest matching frame from the second file
        file2_indx = np.argmin(np.abs(file_2.ts - file_1.ts[i]))
        
        # merge the images
        im0 = Image.open(io.BytesIO(file_1.get_frame(i)))
        im1 = Image.open(io.BytesIO(file_2.get_frame(file2_indx)))
        
        im0_r = im0.resize((FRAME_SZ[0]//2, FRAME_SZ[1]), Image.Resampling.LANCZOS)
        im1_r = im1.resize((FRAME_SZ[0]//2, FRAME_SZ[1]), Image.Resampling.LANCZOS)
        
        res = Image.new('RGB', FRAME_SZ)
        res.paste(im0_r, (0, 0))
        res.paste(im1_r, (FRAME_SZ[0]//2, 0))
    
        # write the merged image to the output file
        buf = io.BytesIO()
        res.save(buf, 'JPEG')
        frame_size = len(buf.getvalue())
        out_file.write(struct.pack('Q', int(file_1.ts[i])))
        out_file.write(struct.pack('I', frame_size))
        out_file.write(buf.getvalue())
        buf.close()
        
        if (i + 1) % 100 == 0:
            print(f'Processed {i + 1} / {len(file_1.ts)} frames...')
        
    out_file.close()
    print(f'Done! Merged video saved to: {args.output}')
    return 0


if __name__ == '__main__':
    exit(main())
