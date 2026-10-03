"""118-120: the collage rebuilt with new illustrations (Codex) composited on the CPU on the source's timing and layout (no H3).

The user (2026-10-02 15:00): “118-120……原图用了大量的插画，我觉得我们也要有不同的插画。但是需要是完全不同的设计”, then on my
proposal “我觉得底图可以是一只deepseek大鲸鱼。但是可以狰狞一点。”
Source (21 frames): a symmetric orange-red illustration (frames 0-2); a silver foil card drops in the centre (3); a red palm-leaf card
with a dark figure lands on it with a torn black-and-white strip at the top right (5); three small stickers pop in (7-10); the whole
collage flips to a colour negative (12) and holds; a slow push-in throughout.
Here: a fierce frontal DeepSeek whale in orange-red (so the negative at frame 12 turns it blue), a red-ink neural-network tree with
the paperclip maximizer's silhouette, a blue chat bubble, a pixel token grid, a yellow toy graphics card and a strip of binary
punched tape; the foil is generated in code.
Usage: collage_118.py draw | layout | render [--no-register]
"""
import json
import pathlib
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image
from scipy import ndimage

import render_shot as runner
from codex_keyframes_0003 import CODEX
from common import PROD, ROOT, p
from title_057 import frames

UID, REV = '118-120', 'collage_code_v2'
DIR = ROOT / 'deliverables/jujutsu/静帧'
OUT = PROD / 'shots' / UID / REV
DS = ROOT / 'assets/人设/鲸鱼娘.png'
CLIP = ROOT / 'deliverables/jujutsu/人设/paperclip_maximizer_v2.png'
LABEL = '拼贴插画全部重新设计（v2：蓝色侧面的狰狞 DeepSeek 大鲸鱼底图、神经网络树、代码纸折的小船、token 网格、玩具显卡、二进制纸带；时间与版面照原片；未经 H3）'
FLAT = ('Flat, bold, hand-made collage illustration style like a screen print, strong outlines, no text, no letters, no logos. '
        'Do not create or modify any other files.')
ART = {
    'base': ('collage118_base_v1.png', [],
             'A 16:9 landscape illustration: a giant, FIERCE whale seen exactly from the front, perfectly left-right symmetric, filling '
             'the frame - the whale of the DeepSeek AI logo turned into a monster: its huge mouth open with rows of sharp teeth, glowing slit eyes on '
             'both sides of its head, its two pectoral fins spread like wings, ridged armour-like plates on its head. Painted entirely in '
             'orange, red, deep maroon and a little violet (no blue at all), on white paper with a thick black border around the picture, '
             'and four long magenta rods crossing over it diagonally. ' + FLAT),
    'card': ('collage118_card_v1.png', [CLIP],
             'A square illustration card on white: a tree drawn in red ink whose branches and leaves are a neural network - round nodes '
             'joined by thin lines spreading like palm fronds - and under it, small, the dark silhouette of the girl of Image 1 (long '
             'hair in a half-up bun, a long robe) standing still. Only red ink and black on white. ' + FLAT),
    'bubble': ('collage118_bubble_v1.png', [], 'A small rectangular sticker card: a bright blue speech bubble with three white dots '
               '(typing), on a pale blue background with a white border. ' + FLAT),
    'grid': ('collage118_grid_v1.png', [], 'A small rectangular sticker card: a black-and-white pixel grid like a QR code or a field of '
             'tokens, with a few cells glowing, on white with a thin black frame. ' + FLAT),
    'gpu': ('collage118_gpu_v1.png', [], 'A small rectangular sticker card: a cute yellow toy graphics card with two round fans, like a '
            'toy car, on a bright yellow background with a white border. ' + FLAT),
    'tape': ('collage118_tape_v1.png', [], 'A long horizontal strip of black punched paper tape printed with rows of white 0s and 1s and '
             'punched holes, its top edge torn and ragged, on plain white. Wide 4:1 landscape image. ' + FLAT),
}


# where and when each piece lands (measured on the source: the pixels that change on its entrance frame)
LAYOUT = [  # (art key or 'foil', first frame, x0, y0, x1, y1)
    ('base', 0, 0, 0, 1024, 576),
    ('foil', 3, 390, 49, 749, 445),
    ('card', 5, 357, 117, 673, 389),
    ('tape', 5, 540, 0, 1024, 105),
    ('bubble', 7, 3, 343, 191, 459),
    ('grid', 9, 820, 128, 991, 226),
    ('gpu', 10, 293, 403, 508, 538),
]
NEGATIVE_FROM = 12  # the whole collage flips to a colour negative and holds


