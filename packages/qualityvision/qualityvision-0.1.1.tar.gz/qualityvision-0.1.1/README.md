`````~~`````# QualityVision – Intelligent Image Quality Validator

`qualityvision` is a Python package designed to automatically validate image quality for AI and vision pipelines.
It helps you filter out **blurry, invalid, or low-quality images** before training or inference, ensuring only the best data passes through.

---

## Features

- Validate image **sharpness** using Laplacian variance  
- Check file **size limits** (MB)  
- Validate **file format** (`.jpg`, `.jpeg`, `.png`)  
- Works with both **local paths** and **URLs**  
- Returns structured JSON output for easy integration  

---

## Installation

Install from PyPI:

```bash
pip install qualityvision
````

---

## Quick Start

```python
from qualityvision.blur_detector import BlurDetector

# Initialize detector
detector = BlurDetector(threshold=100, max_size_mb=0.16)

# Define input files or URLs
inputs = [
    "images/sample_1.jpg",
    "images/sample_2.png",
    "logs/debug_output.log"   # non-image file (included in output)
]

# Run validation
results = detector.process_multiple(inputs)

# Print results
for res in results:
    print(res)
```

---

## Example Output

```json
{
  "results": [
    {
      "id": 1,
      "fileName": "images/sample_1.jpg",
      "isValid": true,
      "sizeValid": true,
      "formatValid": true,
      "blurnessValidation": true,
      "size_mb": 0.14
    },
    {
      "id": 2,
      "fileName": "images/sample_2.png",
      "isValid": false,
      "sizeValid": false,
      "formatValid": true,
      "blurnessValidation": false,
      "size_mb": 0.20
    },
    {
      "id": 3,
      "fileName": "logs/debug_output.log",
      "isValid": false,
      "sizeValid": true,
      "formatValid": false,
      "blurnessValidation": false,
      "size_mb": 0.02
    }
  ]
}
```

---

## Parameters

| Parameter      | Type    | Default                     | Description                                      |
| -------------- | ------- | --------------------------- | ------------------------------------------------ |
| `threshold`    | `int`   | `100`                       | Laplacian variance threshold for blur detection. |
| `max_size_mb`  | `float` | `5.0`                       | Maximum allowed file size (MB).                  |
| `allowed_exts` | `tuple` | `('.jpg', '.jpeg', '.png')` | Allowed image file extensions.                   |

---

## Validation Rules

| Check                 | Description                                          | Result Flag          |
| --------------------- | ---------------------------------------------------- | -------------------- |
| **Format Validation** | Validates file extension or MIME type.               | `formatValid`        |
| **Size Validation**   | Checks if file size ≤ `max_size_mb`.                 | `sizeValid`          |
| **Blur Validation**   | Detects blur using Laplacian variance ≥ `threshold`. | `blurnessValidation` |
| **Overall Validity**  | True only if all checks pass.                        | `isValid`            |

---

## How Blur Detection Works

The algorithm uses **OpenCV**’s Laplacian variance to measure image sharpness:

```python
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
score = np.var(cv2.Laplacian(gray, cv2.CV_64F))
if score >= threshold:
    image_is_sharp = True
```

Images with low variance are considered **blurry**.

---

## Supported Inputs

* Local file paths (`.jpg`, `.jpeg`, `.png`)
* HTTP/HTTPS URLs
* Non-image files (included but marked invalid)
* Directories and `None` values are ignored

---

## JSON Serialization Helper

To safely serialize NumPy types:

```python
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
```

---

## Command-Line Example

If installed via pip, you can also run directly:

```bash
python -m qualityvision.blur_detector
```

Output:

```
Result: {'fileName': 'images/sample_1.jpg', 'isValid': True, 'sizeValid': True, 'formatValid': True, 'blurnessValidation': True, 'size_mb': 0.14}
```

---

## Requirements

* Python 3.8+
* `opencv-python`
* `numpy`
* `requests`

Install manually if needed:

```bash
pip install opencv-python numpy requests
```

---

## License

MIT License © 2025 Rahul Patekar

---

## Author

**Rahul Patekar**
Email: [rahul.patekar@nagarro.com](mailto:rahul.patekar@nagarro.com)
GitHub: [rahulpatekar](https://github.com/ngrahulp)

---~~


``````````