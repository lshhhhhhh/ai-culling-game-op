"""140: the bomb falling onto the city becomes a falling RTX 3090 - a Codex sprite composited on the CPU (no H3).

The user (2026-10-02): on gpu3090_kf_h3_v1 “替换失败” - H3 drew the card only in frame 0 (the keyframe), from frame 1 on the bomb was
back, as in 090. Source (17 frames): an aerial view of a city seen from straight above that does not move at all; a dark bomb, nose down,
falls away from the camera toward a point just above the centre - huge and cut off by the top edge at frame 0, a dot by frame 15.
Here: the clean plate is the last frame with the bomb's dot filled in, so in every frame the bomb is simply where the frame differs from
the plate; it is replaced by the plate, and a Codex sprite of the card (drawn after the card of our frame-0 keyframe) is laid over it -
its far end on the bomb's nose, as long as the bomb (frames 0-2, where the bomb runs off the top, sized from its body width).
Usage: sprite_140.py draw | render [--no-register]
"""
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

UID, REV = '140', 'gpu_sprite_v1'
DIR = ROOT / 'deliverables/jujutsu/静帧'
OUT = PROD / 'shots' / UID / REV
SRC = PROD / 'shots' / UID / 'gpu3090_kf_h3_v1' / 'source_exact_with_audio.mp4'
CARD_REF = ROOT / 'deliverables/jujutsu/关键帧/kf_140_f000_gpu_v2.png'
SPRITE = DIR / 'rtx3090_falling_v1.png'
LABEL = '落下的炸弹→RTX 3090（Codex 画显卡、代码合成：原片背景不动，炸弹用干净底板抹掉，显卡按炸弹逐帧的位置和大小贴上；未经 H3）'
PROMPT = ('Image 1 shows a graphics card falling toward a city - a card modelled on the NVIDIA GeForce RTX 3090 Founders Edition: a long, '
          'thick card with a dark gunmetal shroud, a silver X-shaped metal frame and a large black fan at its lower end. Draw that same '
          'card, whole, as a clean 2D anime illustration with crisp outlines and cel shading, falling straight down: the card stands '
          'VERTICALLY with its long axis up and down, seen face-on so the silver X frame and the fan are clearly visible, the fan end at '
          'the bottom. A tall portrait image, the card filling most of the height. Background: flat pure magenta (#FF00FF) everywhere, '
          'no shadow, no text, no logos. Do not create or modify any other files.')


def draw():
    if SPRITE.exists():
        return
    args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
            '-o', str(DIR / f'codex_last_message_{SPRITE.stem}.txt'), '-i', str(CARD_REF), '--',
            f'Use your image generation tool to create ONE image and save it in the current directory as {SPRITE.name}. {PROMPT}']
    t = time.time()
    subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
    print('done' if SPRITE.exists() else 'FAILED', SPRITE.name, f'{time.time() - t:.0f} s', flush=True)


