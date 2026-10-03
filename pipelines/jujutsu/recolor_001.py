"""001: bring the generated DeepSeek into the shot's red-and-black two-tone (CPU only, no new inference).

User (2026-10-01): “唯一的问题是颜色。有什么滤镜，算法之类的，可以直接调整颜色吗？” The source of 001 is nearly a fixed
brightness → colour ramp (black shadows, saturated red mid-tones, light red highlights). The ramp is learned from the
source frames (median colour per brightness level). In the generated frames, pixels that already sit on the red/black
palette stay as they are; the off-palette ones (DeepSeek's blue-grey hair, white apron and frills) are recoloured by
their brightness through the ramp, with a feathered mask. Frames 0–62 are the source and stay untouched.
Usage: recolor_001.py [--preview FRAME ...] | [--render]
"""
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

from common import PROD, p
import render_shot as runner

UID = '001'
BASE = PROD / 'shots/001/deepseek_h3_v1_joined'
OUT = PROD / 'shots/001/deepseek_h3_v1_recolor'
CUT = 63
W, H = 1024, 576
LABEL = 'DeepSeek社区形象·颜色映射到原片红黑（CPU）'


def frames(path):
    raw = subprocess.run([str(p.FFMPEG), '-v', 'error', '-i', str(path), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


def luma(x):
    return x[..., 0] * 0.299 + x[..., 1] * 0.587 + x[..., 2] * 0.114


def learn_ramp(src):
    """Median source colour for each brightness level 0..255 (empty levels interpolated)."""
    sample = src[::3, ::4, ::4].reshape(-1, 3).astype(np.float32)
    y = np.clip(luma(sample).round().astype(int), 0, 255)
    ramp = np.full((256, 3), np.nan, np.float32)
    for level in range(256):
        sel = sample[y == level]
        if len(sel) >= 30:
            ramp[level] = np.median(sel, axis=0)
    known = np.nonzero(~np.isnan(ramp[:, 0]))[0]
    for c in range(3):
        ramp[:, c] = np.interp(np.arange(256), known, ramp[known, c])
    return ramp


def off_palette(img):
    """1 where a pixel is not on the source's red/black palette (bluish, greyish or white), feathered."""
    f = img.astype(np.float32) / 255
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    mx, mn = f.max(-1), f.min(-1)
    sat = (mx - mn) / (mx + 1e-6)
    reddish = (r >= mx - 1e-6) & (sat > 0.45)          # red/orange dominant and saturated: already on palette
    dark = mx < 0.10                                     # near black: the ramp maps it to black anyway
    m = (~reddish & ~dark).astype(np.float32)
    m = ndimage.binary_opening(m > 0.5, iterations=1).astype(np.float32)
    return np.clip(ndimage.gaussian_filter(m, 1.5) * 1.4, 0, 1)


RED_SHARE = 0.6   # share of the recoloured figure that becomes flat red; the rest goes to black lines and shadows


def source_red(src):
    """The flat red of the source's figures: median of bright, saturated, red-dominant source pixels."""
    f = src[::3, ::4, ::4].reshape(-1, 3).astype(np.float32)
    mx, mn = f.max(-1), f.min(-1)
    sel = (f[:, 0] >= mx) & ((mx - mn) / (mx + 1e-6) > 0.7) & (mx > 150)
    return np.median(f[sel], axis=0)


def recolor(img, ramp, red=None):
    """Two-tone like the source: the off-palette figure becomes flat red above a per-frame brightness split and black
    below it, with a short soft transition; on-palette pixels stay."""
    m = off_palette(img)
    y = luma(img.astype(np.float32))
    inside = y[m > 0.5]
    if red is None or len(inside) < 200:
        mapped = ramp[np.clip(y.round().astype(int), 0, 255)]
    else:
        split = np.percentile(inside, 100 * (1 - RED_SHARE))
        ys = ndimage.gaussian_filter(y, 1.2)  # smooth first, so fine texture does not speckle across the split
        t = np.clip((ys - (split - 12)) / 24, 0, 1)
        t = t * t * (3 - 2 * t)
        mapped = t[..., None] * red[None, None, :]
    m = m[..., None]
    return np.clip(img * (1 - m) + mapped * m, 0, 255).astype(np.uint8), m[..., 0]


def main():
    src, gen = frames(BASE / 'source_exact_with_audio.mp4'), frames(BASE / 'native_fullframe.mp4')
    ramp = learn_ramp(src)
    red = source_red(src)
    OUT.mkdir(parents=True, exist_ok=True)
    np.save(OUT / 'ramp.npy', ramp)
    if '--preview' in sys.argv:
        picks = [int(x) for x in sys.argv[sys.argv.index('--preview') + 1:]]
        rows = []
        for k in picks:
            new, m = recolor(gen[k], ramp, red)
            row = np.concatenate([src[k], gen[k], new], axis=1)
            rows.append(np.asarray(Image.fromarray(row).resize((3 * 320, 180))))
        Image.fromarray(np.concatenate(rows, axis=0)).save(OUT / 'preview.jpg', quality=88)
        print('preview', OUT / 'preview.jpg')
        return
    out = [gen[k] if k < CUT else recolor(gen[k], ramp, red)[0] for k in range(len(gen))]
    silent = OUT / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                           '-r', '24000/1001', '-i', '-', '-frames:v', str(len(out)), '-c:v', 'libx264', '-crf', '12',
                           '-pix_fmt', 'yuv420p', str(silent)], input=np.stack(out).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    source = BASE / 'source_exact_with_audio.mp4'
    clip = OUT / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', source, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy',
           '-movflags', '+faststart', clip])
    runner.configure(OUT)
    check = runner.batch.validate_output(clip, len(out), True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(source)
    (OUT / 'source_exact_with_audio.mp4').write_bytes(source.read_bytes())
    record = OUT / 'multistage.json'
    base_parts = runner.batch.read(BASE / 'multistage.json')['parts']
    p.write_json(record, dict(kind='h3_multistage', parts=base_parts, postprocessing=dict(
        type='cpu_palette_ramp', ramp=str(OUT / 'ramp.npy'), applied_from_frame=CUT),
        note='在 001 生成版基础上做纯 CPU 调色：只把不在红黑色板上的像素（DeepSeek 的蓝灰头发、白围裙等）改成原片式的双色——按每帧她自身亮度分布，较亮的约六成涂成原片的平涂红（从原片学出），较暗的线条与阴影涂黑，中间短过渡，羽化蒙版；第 0–62 帧原片不动。没有新推理。原片原音。'))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('DONE', clip, check)


if __name__ == '__main__':
    main()
