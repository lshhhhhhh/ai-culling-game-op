"""JJK keyframes for 057 (title + bomb) by Codex image editing; stdin closed, 10-minute timeout.

User (2026-10-02) on title_cpu_v2: “4秒左右，画面变淡的时候原版的字又出现了。其实我觉得这个镜头可能还是要用模型，这个炸弹的画面我想改掉。
这样如何？我们把炸弹改成显卡，然后让模型处理文字。如果模型处理文字失败，再用你的算法把字去掉，手动添加”.
Keyframes for H3 (render_057_kf.py): the title rewritten as 模型回战 (frames 40 and 88) and the bomb turned into a falling graphics card
(frames 106 and 114). Only what the source itself shows changes; the subtitle 死滅回游 前編, the city, the sky and the black sun stay.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

from codex_keyframes_0001 import DIR, source_frame

CODEX = Path(os.environ['LOCALAPPDATA']) / 'OpenAI/Codex/bin/faa963e871dd422c/codex.exe'
LOGO = Path(r'deliverables\jujutsu\标题\title_057_logo_v1.png')
TITLE = ('Rewrite the big title: replace the four characters 呪術廻戦 with 模型回战 (simplified Chinese, left to right) in exactly the same '
         'style, size and place - thin gold double-outlined brush strokes with a dark brown fill, like the logo in Image 2 - and replace '
         'the small kana line above its right end with もけいかいせん in the same small gold style. Keep the subtitle 死滅回游 前編 below it '
         'exactly as it is. ')
GPU = ('Replace the falling bomb with a falling graphics card of about the same size, angle and dark silhouette: a long black GPU card '
       'with two round fans on its side and a metal bracket at one end, tumbling down through the sky. ')
KEEP = ('Keep EVERYTHING else exactly as in Image 1 - the background, the light, the colours, the camera framing and the 2D anime rendering. '
        'The output is a 16:9 image with the framing of Image 1. Do not create or modify any other files.')
RED = 'a dark red sky streaked with black clouds and a black eclipsed sun with a glowing red ring'
# The bomb appears only around frame 100 (small, upper right) and dives toward the camera, huge by frame 114; the title has faded by
# then. So frames 40 and 88 change only the title, frames 106 and 114 only the bomb.
EDITS = [
    ('057', 40, 'kf_057_f040_title_v1.png', [LOGO], 'Image 1 is a frame from an anime opening: a title over a black-and-white city. ' + TITLE),
    ('057', 88, 'kf_057_f088_title_v1.png', [LOGO], f'Image 1 is a frame from an anime opening: a title over {RED}. ' + TITLE),
    ('057', 106, 'kf_057_f106_gpu_v1.png', [], f'Image 1 is a frame from an anime opening: {RED}, and a small dark bomb falling in the '
     'upper right. ' + GPU + 'If a faint trace of an old title is still visible, remove it. '),
    ('057', 114, 'kf_057_f114_gpu_v1.png', [], f'Image 1 is a frame from an anime opening: {RED}, and a huge dark bomb diving nose-first '
     'toward the lower left, close to the camera, filling the right half of the frame. ' + GPU.replace('of about the same size', 'just as huge and close')
     + 'Show its fans and the gold contacts along one edge in dark red light. '),
]


def main():
    only = set(sys.argv[1:])
    for unit, local, name, refs, prompt in EDITS:
        if only and name not in only:
            continue
        if (DIR / name).exists():
            print('skip', name, flush=True)
            continue
        src = source_frame(unit, local, DIR / f'src_{unit}_f{local:03d}.png')
        args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
                '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt'), '-i', str(src)]
        for r in refs:
            args += ['-i', str(r)]
        args += ['--', f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {prompt}{KEEP}']
        t = time.time()
        try:
            subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
        except subprocess.TimeoutExpired:
            print('TIMEOUT', name, flush=True)
            continue
        print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', flush=True)
    composite()


def composite():
    """v2 of the title keyframes: Codex redrew the whole black-and-white city at frame 40 (27 % of the pixels moved by more than 40), so
    only the title is taken from Codex - the old and new gold glyphs, filled and grown by 4 px, feathered - and the rest is the source frame."""
    import numpy as np
    from PIL import Image
    from scipy import ndimage
    from title_057 import gold
    for local, name in ((40, 'kf_057_f040_title_v1.png'), (88, 'kf_057_f088_title_v1.png')):
        out = DIR / name.replace('_v1', '_v2')
        if out.exists() or not (DIR / name).exists():
            continue
        a = np.asarray(Image.open(DIR / name).convert('RGB').resize((1024, 576), Image.LANCZOS))
        b = np.asarray(Image.open(DIR / f'src_057_f{local:03d}.png').convert('RGB').resize((1024, 576), Image.LANCZOS))
        m = gold(a) | gold(b)
        m = ndimage.binary_dilation(ndimage.binary_fill_holes(ndimage.binary_closing(m, iterations=3)) | m, iterations=4)
        w = ndimage.gaussian_filter(m.astype(np.float32), 2)[..., None]
        Image.fromarray((a * w + b * (1 - w)).round().clip(0, 255).astype(np.uint8)).save(out)
        print('composited', out.name, f'{100 * m.mean():.1f} % from Codex', flush=True)


if __name__ == '__main__':
    main()
