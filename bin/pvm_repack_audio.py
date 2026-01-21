#!/usr/bin/env python

"""
Repack an audio file (change the buffer size).

Usage: pvm_repack_audio input_file new_buffer_sz output_file

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

import struct
import sys
import numpy

import pyvideomeg


def main():
    assert(len(sys.argv) == 4)

    aud_file = pyvideomeg.AudioData(sys.argv[1])
    new_buf_sz = int(sys.argv[2])
    old_buf_sz = aud_file.buf_sz / (aud_file.nchan * 2)
    old_buf_cnt = len(aud_file.ts)
    new_buf_cnt = int((old_buf_sz * old_buf_cnt) // new_buf_sz)

    print('Old file: %i buffers of the size %i' % (old_buf_cnt, int(old_buf_sz)))
    print('New file: %i buffers of the size %i, last %i samples discarded' % (new_buf_cnt, new_buf_sz, int((old_buf_sz * old_buf_cnt) % new_buf_sz)))

    t_old = numpy.arange(0, old_buf_cnt) * old_buf_sz + (old_buf_sz-1)
    t_new = numpy.arange(0, new_buf_cnt) * new_buf_sz + (new_buf_sz-1)
    ts_new = numpy.interp(t_new, t_old, aud_file.ts).round().astype(int)

    out_file = open(sys.argv[3], 'wb')

    out_file.write(b'HELSINKI_VIDEO_MEG_PROJECT_AUDIO_FILE')
    out_file.write(struct.pack('I', aud_file.ver)) # preserve original file format version

    out_file.write(struct.pack('I', aud_file.srate))
    out_file.write(struct.pack('I', aud_file.nchan))
    if aud_file.ver == 0:
        out_file.write(aud_file.format_string.encode('ascii')) # preserve format_string for version 0 

    for i in range(new_buf_cnt):
        out_file.write(struct.pack('Q', ts_new[i]))
        out_file.write(struct.pack('I', new_buf_sz * (aud_file.nchan * 2)))
        out_file.write(aud_file.raw_audio[i*new_buf_sz*(aud_file.nchan*2) : (i+1)*new_buf_sz*(aud_file.nchan*2)])

    out_file.close()


if __name__ == '__main__':
    main()