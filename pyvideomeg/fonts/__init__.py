"""
Font utilities for PyVideoMEG.

This module provides a bundled font for consistent text rendering
across all platforms. The bundled DejaVu Sans Mono font is used
exclusively to ensure consistent appearance regardless of the
user's operating system.
"""

from pathlib import Path

from PIL import ImageFont

# Default font size used across the package
DEFAULT_FONT_SIZE = 20

# Get the directory where this module is located
_FONTS_DIR = Path(__file__).parent

# Bundled font filename (DejaVu Sans Mono - free and widely compatible)
BUNDLED_FONT_FILENAME = "DejaVuSansMono.ttf"


def get_bundled_font_path():
    """
    Get the path to the bundled font file.

    Returns
    -------
    Path or None
        Path to the bundled font file if it exists, None otherwise.
    """
    font_path = _FONTS_DIR / BUNDLED_FONT_FILENAME
    if font_path.exists():
        return font_path
    return None


def load_font(size=DEFAULT_FONT_SIZE):
    """
    Load the bundled font for use with PIL/Pillow.

    This function uses only the bundled DejaVu Sans Mono font to ensure
    consistent text rendering across all platforms. If the bundled font
    cannot be loaded, falls back to PIL's default font with a warning.

    Parameters
    ----------
    size : int, optional
        Font size in pixels. Default is 20.

    Returns
    -------
    PIL.ImageFont.FreeTypeFont or PIL.ImageFont.ImageFont
        A font object that can be used with PIL's ImageDraw.
    """
    font_path = get_bundled_font_path()

    if font_path is not None:
        try:
            return ImageFont.truetype(str(font_path), size)
        except Exception as e:
            print(f"Warning: Could not load bundled font from {font_path}: {e}")
            print("Warning: This may indicate a problem with the installation.")
    else:
        print(
            "Warning: Bundled font file not found. This may indicate a problem with the installation."
        )

    # Fall back to default font only if bundled font is unavailable
    print("Warning: Using PIL default font. Text may appear small and inconsistent.")
    return ImageFont.load_default()
