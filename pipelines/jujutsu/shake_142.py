"""142: the Codex still of MiniMax with the source's comic shake (CPU; no H3).

User (2026-10-02 11:20) on codex_still_v1: “142不是静止帧，是有动画效果的”. Measured: 3 frames; the face is redrawn every frame (line
boil) and drifts 2 then 4 px diagonally (phase correlation on the face region); the wavy background rings morph rather than move.
So each frame is the SOURCE frame (its background, rings, phone and dots animate as they do) with the MiniMax layer from the still
on top: the layer is the area Codex changed, grown so that the man's outline never peeks out, shifted by the measured face drift and
warped by a small smooth random field (about 1.5 px) for the line boil.
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

UID, REV = '142', 'codex_shake_v1'
SRC = PROD / 'shots/142/minimax_flat_h3_v1/source_exact_with_audio.mp4'
STILL = ROOT / 'deliverables/jujutsu/静帧/still_142_seg1_v1.png'
DRIFT = [(0, 0), (2, 2), (4, 4)]  # face offset of frames 1 and 2 against frame 0 (x, y)
LABEL = '高羽→MiniMax·扁平卡通吃惊掉手机（Codex 静帧＋原片的抖动：背景用原片逐帧，人物按测得位移平移并加线条抖动）'


def warp(img, dx, dy, seed, amp=1.5):
    H, W = img.shape[:2]
    rng = np.random.default_rng(seed)
    fx = ndimage.gaussian_filter(rng.standard_normal((H, W)), 24)
    fy = ndimage.gaussian_filter(rng.standard_normal((H, W)), 24)
    fx *= amp / (np.abs(fx).max() + 1e-6)
    fy *= amp / (np.abs(fy).max() + 1e-6)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    coords = [yy - dy + fy, xx - dx + fx]
    if img.ndim == 2:
        return ndimage.map_coordinates(img, coords, order=1, mode='nearest')
    return np.stack([ndimage.map_coordinates(img[..., c], coords, order=1, mode='nearest') for c in range(img.shape[2])], -1)


def main():
    out = PROD / 'shots' / UID / REV
    out.mkdir(parents=True, exist_ok=True)
    src = frames(SRC).astype(np.float32)
    still = np.asarray(Image.open(STILL).convert('RGB').resize((1024, 576), Image.LANCZOS)).astype(np.float32)
    d = np.abs(still - src[0]).max(-1) > 30
    lab, n = ndimage.label(ndimage.binary_closing(d, iterations=2))
    sizes = ndimage.sum(np.ones_like(d), lab, range(1, n + 1))
    m = np.isin(lab, [k + 1 for k, z in enumerate(sizes) if z >= 40])
    m = ndimage.binary_dilation(ndimage.binary_fill_holes(m), iterations=8).astype(np.float32)
    result = []
    for i, (dx, dy) in enumerate(DRIFT):
        layer = warp(still, dx, dy, seed=142 + i)
        w = ndimage.gaussian_filter(warp(m, dx, dy, seed=142 + i), 2)[..., None]
        result.append(np.clip(src[i] * (1 - w) + layer * w, 0, 255).astype(np.uint8))
    full = out / 'source_exact_with_audio.mp4'
    if not full.exists():
        shutil.copy2(SRC, full)
    silent = out / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(result)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(result).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = out / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    runner.configure(out)
    check = runner.batch.validate_output(clip, len(result), True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    me = pathlib.Path(__file__).resolve()
    record = out / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), still=str(STILL), drift=DRIFT, recipe_text=(
        '原片 3 帧是搞笑抖动（人脸每帧重描、斜向漂移 2/4 像素，背景波纹变形）：每帧用原片当帧作背景，叠 Codex 静帧里的 MiniMax'
        '（Codex 改动区域外扩 8 像素），按测得位移平移并加约 1.5 像素的平滑随机扭曲模拟线条抖动。原片原音。未经 H3。')))
    p.write_json(out / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if '--no-register' not in sys.argv and not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, 'layer %.1f %% of the frame' % (100 * m.mean()), flush=True)


if __name__ == '__main__':
    main()
