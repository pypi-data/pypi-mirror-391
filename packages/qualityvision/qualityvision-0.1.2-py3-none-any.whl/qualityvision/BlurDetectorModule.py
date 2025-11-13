import os
import cv2
import numpy as np
import requests
from typing import List, Dict, Union
from urllib.parse import urlparse
import json


class BlurDetector:
    """
    BlurDetector that validates image format, size, and blur.
    Returns structured JSON-style results.
    """

    def __init__(self, threshold: int = 100, max_size_mb: float = 5.0):
        """
        :param threshold: Laplacian variance threshold; lower = blurrier.
        :param max_size_mb: Maximum allowed image size in MB.
        """
        self.threshold = threshold
        self.max_size_mb = max_size_mb
        self.allowed_exts = ('.jpg', '.jpeg', '.png')
        self.allowed_mimetypes = ('image/jpeg', 'image/png')

    # ------------------------------
    # Helpers
    # ------------------------------
    def _is_url(self, path: str) -> bool:
        return isinstance(path, str) and path.startswith(("http://", "https://"))

    def _get_file_size_mb(self, path: str) -> float:
        """Return size in MB for file or URL."""
        try:
            if self._is_url(path):
                r = requests.head(path, allow_redirects=True, timeout=5)
                if "Content-Length" in r.headers:
                    return round(int(r.headers["Content-Length"]) / (1024 * 1024), 2)
                return 0.0
            return round(os.path.getsize(path) / (1024 * 1024), 2)
        except Exception:
            return 0.0

    def _is_valid_format(self, path: str) -> bool:
        """Validate image format via extension or MIME."""
        if not path or not isinstance(path, str):
            return False
        if os.path.isdir(path):
            return False
        if not self._is_url(path):
            ext = os.path.splitext(path)[1].lower()
            return ext in self.allowed_exts
        try:
            head = requests.head(path, allow_redirects=True, timeout=5)
            ctype = head.headers.get("Content-Type", "").lower()
            if any(m in ctype for m in self.allowed_mimetypes):
                return True
            ext = os.path.splitext(urlparse(path).path)[1].lower()
            return ext in self.allowed_exts
        except Exception:
            return False

    def _read_image(self, path: str) -> Union[np.ndarray, None]:
        """Read an image from local or URL. Return None if cannot read/decoded."""
        try:
            if self._is_url(path):
                resp = requests.get(path, timeout=10)
                if resp.status_code == 200:
                    arr = np.frombuffer(resp.content, np.uint8)
                    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                    return img
                return None
            # local file
            if not os.path.exists(path):
                return None
            return cv2.imread(path)
        except Exception:
            return None

    def _estimate_blur(self, image: Union[np.ndarray, None]) -> bool:
        """Return True if image passes blur test. If image is None, return False."""
        if image is None:
            return False
        try:
            if image.ndim == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            blur_map = cv2.Laplacian(gray, cv2.CV_64F)
            score = float(np.var(blur_map))
            # debug print removed in library code; keep if you need debugging
            # print('score', score)
            return score >= self.threshold
        except Exception:
            return False

    # ------------------------------
    # Main
    # ------------------------------
    def process_multiple(self, image_paths: List[str]) -> List[Dict[str, Union[str, bool, int, float]]]:
        """
        Process multiple image paths or URLs.
        Returns list of dicts with validation flags.
        Non-image files (e.g. .log) are included with appropriate flags set.
        Directories and None/invalid types are still skipped.
        """
        if not isinstance(image_paths, list):
            raise ValueError("Input must be a list of image paths or URLs.")

        results = []
        id_counter = 1

        for path in image_paths:
            # Skip completely invalid entries like None, not a string, or directories
            if not path or not isinstance(path, str) or os.path.isdir(path):
                continue  # skip folders and None

            # Determine format validity (True if recognized image format)
            format_valid = self._is_valid_format(path)

            # Always attempt to get size (0.0 if unavailable)
            size_mb = self._get_file_size_mb(path)
            size_valid = size_mb <= self.max_size_mb if size_mb > 0 else True

            # Try to read image; for non-image files this returns None
            image = self._read_image(path)
            blurness_ok = self._estimate_blur(image)

            # Compute overall validity: only True if all checks pass
            is_valid = all([format_valid, size_valid, blurness_ok])

            results.append({
                "fileName": path,
                "isValid": is_valid,
                "sizeValid": size_valid,
                "formatValid": format_valid,
                "blurnessValidation": blurness_ok,
                "size_mb": size_mb
            })
            id_counter += 1

        return results


if __name__ == "__main__":
    detector = BlurDetector(threshold=100, max_size_mb=0.16)

    inputs = [
        "/home/rahulpatekar/pip_recovery_code/qualityvision/blurriness_sample_input/sample_2.png",
        "/home/rahulpatekar/pip_recovery_code/qualityvision/blurriness_sample_input/sample_1.jpg",
        "sample_2.png",
        "/home/rahulpatekar/java_error_in_pycharm_7920.log",  # should now be included in results
        "images/",  # ignored (directory)
        None  # ignored
    ]

    results = detector.process_multiple(inputs)

    def convert_numpy(obj):
        if isinstance(obj, (np.bool_, np.bool8)):
            return bool(obj)
        elif isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        raise TypeError(f"Type {type(obj)} not serializable")

    print(json.dumps({"results": results}, indent=2, default=convert_numpy))

    for res in results:
        print(f"\nResult: {res}")
