"""057 title on the CPU: 「呪術廻戦」 (gold outline brush logo with kana) -> 「模型回战」; the subtitle 「死滅回游 前編」 stays.

User (2026-10-01): “标题也需要重新设计”; chose 「模型回战」 and keeping the subtitle. The logo is a Codex drawing on black
(deliverables/jujutsu/标题/title_057_logo_v1.png, codex_titles_0001.py).
Per frame: find the old gold strokes (saturated yellow; the B/W city, the white subtitle and the red sky do not match), erase them by
normalized-convolution fill (the strokes are thin), and lay the new logo over the same box. The source title slowly shrinks
(about 760 -> 560 px wide over frames 0-85) and fades out by frame 100, so the box is a quadratic fit over the frames where the title
is fully visible and the opacity follows the stroke density.
"""
import json
import pathlib
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

import render_shot as runner
from common import PROD, ROOT, p

UID, REV = '057', 'title_cpu_v2'
START, END = 827, 942
LOGO = ROOT / 'deliverables/jujutsu/标题/title_057_logo_v1.png'
LABEL = '标题→「模型回战」（CPU v2：整字擦除含深色填充，新标志也加深色填充，副标题保留）'
OUT = PROD / 'shots' / UID / REV


def frames(path, vf=''):
    raw = subprocess.run([str(p.FFMPEG), '-v', 'error', '-i', str(path), *(['-vf', vf] if vf else []), '-vsync', '0',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 576, 1024, 3)


def gold(fr):
    r, g, b = (fr[..., c].astype(np.int16) for c in range(3))
    return (r > 100) & (g > 85) & (b < 0.8 * g) & (r - b > 45) & (r - g < 70)


def fill(fr, mask):
    """Replace masked pixels from their surroundings (normalized convolution, coarse to fine)."""
    out = fr.astype(np.float32)
    known = (~mask).astype(np.float32)
    filled = out.copy()
    for sigma in (12, 6, 3, 1.5):
        w = ndimage.gaussian_filter(known, sigma)
        est = np.stack([ndimage.gaussian_filter(out[..., c] * known, sigma) for c in range(3)], -1) / np.maximum(w, 1e-4)[..., None]
        ok = w > 0.05
        filled[mask & ok] = est[mask & ok]
    return filled


def logo():
    a = np.asarray(Image.open(LOGO).convert('RGB')).astype(np.float32)
    alpha = np.clip((a.max(-1) - 25) / 100, 0, 1)
    ys, xs = np.nonzero(alpha > 0.15)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    colour = np.clip(a / np.maximum(alpha, 0.05)[..., None], 0, 255)
    return colour[y0:y1, x0:x1], alpha[y0:y1, x0:x1]


def track(src):
    boxes, density = [], []
    for fr in src:
        m = gold(fr)
        ys, xs = np.nonzero(m)
        if len(xs) > 2000:
            box = [np.percentile(xs, 1), np.percentile(ys, 1), np.percentile(xs, 99), np.percentile(ys, 99)]
            boxes.append(box)
            density.append(m.sum() / ((box[2] - box[0]) * (box[3] - box[1])))
        else:
            boxes.append(None)
            density.append(0.0)
    n = np.arange(len(src))
    full = [i for i, b in enumerate(boxes) if b is not None and i <= 85]
    fit = [np.polyval(np.polyfit(full, [boxes[i][k] for i in full], 2), n) for k in range(4)]
    ref = np.median([density[i] for i in full])
    opacity = np.clip(np.array(density) / ref, 0, 1)
    opacity[:86] = 1.0  # fully visible while the box is fitted; follow the measured fade afterwards
    opacity = ndimage.uniform_filter1d(opacity, 3)
    return np.stack(fit, 1), opacity


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    inv = json.loads((PROD / 'source_inventory/inventory.json').read_text(encoding='utf-8'))
    fps = 24000 / 1001
    full = OUT / 'source_exact_with_audio.mp4'
    if not full.exists():
        p.run([p.FFMPEG, '-v', 'error', '-y', '-i', inv['source'], '-map', '0:v:0', '-map', '0:a:0',
               '-vf', f'trim=start_frame={START}:end_frame={END},setpts=PTS-STARTPTS,scale=1024:576:flags=lanczos,setsar=1,format=yuv420p',
               '-af', f'atrim=start={START / fps:.9f}:end={END / fps:.9f},asetpts=PTS-STARTPTS',
               '-r', '24000/1001', '-c:v', 'libx264', '-crf', '12', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', full])
    src = frames(full)
    assert len(src) == END - START, len(src)
    box, opacity = track(src)
    colour, alpha = logo()
    # v2, the user: “057是你用算法把原版的字去掉的吗？没有去完整，特别是后面几帧”. The old glyphs are gold outlines with a dark brown
    # fill; v1 erased only the gold outline, so the fill stayed as a dark shadow (plain to see on the red sky at the end) and the fading
    # frames, whose outline is too faint to detect, kept even more. Now the whole glyph (outline + fill) is taken from a clear frame,
    # moved along the fitted box into every frame, and erased; the new logo gets the same dark fill inside its strokes.
    T0 = 40
    g0 = gold(src[T0])
    glyph0 = ndimage.binary_fill_holes(ndimage.binary_closing(g0, iterations=4)) | g0
    glyph0 = ndimage.binary_dilation(glyph0, iterations=2)
    ink = np.median(src[T0][glyph0 & ~ndimage.binary_dilation(g0, iterations=2)], axis=0).astype(np.float32)
    gy, gx = np.nonzero(glyph0)
    gy0, gy1, gx0, gx1 = gy.min(), gy.max() + 1, gx.min(), gx.max() + 1
    tmpl = Image.fromarray((glyph0[gy0:gy1, gx0:gx1] * 255).astype(np.uint8))
    outline = alpha > 0.15
    inside = ndimage.binary_fill_holes(ndimage.binary_closing(outline, iterations=2)) & ~outline
    colour = np.where(inside[..., None], ink, colour)
    alpha = np.where(inside, 1.0, alpha)
    result = []
    for i, fr in enumerate(src):
        mask = ndimage.binary_dilation(gold(fr), iterations=2)
        if opacity[i] > 0.01 or mask.sum() > 200:
            s = (box[i][2] - box[i][0]) / (box[T0][2] - box[T0][0])
            W, H = max(1, round((gx1 - gx0) * s)), max(1, round((gy1 - gy0) * s))
            X, Y = round(box[i][0] + (gx0 - box[T0][0]) * s), round(box[i][1] + (gy0 - box[T0][1]) * s)
            warped = np.asarray(tmpl.resize((W, H), Image.NEAREST)) > 127
            ys0, xs0 = max(Y, 0), max(X, 0)
            ys1, xs1 = min(Y + H, 576), min(X + W, 1024)
            if ys1 > ys0 and xs1 > xs0:
                mask[ys0:ys1, xs0:xs1] |= warped[ys0 - Y:ys1 - Y, xs0 - X:xs1 - X]
            mask = ndimage.binary_dilation(mask, iterations=1)
        out = fill(fr, mask) if mask.any() else fr.astype(np.float32)
        x0, y0, x1, y1 = box[i]
        if opacity[i] > 0.01:
            w = x1 - x0
            h = w * alpha.shape[0] / alpha.shape[1]
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            W, H = max(1, round(w)), max(1, round(h))
            c = np.asarray(Image.fromarray(colour.astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(np.float32)
            a = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(np.float32) / 255 * opacity[i]
            X, Y = round(cx - W / 2), round(cy - H / 2)
            sx0, sy0 = max(0, -X), max(0, -Y)
            dx0, dy0 = max(0, X), max(0, Y)
            dx1, dy1 = min(1024, X + W), min(576, Y + H)
            if dx1 > dx0 and dy1 > dy0:
                cc = c[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0]
                aa = a[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0, None]
                out[dy0:dy1, dx0:dx1] = out[dy0:dy1, dx0:dx1] * (1 - aa) + cc * aa
        result.append(np.clip(out, 0, 255).astype(np.uint8))
    silent = OUT / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(END - START), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(result).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = OUT / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    runner.configure(OUT)
    check = runner.batch.validate_output(clip, END - START, True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    record = OUT / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(pathlib.Path(__file__).resolve()), builder_sha256=p.sha(pathlib.Path(__file__).resolve()),
                              recipe_text=f'原标题「呪術廻戦」整字擦除（金色描边＋深棕填充，取第 40 帧整字形状按拟合框逐帧缩放平移，淡出帧也擦），新标志笔画内同样填深棕色；叠 Codex 画的「模型回战」新标志（{LOGO.name}），位置与大小按原标题逐帧拟合，淡出跟随原标题；副标题「死滅回游 前編」和背景未动。未经 H3。'))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    for k in (40, 88, 96):
        Image.fromarray(result[k]).save(OUT / f'preview_f{k:03d}.png')
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if '--no-register' not in sys.argv and not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, 'opacity fade frames', [int(i) for i in np.nonzero(opacity < 0.99)[0]][:20], flush=True)


if __name__ == '__main__':
    main()
