"""133: Liang pushing Qwen in the wheelchair - one Codex still and the source's push-in, on the CPU (no H3).

The user (2026-10-02), after liang_qwen_kf_h3_v2 brought the source's sister back: “133为什么这么难？不能用静止帧吗？” - it can: measured
on the source, the figures and the trees scale together (1.09 at frame 3, 1.19 at frame 6, 2.08 at frame 20) with almost no shift, so
shot 1 (frames 0-20) is one drawing under an accelerating push-in; shot 2 (21-22) is a closer view pushed in 4.5 %.
Here: a sharp still of shot 1 is put together from our liang_gptgirl_h3_v1 frames (Liang already right), each frame scaled back by its
measured zoom so the later, closer frames supply the detail in the middle; Codex replaces only the girl in the wheelchair with Qwen; every
frame is cut from that still at the measured zoom. Shot 2 is the Qwen keyframe of frame 22 (codex_keyframes_0007.py) pushed in.
Usage: zoom_133.py draw | render [--no-register]
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

UID, REV = '133', 'qwen_zoom_v1'
DIR = ROOT / 'deliverables/jujutsu/静帧'
OUT = PROD / 'shots' / UID / REV
V1 = PROD / 'shots/133/liang_gptgirl_h3_v1'
QWEN = ROOT / 'assets/人设/qwen娘.jpg'
SHOT2 = ROOT / 'deliverables/jujutsu/关键帧/kf_133_f022_qwen_v2.png'
CUT = 21
# v2, the user on qwen_zoom_v1: “133最后一帧莫名变了一下，为什么？不能用一张图吗” - frames 21-22 are no cut (the plan's “hard cut at 21”
# was a misdetection): the same drawing keeps being pushed in (x1.055 from 20 to 21, 2.29 from frame 0 at 22). v2 cuts all 23 frames
# from the one still.
V2 = '--v2' in sys.argv or '--v3' in sys.argv
# v3, the user (2026-10-02): “133是梁文锋推着千问有点奇怪。不如让动漫版马云推着，更加合理” - Qwen is Alibaba's, so the man pushing her
# becomes the anime Jack Ma (人设/ma_yun_v1.png, drawn after the Wikimedia photo the user chose); the v1 still edited once more by Codex,
# still cut along the whole push-in as v2
V3 = '--v3' in sys.argv
MAYUN = ROOT / 'deliverables/jujutsu/人设/ma_yun_v1.png'
STILL3 = 'still_133_qwen_mayun_v1.png'
PROMPT3 = ('Image 1 is a frame from an anime opening: in a sunlit forest clearing, a man in a dark suit and glasses pushes a wheelchair in '
           'which a girl with long blue-violet hair and a beret sits quietly. Image 2 is the character design of a man. Redraw ONLY the man '
           'pushing the wheelchair as the man of Image 2 - his face, his short black hair combed up and back, his slight build, his dark '
           'navy suit, white shirt and light blue tie, no glasses - in exactly the same pose, both hands on the wheelchair\'s handles, at '
           'the same place and size, with a calm, kind expression, lit by the same soft forest light and drawn in the same anime style. '
           'Keep the girl in the wheelchair, the wheelchair and the forest exactly as they are, with all their detail. The output is a '
           '16:9 image with the framing of Image 1. No text. Do not create or modify any other files.')
if V2:
    REV = 'qwen_zoom_v2'
    OUT = PROD / 'shots' / UID / REV
    CUT = None  # no cut: every frame
if V3:
    REV = 'qwen_mayun_zoom_v3'
    OUT = PROD / 'shots' / UID / REV
    LABEL = '日下部与妹妹→动漫版马云推着坐轮椅的千问·林间（一张 Codex 静帧＋按原片测得的推进逐帧裁切；未经 H3）'
C = (512.0, 288.0)
MOSAIC = DIR / 'mosaic_133_v1.png'
STILL = 'still_133_qwen_v1.png'
LABEL = '日下部与妹妹→梁文锋推着坐轮椅的千问·林间（原片是一张画在推镜头：Codex 静帧＋按原片测得的推进逐帧裁切；未经 H3）'
PROMPT = ('Image 1 is a frame from an anime opening: in a sunlit forest clearing, a man in a dark suit and glasses pushes a wheelchair in '
          'which a pale girl with long white hair sits quietly, her hands folded in her lap. Image 2 is Qwen, a girl with long wavy '
          'blue-violet hair, purple eyes, a small navy beret with a white flower, and a long white-and-blue Chinese-style robe under a navy '
          'coat. Redraw ONLY the girl in the wheelchair as the girl of Image 2 - her face, blue-violet hair, beret, white-and-blue robe and '
          'navy coat - sitting quietly in the wheelchair in exactly the same pose (hands folded in her lap, a calm, slightly frail look), '
          'place and size, lit by the same soft forest light. Nothing of the white-haired girl remains. Keep the man pushing the '
          'wheelchair, the wheelchair and the forest exactly as they are, with all their detail. The output is a 16:9 image with the '
          'framing of Image 1. No text. Do not create or modify any other files.')


def zoom_fit(lum, a, b, lo, hi, step):
    """(scale, dy, dx) with frame-a point p shown at frame-b point C + s * (p - d - C): scale searched, shift by phase correlation."""
    yy, xx = np.mgrid[0:576, 0:1024].astype(np.float32)
    best = None
    for s in np.arange(lo, hi, step):
        w = ndimage.map_coordinates(lum[b], [C[1] + s * (yy - C[1]), C[0] + s * (xx - C[0])], order=1)
        A, B = lum[a][40:540, 80:944], w[40:540, 80:944]
        F = np.fft.fft2(A - A.mean()) * np.conj(np.fft.fft2(B - B.mean()))
        r = np.fft.ifft2(F / (np.abs(F) + 1e-6)).real
        k = np.unravel_index(r.argmax(), r.shape)
        dy = k[0] if k[0] < r.shape[0] // 2 else k[0] - r.shape[0]
        dx = k[1] if k[1] < r.shape[1] // 2 else k[1] - r.shape[1]
        if best is None or r.max() > best[0]:
            best = (r.max(), s, dy, dx)
    return best[1:]


def zooms():
    """Shot 1's push-in measured on the source (frame 0 to each frame, each search starting from the last), smoothed by a cubic fit."""
    src = frames(V1 / 'source_exact_with_audio.mp4').astype(np.float32)
    lum = src @ np.array([0.299, 0.587, 0.114], np.float32)
    last = CUT or len(src)
    meas, prev = [(1.0, 0, 0)], 1.0
    for b in range(1, last):
        z = zoom_fit(lum, 0, b, prev - 0.01, prev + 0.12, 0.005)
        meas.append(z)
        prev = z[0]
    meas = np.array(meas, np.float32)
    f = np.arange(last)
    fit = np.stack([np.polyval(np.polyfit(f, meas[:, c], 3), f) for c in range(3)], -1)
    fit[0] = (1, 0, 0)
    s2 = zoom_fit(lum, CUT, CUT + 1, 0.98, 1.1, 0.005) if CUT else None
    print('push-in', np.round(fit[:, 0], 3).tolist(), 'shot 2', s2, flush=True)
    return fit, s2


