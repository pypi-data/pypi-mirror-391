# edolview

Lightweight Python client for sending images (numpy or torch tensors) to the **edolview-rs** application for interactive inspection.

## Features
- Accepts `numpy.ndarray` or `torch.Tensor` input
- Shape normalization: `(B,C,H,W)`, `(C,H,W)`, `(H,W)`, `(H,W,C)` -> `(H,W,C)`
- Channels 1–4 supported
- Optional area downscale (fast average pooling)
- Optional compression: PNG for integer types (if OpenCV available) or zlib for float data
- Optional float16 conversion for reduced bandwidth

## Install
```bash
pip install edolview
```

## Usage
```python
import numpy as np
from edolview import send_image

# Example image (H,W,C) uint8
img = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)

# Send to viewer running at host:port
send_image("127.0.0.1", 4567, "random", img, float_to_half=True, do_compression=True)
```

Or use the class directly:
```python
from edolview import EdolView
viewer = EdolView("127.0.0.1", 4567)
viewer.send_image("frame0", img, do_compression=True)
```

### Torch tensor example
```python
import torch
from edolview import send_image

x = torch.rand(1, 3, 256, 256)  # BCHW float32
send_image("127.0.0.1", 4567, "torch_example", x, do_compression=True)
```

### Downscale
```python
send_image("127.0.0.1", 4567, "big_image", big_img, downscale_factor=4)
```

## API
`send_image(host, port, name, image, float_to_half=True, do_compression=False, downscale_factor=1)`

`EdolView(host, port).send_image(...)`

## License
MIT. See `LICENSE`.

## Development
```bash
# from python/ directory
python -m pip install -e .[dev]
pytest
```

## Publish (manual)
```bash
# Ensure version bumped in pyproject.toml
python -m pip install --upgrade build twine
python -m build
python -m twine upload dist/*
```
