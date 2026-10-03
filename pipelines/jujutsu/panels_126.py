"""126: the collage panels that pop up around GPT redrawn for her (Codex art composited on the CPU, no H3).

The user (2026-10-02): “126的gpt很完美，但是后面贴上来的小图还在用原片，我也不知道该设计成什么”, then on my proposal “126按你的方案全部做吧”.
The source's five panels are Yuta's memories of Rika (grainy black-and-white photos with a red/cyan split): a pinky promise (frame 4),
an empty chair in a dark room (7), two hands on black (14), a strip of jagged white teeth (19), white flowers (22). Here each becomes
GPT's: a human hand and a robot hand making a pinky promise; an empty office chair before a glowing monitor with only a blinking
cursor; two hands typing on a keyboard in the screen's glow; a strip of white chat bubbles; white flowers shaped like her knot.
The base is the approved still of codex_drift_v1 (still_drift.py 126: our H3 frame 0 with the knot redrawn) moved with the source's
drift and carrying its grain; each panel lands on its measured rectangle on its entrance frame and follows that panel's own slow drift.
Usage: panels_126.py draw | render [--no-register]
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
from pan_040 import shift
from title_057 import frames

UID, REV = '126', 'panels_code_v2'
DIR = ROOT / 'deliverables/jujutsu/静帧'
OUT = PROD / 'shots' / UID / REV
SOURCE = PROD / 'shots/126/gpt6_grey_h3_v1/source_exact_with_audio.mp4'
STILL = DIR / 'still_126_codex_drift_v1_patched.png'
GPT = ROOT / 'deliverables/jujutsu/人设/gpt_yuta_v6.png'
LABEL = ('乙骨→GPT·黑白持刀与拼贴（GPT 沿用 codex_drift_v1；五张小图全部重画成她的回忆：人手与机器人手勾小指、空办公椅对着只有光标的屏幕、'
         '键盘上的手、聊天气泡条、结形白花；Codex 画、代码合成，未经 H3）')
STYLE = ('Draw a new photo in exactly the same style as Image 1 - a grainy, soft-focus black-and-white photograph from an anime opening, '
         'the same contrast and lighting mood - with the same framing and aspect ratio. No text, no letters, no logos. Do not create or '
         'modify any other files.')
# (first frame, measured rectangle x0, y0, x1, y1, output name, prompt)
PANELS = [
    (4, (640, 150, 984, 357), 'panel_126_promise_v1.png',
     'Image 1 is a small photo: two hands hooking their little fingers in a pinky promise. ' + STYLE + ' The new photo: a human hand and a '
     'robot hand (smooth white plastic shells and metal finger joints) hooking their little fingers in a pinky promise.'),
    (7, (54, 89, 311, 400), 'panel_126_cursor_v1.png',
     'Image 1 is a small photo: an empty wooden chair in a dark room lit by a pale spotlight. ' + STYLE + ' The new photo: an empty office '
     'chair facing an old computer monitor on a desk in a dark room; the screen glows pale and is blank except for a single text cursor.'),
    (14, (491, 333, 693, 509), 'panel_126_typing_v1.png',
     'Image 1 is a small photo: two hands faintly lit on black. ' + STYLE + ' The new photo: on black, two hands resting on a computer '
     'keyboard, typing, lit from the front only by the glow of a screen.'),
    (19, (209, 106, 391, 223), 'panel_126_bubbles_v1.png',
     'Image 1 is a narrow black strip with a row of jagged white shapes like teeth. ' + STYLE + ' The new strip: on black, a row of white '
     'chat speech bubbles (rounded rectangles with little tails), some showing three dots, in the same high-contrast look.'),
    (22, (86, 297, 235, 493), 'panel_126_knotflowers_v1.png',
     'Image 1 is a small photo: a bunch of white flowers on black. Image 2 is a character design; look at the white knot-shaped ornament in '
     'her hair (interlaced loops forming a rosette). ' + STYLE + ' The new photo: on black, a bunch of white flowers whose blossoms are each '
     'shaped like that knot ornament.'),
]


def draw():
    src = frames(SOURCE)

    def one(item):
        f, (x0, y0, x1, y1), name, prompt = item
        if (DIR / name).exists():
            return name, True
        ref = DIR / f'src_126_panel_f{f:03d}.png'
        Image.fromarray(src[min(f + 3, len(src) - 1)][y0:y1, x0:x1]).resize(((x1 - x0) * 3, (y1 - y0) * 3), Image.LANCZOS).save(ref)
        refs = [ref] + ([GPT] if 'Image 2' in prompt else [])
        args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
                '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt'), *[a for r in refs for a in ('-i', str(r))], '--',
                f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {prompt}']
        t = time.time()
        try:
            subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
        except subprocess.TimeoutExpired:
            pass
        print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', flush=True)
        return name, (DIR / name).exists()
    with ThreadPoolExecutor(len(PANELS)) as pool:
        print(list(pool.map(one, PANELS)))


def cover(path, w, h):
    im = Image.open(path).convert('RGB')
    s = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * s)), max(h, round(im.height * s))), Image.LANCZOS)
    x0, y0 = (im.width - w) // 2, (im.height - h) // 2
    return np.asarray(im.crop((x0, y0, x0 + w, y0 + h)), np.float32)


def translate(img, dx, dy):
    return ndimage.shift(img, (dy, dx) + (0,) * (img.ndim - 2), order=1, mode='nearest')


def local_shift(a, b):
    """Integer translation moving b onto a (phase correlation on a crop)."""
    F = np.fft.fft2(a - a.mean()) * np.conj(np.fft.fft2(b - b.mean()))
    r = np.fft.ifft2(F / (np.abs(F) + 1e-6)).real
    dy, dx = np.unravel_index(r.argmax(), r.shape)
    return (dy if dy < a.shape[0] // 2 else dy - a.shape[0]), (dx if dx < a.shape[1] // 2 else dx - a.shape[1])


def render():
    OUT.mkdir(parents=True, exist_ok=True)
    full = OUT / 'source_exact_with_audio.mp4'
    if not full.exists():
        shutil.copy2(SOURCE, full)
    src = frames(full)
    lum = src.astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
    still = np.asarray(Image.open(STILL).convert('RGB'), np.float32)
    # each panel: art toned like the source panel (grey, with the panel's own colour cast), and its own drift, a straight-line fit of the
    # per-frame phase correlation of its rectangle (single frames that jump, e.g. when another panel lands next to it, are outliers)
    arts, moves = [], []
    for f, (x0, y0, x1, y1), name, _ in PANELS:
        a = cover(DIR / name, x1 - x0, y1 - y0) @ np.array([0.299, 0.587, 0.114], np.float32)
        ref = src[min(f + 3, len(src) - 1)][y0:y1, x0:x1].astype(np.float32)
        tint = ref.mean((0, 1)) / max(ref.mean(), 1)
        a = (a - a.mean()) / (a.std() + 1e-6) * ref.mean(-1).std() + ref.mean()  # the source panel's brightness and contrast
        arts.append(np.clip(a[..., None] * tint, 0, 255))
        ks = np.arange(f, len(src))
        # (dy, dx) of the panel at k: local_shift moves frame k back onto frame f, the panel itself moved the opposite way
        off = -np.array([local_shift(lum[f][y0:y1, x0:x1], lum[k][y0:y1, x0:x1]) for k in ks], np.float32)
        fit = []
        for c in range(2):
            good = np.ones(len(ks), bool)
            for _ in range(2):
                k1, k0 = np.polyfit(ks[good], off[good, c], 1)
                good = np.abs(off[:, c] - (k1 * ks + k0)) <= 3
            fit.append((k1, k0))
        moves.append(fit)
        print('panel', name, 'moves', [round(v[0] * (len(src) - 1 - f), 1) for v in fit], 'px (dy, dx) to the end', flush=True)
    result, drifts = [], []
    for i in range(len(src)):
        dy, dx, _ = shift(src[0], src[i])
        dx, dy = -float(dx), -float(dy)
        drifts.append((round(dx, 1), round(dy, 1)))
        si = src[i].astype(np.float32)
        diff = si - translate(src[0].astype(np.float32), dx, dy)
        grain = np.where(np.abs(diff).max(-1, keepdims=True) < 20, diff, 0)
        out = translate(still, dx, dy) + grain
        for (f, (x0, y0, x1, y1), name, _), art, fit in zip(PANELS, arts, moves):
            if i < f:
                continue
            ody, odx = (fit[0][0] * i + fit[0][1]), (fit[1][0] * i + fit[1][1])
            ody, odx = ody - (fit[0][0] * f + fit[0][1]), odx - (fit[1][0] * f + fit[1][1])  # zero on the entrance frame
            # the source's red/cyan split, wide on the entrance frame and settling to 2 px
            split = 6 if i == f else 4 if i == f + 1 else 2
            h, w = art.shape[:2]
            layer = np.zeros((576, 1024, 3), np.float32)
            mask = np.zeros((576, 1024), np.float32)
            X, Y = x0 + odx, y0 + ody
            for c, sx in ((0, split), (1, 0), (2, -split)):
                pad = np.zeros((576, 1024), np.float32)
                pad[y0:y1, x0:x1] = art[..., c]
                layer[..., c] = ndimage.shift(pad, (Y - y0, X - x0 + sx), order=1)
            box = np.zeros((576, 1024), np.float32)
            box[y0:y1, x0:x1] = 1
            mask = ndimage.shift(box, (Y - y0, X - x0), order=1)
            for c, sx in ((0, split), (2, -split)):  # the split channels' fringes reach past the paper edge, as in the source
                mask = np.maximum(mask, 0.5 * ndimage.shift(box, (Y - y0, X - x0 + sx), order=1))
            m = mask[..., None]
            out = out * (1 - m) + layer * m
        result.append(np.clip(out, 0, 255).astype(np.uint8))
    silent = OUT / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(result)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(result).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = OUT / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    for k in (5, 15, 26):
        Image.fromarray(result[k]).save(OUT / f'preview_f{k:03d}.png')
    if '--no-register' in sys.argv:
        print('PREVIEW', clip, flush=True)
        return
    runner.configure(OUT)
    check = runner.batch.validate_output(clip, len(result), True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    me = pathlib.Path(__file__).resolve()
    record = OUT / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), still=STILL.name, drift=drifts,
                              panels=[dict(frame=f, rect=r, art=n) for f, r, n, _ in PANELS], recipe_text=(
        'GPT 沿用 codex_drift_v1 的静帧（我们的 H3 第 0 帧＋Codex 重画的结形发饰），按原片镜头漂移平移并叠原片颗粒；原片的五张回忆小图'
        '全部换成 Codex 新画的（按原片小图调成灰度与色偏），在原片测得的位置与出场帧（4/7/14/19/22）贴上，跟随各自的缓慢漂移，'
        '加红青错位（出场帧更大）。原片原音。未经 H3。\n' + '\n'.join(f'（第 {f} 帧）{pr}' for f, _, _, pr in PANELS))))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, flush=True)


if __name__ == '__main__':
    {'draw': draw, 'render': render}[sys.argv[1]]()
