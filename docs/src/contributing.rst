.. _contributing:

Contributing
============

Contributions are welcome. This page describes how to set up a development
environment and submit changes.

Development setup
-----------------

1. Clone the repository:

.. code-block:: bash

   git clone https://github.com/Helsinki-VideoMEG-Project/PyVideoMEG.git
   cd PyVideoMEG

2. Install in editable mode with dev extras (pytest, pytest-cov, ruff):

.. code-block:: bash

   pip install -e ".[dev]"

3. (Optional) Install analysis extras for running examples:

.. code-block:: bash

   pip install -e ".[analysis]"

Code style and formatting
-------------------------

The project uses **Ruff** for formatting and linting (Black-compatible style).

- **Format** — run before committing:

  .. code-block:: bash

     ruff format .

- **Lint** — auto-fix imports, style, and common issues:

  .. code-block:: bash

     ruff check . --fix

See ``pyproject.toml`` for line length (88) and target Python versions.

Building the documentation
--------------------------

.. code-block:: bash

   pip install -e ".[docs]"
   cd docs && make html

Output is in ``docs/_build/html/``. Documentation sources are in ``docs/src/``.

How to contribute
-----------------

- **Bug reports and feature requests:** open an issue on
  `GitHub Issues <https://github.com/Helsinki-VideoMEG-Project/PyVideoMEG/issues>`_.
- **Code changes:** submit a Pull Request. Please:

  1. Use an editable install and dev extras as above.
  2. Run ``ruff format .`` and ``ruff check . --fix`` and fix any remaining issues.
  3. Keep the scope of each PR focused.

License
-------

By contributing, you agree that your contributions will be licensed under the
same **GPL v3** license as the project.