def foil(w, h, seed=118):
    """Crumpled silver foil: a soft grey gradient, crinkle relief from smoothed noise, sparse bright glints."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    base = 150 + 60 * (xx / w) - 30 * (yy / h)
    n = ndimage.gaussian_filter(rng.standard_normal((h, w)), 3) * 1.0 + ndimage.gaussian_filter(rng.standard_normal((h, w)), 1.2) * 0.6
    gy, gx = np.gradient(n)
    relief = (gx - gy) * 220
    glint = (ndimage.gaussian_filter(rng.random((h, w)), 1) > 0.62) * 40
    g = np.clip(base + relief + glint, 40, 255)
    return np.repeat(g[..., None], 3, axis=-1)


def piece(key, w, h):
    if key == 'foil':
        return foil(w, h)
    im = Image.open(DIR / ART[key][0]).convert('RGB')
    # fill the slot (cover), centred
    s = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * s)), max(h, round(im.height * s))), Image.LANCZOS)
    x0, y0 = (im.width - w) // 2, (im.height - h) // 2
    return np.asarray(im.crop((x0, y0, x0 + w, y0 + h)), np.float32)


def render():
    src = frames(OUT / 'source_exact_with_audio.mp4')
    pieces = {k: piece(k, x1 - x0, y1 - y0) for k, _, x0, y0, x1, y1 in LAYOUT}
    result = []
    for f in range(len(src)):
        canvas = np.zeros((576, 1024, 3), np.float32)
        for k, first, x0, y0, x1, y1 in LAYOUT:
            if f >= first:
                canvas[y0:y1, x0:x1] = pieces[k]
                if k not in ('base',):  # a thin shadow under every pasted piece, like paper on paper
                    sh = np.zeros((576, 1024), np.float32)
                    sh[min(y1, 575):min(y1 + 4, 576), x0 + 4:min(x1 + 4, 1024)] = 1
                    sh[y0 + 4:y1, min(x1, 1023):min(x1 + 4, 1024)] = 1
                    canvas *= (1 - 0.35 * ndimage.gaussian_filter(sh, 1.5))[..., None]
        if f >= NEGATIVE_FROM:
            canvas = 255 - canvas
        result.append(np.clip(canvas, 0, 255).astype(np.uint8))
    full = OUT / 'source_exact_with_audio.mp4'
    silent = OUT / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(result)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(result).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = OUT / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    for k in (2, 6, 11, 15):
        Image.fromarray(result[k]).save(OUT / f'preview_f{k:03d}.png')
    if '--no-register' in sys.argv:
        print('PREVIEW', clip, flush=True)
        return
    runner.configure(OUT)
    check = runner.batch.validate_output(clip, len(result), True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    me = pathlib.Path(__file__).resolve()
    record = OUT / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), layout=LAYOUT, recipe_text=(
        '原片是一层层贴上去的拼贴（第 3 帧锡箔、第 5 帧中间卡片与右上纸条、第 7/9/10 帧三张小贴纸、第 12 帧起整体负片）。所有插画由 Codex '
        '重新设计（狰狞的 DeepSeek 大鲸鱼底图、红墨神经网络树＋回形针最大化器剪影、蓝色对话气泡、token 网格、黄色玩具显卡、二进制纸带），'
        '锡箔由代码生成，按原片测得的位置与出场帧拼贴，第 12 帧起反色。原片原音。未经 H3。')))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, flush=True)


# v2, the user on collage_code_v1: “118地图看不出是deepseek鲸鱼。要不换成蓝色？还有那个对话泡泡不好看，有点过于简陋敷衍了，换成别的设计吧”
ART['base'] = ('collage118_base_v2.png', [],
               'A 16:9 landscape illustration: the whale of the DeepSeek AI logo - a rounded, stylised whale seen from the SIDE exactly like '
               'the logo, deep DeepSeek blue (#4D6BFE) with a pale blue-white belly curve and a small round eye - drawn huge, filling the '
               'frame, turned into a fierce monster: its jaws wide open with rows of sharp white teeth, a glowing angry eye, ridged scars '
               'and armour plates along its back, its tail raised. Blues and white only, with deep navy shadows. On white paper with a '
               'thick black border around the picture, and four long magenta rods crossing over it diagonally. ' + FLAT)
ART['bubble'] = ('collage118_boat_v2.png', [],
                 'A small rectangular sticker card: a little paper boat folded from a printed page covered in fine lines of code and chat '
                 'transcript (only squiggles and dashes, no readable letters), floating on a few stylised waves, on a bright blue '
                 'background with a white border, crisp paper folds and shading. ' + FLAT)


def draw():
    def one(item):
        name, refs, prompt = item
        if (DIR / name).exists():
            return name, True
        args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
                '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt'), *[a for r in refs for a in ('-i', str(r))], '--',
                f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {prompt}']
        t = time.time()
        try:
            subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
        except subprocess.TimeoutExpired:
            return name, False
        print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', flush=True)
        return name, (DIR / name).exists()
    with ThreadPoolExecutor(len(ART)) as pool:
        print(list(pool.map(one, ART.values())))


if __name__ == '__main__':
    {'draw': draw, 'render': render}[sys.argv[1]]()
