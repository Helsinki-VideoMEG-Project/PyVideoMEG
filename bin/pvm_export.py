#!/usr/bin/env python

"""
Export a pair of video and audio files to a standard video format. Requires
either ffmpeg or mencoder.

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

import sys
import os
import tempfile
import shutil
import glob
import numpy
import subprocess

from PIL import Image, ImageDraw, ImageFont
try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO

import pyvideomeg
from pyvideomeg.fonts import load_font, DEFAULT_FONT_SIZE


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
    tmp_fldr = tempfile.mkdtemp()
    print('Using \'%s\' for storing temporary files' % tmp_fldr)

    if len(sys.argv) < 3:
        print('Usage: pvm_export video_file_name [audio_file_name] output_file_name')
        print('  If audio_file_name is omitted, only video will be exported')
        sys.exit(1)

    vid_file = pyvideomeg.VideoData(sys.argv[1])

    # Load font using the bundled font utility
    fnt = load_font(DEFAULT_FONT_SIZE)

    for i in range(len(vid_file.ts)):
        img = Image.open(BytesIO(vid_file.get_frame(i)))
        draw = ImageDraw.Draw(img)
        draw.text((10,0), '%i  :  %s' % (vid_file.ts[i], pyvideomeg.ts2str(vid_file.ts[i])), font=fnt, fill='black')
        img.save('%s/%08i.jpg' % (tmp_fldr, i))

    if len(sys.argv) == 3:
        print('No audio file is specified, using only the video')
        fps = len(vid_file.ts) / (float(vid_file.ts[-1] - vid_file.ts[0]) / 1000)
        print('FPS: %f' % fps)

        encoder = find_encoder()
        if encoder is None:
            print('Error: Neither ffmpeg nor mencoder found. Please install one of them.')
            shutil.rmtree(tmp_fldr)
            del(vid_file)
            sys.exit(1)

        print('Using encoder: %s' % encoder)

        output_file = sys.argv[2]

        if encoder == 'ffmpeg':
            pattern = '%s/%%08d.jpg' % tmp_fldr
            cmd = ['ffmpeg', '-y', '-framerate', str(fps), '-i', pattern,
                   '-c:v', 'libx264', '-pix_fmt', 'yuv420p', output_file]
            try:
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                ret_code = result.returncode
                if ret_code != 0:
                    print('ffmpeg stderr output:')
                    print(result.stderr)
            except Exception as e:
                print('Error running ffmpeg: %s' % e)
                ret_code = 1
        else:
            vid_opts = 'mf://%s/*.jpg -mf type=jpg:fps=%f' % (tmp_fldr, fps)
            cmd = 'mencoder %s -ovc lavc -lavcopts vcodec=msmpeg4v2 -nosound -o %s > %s 2>&1' % (
                vid_opts, output_file, os.devnull)
            ret_code = os.system(cmd)

        if ret_code != 0:
            print('ERROR: Encoding failed with return code %i' % ret_code)
            shutil.rmtree(tmp_fldr)
            del(vid_file)
            sys.exit(1)

        shutil.rmtree(tmp_fldr)
        del(vid_file)
        sys.exit(0)

    aud_file = pyvideomeg.AudioData(sys.argv[2])

    if aud_file.ts[0] < vid_file.ts[0]:
        first_vid_indx = 0
        first_aud_indx = numpy.argmin(abs(aud_file.ts-vid_file.ts[0]))
    else:
        first_aud_indx = 0
        first_vid_indx = numpy.argmin(abs(vid_file.ts-aud_file.ts[0]))

    if aud_file.ts[-1] > vid_file.ts[-1]:
        last_vid_indx = len(vid_file.ts) - 1
        last_aud_indx = numpy.argmin(abs(aud_file.ts-vid_file.ts[-1]))
    else:
        last_aud_indx = len(aud_file.ts) - 1
        last_vid_indx = numpy.argmin(abs(vid_file.ts-aud_file.ts[-1]))
        
    # make sure there is an overlap between video and audio
    assert((first_aud_indx != last_aud_indx) & (first_vid_indx != last_vid_indx))

    # delete the video frames for which there is no audio and renumber the remaining ones
    remaining_frames = []
    for i in range(len(vid_file.ts)):
        if (i < first_vid_indx) | (i > last_vid_indx):
            os.remove('%s/%08i.jpg' % (tmp_fldr, i))
        else:
            remaining_frames.append(i)

    # Renumber remaining frames sequentially so ffmpeg can read them
    for new_idx, old_idx in enumerate(remaining_frames):
        old_path = '%s/%08i.jpg' % (tmp_fldr, old_idx)
        new_path = '%s/%08i.jpg' % (tmp_fldr, new_idx)
        if old_idx != new_idx:
            os.rename(old_path, new_path)

    # dump the relevant part of the audio to the file
    out_file = open(tmp_fldr + '/audio.raw', 'wb')
    out_file.write(aud_file.raw_audio[(first_aud_indx*aud_file.buf_sz) : ((last_aud_indx+1)*aud_file.buf_sz)])
    out_file.close()

    # compute some statistics
    video_frame_cnt = last_vid_indx - first_vid_indx + 1
    audio_frame_cnt = last_aud_indx - first_aud_indx + 1

    print('Discarded %i video frames out of %i' % (len(vid_file.ts) - video_frame_cnt, len(vid_file.ts)))
    print('Discarded %i audio buffers out of %i' % (len(aud_file.ts) - audio_frame_cnt, len(aud_file.ts)))

    fps = video_frame_cnt / (float(vid_file.ts[last_vid_indx] - vid_file.ts[first_vid_indx]) / 1000)
    print('FPS: %f' % fps)

    wc_srate = (audio_frame_cnt * aud_file.buf_sz / 2 / aud_file.nchan) / (float(aud_file.ts[last_aud_indx] - aud_file.ts[first_aud_indx]) / 1000)
    fixed_fps = fps * aud_file.srate / wc_srate      # correct for the difference between soundcard and computer clocks 
    print('nominal sampling rate is %i\nwall clock sampling rate is %f\nnumber of channels: %i\nfixed FPS: %f' % (aud_file.srate, wc_srate, aud_file.nchan, fixed_fps))

    encoder = find_encoder()
    if encoder is None:
        print('Error: Neither ffmpeg nor mencoder found. Please install one of them.')
        shutil.rmtree(tmp_fldr)
        sys.exit(1)

    print('Using encoder: %s' % encoder)

    output_file = sys.argv[3]
    audio_file = tmp_fldr + '/audio.raw'

    if encoder == 'ffmpeg':
        pattern = '%s/%%08d.jpg' % tmp_fldr
        cmd = ['ffmpeg', '-y', 
               '-framerate', str(fixed_fps),
               '-i', pattern,
               '-f', 's16le',
               '-ar', str(aud_file.srate),
               '-ac', str(aud_file.nchan),
               '-i', audio_file,
               '-c:v', 'libx264',
               '-pix_fmt', 'yuv420p',
               '-c:a', 'aac',
               '-shortest',
               output_file]
        print('Executing ffmpeg command: %s' % ' '.join(cmd))
        img_files = glob.glob('%s/*.jpg' % tmp_fldr)
        print('Found %i image files in temp directory' % len(img_files))
        if len(img_files) == 0:
            print('ERROR: No image files found in temp directory %s' % tmp_fldr)
            ret_code = 1
        else:
            try:
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=300)
                ret_code = result.returncode
                if ret_code != 0:
                    print('ffmpeg stderr output:')
                    print(result.stderr)
                    if result.stdout:
                        print('ffmpeg stdout output:')
                        print(result.stdout)
            except subprocess.TimeoutExpired:
                print('ERROR: ffmpeg command timed out after 300 seconds')
                ret_code = 1
            except Exception as e:
                print('Error running ffmpeg: %s' % e)
                ret_code = 1
    else:
        aud_opts = '-audiofile %s -audio-demuxer 20 -rawaudio rate=%i:channels=%i:samplesize=2' % (
            audio_file, aud_file.srate, aud_file.nchan)
        vid_opts = 'mf://%s/*.jpg -mf type=jpg:fps=%f' % (tmp_fldr, fixed_fps)
        cmd = 'mencoder %s %s -ovc lavc -lavcopts vcodec=msmpeg4v2 -oac mp3lame -o %s > %s 2>&1' % (
            vid_opts, aud_opts, output_file, os.devnull)
        print('Executing mencoder command: %s' % cmd)
        ret_code = os.system(cmd)

    if ret_code != 0:
        print('ERROR: Encoding failed with return code %i' % ret_code)
        shutil.rmtree(tmp_fldr)
        sys.exit(1)

    shutil.rmtree(tmp_fldr)


if __name__ == '__main__':
    main()
