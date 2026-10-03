"""090 with the 040 method: the Klimt pan redrawn by Codex and panned on the CPU; the bomb shot after it kept from the approved run.

User (2026-10-02 14:20): “我觉得090也要按照040的方法制作”. Measured: frames 0-15 are one constant vertical pan (-48.9 px per
frame, phase-correlation peaks 0.4-0.6); frames 16-24 are the bomb shot (not a pan), taken as they are from gpt6_klimt_bomb_h3_v3.
Usage: pan_090.py mosaic | codex | render [--no-register]
"""
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

UID, REV = '090', 'pan_codex_v4'
RUN = PROD / 'shots/090/gpt6_klimt_bomb_h3_v3'
SRC = RUN / 'source_exact_with_audio.mp4'
OUT = PROD / 'shots' / UID / REV
DIR = ROOT / 'deliverables/jujutsu/静帧'
PAN = (0, 16)
GPT = ROOT / 'deliverables/jujutsu/人设/gpt_yuta_v6.png'
PAINT_SRC, PAINT_NEW = DIR / 'pan_090_painting_src.png', DIR / 'pan_090_painting_gpt_v2.png'
# v2, the user on v1: “090可以把gpt的下半身变成她的制服，而不是名画的原始设计吗？否则人物辨识度不够” - her whole outfit is her uniform
LABEL = '乙骨→GPT·克林姆特《吻》（v4：GPT 全身换成她的制服、后面落下的炸弹换成 GTX 690；040 的方法：整幅画由 Codex 重画、按原片竖直摇镜头逐帧平移；后面炸弹一幕沿用已通过的版本；未经 H3）'
PROMPT = ('Image 1 is a tall painting in the style of Gustav Klimt (The Kiss), from an anime opening: gold mosaic patterns and flat '
          'ornaments, a young man with short black hair held in an embrace by a dark curse creature, both wrapped in patterned golden '
          'robes. Redraw the young man as the girl of Image 2 (GPT): very long wavy white hair with a small ahoge and a small white '
          'knot-shaped hair ornament, lavender eyes - in exactly his pose, place and size, held the same way by the creature, wrapped in '
          'the same golden robes, painted in exactly the same Klimt gold-mosaic style, outlines and colours as the rest of the painting. '
          'Her WHOLE outfit, head to toe, is her own uniform from Image 2 - the off-white blazer with the black sailor collar and white '
          'stripes, the dark green tie, the short black pleated skirt with white stripes, black socks and black shoes - drawn as part of '
          'the Klimt painting with gold-mosaic patterns worked into it; nothing of the original trousers or sneakers remains, and her '
          'legs below the skirt follow the pose of his legs. '
          'Keep the dark curse creature, the ornaments, the gold patterns, the composition and everything else exactly as in Image 1. '
          'The output is a portrait image with the same framing and aspect as Image 1. No text, no signature. Do not create or modify '
          'any other files.')


# v3, the user: “090后半段有一个炸弹落下的镜头没处理。应该是丢下一个GTX690。你上网搜索一下这个型号的照片。” and then a photo
# (assets/人设/gtx690_user_photo.png; no GTX 690 picture on Wikimedia Commons). The bomb of frames 16-24 (approved run) is covered by
# a Codex sprite of the card, tracked on the bomb (bluish grey against the red streaks) and lit like it.
GPU_PHOTO = ROOT / 'assets/人设/gtx690_user_photo.png'
GPU_SPRITE = DIR / 'gtx690_falling_v1.png'
GPU_PROMPT = ('Image 1 is a photo of an NVIDIA GeForce GTX 690 graphics card. Draw that exact card as a clean 2D anime illustration '
              'with crisp outlines and cel shading: its silver metal shroud, the single black fan in the middle and the two windows over '
              'the fin stacks on either side, falling straight down - the card stands VERTICALLY with its long axis up and down, the '
              'bracket end at the top, the other end pointing down, seen face-on so the fan and both windows are clearly visible. A '
              'tall portrait image, the card filling most of the height. Background: flat pure magenta (#FF00FF) everywhere, no shadow, '
              'no text, no logos. Do not create or modify any other files.')


