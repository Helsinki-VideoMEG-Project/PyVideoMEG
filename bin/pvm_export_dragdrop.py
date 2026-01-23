#!/usr/bin/env python

"""This makes a simple drag-and-drop target to convert recorded files
"""

import sys
import os
from os import path as op
import subprocess
import ffmpeg

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
            try:
                (
                    ffmpeg
                    .input(avi_file)
                    .output(mov_file + '.tmp', vcodec='libx264', acodec='aac', f='mov')
                    .overwrite_output()
                    .run(quiet=True, capture_stderr=True)
                )
                os.rename(mov_file + '.tmp', mov_file)
            except ffmpeg.Error as e:
                print('Error converting to MOV:')
                print(e.stderr.decode() if e.stderr else str(e))
                continue
            except Exception as e:
                print('Error converting to MOV: %s' % e)
                continue


if __name__ == '__main__':
    main()
