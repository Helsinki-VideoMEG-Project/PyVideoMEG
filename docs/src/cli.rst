.. _cli:

Command-Line Tools
==================

PyVideoMEG provides several CLI utilities for inspecting, converting, and repairing
video-MEG files. They are available after installation (e.g. ``pvm_show_info``, ``pvm_export``).

pvm_show_info
-------------

Print metadata and timing info for a ``.vid`` or ``.aud`` file (version, frame/buffer count, timestamps, FPS, etc.).

**Usage:**

.. code-block:: bash

   pvm_show_info <file.vid|file.aud>

**Examples:**

.. code-block:: bash

   pvm_show_info recording.vid
   pvm_show_info recording.aud

----

pvm_export
----------

Export video (and optionally audio) to MP4, AVI, or MOV. Requires **ffmpeg**.
Frames are stamped with timestamps. If audio is given, video and audio are trimmed
to the overlapping interval and then muxed.

**Usage:**

.. code-block:: bash

   pvm_export <video.vid> [audio.aud] <output.mp4|.avi|.mov>

- **Video only:** omit the audio argument; output is the third argument.
- **Video + audio:** pass video, audio, then output.

**Examples:**

.. code-block:: bash

   # Video only
   pvm_export recording.vid output.mp4

   # Video with audio
   pvm_export recording.vid recording.aud output.mp4
   pvm_export recording.vid recording.aud output.avi
   pvm_export recording.vid recording.aud output.mov

----

pvm_export_audio
----------------

Convert ``.aud`` to ``.wav`` (same base name). Skips if the ``.wav`` already exists.
Requires **scipy**.

**Usage:**

.. code-block:: bash

   pvm_export_audio <file1.aud> [file2.aud ...]

**Examples:**

.. code-block:: bash

   pvm_export_audio recording.aud
   pvm_export_audio file1.aud file2.aud file3.aud

----

pvm_merge
---------

Merge two ``.vid`` files **side-by-side** into one standard-format video. The streams
must overlap in time. Requires **ffmpeg**.

**Usage:**

.. code-block:: bash

   pvm_merge <video1.vid> <video2.vid> <output.mp4>

**Example:**

.. code-block:: bash

   pvm_merge 2025-09-04--14-44-09_video_01.vid 2025-09-04--14-44-09_video_02.vid merged.mp4

----

pvm_repair
----------

Try to fix a corrupted ``.vid`` or ``.aud`` file by truncating at the last valid block.
Assumes damage is at the **end** of the file.

**Usage:**

.. code-block:: bash

   pvm_repair <corrupted.vid|.aud> <fixed.vid|.aud>

**Example:**

.. code-block:: bash

   pvm_repair corrupted.vid fixed.vid
   pvm_repair corrupted.aud fixed.aud

----

pvm_repack_audio
----------------

Change the buffer size of an ``.aud`` file. Output is a new ``.aud`` with the requested
buffer size; some samples at the end may be discarded.

**Usage:**

.. code-block:: bash

   pvm_repack_audio <input.aud> <new_buffer_sz> <output.aud>

**Example:**

.. code-block:: bash

   pvm_repack_audio input.aud 1024 output.aud

----

pvm_data_converter0_1
---------------------

Upgrade a ``.vid`` or ``.aud`` file from format **version 0 to 1**. Only the header
version is changed; the converted file is written as ``<original>.fixed``.

**Usage:**

.. code-block:: bash

   pvm_data_converter0_1 <file.vid|file.aud>

**Example:**

.. code-block:: bash

   pvm_data_converter0_1 old_recording.vid
   # creates old_recording.vid.fixed

----

pvm_export_dragdrop
-------------------

Batch converter aimed at drag-and-drop: given one or more ``.vid`` paths, it expects
co-located ``*_audio_00.aud`` and produces ``.avi`` and ``.mov`` in the same folder.
Skips ``.aud`` files passed as arguments. Requires **ffmpeg**.

**Usage:**

.. code-block:: bash

   pvm_export_dragdrop <file1.vid> [file2.vid ...]

**Example:**

.. code-block:: bash

   pvm_export_dragdrop 2025-09-04--14-44-09_video_01.vid
   # expects 2025-09-04--14-44-09_audio_00.aud in the same directory
   # creates 2025-09-04--14-44-09_01.avi and 2025-09-04--14-44-09_01.mov
