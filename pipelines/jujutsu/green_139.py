"""139: the blue pillar of light over the city turned green - a colour change in code (no H3, no Codex).

The user (2026-10-02): “139可以把光柱变成绿色吗” (on the plan: “需要设计”). Source (7 frames): a city at dusk in blue light, a bright
pillar of light (white core, cyan-blue glow) rising behind the buildings, the dust it raises lit blue; the camera drifts.
Here: in each frame the pillar's core is found (the brightest pixels above the horizon); around it, a soft area covers the pillar, its glow
and the lit dust, and inside it light pixels get the green swapped in for the blue (white stays white, deep blue sky and the far city are
outside the area or too dark to change).
Usage: green_139.py [--no-register]
"""
import pathlib
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

import render_shot as runner
from common import PROD, ROOT, p
from title_057 import frames

UID, REV = '139', 'green_code_v1'
OUT = PROD / 'shots' / UID / REV
SOURCE = ROOT / 'assets/jujutsu/op1_v1/review/source_units/139.mp4'
LABEL = '城市上空的光柱→绿色（代码改色：只改光柱、光晕和被照亮的烟尘，天空和城市保持原来的蓝调；未经 H3）'
LUMA = np.array([0.299, 0.587, 0.114], np.float32)


def green(f):
    """Blue-cyan light to green-cyan: green and blue swapped, red a little lower; white and greys are unchanged by the swap."""
    out = f.copy()
    out[..., 0] = f[..., 0] * 0.85
    out[..., 1] = f[..., 2]
    out[..., 2] = f[..., 1] * 0.85
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    full = OUT / 'source_exact_with_audio.mp4'
    if not full.exists():
        shutil.copy2(SOURCE, full)
    src = frames(full).astype(np.float32)
    yy, xx = np.mgrid[0:576, 0:1024].astype(np.float32)
    result, cores = [], []
    for f in src:
        lum = f @ LUMA
        core = (lum > 235) & (yy < 0.65 * 576)
        lab, n = ndimage.label(core)
        k = 1 + int(np.argmax(ndimage.sum(core, lab, range(1, n + 1))))
        ys, xs = np.nonzero(lab == k)
        cx, top, bot = float(xs.mean()), float(ys.min()), float(ys.max())
        cores.append((round(cx), round(top), round(bot)))
        # distance to the pillar's axis (a vertical segment from its top to the dust below it)
        dy = np.clip(yy, top, bot + 140) - yy
        d = np.hypot(xx - cx, dy)
        area = np.exp(-(d / 150) ** 2)
        light = np.clip((lum - 70) / 60, 0, 1)  # the glow and the lit dust, not the dark sky or shadows
        w = (area * light)[..., None]
        result.append(np.clip(f * (1 - w) + green(f) * w, 0, 255).astype(np.uint8))
    print('pillar core per frame (x, top, bottom):', cores, flush=True)
    silent = OUT / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(result)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(result).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = OUT / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    if '--no-register' in sys.argv:
        print('PREVIEW', clip, flush=True)
        return
    runner.configure(OUT)
    check = runner.batch.validate_output(clip, len(result), True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    me = pathlib.Path(__file__).resolve()
    record = OUT / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), cores=cores, recipe_text=(
        '逐帧找出光柱最亮的芯（地平线以上），以光柱为轴取一块柔和的区域（光柱、光晕与下方被照亮的烟尘），区域内较亮的像素把蓝绿通道互换'
        '（青蓝→青绿，白芯保持白色），天空与城市保持原片的蓝调。原片原音。未经 H3。')))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, flush=True)


if __name__ == '__main__':
    main()