def mosaic(fit):
    """Shot 1 at the density of its closest frame: every frame of our H3 run scaled back by its zoom, the closer frames over the middle,
    each feathered 24 px in from its own edges."""
    v1 = frames(V1 / 'native_fullframe.mp4').astype(np.float32)
    K = float(fit[-1, 0])
    H, W = round(576 * K), round(1024 * K)
    YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
    canvas = np.zeros((H, W, 3), np.float32)
    for i in range(CUT):
        s, dy, dx = fit[i]
        py, px = YY / K, XX / K  # frame-0 point of each canvas pixel
        qy, qx = C[1] + s * (py - dy - C[1]), C[0] + s * (px - dx - C[0])  # where frame i shows it
        inside = np.clip(np.minimum.reduce([qx, 1023 - qx, qy, 575 - qy]) / 24, 0, 1)
        if i == 0:
            inside = (inside > 0).astype(np.float32)
        sample = np.stack([ndimage.map_coordinates(v1[i][..., c], [qy, qx], order=3, mode='nearest') for c in range(3)], -1)
        canvas = canvas * (1 - inside[..., None]) + sample * inside[..., None]
    Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8)).save(MOSAIC)
    print('mosaic', W, 'x', H, flush=True)


def draw():
    fit, _ = zooms()
    if not MOSAIC.exists():
        mosaic(fit)
    if (DIR / STILL).exists():
        return
    args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
            '-o', str(DIR / f'codex_last_message_{STILL[:-4]}.txt'), '-i', str(MOSAIC), '-i', str(QWEN), '--',
            f'Use your image generation tool to create ONE image and save it in the current directory as {STILL}. {PROMPT}']
    t = time.time()
    subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
    print('done' if (DIR / STILL).exists() else 'FAILED', STILL, f'{time.time() - t:.0f} s', flush=True)


