"""040 as two camera pans over two Codex-redrawn paintings (CPU; no H3).

User (2026-10-02 02:42, on gpt6_ukiyoe_h3_v1): “效果其实差了点。有没有可能借用关键帧？或者说，我们把这一幕的两个画作提取出来，用GPT
生成对应的两张，然后再用两个上下的镜头模拟这个画面？” then “040我有一个方案，你能试试吗？”.
Measured (phase correlation, scales 0.94-1.06 tried): two pure vertical pans at constant speed, no zoom, no sideways drift -
frames 0-12 (cut after 12) and 13-30. `mosaic` stitches each pan into the full painting (per-pixel median of the aligned frames),
`codex` has Codex redraw each painting with Yuta as GPT (gpt_yuta_v6), and `render` pans over the new paintings along the measured
path and registers the clip (source audio).
Usage: pan_040.py mosaic | codex | render [--no-register]
"""
import json
import pathlib
import subprocess
import sys
import time

import numpy as np
from PIL import Image

import render_shot as runner
from codex_keyframes_0003 import CODEX
from common import PROD, ROOT, p
from title_057 import frames

UID, REV = '040', 'pan_codex_v1'
OUT = PROD / 'shots' / UID / REV
DIR = ROOT / 'deliverables/jujutsu/静帧'
SRC = PROD / 'shots/040/gpt6_ukiyoe_h3_v1/source_exact_with_audio.mp4'
SEGMENTS = [(0, 13), (13, 31)]
GPT = ROOT / 'deliverables/jujutsu/人设/gpt_yuta_v6.png'
LABEL = '乙骨→GPT·国芳武者绘（两幅画由 Codex 重画，按原片测得的竖直摇镜头逐帧平移；未经 H3）'


def shift(a, b):
    """Vertical shift of b relative to a, full resolution, sub-pixel (phase correlation on grey, Hann window)."""
    ga, gb = (np.asarray(Image.fromarray(f).convert('L'), np.float32) for f in (a, b))
    win = np.outer(np.hanning(576), np.hanning(1024)).astype(np.float32)
    ga, gb = (ga - ga.mean()) * win, (gb - gb.mean()) * win
    F = np.fft.fft2(ga) * np.conj(np.fft.fft2(gb))
    r = np.fft.ifft2(F / (np.abs(F) + 1e-6)).real
    y, x = np.unravel_index(np.argmax(r), r.shape)
    ym, yp = r[(y - 1) % 576, x], r[(y + 1) % 576, x]
    sub = 0.5 * (ym - yp) / (ym - 2 * r[y, x] + yp + 1e-9)
    y = y + sub
    if y > 288:
        y -= 576
    if x > 512:
        x -= 1024
    return float(y), int(x), float(r.max())


def mosaic():
    OUT.mkdir(parents=True, exist_ok=True)
    src = frames(SRC)
    path = {}
    for k, (a, b) in enumerate(SEGMENTS):
        steps = [shift(src[i - 1], src[i]) for i in range(a + 1, b)]
        dy = float(np.median([s[0] for s in steps]))
        # frame i shows the painting from row top_i; row r + dy of one frame is row r of the next (checked directly: error 5.6
        # at +54 rows in the first pan against 48 unshifted), so the window moves down the painting by dy per frame
        tops = np.array([(i - a) * dy for i in range(a, b)])
        tops -= tops.min()
        height = int(np.ceil(tops.max())) + 576
        stack = np.full((b - a, height, 1024, 3), np.nan, np.float32)
        for j, i in enumerate(range(a, b)):
            t = int(round(tops[j]))
            stack[j, t:t + 576] = src[i]
        paint = np.nanmedian(stack, axis=0)
        Image.fromarray(np.clip(paint, 0, 255).astype(np.uint8)).save(DIR / f'pan_040_painting{k + 1}_src.png')
        path[k] = dict(frames=[a, b], dy=dy, tops=[round(float(t), 2) for t in tops], height=height,
                       steps=[[round(s[0], 2), s[1], round(s[2], 3)] for s in steps])
        # how well the painting explains each frame (mean abs error of the re-cropped frame)
        err = [float(np.abs(paint[int(round(tops[j])):int(round(tops[j])) + 576] - src[i]).mean()) for j, i in enumerate(range(a, b))]
        print('painting', k + 1, 'dy %.2f' % dy, 'height', height, 'x drift', sorted({s[1] for s in steps}), 'reprojection error', [round(e, 1) for e in err], flush=True)
    p.write_json(OUT / 'pan_path.json', path)


