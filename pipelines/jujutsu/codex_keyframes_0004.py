"""057 v2 keyframes: the frames with ALL text removed (title, kana, subtitle); the text is laid over the H3 output on the CPU afterwards.

User (2026-10-02) on the title keyframes of codex_keyframes_0003.py: “这个视频一定会失败，因为标题的“回”就不一样。要不这样。让模型去掉字，
直接你来写？” - Codex drew 回 differently at frames 40 and 88, so H3 would morph between two glyphs. Now H3 makes a text-free clip and one
fixed logo drawing (title_057_logo_v1.png) plus the subtitle are composited per frame (title_057.py v3).
Codex redraws the whole background when asked to edit, so only the text area is taken from it: inside the box around the source text,
the pixels where Codex differs from the source by more than 30, grown by 3 px and feathered; everything else is the source frame.
"""
import subprocess
import sys
import time

import numpy as np
from PIL import Image
from scipy import ndimage

from codex_keyframes_0001 import DIR, source_frame
from codex_keyframes_0003 import CODEX, RED
from title_057 import gold

CLEAN = ('Remove ALL the text from Image 1: the big gold-outlined title, the small kana above its right end and the white subtitle below '
         'it. Fill in what was behind the letters so that it continues the surrounding background seamlessly; add nothing new. Keep '
         'EVERYTHING else exactly as in Image 1 - the background, the light, the colours, the camera framing and the 2D anime rendering. '
         'The output is a 16:9 image with the framing of Image 1. Do not create or modify any other files.')
EDITS = [(0, 'kf_057_f000_clean_v1.png', 'a title over a black-and-white city of tall buildings.'),
         (40, 'kf_057_f040_clean_v1.png', 'a title and a subtitle over a black-and-white city of tall buildings.'),
         (88, 'kf_057_f088_clean_v1.png', f'a title and a subtitle over {RED}.')]


def text_box(src):
    """The box around the title, its kana and the subtitle: the gold glyphs, extended down by 45 % of their height for the subtitle."""
    ys, xs = np.nonzero(gold(src))
    x0, y0, x1, y1 = np.percentile(xs, 0.5), np.percentile(ys, 0.5), np.percentile(xs, 99.5), np.percentile(ys, 99.5)
    pad = 16
    return int(max(x0 - pad, 0)), int(max(y0 - pad, 0)), int(min(x1 + pad, 1024)), int(min(y1 + 0.45 * (y1 - y0) + pad, 576))


def composite(local, name):
    out = DIR / name.replace('_v1', '_v2')
    a = np.asarray(Image.open(DIR / name).convert('RGB').resize((1024, 576), Image.LANCZOS)).astype(np.float32)
    b = np.asarray(Image.open(DIR / f'src_057_f{local:03d}.png').convert('RGB').resize((1024, 576), Image.LANCZOS)).astype(np.float32)
    x0, y0, x1, y1 = text_box(b.astype(np.uint8))
    box = np.zeros((576, 1024), bool)
    box[y0:y1, x0:x1] = True
    m = box & (np.abs(a - b).max(-1) > 30)
    m = ndimage.binary_dilation(ndimage.binary_closing(m, iterations=2), iterations=3) & ndimage.binary_dilation(box, iterations=3)
    w = ndimage.gaussian_filter(m.astype(np.float32), 1.5)[..., None]
    c = (a * w + b * (1 - w)).round().clip(0, 255).astype(np.uint8)
    Image.fromarray(c).save(out)
    print('composited', out.name, 'box', (x0, y0, x1, y1), f'{100 * m.mean():.1f} % from Codex', 'gold left', int(gold(c).sum()), flush=True)


def main():
    only = set(sys.argv[1:])
    for local, name, what in EDITS:
        if only and name not in only:
            continue
        if not (DIR / name).exists():
            src = source_frame('057', local, DIR / f'src_057_f{local:03d}.png')
            args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
                    '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt'), '-i', str(src), '--',
                    f'Use your image generation tool to create ONE image and save it in the current directory as {name}. '
                    f'Image 1 is a frame from an anime opening: {what} {CLEAN}']
            t = time.time()
            try:
                subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
            except subprocess.TimeoutExpired:
                print('TIMEOUT', name, flush=True)
                continue
            print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', flush=True)
        if (DIR / name).exists():
            composite(local, name)


if __name__ == '__main__':
    main()
