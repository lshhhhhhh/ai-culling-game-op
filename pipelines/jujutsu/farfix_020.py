"""020-026a: recolour the tiny distant Itadori of frames 2-4 into DeepSeek blue (CPU, on the H3 output).

User (2026-10-01): “020大肥鱼出场的前几帧还是虎杖。这也算是老问题了，远景没有替换”. In the H3 output the figure is a 30x40 px orange
speck over a pure red ground in frames 2-4 (H3 left it as Itadori), greyish blue in 5-7 and DeepSeek from 8 on. Inside a small box around
the figure, only its orange/peach pixels (hue 12-50 degrees; the ground is red, about 0 degrees) are shifted to the blue of the
DeepSeek that follows, keeping their brightness; nothing else changes. Registered as a new version of 020-026a.
"""
import pathlib
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

import render_shot as runner
from common import PROD, p

UID = '020-026a'
SRC = PROD / 'shots' / UID / 'deepseek_h3_v1'
OUT = PROD / 'shots' / UID / 'deepseek_h3_v1_farfix'
LABEL = '虎杖→DeepSeek·高空坠落与连续出拳（修远景：第2–4帧的小人改成 DeepSeek 蓝）'
FIX = {2: (496, 396, 546, 444), 3: (496, 384, 546, 444), 4: (496, 397, 546, 444)}  # frame -> box around the speck (1024x576)
BLUE_HUE = 228 / 360  # the DeepSeek of frames 8+


def frames(path):
    raw = subprocess.run([str(p.FFMPEG), '-v', 'error', '-i', str(path), '-vsync', '0', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 576, 1024, 3)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    gen = frames(SRC / 'native_fullframe.mp4').copy()
    changed = {}
    for i, (x0, y0, x1, y1) in FIX.items():
        patch = Image.fromarray(gen[i, y0:y1, x0:x1])
        hsv = np.asarray(patch.convert('HSV')).astype(np.float32)
        h, s, v = hsv[..., 0] / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
        # The red ground is very uniform (hue about 1 degree, saturation 0.9, value 0.58); the figure spans hues 6-42 degrees, so a hue
        # cut-off left its reddish parts orange (first try). Everything that is not ground is a candidate; the figure is the largest
        # blob that does not touch the top of the box (the building and its orange stripe come in from the top).
        ground = (s > 0.7) & ((h < 6 / 360) | (h > 345 / 360)) & (v > 0.42) & (v < 0.72)
        # the figure hangs from the black building edge, so near-black building pixels are cut away first and the blob is picked by a
        # seed at the figure's middle (521, 420)
        lab, n = ndimage.label(~ground & (v > 0.11))
        sy, sx = 420 - y0, 521 - x0
        ys, xs = np.nonzero(lab)
        k = lab[ys, xs][np.argmin((ys - sy) ** 2 + (xs - sx) ** 2)] if len(ys) else 0
        fig = (lab == k) if k else np.zeros(h.shape, bool)
        out = hsv.copy()
        out[..., 0][fig] = BLUE_HUE * 255
        out[..., 1][fig] = np.clip(s[fig] * 0.75, 0, 1) * 255
        out[..., 2][fig] = v[fig] * 0.85 * 255
        rgb = np.asarray(Image.fromarray(out.astype(np.uint8), 'HSV').convert('RGB'))
        region = gen[i, y0:y1, x0:x1]
        gen[i, y0:y1, x0:x1] = np.where(fig[..., None], rgb, region)
        changed[i] = int(fig.sum())
    silent = OUT / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(gen)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=gen.tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    for i in FIX:
        x0, y0, x1, y1 = FIX[i]
        Image.fromarray(gen[i]).crop((x0 - 40, y0 - 40, x1 + 40, y1 + 40)).resize(((x1 - x0 + 80) * 3, (y1 - y0 + 80) * 3), Image.NEAREST).save(OUT / f'preview_f{i:02d}.png')
    full = SRC / 'source_exact_with_audio.mp4'
    clip = OUT / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    runner.configure(OUT)
    check = runner.batch.validate_output(clip, len(gen), True)
    record = OUT / 'title_compositing.json'
    builder = pathlib.Path(__file__).resolve()
    p.write_json(record, dict(kind='cpu_text', builder=str(builder), builder_sha256=p.sha(builder),
                              recipe_text=f'在 H3 结果（deepseek_h3_v1）上只改第 2–4 帧远处的小人：框内橙色像素改成后面 DeepSeek 的蓝色，亮度不变；'
                                          f'改动像素数 {changed}。其余帧与像素不变。'))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    if '--no-register' not in sys.argv:
        entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
        if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
            runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, 'changed px per frame', changed, flush=True)


if __name__ == '__main__':
    main()