def gpu_sprite():
    if not GPU_SPRITE.exists():
        args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
                '-o', str(DIR / f'codex_last_message_{GPU_SPRITE.stem}.txt'), '-i', str(GPU_PHOTO), '--',
                f'Use your image generation tool to create ONE image and save it in the current directory as {GPU_SPRITE.name}. {GPU_PROMPT}']
        subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
        print('done' if GPU_SPRITE.exists() else 'FAILED', GPU_SPRITE.name, flush=True)
    a = np.asarray(Image.open(GPU_SPRITE).convert('RGB')).astype(np.float32)
    alpha = np.clip((np.linalg.norm(a - np.array([255, 0, 255], np.float32), axis=-1) - 60) / 80, 0, 1)
    ys, xs = np.nonzero(alpha > 0.5)
    a, alpha = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], alpha[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    a = np.where(alpha[..., None] < 1, a - np.array([255, 0, 255], np.float32) * (1 - alpha[..., None]) * 0.6, a)
    return np.clip(a, 0, 255), alpha


def bomb_track(run):
    """Centre and height of the bomb in frames 16-24: measured where it is large (16-21), log-linear fit for its fall."""
    from scipy import ndimage
    pts = []
    for i in range(PAN[1], len(run)):
        f = run[i].astype(np.float32)
        m = (f[..., 2] >= 0.9 * f[..., 0]) & (f.max(-1) > 45)
        lab, n = ndimage.label(ndimage.binary_closing(m, iterations=2))
        if not n:
            continue
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        if sizes.max() < 1500:
            continue
        ys, xs = np.nonzero(lab == int(np.argmax(sizes)) + 1)
        pts.append((i, (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2, ys.max() - ys.min() + 1, f[lab == int(np.argmax(sizes)) + 1].mean(0)))
    fs = np.array([q[0] for q in pts], np.float32)
    kx, cx = np.polyfit(fs, [q[1] for q in pts], 1)
    ky, cy = np.polyfit(fs, [q[2] for q in pts], 1)
    kh, ch = np.polyfit(fs, np.log([q[3] for q in pts]), 1)
    colour = np.mean([q[4] for q in pts], axis=0)
    return {i: (kx * i + cx, ky * i + cy, float(np.exp(kh * i + ch))) for i in range(PAN[1], len(run))}, colour, pts


def tops_and_height():
    src = frames(SRC)
    a, b = PAN
    dy = float(np.median([shift(src[i - 1], src[i])[0] for i in range(a + 1, b)]))
    tops = np.array([(i - a) * dy for i in range(a, b)])
    tops -= tops.min()
    return src, tops, int(np.ceil(tops.max())) + 576, dy


def mosaic():
    src, tops, height, dy = tops_and_height()
    a, b = PAN
    stack = np.full((b - a, height, 1024, 3), np.nan, np.float32)
    for j, i in enumerate(range(a, b)):
        t = int(round(tops[j]))
        stack[j, t:t + 576] = src[i]
    paint = np.nanmedian(stack, axis=0)
    Image.fromarray(np.clip(paint, 0, 255).astype(np.uint8)).save(PAINT_SRC)
    err = [float(np.abs(paint[int(round(tops[j])):int(round(tops[j])) + 576] - src[i]).mean()) for j, i in enumerate(range(a, b))]
    print('dy %.2f height %d reprojection error' % (dy, height), [round(e, 1) for e in err], flush=True)


def codex():
    if PAINT_NEW.exists():
        return
    src = Image.open(PAINT_SRC)
    w, h = src.size
    pad = max(0, round(w * 1.5) - h)
    arr = np.asarray(src)
    padded = np.pad(arr, ((pad // 2, pad - pad // 2), (0, 0), (0, 0)), mode='reflect') if pad else arr
    inp = DIR / 'pan_090_painting_src_2x3.png'
    Image.fromarray(padded).save(inp)
    args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
            '-o', str(DIR / f'codex_last_message_{PAINT_NEW.stem}.txt'), '-i', str(inp), '-i', str(GPT), '--',
            f'Use your image generation tool to create ONE image and save it in the current directory as {PAINT_NEW.name}. {PROMPT}']
    t = time.time()
    subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
    print('done' if PAINT_NEW.exists() else 'FAILED', PAINT_NEW.name, f'{time.time() - t:.0f} s', 'pad', pad, flush=True)


def render():
    src, tops, height, dy = tops_and_height()
    w = 1024
    pad = max(0, round(w * 1.5) - height)
    new = Image.open(PAINT_NEW).convert('RGB').resize((w, height + pad), Image.LANCZOS)
    new = np.asarray(new, np.float32)[pad // 2:pad // 2 + height]
    result = []
    for t in tops:
        y0 = int(np.floor(t))
        f = t - y0
        y1 = min(y0 + 1, height - 576)
        result.append(np.clip(new[y0:y0 + 576] * (1 - f) + new[y1:y1 + 576] * f, 0, 255).astype(np.uint8))
    run = frames(RUN / 'native_fullframe.mp4')
    rgb, al = gpu_sprite()
    track, bomb_colour, pts = bomb_track(run)
    tone = np.clip(bomb_colour / np.maximum(rgb[al > 0.5].mean(0), 1), 0.3, 1.2)
    print('bomb measured on frames', [q[0] for q in pts], 'tone', tone.round(2), flush=True)
    from scipy import ndimage
    for i in range(PAN[1], len(src)):
        frame = run[i].astype(np.float32)
        x, y, h = track[i]
        # erase the whole bomb first (its fins showed above the card in the small late frames): inside a box around the track, every
        # pixel that is not red-dominated (the bomb is neutral or bluish grey, the streaks are red even where dark), filled from the
        # streaks around it
        box = np.zeros((576, 1024), bool)
        bx0, bx1 = int(max(0, x - 0.35 * h - 8)), int(min(1024, x + 0.35 * h + 8))
        by0, by1 = int(max(0, y - 1.4 * h - 10)), int(min(576, y + 0.9 * h + 8))
        box[by0:by1, bx0:bx1] = True
        lum = frame @ np.array([0.299, 0.587, 0.114], np.float32)
        level = np.percentile(lum[box], 75)
        # the body is neutral grey; the fins are shaded dark red - both are much darker than the streaks around them, or not red
        bomb = box & ((lum < 0.72 * level) | ((frame[..., 0] - np.maximum(frame[..., 1], frame[..., 2])) < 25))
        lab, n = ndimage.label(ndimage.binary_closing(bomb, iterations=2))
        if n:
            sizes = ndimage.sum(np.ones_like(bomb), lab, range(1, n + 1))
            bomb = lab == int(np.argmax(sizes)) + 1
            ys_b, xs_b = np.nonzero(bomb)
            if ys_b.max() - ys_b.min() + 1 > 0.8 * h:  # the whole bomb found: place the card on it
                x, y = (xs_b.min() + xs_b.max()) / 2, (ys_b.min() + ys_b.max()) / 2 + 0.04 * h
                h = (ys_b.max() - ys_b.min() + 1 - 12) / 1.45
        bomb = ndimage.binary_dilation(bomb, iterations=3)
        if bomb.any():
            # fine to coarse, each pixel filled by the smallest blur that reaches known streaks (a coarse-last loop left the middle
            # of a large hole black)
            known = (~bomb).astype(np.float32)
            est, todo = frame.copy(), bomb.copy()
            for sigma in (4, 8, 16, 32, 64):
                wgt = ndimage.gaussian_filter(known, sigma)
                e = np.stack([ndimage.gaussian_filter(frame[..., ch] * known, sigma) for ch in range(3)], -1) / np.maximum(wgt, 1e-6)[..., None]
                ok = todo & (wgt > (0.15 if sigma < 64 else 1e-4))
                est[ok] = e[ok]
                todo &= ~ok
            frame = est
        # the track measures the bomb's body only; its tail fins above and nose below make it ~1.4x as long (frame 16: 64-533
        # against a body of 145-479), so the card is sized and centred on the whole bomb
        H = max(4, round(h * 1.45 + 12))  # + a fixed margin: the tiny late frames under-measure the bomb
        y = y - 0.04 * h
        W = max(2, round(H * rgb.shape[1] / rgb.shape[0]))
        c = np.asarray(Image.fromarray(rgb.astype(np.uint8)).resize((W, H), Image.LANCZOS), np.float32) * tone
        a = np.asarray(Image.fromarray((al * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS), np.float32)[..., None] / 255
        X, Y = round(x - W / 2), round(y - H / 2)
        sx0, sy0, dx0, dy0 = max(0, -X), max(0, -Y), max(0, X), max(0, Y)
        dx1, dy1 = min(1024, X + W), min(576, Y + H)
        if dx1 > dx0 and dy1 > dy0:
            cc, aa = c[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0], a[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0]
            frame[dy0:dy1, dx0:dx1] = frame[dy0:dy1, dx0:dx1] * (1 - aa) + cc * aa
        result.append(np.clip(frame, 0, 255).astype(np.uint8))
    assert len(result) == len(src)
    OUT.mkdir(parents=True, exist_ok=True)
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
    if '--no-register' in sys.argv:
        print('PREVIEW', clip, flush=True)
        return
    runner.configure(OUT)
    check = runner.batch.validate_output(clip, len(result), True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    me = pathlib.Path(__file__).resolve()
    record = OUT / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), painting=str(PAINT_NEW), recipe_text=(
        f'第 0–15 帧：原片是匀速竖直摇镜头（每帧 {dy:.1f} 像素），拼成整幅画后由 Codex 重画（乙骨→GPT v6，克林姆特金色马赛克画风，'
        '黑沐死保留），按原轨迹逐帧裁切；第 16–24 帧（炸弹）沿用已通过的 gpt6_klimt_bomb_h3_v3。原片原音。')))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, flush=True)


if __name__ == '__main__':
    {'mosaic': mosaic, 'codex': codex, 'render': render}[sys.argv[1]]()
