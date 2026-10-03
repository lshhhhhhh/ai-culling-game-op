"""134: Maki -> Gemini (black sailor design v4), standing still while the red fog swallows her - Codex drawings composited on the CPU
(no H3).

The user (2026-10-02): on gemini_maki4_red_h3_v1 “这个和原作镜头不一样啊。”, then “134其实是一个任务静止不动，但是被雪雾吞没的动画。我们的动画
模型理解错了”. Source (24 frames, on twos: 12 drawings): Maki frozen mid-swing with her sword in red light; red and black fog shapes
churn over her and eat her away; the camera does not move.
Here: drawing 0 is the source frame with Maki redrawn as Gemini; drawings 1-11 are each source drawing redrawn with drawing 0 as the
reference for her (in parallel - she does not move, so every drawing is anchored on the same picture instead of a chain). In every
frame, where the source has not changed since frame 0 (she is still untouched) drawing 0 is used, so she is perfectly still; where the
fog has changed the source, that frame's drawing; outside her area, the source itself.
Usage: fog_134.py draw | render [--no-register]
"""
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

UID, REV = '134', 'fog_codex_v1'
# v2, the user on v1: “等下，134的人设是不是错了？怎么变成长裤了？” - drawing 0 kept Maki's black trousers (a frill of skirt at the waist);
# the design has a black pleated skirt, bare legs in black knee socks, loafers and a cat tail. All 12 drawings are redrawn (the other 11
# are anchored on drawing 0).
VER = 2 if ('--v2' in sys.argv or '--v3' in sys.argv) else 1  # v3 renders v2's drawings with a new compositing
V3 = '--v3' in sys.argv
if VER == 2:
    REV = 'fog_codex_v3' if V3 else 'fog_codex_v2'
OUT = PROD / 'shots' / UID / REV
SRC = PROD / 'shots/134/gemini_maki4_red_h3_v1/source_exact_with_audio.mp4'
DIR = ROOT / 'deliverables/jujutsu/静帧'
GEM = ROOT / 'deliverables/jujutsu/人设/gemini_maki_v4.png'
LABEL = '真希→Gemini黑水手服·静止的挥刀姿势被红雾吞没（Codex 逐张画、第 0 张为准；未被雾碰到处保持第 0 张，人物完全静止；未经 H3）'
if VER == 2:
    LABEL = '真希→Gemini黑水手服·静止的挥刀姿势被红雾吞没（v2：按设定改成百褶短裙、黑色及膝袜、乐福鞋和猫尾巴；未经 H3）'
if V3:
    LABEL = '真希→Gemini黑水手服·静止的挥刀姿势被红雾吞没（v3：每张画都按手和刀对齐到原片，手不再跳动；未经 H3）'
KEEP = (' Keep EVERYTHING else exactly as in Image 1 - the red light, the red and black fog shapes and where they cover her, the '
        'colours, the 2D anime rendering and the framing. The output is a 16:9 image with the framing of Image 1. No text. Do not create '
        'or modify any other files.')
FIRST = ('Image 1 is a frame from an anime opening: in a red void, a young woman with short dark hair frozen mid-swing, leaping with a '
         'long sword, lit entirely in red and black, with red and black fog shapes drifting around her. Image 2 is the character design '
         'of a girl: long purple-to-pink hair in a high ponytail, cat ears, thin rectangular glasses, a black sailor uniform with a '
         'gradient bow, a black pleated skirt, a katana. Redraw ONLY the woman as the girl of Image 2 - her face, glasses, cat ears, '
         'ponytail and black sailor uniform - in exactly the same frozen pose (the same leap, the same arms and the sword in the same '
         'place and angle), at the same place and size, lit and tinted entirely in the same red and black as the rest of the frame.'
         + (' She wears exactly the outfit of Image 2 from the waist down: a short black pleated skirt, bare legs, black knee socks and '
            'black loafers - NO trousers, no long pants - and her fluffy cat tail, long and gradient like her hair, swings out behind her.'
            if VER == 2 else '') + KEEP)
NEXT = ('Image 1 is a later frame of the same shot from an anime opening: the same frozen figure in a red void, now being swallowed '
        'by churning red and black fog that covers and eats away parts of her. Image 2 is the first frame of the shot, already edited: '
        'the girl who replaces that figure. Redraw the figure of Image 1 as exactly the girl of Image 2 - the same face, glasses, cat '
        'ears, ponytail, uniform, short pleated skirt, knee socks, cat tail, pose, sword, place, size and red tint - and only where the figure of Image 1 is still visible: wherever '
        'the fog covers or has eaten away part of the figure in Image 1, it covers or eats away the same part of her.' + KEEP)


def name(k):
    return f'still_134_d{k:02d}_fog_v{VER}.png'