def draw_v3():
    if (DIR / STILL3).exists():
        return
    args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
            '-o', str(DIR / f'codex_last_message_{STILL3[:-4]}.txt'), '-i', str(DIR / STILL), '-i', str(MAYUN), '--',
            f'Use your image generation tool to create ONE image and save it in the current directory as {STILL3}. {PROMPT3}']
    t = time.time()
    subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
    print('done' if (DIR / STILL3).exists() else 'FAILED', STILL3, f'{time.time() - t:.0f} s', flush=True)


def cut(img, s, dy, dx):
    """The 1024 x 576 frame that shows img (framed like frame 0, any size) at zoom s: output q shows frame-0 point C + (q - C) / s + d."""
    k = img.width / 1024
    a = k / s
    return img.transform((1024, 576), Image.AFFINE, (a, 0, k * (C[0] * (1 - 1 / s) + dx), 0, a, k * (C[1] * (1 - 1 / s) + dy)),
                         resample=Image.BICUBIC)


def render():
    OUT.mkdir(parents=True, exist_ok=True)
    full = OUT / 'source_exact_with_audio.mp4'
    if not full.exists():
        shutil.copy2(V1 / 'source_exact_with_audio.mp4', full)
    fit, s2 = zooms()
    still = Image.open(DIR / (STILL3 if V3 else STILL)).convert("RGB")
    n = len(frames(full))
    result = [np.asarray(cut(still, *fit[i])) for i in range(CUT or n)]
    if CUT:
        shot2 = Image.open(SHOT2).convert('RGB')
        result += [np.asarray(shot2.resize((1024, 576), Image.LANCZOS))]
        result += [np.asarray(cut(shot2, s2[0], 0, 0)) for _ in range(n - CUT - 1)]
    assert len(result) == n
    silent = OUT / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(n), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(result).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = OUT / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    for k in (0, 10, 20, n - 1):
        Image.fromarray(result[k]).save(OUT / f'preview_f{k:03d}.png')
    if '--no-register' in sys.argv:
        print('PREVIEW', clip, flush=True)
        return
    runner.configure(OUT)
    check = runner.batch.validate_output(clip, n, True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    me = pathlib.Path(__file__).resolve()
    record = OUT / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), still=STILL3 if V3 else STILL,
                              zoom=np.round(fit, 4).tolist(),
                              recipe_text=((
        '原片全部 23 帧是同一张画在加速推镜头（人物与树林同比例放大，第 22 帧 2.29 倍；第 21 帧并非切镜）：用我们 liang_gptgirl_h3_v1 '
        '第 0–20 帧按推进比例拼成一张高清图，Codex 只把轮椅上的人换成千问，全部帧都按原片测得的推进从这一张图裁切。原片原音。未经 H3。'
        ) if not CUT else (
        '原片第 0–20 帧是一张画在加速推镜头（人物与树林同比例放大，第 20 帧 2.08 倍）：用我们 liang_gptgirl_h3_v1 的各帧按推进比例拼成'
        '一张高清图，Codex 只把轮椅上的人换成千问，按原片测得的推进逐帧裁切；第 21–22 帧用第 22 帧的千问关键帧并推近 '
        f'{(s2[0] - 1) * 100:.1f}%。原片原音。未经 H3。') + '\nCodex 提示词：' + PROMPT + (
        '\nv3：该静帧再由 Codex 把推轮椅的人换成动漫版马云（人设/ma_yun_v1.png）。提示词：' + PROMPT3 if V3 else ''))))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, flush=True)


if __name__ == '__main__':
    {'draw': draw_v3 if V3 else draw, 'render': render}[sys.argv[1]]()
