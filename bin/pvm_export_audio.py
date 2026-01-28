#!/usr/bin/env python

"""
Export an audio file to a standard audio format. Requires scipy.

Usage: pvm_export_audio audio_file_name

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
from os import path as op

import numpy as np
from scipy.io import wavfile

import pyvideomeg


def main():
    for aud_file in sys.argv[1:]:
        if not op.isfile(aud_file):
            raise IOError("file not found: %s" % aud_file)
        if op.splitext(aud_file)[1] != ".aud":
            raise ValueError('unknown extension "%s"' % op.splitext(aud_file)[1])
        out_file = op.splitext(aud_file)[0] + ".wav"
        if op.isfile(out_file):
            print("Skipping, output file exists: %s" % out_file)
            continue
        try:
            aud_data = pyvideomeg.AudioData(aud_file)
        except pyvideomeg.UnknownVersionError:
            print("The file %s has unknown version, skipping" % aud_file)
            continue
        print("Creating file: %s" % out_file)
        sys.stdout.flush()
        rate = aud_data.srate
        n_ch = aud_data.nchan
        aud_data = np.frombuffer(aud_data.raw_audio, aud_data.format_string).reshape(
            -1, n_ch
        )
        wavfile.write(out_file, rate, aud_data)


if __name__ == "__main__":
    main()