def draw():
    src = frames(SRC)
    for k in range(len(src) // 2):
        sf = DIR / f'src_134_f{2 * k:03d}.png'
        if not sf.exists():
            Image.fromarray(src[2 * k]).save(sf)

    def one(k):
        if (DIR / name(k)).exists():
            return k, True
        refs = [DIR / f'src_134_f{2 * k:03d}.png', GEM if k == 0 else DIR / name(0)]
        args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
                '-o', str(DIR / f'codex_last_message_{name(k)[:-4]}.txt'), *[a for r in refs for a in ('-i', str(r))], '--',
                f'Use your image generation tool to create ONE image and save it in the current directory as {name(k)}. '
                f'{FIRST if k == 0 else NEXT}']
        t = time.time()
        try:
            subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
        except subprocess.TimeoutExpired:
            pass
        print('done' if (DIR / name(k)).exists() else 'FAILED', name(k), f'{time.time() - t:.0f} s', flush=True)
        return k, (DIR / name(k)).exists()
    assert one(0)[1], 'drawing 0 failed'
    with ThreadPoolExecutor(6) as pool:
        print(list(pool.map(one, range(1, len(src) // 2))))


def render():
    OUT.mkdir(parents=True, exist_ok=True)
    full = OUT / 'source_exact_with_audio.mp4'
    if not full.exists():
        shutil.copy2(SRC, full)
    src = frames(full).astype(np.float32)
    n = len(src)
    d = [np.asarray(Image.open(DIR / name(k)).convert('RGB').resize((1024, 576), Image.LANCZOS), np.float32) for k in range(n // 2)]
    if V3:
        # v3, the user on v2: “134有点怪异 感觉手的位置动了” - the fog keeps changing round her hands, so the hands came from each
        # drawing in turn, and the drawings placed them 15-20 px apart. (Taking the source's pixels where the fog covers her, with drawing
        # 0 darkened where it only passes, let Maki's bandaged arms through: tried and dropped.)
        # Codex drew her hands and sword ~8 px higher than Maki's (drawing 0: dy 8, dx -1 on the hands, 6 on the blade), so wherever
        # the source and a drawing meet round the hands they doubled. Each drawing is moved onto the source's hands (static in the
        # source; phase correlation on the hands against source frame 0; a weak peak falls back to drawing 0's shift).
        L = lambda f: f @ np.array([0.299, 0.587, 0.114], np.float32)
        y0, y1, x0, x1 = 220, 340, 400, 580
        win = np.outer(np.hanning(y1 - y0), np.hanning(x1 - x0))

        def hands_shift(img):
            a, b = L(src[0])[y0:y1, x0:x1], L(img)[y0:y1, x0:x1]
            F = np.fft.fft2((a - a.mean()) * win) * np.conj(np.fft.fft2((b - b.mean()) * win))
            r = np.fft.ifft2(F / (np.abs(F) + 1e-6)).real
            ky, kx = np.unravel_index(r.argmax(), r.shape)
            return (ky if ky < r.shape[0] // 2 else ky - r.shape[0]), (kx if kx < r.shape[1] // 2 else kx - r.shape[1]), r.max()
        base = hands_shift(d[0])[:2]
        moved = []
        for k, img in enumerate(d):
            dy, dx, peak = hands_shift(img)
            if peak < 0.15 or abs(dy - base[0]) + abs(dx - base[1]) > 20:
                dy, dx = base
            moved.append(ndimage.shift(img, (dy, dx, 0), order=1, mode='nearest'))
            print('drawing', k, 'moved', (int(dy), int(dx)), 'peak %.2f' % peak, flush=True)
        d = moved
    # her area: where drawing 0 differs from the source frame 0 (Maki's figure and Gemini's), filled and grown
    diff0 = np.abs(d[0] - src[0]).max(-1) > 30
    lab, m = ndimage.label(ndimage.binary_closing(diff0, iterations=3))
    sizes = ndimage.sum(np.ones_like(diff0), lab, range(1, m + 1))
    area = np.isin(lab, [i + 1 for i, z in enumerate(sizes) if z >= 300])
    area = ndimage.binary_dilation(ndimage.binary_fill_holes(area), iterations=8)
    a = ndimage.gaussian_filter(area.astype(np.float32), 3)[..., None]
    # what Gemini has beyond Maki's outline (the long ponytail, the ears): there the source is plain red void, which hardly changes when
    # the fog passes, so v1's test kept her ponytail floating after the fog had eaten the rest of her. There each drawing's own state
    # is used wherever it differs from drawing 0 (Codex ate the ponytail along with her).
    r, g = src[0][..., 0], src[0][..., 1]
    extra = area & diff0 & (r > 70) & (g < 0.35 * r)
    extra = ndimage.binary_dilation(ndimage.binary_opening(extra, iterations=1), iterations=3)
    result = []
    for i in range(n):
        k = i // 2
        # untouched by the fog since frame 0: drawing 0 (she stays perfectly still); changed: this drawing
        changed = ndimage.binary_dilation(ndimage.uniform_filter(np.abs(src[i] - src[0]).max(-1), 5) > 14, iterations=2)
        if V3:
            # per pixel, not smoothed and grown: v2's test reached ~5 px past every change, and the fog changes all round her hands,
            # so even hands left uncovered in the source came from each drawing in turn
            changed = ndimage.binary_opening(np.abs(src[i] - src[0]).max(-1) > 22, iterations=1)
        own = ndimage.binary_dilation(ndimage.uniform_filter(np.abs(d[k] - d[0]).max(-1), 5) > 25, iterations=2)
        changed = np.where(extra, own, changed)
        w = ndimage.gaussian_filter(changed.astype(np.float32), 2)[..., None]
        inside = d[0] * (1 - w) + d[k] * w
        result.append(np.clip(src[i] * (1 - a) + inside * a, 0, 255).astype(np.uint8))
    silent = OUT / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(n), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(result).tobytes(), capture_output=True)
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
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), drawings=[name(k) for k in range(n // 2)],
                              recipe_text=(
        '原片 24 帧一拍二（12 张画）：真希定格在挥刀姿势，红黑色的雾把她一点点吞没，镜头不动。第 0 张由 Codex 把真希换成 Gemini（黑水手服设定），'
        '其余 11 张各自照原片那张的雾、以第 0 张为人物参考重画；合成时原片自第 0 帧未变（还没被雾碰到）的地方一律用第 0 张，人物完全静止，'
        '雾变过的地方用该帧的画，人物区域外用原片。原片原音。未经 H3。\nCodex 提示词（第 0 张）：' + FIRST + '\n（其余）：' + NEXT)))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, flush=True)


if __name__ == '__main__':
    {'draw': draw, 'render': render}[sys.argv[1]]()
