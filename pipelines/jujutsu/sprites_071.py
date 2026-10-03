"""071 by hand: a Codex run cycle of a tiny chibi HY composited over the clean plate, along the pandas' tracks (CPU; no H3).

The user (2026-10-02) on the Codex redraw of each drawing (codex_twos_v1): “有点不好，因为大小穿帮了，没有运动的效果。我觉得应该这样：
做出小HY奔跑的动作，比如5帧，然后你手动放进背景”.
- `sheet`: Codex draws a 5-frame run cycle of chibi HY (side view, running right) on flat magenta; keyed into 5 RGBA sprites.
- `render`: the clean plate is the per-pixel median of the 20 source frames (the pandas keep moving, so every pixel is free most of
  the time); each drawing's pandas are what differs from it. Pandas are matched between consecutive drawings (nearest, within
  90 px); each HY moves smoothly between her panda's places, playing the run cycle, scaled to the panda's height, facing her way.
Usage: sprites_071.py sheet | render [--no-register]
"""
import json
import pathlib
import shutil
import subprocess
import sys
import time

import numpy as np
from PIL import Image
from scipy import ndimage

import render_shot as runner
from codex_keyframes_0003 import CODEX
from common import PROD, ROOT, p
from title_057 import frames

UID, REV = '071', 'sprites_v2'
SRC = PROD / 'shots/071/hys_kf_h3_v3/source_exact_with_audio.mp4'
DIR = ROOT / 'deliverables/jujutsu/静帧'
SHEET = DIR / 'hy_run_cycle_v1.png'
HY = ROOT / 'assets/人设/HY娘.png'
LABEL = '熊猫群→一群小 HY 奔跑（v2：定格感——位置照原片每 4 帧一跳，姿势随跳换；石头挡在前面；未经 H3）'


def sheet():
    if SHEET.exists():
        return
    args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
            '-o', str(DIR / 'codex_last_message_hy_run_cycle_v1.txt'), '-i', str(HY), '--',
            f'Use your image generation tool to create ONE image and save it in the current directory as {SHEET.name}. Image 1 is HY, a '
            'girl with long black-blue hair and a red scarf. Draw a sprite sheet of a RUN CYCLE: exactly 5 frames of the same tiny chibi '
            'version of her (big head, short body, her long black-blue hair and red scarf flying behind her) running to the RIGHT, seen '
            'from the side, the 5 frames evenly spaced in ONE horizontal row, every frame the same size and on the same baseline, a '
            'smooth loop (contact, down, passing, up, contact). Clean 2D anime line art and flat cel shading. Background: flat pure '
            'magenta (#FF00FF) everywhere, no ground, no shadow, no text. Do not create or modify any other files.']
    t = time.time()
    subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
    print('done' if SHEET.exists() else 'FAILED', SHEET.name, f'{time.time() - t:.0f} s', flush=True)


def sprites():
    a = np.asarray(Image.open(SHEET).convert('RGB')).astype(np.float32)
    magenta = np.array([255, 0, 255], np.float32)
    dist = np.linalg.norm(a - magenta, axis=-1)
    alpha = np.clip((dist - 60) / 80, 0, 1)
    fg = alpha > 0.5
    cols = fg.any(0)
    runs, start = [], None
    for x in range(a.shape[1] + 1):
        on = x < a.shape[1] and cols[x]
        if on and start is None:
            start = x
        if not on and start is not None:
            if x - start > 20:
                runs.append((start, x))
            start = None
    out = []
    for x0, x1 in runs:
        rows = np.nonzero(fg[:, x0:x1].any(1))[0]
        y0, y1 = rows.min(), rows.max() + 1
        rgb = a[y0:y1, x0:x1]
        al = alpha[y0:y1, x0:x1]
        # remove the magenta fringe from the edge colour
        rgb = np.where(al[..., None] < 1, rgb - magenta * (1 - al[..., None]) * 0.6, rgb)
        out.append((np.clip(rgb, 0, 255), al))
    return out


def tracks(src):
    plate = np.median(src, axis=0)
    drawings = list(range(0, len(src), 2))
    found = []
    for i in drawings:
        d = np.abs(src[i] - plate).max(-1) > 40
        lab, n = ndimage.label(ndimage.binary_closing(d, iterations=2))
        blobs = []
        for k in range(1, n + 1):
            ys, xs = np.nonzero(lab == k)
            if len(ys) >= 40:
                blobs.append(dict(x=float(xs.mean()), bottom=float(ys.max()), h=float(ys.max() - ys.min() + 1), mask=(lab == k)))
        found.append(blobs)
    # chain blobs into tracks, drawing to drawing
    tracks_ = [[(0, b)] for b in found[0]]
    for j in range(1, len(found)):
        free = list(found[j])
        for t in tracks_:
            last_j, last = t[-1]
            if last_j != j - 1 or not free:
                continue
            best = min(free, key=lambda b: (b['x'] - last['x']) ** 2 + (b['bottom'] - last['bottom']) ** 2)
            if (best['x'] - last['x']) ** 2 + (best['bottom'] - last['bottom']) ** 2 < 90 ** 2:
                t.append((j, best))
                free.remove(best)
        tracks_ += [[(j, b)] for b in free]
    return plate, drawings, found, tracks_




