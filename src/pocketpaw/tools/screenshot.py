"""Screenshot tool with multi-platform support and error handling."""

import io
import logging
import platform
import subprocess
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Step 1: Try importing pyautogui
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"pyautogui not available: {e}")
    PYAUTOGUI_AVAILABLE = False

# Step 2: Try importing PIL for ImageGrab (Windows/macOS fallback)
try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def _take_screenshot_pyautogui() -> Tuple[Optional[bytes], Optional[str]]:
    """
    Step 3a: Try pyautogui method (cross-platform).
    Returns: (image_bytes, error_message)
    """
    if not PYAUTOGUI_AVAILABLE:
        return None, "pyautogui not available"

    try:
        screenshot = pyautogui.screenshot()
        buffer = io.BytesIO()
        screenshot.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.getvalue(), None
    except Exception as e:
        error_msg = f"pyautogui failed: {type(e).__name__}: {str(e)}"
        logger.error(error_msg)
        return None, error_msg


def _take_screenshot_pil() -> Tuple[Optional[bytes], Optional[str]]:
    """
    Step 3b: Try PIL ImageGrab (Windows/macOS only).
    Returns: (image_bytes, error_message)
    """
    if not PIL_AVAILABLE:
        return None, "PIL/Pillow not available"

    try:
        screenshot = ImageGrab.grab()
        buffer = io.BytesIO()
        screenshot.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.getvalue(), None
    except Exception as e:
        error_msg = f"PIL ImageGrab failed: {type(e).__name__}: {str(e)}"
        logger.error(error_msg)
        return None, error_msg


def _take_screenshot_gnome() -> Tuple[Optional[bytes], Optional[str]]:
    """
    Step 3c: Try gnome-screenshot on Linux.
    Returns: (image_bytes, error_message)
    """
    temp_file = Path("/tmp/pocketpaw_screenshot.png")
    try:
        subprocess.run(
            ["gnome-screenshot", "-f", str(temp_file)],
            check=True,
            capture_output=True,
            timeout=5,
        )
        if temp_file.exists():
            with open(temp_file, "rb") as f:
                img_bytes = f.read()
            temp_file.unlink()
            return img_bytes, None
        else:
            return None, "gnome-screenshot did not create file"
    except Exception as e:
        error_msg = f"gnome-screenshot failed: {type(e).__name__}: {str(e)}"
        logger.debug(error_msg)
        return None, error_msg


def _take_screenshot_scrot() -> Tuple[Optional[bytes], Optional[str]]:
    """
    Step 3d: Try scrot on Linux (lightweight).
    Returns: (image_bytes, error_message)
    """
    temp_file = Path("/tmp/pocketpaw_screenshot.png")
    try:
        subprocess.run(
            ["scrot", str(temp_file)],
            check=True,
            capture_output=True,
            timeout=5,
        )
        if temp_file.exists():
            with open(temp_file, "rb") as f:
                img_bytes = f.read()
            temp_file.unlink()
            return img_bytes, None
        else:
            return None, "scrot did not create file"
    except Exception as e:
        error_msg = f"scrot failed: {type(e).__name__}: {str(e)}"
        logger.debug(error_msg)
        return None, error_msg


def _take_screenshot_macos() -> Tuple[Optional[bytes], Optional[str]]:
    """
    Step 3e: Try screencapture on macOS.
    Returns: (image_bytes, error_message)
    """
    temp_file = Path("/tmp/pocketpaw_screenshot.png")
    try:
        subprocess.run(
            ["screencapture", "-x", str(temp_file)],
            check=True,
            capture_output=True,
            timeout=5,
        )
        if temp_file.exists():
            with open(temp_file, "rb") as f:
                img_bytes = f.read()
            temp_file.unlink()
            return img_bytes, None
        else:
            return None, "screencapture did not create file"
    except Exception as e:
        error_msg = f"screencapture failed: {type(e).__name__}: {str(e)}"
        logger.debug(error_msg)
        return None, error_msg


def take_screenshot() -> Optional[bytes]:
    """
    Step 4: Main function - try multiple methods in order until one succeeds.
    Returns bytes of PNG image, or None if all methods fail.
    """
    system = platform.system()
    errors = []

    # Step 4a: Try pyautogui first (works on all platforms)
    img_bytes, error = _take_screenshot_pyautogui()
    if img_bytes:
        return img_bytes
    if error:
        errors.append(error)

    # Step 4b: Platform-specific fallbacks
    if system == "Windows":
        img_bytes, error = _take_screenshot_pil()
        if img_bytes:
            return img_bytes
        if error:
            errors.append(error)

    elif system == "Darwin":  # macOS
        img_bytes, error = _take_screenshot_macos()
        if img_bytes:
            return img_bytes
        if error:
            errors.append(error)
        # Also try PIL as fallback
        img_bytes, error = _take_screenshot_pil()
        if img_bytes:
            return img_bytes
        if error:
            errors.append(error)

    elif system == "Linux":
        # Try gnome-screenshot first (more reliable with GUI)
        img_bytes, error = _take_screenshot_gnome()
        if img_bytes:
            return img_bytes
        if error:
            errors.append(error)
        # Then try scrot (lightweight)
        img_bytes, error = _take_screenshot_scrot()
        if img_bytes:
            return img_bytes
        if error:
            errors.append(error)

    # Step 4c: Log all failures
    error_summary = " | ".join(errors) if errors else "All screenshot methods failed"
    logger.error(
        f"Failed to take screenshot on {system}: {error_summary}"
    )
    return None
