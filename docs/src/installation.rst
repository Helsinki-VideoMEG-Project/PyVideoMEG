.. _installation:

Installation
============

Prerequisites
-------------

- **Python ≥ 3.11**
- **ffmpeg** — required for video export and merging. Install from `ffmpeg.org <https://ffmpeg.org/download.html>`_ or your package manager:

  - **macOS:** ``brew install ffmpeg``
  - **Ubuntu/Debian:** ``sudo apt-get install ffmpeg``
  - **Windows:** download from `ffmpeg.org <https://ffmpeg.org/download.html>`_

From source (recommended)
-------------------------

.. code-block:: bash

   git clone https://github.com/Helsinki-VideoMEG-Project/PyVideoMEG.git
   cd PyVideoMEG
   pip install .

Development install (editable)
------------------------------

.. code-block:: bash

   git clone https://github.com/Helsinki-VideoMEG-Project/PyVideoMEG.git
   cd PyVideoMEG
   pip install -e ".[dev]"

Optional dependencies
---------------------

**Analysis tools** (matplotlib, plotly, mne) — for examples and MEG/video sync:

.. code-block:: bash

   pip install -e ".[analysis]"

**All optional extras** (dev + analysis):

.. code-block:: bash

   pip install -e ".[all]"

**Documentation build** (Sphinx, Furo) — to build this documentation:

.. code-block:: bash

   pip install -e ".[docs]"
   cd docs && make html

Output is in ``docs/_build/html/``. Open ``index.html`` in a browser.

The documentation source lives in ``docs/src/``. To publish on **GitHub Pages**, use
**Settings → Pages → Source: GitHub Actions**. The workflow in
``.github/workflows/pages.yml`` builds the site on push to ``main``/``master`` and
deploys it.

Core Python dependencies
------------------------

Installed automatically with the package:

- **NumPy**
- **Pillow**
- **SciPy**
- **ffmpeg-python**
