# Documentation

Source files are in `src/`. Build output goes to `html/html/` (i.e. `docs/html/html/` from the project root).

## Build locally

From the **project root**:

```bash
# 1. Install the package with docs extras (sphinx, furo)
pip install -e ".[docs]"

# 2. Build HTML
cd docs && make html
```

Then open `docs/html/html/index.html` in a browser.

## Commands

| Command       | Description                       |
|---------------|-----------------------------------|
| `make html`   | Build HTML to `html/html/`        |
| `make clean`  | Remove `html/` build directory    |

## GitHub Pages

The workflow in `.github/workflows/pages.yml` builds the docs on push to `main` or `master` and deploys to the `gh-pages` branch. In **Settings → Pages**, set:

- **Source:** Deploy from a branch  
- **Branch:** `gh-pages`  
- **Folder:** / (root)