PROMPT = ('Image 1 is a tall painting in the style of an ukiyo-e warrior print by Utagawa Kuniyoshi, from an anime opening. Redraw the '
          'young man with short black hair as the girl of Image 2 (GPT): very long wavy white hair with a small ahoge and a small white '
          'knot-shaped ornament, lavender eyes, an off-white blazer with a black sailor collar, a dark green necktie and a black pleated '
          'skirt - in exactly his pose and action, holding the katana the same way, at the same size and place, drawn in exactly the same '
          'woodblock-print outlines, textures and muted colours as the rest of the painting. Keep the monsters, the spears, the patterns, '
          'the composition and everything else exactly as in Image 1. The output is a portrait image with the same framing and aspect as '
          'Image 1. No text, no signature. Do not create or modify any other files.')


def codex():
    for k in (1, 2):
        name = f'pan_040_painting{k}_gpt_v1.png'
        if (DIR / name).exists():
            continue
        src = Image.open(DIR / f'pan_040_painting{k}_src.png')
        # Codex draws 2:3 portraits; reflect-pad the painting to 2:3 and crop back afterwards
        w, h = src.size
        target = round(w * 1.5)
        pad = max(0, target - h)
        arr = np.asarray(src)
        padded = np.pad(arr, ((pad // 2, pad - pad // 2), (0, 0), (0, 0)), mode='reflect') if pad else arr
        inp = DIR / f'pan_040_painting{k}_src_2x3.png'
        Image.fromarray(padded).save(inp)
        args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
                '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt'), '-i', str(inp), '-i', str(GPT), '--',
                f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {PROMPT}']
        t = time.time()
        try:
            subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
        except subprocess.TimeoutExpired:
            print('TIMEOUT', name, flush=True)
            continue
        print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', 'pad', pad, flush=True)


def render():
    path = json.loads((OUT / 'pan_path.json').read_text(encoding='utf-8'))
    src = frames(SRC)
    result = []
    for k in (1, 2):
        seg = path[str(k - 1)]
        orig = Image.open(DIR / f'pan_040_painting{k}_src.png')
        w, h = orig.size
        pad = max(0, round(w * 1.5) - h)
        new = Image.open(DIR / f'pan_040_painting{k}_gpt_v1.png').convert('RGB').resize((w, h + pad), Image.LANCZOS)
        new = np.asarray(new, np.float32)[pad // 2:pad // 2 + h]
        for t in seg['tops']:
            y0 = int(np.floor(t))
            f = t - y0
            crop = new[y0:y0 + 576] * (1 - f) + new[min(y0 + 1, h - 576):min(y0 + 1, h - 576) + 576] * f
            result.append(np.clip(crop, 0, 255).astype(np.uint8))
    assert len(result) == len(src), (len(result), len(src))
    OUT.mkdir(parents=True, exist_ok=True)
    full = OUT / 'source_exact_with_audio.mp4'
    if not full.exists():
        import shutil
        shutil.copy2(SRC, full)
    silent = OUT / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(result)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(result).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = OUT / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    runner.configure(OUT)
    check = runner.batch.validate_output(clip, len(result), True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    me = pathlib.Path(__file__).resolve()
    record = OUT / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), recipe_text=(
        '原片是两段匀速竖直摇镜头（第 0–12 帧、第 13–30 帧，无缩放无横移）：把每段拼成整幅画，Codex 按整幅画重画（乙骨→GPT 二设 v6，'
        '国芳武者绘画风不变），再按原片测得的摇镜头轨迹逐帧裁切平移。原片原音。未经 H3。')))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if '--no-register' not in sys.argv and not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, flush=True)


if __name__ == '__main__':
    {'mosaic': mosaic, 'codex': codex, 'render': render}[sys.argv[1]]()