# outlines traced on the clean plate (the camera is fixed); colour thresholds also took the dark grass around the rocks
ROCK_OUTLINES = [[(454, 345), (491, 382), (494, 420), (482, 446), (440, 460), (402, 458), (388, 440), (392, 410), (420, 375)],
                 [(637, 313), (662, 310), (679, 345), (677, 361), (645, 363), (634, 340)]]


def rock_mask(plate):
    """The rocks in front of the runners (v2, the user: “小人应该在石头后面”)."""
    from PIL import ImageDraw
    im = Image.new('L', (plate.shape[1], plate.shape[0]), 0)
    for poly in ROCK_OUTLINES:
        ImageDraw.Draw(im).polygon(poly, fill=255)
    return ndimage.gaussian_filter(np.asarray(im, np.float32) / 255, 1)


def paste(canvas, rgb, al, cx, bottom, h, flip, tone, front=None):
    scale = h / rgb.shape[0]
    W, H = max(1, round(rgb.shape[1] * scale)), max(1, round(h))
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    am = Image.fromarray((al * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    if flip:
        im, am = im.transpose(Image.FLIP_LEFT_RIGHT), am.transpose(Image.FLIP_LEFT_RIGHT)
    c = np.asarray(im, np.float32) * tone
    a = np.asarray(am, np.float32)[..., None] / 255
    X, Y = round(cx - W / 2), round(bottom - H)
    sx0, sy0 = max(0, -X), max(0, -Y)
    dx0, dy0, dx1, dy1 = max(0, X), max(0, Y), min(1024, X + W), min(576, Y + H)
    if dx1 > dx0 and dy1 > dy0:
        cc = c[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0]
        aa = a[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0]
        if front is not None:
            aa = aa * (1 - front[dy0:dy1, dx0:dx1, None])
        canvas[dy0:dy1, dx0:dx1] = canvas[dy0:dy1, dx0:dx1] * (1 - aa) + cc * aa


def render():
    src = frames(SRC).astype(np.float32)
    cycle = sprites()
    assert len(cycle) >= 4, f'{len(cycle)} sprites found in the sheet'
    plate, drawings, found, tr = tracks(src)
    front = rock_mask(plate)
    # the moonlit pandas are pale; light each HY like the panda she replaces (mean colour of the panda over the sheet's mean)
    out_frames = []
    for f in range(len(src)):
        canvas = plate.copy()
        for n_t, t in enumerate(tr):
            # v2, the user: “现在感觉过于灵活了，原版更有定格动画的感觉” - each HY stands exactly where her panda stands in the
            # source drawing of this frame (the pandas hop every 4 frames), and her run pose changes with each hop
            here = [b for j, b in t if drawings[j] <= f < drawings[j] + 2]
            if not here:
                continue
            b = here[0]
            xs = [q['x'] for _, q in t]
            going_left = (xs[-1] - xs[0]) < 0 if len(xs) > 1 else (n_t % 2 == 1)
            h = float(np.median([q['h'] for _, q in t]))  # one size per runner (the user: “大小穿帮了”)
            panda = np.concatenate([src[drawings[j]][q['mask']] for j, q in t]).mean(0)
            tone = np.clip(panda / 255 * 1.4, 0.25, 1.0)
            rgb, al = cycle[(f // 4 + n_t) % len(cycle)]
            paste(canvas, rgb, al, b['x'], b['bottom'], h, going_left, tone, front)
        out_frames.append(np.clip(canvas, 0, 255).astype(np.uint8))
    print('drawings', len(drawings), 'pandas per drawing', [len(b) for b in found], 'tracks', len(tr),
          'track lengths', sorted(len(t) for t in tr), flush=True)
    out = PROD / 'shots' / UID / REV
    out.mkdir(parents=True, exist_ok=True)
    full = out / 'source_exact_with_audio.mp4'
    if not full.exists():
        shutil.copy2(SRC, full)
    silent = out / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(out_frames)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(out_frames).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = out / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    Image.fromarray(plate.astype(np.uint8)).save(out / 'clean_plate.png')
    for k in (0, 9):
        Image.fromarray(out_frames[k]).save(out / f'preview_f{k:03d}.png')
    if '--no-register' in sys.argv:
        print('PREVIEW', clip, flush=True)
        return
    runner.configure(out)
    check = runner.batch.validate_output(clip, len(out_frames), True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    me = pathlib.Path(__file__).resolve()
    record = out / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), sheet=str(SHEET), recipe_text=(
        '干净背景＝原片 20 帧逐像素中位数；每张画面（一拍二）与背景相减得到熊猫，按相邻画面最近距离串成轨迹；每个 HY 在轨迹点之间'
        '逐帧平滑移动，播放 Codex 画的 5 帧奔跑循环，按熊猫高度缩放、按方向翻转、按熊猫亮度着色。原片原音。未经 H3。')))
    p.write_json(out / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, flush=True)


if __name__ == '__main__':
    {'sheet': sheet, 'render': render}[sys.argv[1]]()
