#!/usr/bin/env python

"""This makes a simple drag-and-drop target to convert recorded files
"""

import sys
import os
from os import path as op
import subprocess


def find_encoder():
    """Find available video encoder (ffmpeg or mencoder)."""
    for encoder in ['ffmpeg', 'mencoder']:
        try:
            subprocess.run([encoder, '-version'], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL, 
                         check=True)
            return encoder
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return None


def main():
    for vid_file in sys.argv[1:]:
        if op.splitext(vid_file)[1] == '.aud':
            continue
        if not op.isfile(vid_file):
            raise RuntimeError('Could not find video file %s' % vid_file)
        aud_file = vid_file[:-12] + 'audio_00.aud'
        if not op.isfile(aud_file):
            raise RuntimeError('Could not find audio file %s' % aud_file)
        avi_file = vid_file[:-12] + vid_file.split('_')[-1][:2] + '.avi'
        if not op.isfile(avi_file):
            # Use the local script instead of installed command
            script_dir = op.dirname(op.abspath(__file__))
            export_script = op.join(script_dir, 'pvm_export.py')
            cmd = ['python', export_script, vid_file, aud_file, avi_file + '.tmp']
            subprocess.check_call(cmd)
            os.rename(avi_file + '.tmp', avi_file)
        mov_file = op.splitext(avi_file)[0] + '.mov'
        if not op.isfile(mov_file):
            encoder = find_encoder()
            if encoder is None:
                print('Warning: Neither ffmpeg nor mencoder found. Skipping MOV conversion.')
                continue

            if encoder == 'ffmpeg':
                subprocess.check_call(['ffmpeg', '-y', '-i', avi_file,
                                       '-c:v', 'libx264', '-c:a', 'aac',
                                       '-f', 'mov', mov_file + '.tmp'])
            else:  # mencoder
                subprocess.check_call(['mencoder', avi_file, '-oac', 'mp3lame',
                                       '-ovc', 'x264', '-of', 'lavf', '-lavfopts',
                                       'format=mov', '-o', mov_file + '.tmp'])
            os.rename(mov_file + '.tmp', mov_file)


if __name__ == '__main__':
    main()
