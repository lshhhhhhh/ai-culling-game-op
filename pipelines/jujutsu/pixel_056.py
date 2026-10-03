"""056 on the CPU: the source's crumbling fragments redrawn as square pixels, frame by frame, so they move exactly as in the source.

User (2026-10-01) on the H3 try (pixel_kf_h3_v1): “完全失败。第一帧确实是像素，但是后面全部变成原版。有没有什么代码手段？比如用算法把黑色像素
都选中，然后让它们移动？如果做不到就算了”. The sphere and the background never move; only the fragments at the upper-right edge do.
Per frame, the dark pixels outside the sphere's core (inside the crumbling area) are snapped to a square grid: an 8 px cell is filled
black when fragments cover most of it, otherwise its 4 px sub-cells are tested; empty cells take the clean background (the per-pixel
median over the 12 frames). Because the grid is fixed, fragments hop cell to cell as they drift - the digital look the user chose.
"""
import json
import pathlib
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

import render_shot as runner
import render_batch_0001 as b1
from common import PROD, p

UID, REV = '056', 'pixel_cpu_v1'
OUT = PROD / 'shots' / UID / REV
LABEL = '黑太阳碎裂→边缘碎片逐帧变成方形像素（CPU：保留原片碎开的运动）'
AREA = (490, 140, 660, 360)    # the crumbling area around the upper-right edge (1024x576)
DARK = 70                      # luma below this is the sphere
FRAG = 85                      # the orange ground is about 105; fragments run 60-90 (v1 used 70 and lost the faint ones)
CLEAN = 95                     # the background plate is cleaned of everything darker than this
INK = np.array([10, 4, 4], np.float32)
LUMA = np.array([0.299, 0.587, 0.114], np.float32)


def frames(path):
    raw = subprocess.run([str(p.FFMPEG), '-v', 'error', '-i', str(path), '-vsync', '0', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 576, 1024, 3)


def pixelate(frame, plate, core):
    x0, y0, x1, y1 = AREA
    out = frame.astype(np.float32).copy()
    region = out[y0:y1, x0:x1]
    lum = region @ LUMA
    frag = (lum < FRAG) & ~core[y0:y1, x0:x1]
    new = plate[y0:y1, x0:x1].copy()
    keep = core[y0:y1, x0:x1]
    new[keep] = region[keep]
    for by in range(0, y1 - y0, 8):
        for bx in range(0, x1 - x0, 8):
            cell = frag[by:by + 8, bx:bx + 8]
            if cell.mean() > 0.5:
                new[by:by + 8, bx:bx + 8][~keep[by:by + 8, bx:bx + 8]] = INK
                continue
            for sy in (0, 4):
                for sx in (0, 4):
                    sub = cell[sy:sy + 4, sx:sx + 4]
                    if sub.size and sub.mean() > 0.3:
                        k = keep[by + sy:by + sy + 4, bx + sx:bx + sx + 4]
                        new[by + sy:by + sy + 4, bx + sx:bx + sx + 4][~k] = INK
    out[y0:y1, x0:x1] = new
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    inv = json.loads((PROD / 'source_inventory/inventory.json').read_text(encoding='utf-8'))
    start, end = b1.interval(UID)
    fps = 24000 / 1001
    full = OUT / 'source_exact_with_audio.mp4'
    if not full.exists():
        p.run([p.FFMPEG, '-v', 'error', '-y', '-i', inv['source'], '-map', '0:v:0', '-map', '0:a:0',
               '-vf', f'trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS,scale=1024:576:flags=lanczos,setsar=1,format=yuv420p',
               '-af', f'atrim=start={start / fps:.9f}:end={end / fps:.9f},asetpts=PTS-STARTPTS',
               '-r', '24000/1001', '-c:v', 'libx264', '-crf', '12', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', full])
    src = frames(full)
    assert len(src) == end - start
    plate = np.median(src.astype(np.float32), axis=0)
    # the sphere's core: the largest dark blob of the plate, shrunk so its crumbling rim is pixelated too
    lab, n = ndimage.label((plate @ LUMA) < DARK)
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    disc = lab == (int(np.argmax(sizes)) + 1)
    core = ndimage.binary_erosion(disc, iterations=6)
    # the plate has the static fragments too; outside the core the clean background is the plate with dark pixels filled in
    from title_057 import fill
    plate = fill(plate.astype(np.uint8), ndimage.binary_dilation(((plate @ LUMA) < CLEAN) & ~core, iterations=2))
    result = np.stack([pixelate(fr, plate, core) for fr in src])
    silent = OUT / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(result)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=result.tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    x0, y0, x1, y1 = AREA
    strip = np.concatenate([np.concatenate([src[i][y0:y1, x0:x1], result[i][y0:y1, x0:x1]], axis=0) for i in (0, 5, 11)], axis=1)
    Image.fromarray(strip).resize((strip.shape[1] * 2, strip.shape[0] * 2), Image.NEAREST).save(OUT / 'preview_before_after.png')
    clip = OUT / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    runner.configure(OUT)
    check = runner.batch.validate_output(clip, len(result), True)
    record = OUT / 'title_compositing.json'
    builder = pathlib.Path(__file__).resolve()
    p.write_json(record, dict(kind='cpu_text', builder=str(builder), builder_sha256=p.sha(builder),
                              recipe_text='原片 12 帧不动；右上碎裂区里球体核心以外的黑色碎片逐帧对齐到方格（8px，覆盖不足再看 4px 小格），空格填干净背景。'
                                          '碎片的运动完全来自原片。未经 H3。'))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    if '--no-register' not in sys.argv:
        entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
        if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
            runner.review.register(UID, str(clip), record, LABEL)
    changed = [int((np.abs(result[i].astype(int) - src[i].astype(int)).max(-1) > 20).sum()) for i in range(len(src))]
    moving = [int((np.abs(result[i + 1].astype(int) - result[i].astype(int)).max(-1) > 20).sum()) for i in range(len(src) - 1)]
    print('READY', clip, '| changed vs source per frame', changed, '| frame-to-frame motion', moving, flush=True)


if __name__ == '__main__':
    main()
