.. _library:

Using the Library
=================

PyVideoMEG can be used as a Python library to read, write, and process video-MEG
recordings programmatically.

Quick start
-----------

.. code-block:: python

   import pyvideomeg

   # Read video and audio
   video = pyvideomeg.VideoData("recording.vid")
   audio = pyvideomeg.AudioData("recording.aud")

   # Inspect timestamps
   print(f"Video frames: {len(video.ts)}")
   print(f"First frame: {pyvideomeg.ts2str(video.ts[0])}")

   # Get a single video frame (JPEG bytes)
   frame_jpg = video.get_frame(0)

   # Remember to close when done
   video.close()

Main components
---------------

**Reading data**

- :py:class:`pyvideomeg.VideoData` — read ``.vid`` files. Attributes: ``ts`` (timestamps), ``nframes``, ``ver``. Method: :py:meth:`pyvideomeg.VideoData.get_frame` (returns JPEG bytes).
- :py:class:`pyvideomeg.AudioData` — read ``.aud`` files. Attributes: ``ts``, ``raw_audio``, ``srate``, ``nchan``, ``format_string``, ``buf_sz``, ``ver``. Method: :py:meth:`pyvideomeg.AudioData.format_audio` for interpolated samples and per-sample timestamps (memory‑intensive).

**Utilities**

- :py:func:`pyvideomeg.ts2str` — convert a numeric timestamp to a human‑readable string.
- :py:func:`pyvideomeg.repair_file` — repair a corrupted ``.vid`` or ``.aud`` (damage assumed at end of file).
- :py:func:`pyvideomeg.comp_tstamps` — extract timestamps from a MEG trigger channel (requires `mne` and `comp_tstamps` parameters tuned to your setup).

**Writing and extra I/O**

- :py:class:`pyvideomeg.VideoFile` — write ``.vid``-compatible files.
- :py:class:`pyvideomeg.EvlData`, :py:class:`pyvideomeg.Event` — event list from ``.evl`` files.
- :py:class:`pyvideomeg.FifData` — read timing from MEG ``.fif`` (requires **mne**).

VideoData
---------

.. code-block:: python

   import pyvideomeg
   from io import BytesIO
   from PIL import Image

   vid = pyvideomeg.VideoData("recording.vid")

   # Timestamps (milliseconds)
   print(vid.ts[:5])

   # Decode frame 0 to a PIL Image
   jpg = vid.get_frame(0)
   img = Image.open(BytesIO(jpg))

   # FPS (from first and last timestamp)
   if len(vid.ts) > 1:
       fps = (len(vid.ts) - 1) * 1000.0 / (vid.ts[-1] - vid.ts[0])
       print(f"FPS: {fps:.2f}")

   vid.close()

AudioData
---------

.. code-block:: python

   import pyvideomeg
   import struct

   aud = pyvideomeg.AudioData("recording.aud")

   # Basic info
   print(f"Sample rate: {aud.srate}, channels: {aud.nchan}")
   print(f"Format: {aud.format_string}, buffer size: {aud.buf_sz}")

   # Raw bytes and per-buffer timestamps
   # aud.raw_audio, aud.ts

   # Formatted audio (nchan x nsamp) and per-sample timestamps — uses more memory
   # audio, audio_ts = aud.format_audio()

   # Example: reshape raw to float (for 'h' / int16)
   import numpy as np
   dtype = np.dtype(aud.format_string)
   nsamp = len(aud.raw_audio) // (aud.nchan * dtype.itemsize)
   data = np.frombuffer(aud.raw_audio, dtype=dtype).reshape(-1, aud.nchan).T

Timestamps and repair
---------------------

.. code-block:: python

   import pyvideomeg

   # Timestamp to string
   ts_ms = 1725453849123
   print(pyvideomeg.ts2str(ts_ms))

   # Repair a corrupted file (writes a new file)
   pyvideomeg.repair_file("corrupted.vid", "fixed.vid")

Exceptions
----------

- :py:exc:`pyvideomeg.UnknownVersionError` — file format version is not supported.
- :py:exc:`pyvideomeg.OverWriteError` — attempted to overwrite an existing file (e.g. when creating a :py:class:`pyvideomeg.VideoFile`).

Example scripts
---------------

The ``examples/`` directory in the source tree includes:

- ``sync_test.py``, ``sync_test2.py`` — assess video/audio/MEG synchronization (require **matplotlib**, **mne**).
- ``merge_videos.py`` — merge two videos in Python (similar to ``pvm_merge``).

See the scripts and their ``run_*.sh`` wrappers for patterns and dependencies.
