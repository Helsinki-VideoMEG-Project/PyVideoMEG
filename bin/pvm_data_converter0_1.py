#!/usr/bin/env python

"""
Upgrade video or audio file format from version 0 to 1.

The script only changes the format version number stored in the file header
without making any other changes. File to be converted is given as a command
line argument. The converted file is created with the same name as the original
+ suffix '.fixed'

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

MAGIC_VIDEO_STR = b"HELSINKI_VIDEO_MEG_PROJECT_VIDEO_FILE"
MAGIC_AUDIO_STR = b"HELSINKI_VIDEO_MEG_PROJECT_AUDIO_FILE"


def main():
    in_file = open(sys.argv[1], "rb")

    # Read the full magic string to determine file type (audio is longer, so read that first)
    magic = in_file.read(len(MAGIC_AUDIO_STR))
    if magic == MAGIC_AUDIO_STR:
        # Already at correct position after reading audio magic
        magic = MAGIC_AUDIO_STR
    elif magic[: len(MAGIC_VIDEO_STR)] == MAGIC_VIDEO_STR:
        # It's a video file, but we read one extra byte, so seek back
        magic = MAGIC_VIDEO_STR
        in_file.seek(len(MAGIC_VIDEO_STR))
    else:
        print("Not a valid Helsinki VideoMEG Project video or audio file")
        sys.exit(1)

    ver = struct.unpack("I", in_file.read(4))[0]
    if ver != 0:
        print("Wrong file format version")
        sys.exit(1)

    out_file = open(sys.argv[1] + ".fixed", "wb")
    out_file.write(magic)
    out_file.write(struct.pack("I", 1))

    out_file.write(in_file.read())
    out_file.close()
    in_file.close()


if __name__ == "__main__":
    main()
