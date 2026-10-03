"""057 bridge keyframes: the bomb turned into the graphics card on frames of H3's text-free clip (clean_gpu_h3_v1).

User (2026-10-02) on clean_gpu_h3_v1: “哪里有显卡？显卡只有最后一帧出现了，前面完全没变。除了这个以外，标题什么的几乎完美”.
The bomb (in that clip from about frame 94) stays a bomb until the last frame, which has the card from kf_057_f114_gpu_v1. Only frames
92-114 are regenerated (render_057_bridge.py), so the keyframes are that clip's own frames: 92 and 114 as they are, and 98, 104 and
109 with the bomb replaced by the card of frame 114 (Image 2), at the bomb's place, size and angle.
v2: the user on the joined bridge: “还是有炸弹的画面啊？是不是你关键帧的位置放晚了？” - the bomb is in the source (and that clip) from
about frame 87, dark red rather than black, so my black-pixel test had dated it to frame 100. The bridge now starts at 82 and the card
is added at 88 and 93 too.
"""
import subprocess
import sys
import time

import numpy as np
from PIL import Image
from scipy import ndimage

from codex_keyframes_0001 import DIR
from codex_keyframes_0003 import CODEX
from common import PROD
from title_057 import frames

BASE = PROD / 'shots/057/clean_gpu_h3_v1/native_fullframe.mp4'
CARD = 114
EDITS = [88, 93, 98, 104, 109]  # 88 and 93 added for v2 of the bridge (it starts at 82)


def base_frame(i):
    out = DIR / f'base_057_f{i:03d}.png'
    if not out.exists():
        Image.fromarray(frames(BASE)[i]).save(out)
    return out


def composite(i, name):
    """Codex's frame where it differs from the base in solid areas (the card and the bomb it replaces); the base elsewhere."""
    out = DIR / name.replace('_v1', '_v2')
    a = np.asarray(Image.open(DIR / name).convert('RGB').resize((1024, 576), Image.LANCZOS)).astype(np.float32)
    b = np.asarray(Image.open(base_frame(i)).convert('RGB')).astype(np.float32)
    d = np.abs(a - b).max(-1) > 35
    lab, n = ndimage.label(ndimage.binary_closing(d, iterations=3))
    sizes = ndimage.sum(np.ones_like(d), lab, range(1, n + 1))
    m = np.isin(lab, [k + 1 for k, z in enumerate(sizes) if z >= 300])
    m = ndimage.binary_dilation(ndimage.binary_fill_holes(m), iterations=4)
    w = ndimage.gaussian_filter(m.astype(np.float32), 2)[..., None]
    Image.fromarray((a * w + b * (1 - w)).round().clip(0, 255).astype(np.uint8)).save(out)
    ys, xs = np.nonzero(m)
    print('composited', out.name, f'{100 * d.mean():.1f} % changed by Codex, {100 * m.mean():.1f} % taken',
          (xs.min(), ys.min(), xs.max(), ys.max()) if len(xs) else None, flush=True)


def main():
    card = base_frame(CARD)
    base_frame(92)
    base_frame(82)
    for i in EDITS:
        name = f'kf_057_f{i:03d}_bridge_gpu_v1.png'
        if not (DIR / name).exists():
            args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
                    '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt'), '-i', str(base_frame(i)), '-i', str(card), '--',
                    f'Use your image generation tool to create ONE image and save it in the current directory as {name}. Image 1 is a frame '
                    'from an anime opening: a dark red sky streaked with black clouds and a black eclipsed sun with a glowing red ring; a dark '
                    'bomb falls toward the camera in the upper right. Image 2 is a later frame of the same shot, where the falling object is '
                    'a black graphics card with round fans, close to the camera. Replace the bomb in Image 1 with that same graphics card '
                    'from Image 2 - the same design, colours and lighting - at exactly the place, size and angle of the bomb in Image 1: it '
                    'is the same card earlier in its fall, further away. No bomb remains. Keep EVERYTHING else exactly as in Image 1 - the '
                    'sky, the clouds, the sun, the colours, the framing and the 2D anime rendering. The output is a 16:9 image with the '
                    'framing of Image 1. Do not create or modify any other files.']
            t = time.time()
            try:
                subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
            except subprocess.TimeoutExpired:
                print('TIMEOUT', name, flush=True)
                continue
            print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', flush=True)
        if (DIR / name).exists():
            composite(i, name)


if __name__ == '__main__':
    main()
