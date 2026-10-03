"""Palette versions of character references for monochrome shots (H3 copies reference colours: 001 lesson).

Red: a smooth gradient map black -> dark red -> red -> light red-pink highlights that keeps the line art and shading.
User (2026-10-01) on it versus the first hard two-tone threshold: “现在做的非常好，之前的版本太难看了”.
"""
import numpy as np
from PIL import Image
from scipy import ndimage

RED_STOPS = np.array([[0, 8, 4, 4], [0.30, 70, 6, 8], [0.55, 200, 22, 20], [0.78, 240, 70, 55], [1.0, 255, 205, 190]],
                     np.float32)


def background(y):
    """White background connected to the border (luma > 238), grown by one pixel."""
    lab, _ = ndimage.label(y > 238)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    return ndimage.binary_dilation(np.isin(lab, list(border)), iterations=1)


def tint_stops(hexrgb):
    """Same shape of gradient for a single coloured light on black (JJK 091-094): black, dark hue, hue, pale highlight."""
    c = np.array([int(hexrgb[i:i + 2], 16) for i in (0, 2, 4)], np.float32)
    rows = [(0, (6, 6, 6)), (0.35, c * 0.35), (0.7, c), (1.0, c + (255 - c) * 0.7)]
    return np.array([[t, *rgb] for t, rgb in rows], np.float32)


def toned(im, tone):
    """im: RGB PIL image. tone 'redblack' (gradient map on a black background), 'tint_RRGGBB' (same, in that light colour)
    or 'grey' (luma)."""
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    y = a @ np.array([0.299, 0.587, 0.114], np.float32)
    if tone == 'grey':
        return Image.fromarray(np.repeat(np.clip(y, 0, 255)[..., None], 3, axis=-1).astype(np.uint8))
    stops = tint_stops(tone[5:]) if tone.startswith('tint_') else RED_STOPS
    bg = background(y)
    lo, hi = np.percentile(y[~bg], 2), np.percentile(y[~bg], 98)
    v = np.clip((y - lo) / (hi - lo + 1e-6), 0, 1)
    out = np.stack([np.interp(v, stops[:, 0], stops[:, c]) for c in (1, 2, 3)], -1)
    out[bg] = stops[0, 1:]
    return Image.fromarray(out.astype(np.uint8))
