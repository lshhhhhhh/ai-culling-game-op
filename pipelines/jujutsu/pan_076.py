"""076: Kusakabe's sister and her son as Qwen and chibi DeepSeek in the Kollwitz pencil sketch - 040's method (no H3).

The user (2026-10-02): “接下来看076.我觉得这个也是040的技术路线”, and on the casting question (the mother is the same sister who sits
in 133's wheelchair, now Qwen) “千问（与 133 一致）”. gptgirl_takeru_h3_v1 had copied the source.
Source (17 frames): one pencil sketch on beige paper (a mother hugging her small son, a band-aid on his cheek) under a vertical tilt up:
the drawing moves down 51 px a frame, easing out over the last five frames (47, 38, 25, 14, 6, 1); no horizontal move, no zoom.
Here: the frames are stacked into the whole sketch along the measured path (each step by phase correlation, so the ease-out is kept),
Codex redraws the whole sketch with the two of them recast, and every frame is cut from it along the same path.
Usage: pan_076.py mosaic | codex | render [--no-register]
"""
import json
import pathlib
import shutil
import subprocess
import sys
import time

import numpy as np
from PIL import Image

import render_shot as runner
from codex_keyframes_0003 import CODEX
from common import PROD, ROOT, p
from pan_040 import shift
from title_057 import frames

UID, REV = '076', 'pan_codex_v1'
OUT = PROD / 'shots' / UID / REV
DIR = ROOT / 'deliverables/jujutsu/静帧'
SRC = PROD / 'shots/076/gptgirl_takeru_h3_v1/source_exact_with_audio.mp4'
QWEN = ROOT / 'assets/人设/qwen娘.jpg'
DSQ = ROOT / 'assets/人设/鲸鱼娘-小.jpg'
PAINT_SRC = DIR / 'pan_076_sketch_src.png'
PAINT_NEW = DIR / 'pan_076_sketch_qwen_dsq_v1.png'
LABEL = '日下部的妹妹与儿子武→千问与Q版DeepSeek·珂勒惠支铅笔素描（040 的方法：整幅素描由 Codex 重画，按原片的竖直摇镜头逐帧裁切；未经 H3）'
PROMPT = ('Image 1 is a tall pencil sketch on beige paper in the style of Kathe Kollwitz, from an anime opening: a young mother with a bob '
          'hugs her small son tightly against her cheek, both smiling with their eyes closed, a band-aid on the boy\'s cheek. Image 2 is '
          'Qwen, a young woman with long wavy hair, a small beret with a flower, and a long Chinese-style robe under a coat. Image 3 is '
          'chibi DeepSeek, a small chibi girl with very long wavy hair, a frilled maid headband, small whale-fin ears and a maid dress with '
          'an apron. Redraw the mother as the woman of Image 2 and the small son as the chibi girl of Image 3 - their faces, hair, headwear '
          'and clothes - in exactly the same poses and the same tight, happy hug, at the same places and sizes; the chibi girl keeps the '
          'band-aid on her cheek. Draw everything in exactly the same grey pencil lines, hatching and smudged shading on the same beige '
          'paper as the rest of the sketch: no colour at all apart from the paper (their hair, the beret and the clothes are pencil greys '
          'only). Keep the composition, the lines\' character and everything else exactly as in Image 1. The output is a tall portrait '
          'image with the framing of Image 1. No text. Do not create or modify any other files.')


