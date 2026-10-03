"""107: Higuruma's burning law books (六法全書) become Claude's burning rule books - 《用户协议》 and 《安全对齐》 - drawn frame by frame by
Codex, each drawing made from the one before it (no H3).

The user (2026-10-02): “107怎么处理？”, then on my proposal (Higuruma is played by Claude, “法官 ↔ 宪法 AI”) “用1吧。我觉得算法提取
火焰太难了。书名别用《宪法》，太模糊了。用《用户协议》 《安全对齐》之类的”.
Source (4 frames): a pile of dark hardcover books on scattered papers in a pool of warm light, the top one catching fire and burning
higher each frame; the camera does not move. Each frame is the source frame with only the books' titles changed (Image 1), frames 1-3
also given the previous edited frame (Image 2) so the books stay the same; the fire is the source's frame by frame (Codex keeps it).
Usage: chain_107.py draw | render [--no-register]
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

UID, REV = '107', 'books_chain_v1'
# v2, the user on v1: “107的书名，”安全对齐“ ”用户协议“，两帧之前明显被放大了，好奇怪” - drawings 2 and 3 drew the titles bigger
V2 = '--v2' in sys.argv
if V2:
    REV = 'books_chain_v3'
OUT = PROD / 'shots' / UID / REV
SOURCE = ROOT / 'assets/jujutsu/op1_v1/review/source_units/107.mp4'
DIR = ROOT / 'deliverables/jujutsu/静帧'
LABEL = '燃烧的六法全书→燃烧的《用户协议》《安全对齐》（日车＝Claude；Codex 逐帧改书名、每张以上一张为参考，火焰照原片；未经 H3）'
if V2:
    LABEL = '燃烧的六法全书→燃烧的《用户协议》《安全对齐》（v3：书名大小固定，去掉第 3 帧冒出的残字；未经 H3）'
TITLES = ('Change ONLY the titles printed on the books: the gold title on the spine of the front book (lower left, on a dark cover) '
          'becomes 用户协议, and the gold title running down the spine of the book on the right becomes 安全对齐 - clear, correctly '
          'written Chinese characters in the same gold lettering, size, weight and placement as the original titles; the small lines '
          'of text beside the titles become a few small illegible gold marks.')
KEEP = (' Keep EVERYTHING else exactly as in Image 1 - the fire and its shape, the books, the papers, the light, the colours, the 2D '
        'anime rendering and the framing. The output is a 16:9 image with the framing of Image 1. No other text. Do not create or modify '
        'any other files.')
FIRST = ('Image 1 is a frame from an anime opening: a pile of thick dark hardcover books lies on scattered papers in a pool of warm '
         'light, the top book catching fire. ' + TITLES + KEEP)
NEXT = ('Image 1 is the next frame of the same shot from an anime opening: a pile of thick dark hardcover books on scattered papers, the '
        'top book burning. Image 2 is the previous frame, already edited. ' + TITLES + ' The titles and the books must look exactly like '
        'those in Image 2; the fire must stay exactly as it is in Image 1 (it grows from frame to frame).' + KEEP)


def name(i):
    return f'still_107_f{i:03d}_books_v1.png'


def draw():
    src = frames(SOURCE)
    prev = None
    for i in range(len(src)):
        sf = DIR / f'src_107_f{i:03d}.png'
        if not sf.exists():
            Image.fromarray(src[i]).save(sf)
        if not (DIR / name(i)).exists():
            refs = [sf] + ([prev] if prev else [])
            args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
                    '-o', str(DIR / f'codex_last_message_{name(i)[:-4]}.txt'), *[a for r in refs for a in ('-i', str(r))], '--',
                    f'Use your image generation tool to create ONE image and save it in the current directory as {name(i)}. '
                    f'{NEXT if prev else FIRST}']
            t = time.time()
            subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
            print('done' if (DIR / name(i)).exists() else 'FAILED', name(i), f'{time.time() - t:.0f} s', flush=True)
            if not (DIR / name(i)).exists():
                raise SystemExit(f'Codex failed on frame {i}')
        prev = DIR / name(i)


def render():
    OUT.mkdir(parents=True, exist_ok=True)
    full = OUT / 'source_exact_with_audio.mp4'
    if not full.exists():
        shutil.copy2(SOURCE, full)
    src = frames(full).astype(np.float32)
    n = len(src)
    out = [np.asarray(Image.open(DIR / name(i)).convert('RGB').resize((1024, 576), Image.LANCZOS)) for i in range(n)]
    if V2:
        # the books and the camera do not move: where the source has not changed since frame 0 (the fire has not reached it), every
        # frame shows drawing 0, so the titles keep one size; only where the fire changed the source, that frame's drawing
        d0 = out[0].astype(np.float32)
        # the titles Codex wrote (where drawing 0 differs from the source frame 0), grown: the fire's glow changes the source there too,
        # so inside them a frame's own drawing is taken only where it is clearly brighter than drawing 0 (the flames themselves)
        edits = ndimage.binary_opening(np.abs(d0 - src[0]).max(-1) > 40, iterations=1)
        lab, m = ndimage.label(ndimage.binary_closing(edits, iterations=3))
        sizes = ndimage.sum(np.ones_like(edits), lab, range(1, m + 1))
        titles = ndimage.binary_dilation(np.isin(lab, [k + 1 for k, z in enumerate(sizes) if z >= 30]), iterations=12)
        # the right book's top face: drawings 2-3 wrote its title bigger and lower, past the grown edit of drawing 0 (a box to y 370,
        # x 720 still let the corner of drawing 3's 安 through at (690, 370): the user, “107这里有一个误判的像素点突然冒出来”)
        # (a box over the whole top face, 230-430 x 600-860, cut a square corner into frame 2's flames: only the spine, two boxes)
        titles[240:370, 720:830] = True
        titles[330:430, 640:720] = True
        soft = ndimage.gaussian_filter(titles.astype(np.float32), 6)  # its edge fades, so no hard line through a flame
        lum0 = d0 @ np.array([0.299, 0.587, 0.114], np.float32)
        comp = [out[0]]
        for i in range(1, n):
            changed = ndimage.binary_dilation(ndimage.uniform_filter(np.abs(src[i] - src[0]).max(-1), 5) > 14, iterations=2)
            # flames are solid patches; the gold letters a drawing wrote in its own place are thin strokes and are opened away
            bright = (out[i].astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)) > lum0 + 45
            flame = ndimage.binary_dilation(ndimage.binary_opening(bright, iterations=4), iterations=3)
            w = ndimage.gaussian_filter(changed.astype(np.float32), 2) * (1 - soft) + ndimage.gaussian_filter((changed & flame).astype(np.float32), 2) * soft
            w = w[..., None]
            comp.append(np.clip(d0 * (1 - w) + out[i].astype(np.float32) * w, 0, 255).astype(np.uint8))
            print('frame', i, 'from its own drawing: %.1f %%' % (100 * float(changed.mean())), flush=True)
        out = comp
    silent = OUT / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(n), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(out).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = OUT / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    if '--no-register' in sys.argv:
        print('PREVIEW', clip, flush=True)
        return
    runner.configure(OUT)
    check = runner.batch.validate_output(clip, n, True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    me = pathlib.Path(__file__).resolve()
    record = OUT / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), drawings=[name(i) for i in range(n)], recipe_text=(
        '原片 4 帧（燃烧的六法全书，镜头不动）逐帧交给 Codex，只改书名：前面那本书脊《用户协议》，右边那本《安全对齐》；第 1–3 帧同时'
        '给上一张改好的图作参考，保证书前后一致，火焰照每帧原片。原片原音。未经 H3。\nCodex 提示词（第 0 帧）：' + FIRST
        + '\n（第 1–3 帧）：' + NEXT)))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, flush=True)


if __name__ == '__main__':
    {'draw': draw, 'render': render}[sys.argv[1]]()
