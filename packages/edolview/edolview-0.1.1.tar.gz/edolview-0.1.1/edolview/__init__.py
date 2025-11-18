"""edolview: lightweight image sending client for the edolview-rs application.

Main entrypoints:
- EdolView(host, port).send_image(name, image, float_to_half=True, do_compression=False, downscale_factor=1)
- send_image(host, port, name, image, float_to_half=True, do_compression=False, downscale_factor=1)

Supports numpy arrays (preferred) and torch tensors. Converts tensor -> cpu numpy automatically.
Auto shape normalization to (H,W,C) with C in [1..4]. Optional downscale (area). Optional compression
(zlib for float, png for integer when OpenCV available). Floats can be converted to float16 when requested.
"""
from __future__ import annotations

from struct import pack
import importlib.util
import socket
import zlib
from typing import Any

import numpy as np

__all__ = ["EdolView", "send_image"]
__version__ = "0.1.0"

# ---------------- internal helpers ---------------- #

def _area_interpolate(im: np.ndarray, scale: int) -> np.ndarray:
    new_h = im.shape[0] // scale
    new_w = im.shape[1] // scale
    clip_h = new_h * scale
    clip_w = new_w * scale
    buf = np.zeros((new_h, new_w, im.shape[2]), dtype=np.float32)
    for i in range(scale):
        for j in range(scale):
            buf += im[i:clip_h:scale, j:clip_w:scale]
    return (buf / (scale * scale)).astype(im.dtype)


def _parse_dtype(dtype: Any) -> int:
    if dtype == np.float64: return 6
    if dtype == np.float32: return 5
    if dtype == np.float16: return 7
    if dtype == np.uint16:  return 2
    if dtype == np.uint8:   return 0
    if dtype == np.int32:   return 4
    if dtype == np.int16:   return 3
    if dtype == np.int8:    return 1
    raise RuntimeError(f"dtype not supported: {dtype}")


def _to_hwc(arr: np.ndarray) -> np.ndarray:
    """(B,C,H,W)/(C,H,W)/(H,W) -> (H,W,C). Leading singleton batch dims removed."""
    a = arr
    while a.ndim > 3:
        a = a[0]
    if a.ndim == 2:
        return a[:, :, None]
    if a.ndim != 3:
        raise RuntimeError(f"invalid shape: {arr.shape}")
    # transpose if channels first
    if a.shape[0] in (1, 3, 4) and a.shape[2] not in (1, 3, 4):
        a = np.transpose(a, (1, 2, 0))
    if a.ndim != 3:
        raise RuntimeError(f"could not normalize shape to HWC: {arr.shape} -> {a.shape}")
    return a


# ---------------- public API ---------------- #

class EdolView:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def send_image(
        self,
        name: str,
        image: Any,
        float_to_half: bool = True,
        do_compression: bool = False,
        downscale_factor: int = 1,
    ) -> None:
        """Send an image to the server.

        Parameters
        ----------
        name : str
            Logical image name.
        image : np.ndarray | torch.Tensor
            Image data: (H,W),(H,W,C),(C,H,W) or (B,C,H,W). C must be 1..4 after normalization.
        float_to_half : bool, default True
            If True and dtype is float32/float64 and compression enabled, convert to float16.
        do_compression : bool, default False
            Use png for integer types (if OpenCV available) or zlib for others.
        downscale_factor : int, default 1
            Area downscale factor (>1 reduces size).
        """
        # torch -> numpy conversion (lazy import)
        if not isinstance(image, np.ndarray):
            torch_spec = importlib.util.find_spec("torch")
            if torch_spec is not None:
                import torch  # type: ignore
                if isinstance(image, torch.Tensor):
                    if hasattr(image, "detach"):
                        image = image.detach()
                    if hasattr(image, "cpu"):
                        image = image.cpu()
                    image = image.numpy()
        if not isinstance(image, np.ndarray):
            raise RuntimeError("image should be np.ndarray or torch.Tensor")

        image = _to_hwc(image)
        initial_shape = tuple(image.shape)

        if downscale_factor != 1:
            image = _area_interpolate(image, downscale_factor)

        if image.shape[2] > 4:
            raise RuntimeError(f"image channel must be <= 4, got shape: {initial_shape}")

        if do_compression and (image.dtype in (np.float32, np.float64)) and float_to_half:
            image = image.astype(np.float16)

        cv2_spec = importlib.util.find_spec("cv2")
        compression = "raw"
        buf_bytes = None

        if do_compression:
            if np.issubdtype(image.dtype, np.integer) and cv2_spec is not None:
                import cv2  # type: ignore
                img_enc = image
                if image.shape[2] == 3:
                    img_enc = image[:, :, ::-1]
                ok, buf = cv2.imencode(".png", img_enc)
                if not ok:
                    raise RuntimeError("cv2.imencode(.png) failed")
                buf_bytes = buf.tobytes()
                compression = "png"
            else:
                if not image.flags["C_CONTIGUOUS"]:
                    image = image.copy()
                buf_bytes = zlib.compress(image.tobytes())
                compression = "zlib"

        if buf_bytes is None:
            if not image.flags["C_CONTIGUOUS"]:
                image = image.copy()
            buf_bytes = image.tobytes()
            compression = "raw"

        nbytes_uncompressed = image.nbytes
        H, W, C = image.shape
        dtype_code = _parse_dtype(image.dtype)

        compression_bytes = compression.encode("utf-8")
        extra_bytes = b"".join([
            pack("!Q", nbytes_uncompressed),  # u64
            pack("!III", H, W, C),            # 3×u32
            pack("!I", dtype_code),           # u32
            compression_bytes                 # utf-8
        ])

        name_bytes = name.encode("utf-8")

        name_len = len(name_bytes)
        extra_len = len(extra_bytes)
        buf_len = len(buf_bytes)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            print(f"[edolview] sending image {name} to {self.host}:{self.port}, payload={buf_len/1024:.1f} KB, comp={compression}")
            s.sendall(pack("!Q", name_len))
            s.sendall(pack("!Q", extra_len))
            s.sendall(pack("!Q", buf_len))
            s.sendall(name_bytes)
            s.sendall(extra_bytes)
            s.sendall(buf_bytes)


def send_image(
    host: str,
    port: int,
    name: str,
    image: Any,
    float_to_half: bool = True,
    do_compression: bool = False,
    downscale_factor: int = 1,
) -> None:
    EdolView(host, port).send_image(name, image, float_to_half, do_compression, downscale_factor)