def mosaic():
    OUT.mkdir(parents=True, exist_ok=True)
    src = frames(SRC)
    steps = [shift(src[i - 1], src[i]) for i in range(1, len(src))]
    # as in pan_040: row r + dy of one frame is row r of the next, so the window moves by dy each frame - here the per-frame dy
    # (-51 easing out to -1), summed, not a median
    tops = np.concatenate([[0.0], np.cumsum([s[0] for s in steps])])
    tops -= tops.min()
    height = int(np.ceil(tops.max())) + 576
    stack = np.full((len(src), height, 1024, 3), np.nan, np.float32)
    for j in range(len(src)):
        t = int(round(tops[j]))
        stack[j, t:t + 576] = src[j]
    paint = np.nanmedian(stack, axis=0)
    Image.fromarray(np.clip(paint, 0, 255).astype(np.uint8)).save(PAINT_SRC)
    err = [float(np.abs(paint[int(round(tops[j])):int(round(tops[j])) + 576] - src[j]).mean()) for j in range(len(src))]
    print('sketch height', height, 'x drift', sorted({s[1] for s in steps}), 'reprojection error', [round(e, 1) for e in err], flush=True)
    p.write_json(OUT / 'pan_path.json', dict(tops=[round(float(t), 2) for t in tops], height=height,
                                             steps=[[round(s[0], 2), s[1], round(s[2], 3)] for s in steps]))


def codex():
    if PAINT_NEW.exists():
        return
    src = Image.open(PAINT_SRC)
    w, h = src.size
    pad = max(0, round(w * 1.5) - h)  # Codex draws 2:3 portraits: reflect-pad and crop back
    arr = np.asarray(src)
    padded = np.pad(arr, ((pad // 2, pad - pad // 2), (0, 0), (0, 0)), mode='reflect') if pad else arr
    inp = DIR / 'pan_076_sketch_src_2x3.png'
    Image.fromarray(padded).save(inp)
    args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
            '-o', str(DIR / f'codex_last_message_{PAINT_NEW.stem}.txt'), '-i', str(inp), '-i', str(QWEN), '-i', str(DSQ), '--',
            f'Use your image generation tool to create ONE image and save it in the current directory as {PAINT_NEW.name}. {PROMPT}']
    t = time.time()
    subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
    print('done' if PAINT_NEW.exists() else 'FAILED', PAINT_NEW.name, f'{time.time() - t:.0f} s', 'pad', pad, flush=True)


def render():
    path = json.loads((OUT / 'pan_path.json').read_text(encoding='utf-8'))
    src = frames(SRC)
    w, h = Image.open(PAINT_SRC).size
    pad = max(0, round(w * 1.5) - h)
    new = Image.open(PAINT_NEW).convert('RGB').resize((w, h + pad), Image.LANCZOS)
    new = np.asarray(new, np.float32)[pad // 2:pad // 2 + h]
    result = []
    for t in path['tops']:
        y0 = int(np.floor(t))
        f = t - y0
        y1 = min(y0 + 1, h - 576)
        result.append(np.clip(new[y0:y0 + 576] * (1 - f) + new[y1:y1 + 576] * f, 0, 255).astype(np.uint8))
    assert len(result) == len(src)
    full = OUT / 'source_exact_with_audio.mp4'
    if not full.exists():
        shutil.copy2(SRC, full)
    silent = OUT / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(result)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(result).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = OUT / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    for k in (0, 8, len(result) - 1):
        Image.fromarray(result[k]).save(OUT / f'preview_f{k:03d}.png')
    if '--no-register' in sys.argv:
        print('PREVIEW', clip, flush=True)
        return
    runner.configure(OUT)
    check = runner.batch.validate_output(clip, len(result), True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    me = pathlib.Path(__file__).resolve()
    record = OUT / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), painting=PAINT_NEW.name, recipe_text=(
        '原片是一张铅笔素描的竖直摇镜头（每帧 51 像素，最后五帧减速停下，无横移无缩放）：按逐帧测得的位移拼成整幅素描，Codex 重画'
        '（日下部的妹妹→千问，儿子武→Q版 DeepSeek，珂勒惠支铅笔画风、只有铅笔灰），再沿同一轨迹逐帧裁切。原片原音。未经 H3。'
        '\nCodex 提示词：' + PROMPT)))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, flush=True)


if __name__ == '__main__':
    {'mosaic': mosaic, 'codex': codex, 'render': render}[sys.argv[1]]()