def sprite():
    """The card cut out of its magenta background (as pan_090.gpu_sprite)."""
    a = np.asarray(Image.open(SPRITE).convert('RGB')).astype(np.float32)
    alpha = np.clip((np.linalg.norm(a - np.array([255, 0, 255], np.float32), axis=-1) - 60) / 80, 0, 1)
    ys, xs = np.nonzero(alpha > 0.5)
    a, alpha = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], alpha[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    a = np.where(alpha[..., None] < 1, a - np.array([255, 0, 255], np.float32) * (1 - alpha[..., None]) * 0.6, a)
    return np.clip(a, 0, 255), alpha


def fill(img, hole):
    """Fine-to-coarse normalized convolution: each hole pixel from the smallest blur that reaches known pixels."""
    known = (~hole).astype(np.float32)
    est, todo = img.copy(), hole.copy()
    for sigma in (2, 4, 8, 16, 32):
        wgt = ndimage.gaussian_filter(known, sigma)
        e = np.stack([ndimage.gaussian_filter(img[..., c] * known, sigma) for c in range(3)], -1) / np.maximum(wgt, 1e-6)[..., None]
        ok = todo & (wgt > (0.15 if sigma < 32 else 1e-4))
        est[ok] = e[ok]
        todo &= ~ok
    return est


def bomb_mask(frame, plate):
    d = ndimage.binary_opening(np.abs(frame - plate).max(-1) > 30, iterations=1)
    lab, n = ndimage.label(ndimage.binary_closing(d, iterations=2))
    if not n:
        return None
    sz = ndimage.sum(np.ones_like(d), lab, range(1, n + 1))
    return ndimage.binary_fill_holes(lab == int(np.argmax(sz)) + 1)


def render():
    OUT.mkdir(parents=True, exist_ok=True)
    full = OUT / 'source_exact_with_audio.mp4'
    if not full.exists():
        shutil.copy2(SRC, full)
    src = frames(full).astype(np.float32)
    # the plate: the last frame with the bomb filled in - it is still a dark oval of ~24 x 29 px with fins there, just above the centre
    # (v1 filled only what changed between frames 14 and 16 and left a dark smudge round the small cards)
    lum = src[-1] @ np.array([0.299, 0.587, 0.114], np.float32)
    win = np.zeros((576, 1024), bool)
    win[220:310, 470:560] = True
    lab, n = ndimage.label(ndimage.binary_closing((lum < 50) & win, iterations=1))
    dot = lab == 1 + int(np.argmax(ndimage.sum(np.ones_like(lum), lab, range(1, n + 1))))
    dot = ndimage.binary_dilation(ndimage.binary_fill_holes(dot), iterations=4)
    ys, xs = np.nonzero(dot)
    print('bomb in the last frame', (xs.min(), ys.min(), xs.max(), ys.max()), flush=True)
    plate = fill(src[-1], dot)
    # where and how big the bomb is in each frame. Its length is no measure (cut off by the top edge in frames 0-1, foreshortened more and
    # more as it falls away), its body width is: the widest row below the fins, smooth from 383 px at frame 0 down to ~19 px
    meas = {}
    for i in range(len(src)):
        m = bomb_mask(src[i], plate)
        if m is None or m.sum() < 30:
            continue
        # measured on its dark body only (near the end the change against the filled-in plate is mostly the city around it)
        m = ndimage.binary_fill_holes(m & ((src[i] @ np.array([0.299, 0.587, 0.114], np.float32)) < 60))
        ys, xs = np.nonzero(m)
        top, bot = ys.min(), ys.max()
        rows = range(int(top + 0.3 * (bot - top)), bot + 1)
        r_w, body = max(((r, m[r].sum()) for r in rows), key=lambda q: q[1])
        meas[i] = dict(top=int(top), bot=int(bot), body=int(body), cx=float(np.nonzero(m[r_w])[0].mean()))
    print('body widths', {i: q['body'] for i, q in meas.items()}, flush=True)
    rgb, al = sprite()
    asp = rgb.shape[1] / rgb.shape[0]
    bomb_colour = np.mean([src[i][bomb_mask(src[i], plate)].mean(0) for i in range(4, 10)], axis=0)
    # only a hint of the bomb's dark blue-grey and the city's violet cast: the card stays a lit metal card
    tone = np.clip((bomb_colour / np.maximum(rgb[al > 0.5].mean(0), 1)) ** 0.25, 0.6, 1.1)
    print('tone', tone.round(2), flush=True)
    last = max(meas)
    result = []
    for i in range(len(src)):
        frame = src[i]
        m = bomb_mask(frame, plate)
        hole = dot.copy() if m is None else ndimage.binary_dilation(m, iterations=4) | dot
        w = ndimage.gaussian_filter(hole.astype(np.float32), 1.0)[..., None]
        frame = frame * (1 - w) + plate * w
        q = meas.get(i, meas[last])
        W = max(2, round(q['body']))  # as wide as the bomb's body, its far end on the bomb's nose
        H = max(3, round(W / asp))
        c = np.asarray(Image.fromarray(rgb.astype(np.uint8)).resize((W, H), Image.LANCZOS), np.float32) * tone
        a = np.asarray(Image.fromarray((al * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS), np.float32)[..., None] / 255
        X, Y = round(q['cx'] - W / 2), q['bot'] + 1 - H
        sx0, sy0, dx0, dy0 = max(0, -X), max(0, -Y), max(0, X), max(0, Y)
        dx1, dy1 = min(1024, X + W), min(576, Y + H)
        if dx1 > dx0 and dy1 > dy0:
            cc, aa = c[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0], a[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0]
            frame[dy0:dy1, dx0:dx1] = frame[dy0:dy1, dx0:dx1] * (1 - aa) + cc * aa
        result.append(np.clip(frame, 0, 255).astype(np.uint8))
        print(i, 'card', W, 'x', H, 'at', X, Y, flush=True)
    silent = OUT / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(result)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(result).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = OUT / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    for k in (0, 3, 8, 14):
        Image.fromarray(result[k]).save(OUT / f'preview_f{k:03d}.png')
    if '--no-register' in sys.argv:
        print('PREVIEW', clip, flush=True)
        return
    runner.configure(OUT)
    check = runner.batch.validate_output(clip, len(result), True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    me = pathlib.Path(__file__).resolve()
    record = OUT / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), sprite=SPRITE.name, recipe_text=(
        '原片背景（俯视城市）完全不动：最后一帧补掉炸弹的小点作干净底板，每帧与底板不同的地方就是炸弹，用底板抹掉；Codex 照第 0 帧关键帧'
        '的显卡画一张竖直的 RTX 3090 贴图，逐帧放在炸弹的位置（远端对齐弹头，长度等于炸弹；第 0–2 帧炸弹超出画面，按弹身宽度推算）。'
        '原片原音。未经 H3。\nCodex 提示词：' + PROMPT)))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, flush=True)


if __name__ == '__main__':
    {'draw': draw, 'render': render}[sys.argv[1]]()
