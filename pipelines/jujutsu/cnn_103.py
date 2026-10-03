"""103: a convolutional network drawn in code over the source's dark red sky (CPU; no H3).

User (2026-10-02 02:09, note on 103): “……也许可以做一个象征着convolution neural network的镜头？……如果模型效果不好，你可以自己用GPT画
一个背景，然后自己用代码做特效。” and on cnn_kf_h3_v1 (10:58): “没有卷曲网络的感觉。卷曲网络应该是从大到小的。”
The source: a small cyan card (frame 0) swings toward the camera and opens into a fan of glass panes receding to the lower right
(frames 1-7), then drifts. Here the card opens into six feature maps that really shrink layer by layer (470 -> 120 px high) while
their channel stacks thicken (1 -> 10 slices) and their grids coarsen; the first map is the input image (the sky behind it,
pixelated); from frame 8 a bright 3x3 kernel slides over it with rays to one cell of the next map. Background: source frame 0 with
the card filled in from its surroundings.
Usage: cnn_103.py [--no-register]
"""
import pathlib
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

import render_shot as runner
from common import PROD, p
from title_057 import fill, frames

UID, REV = '103', 'cnn_code_v6'
SRC = PROD / 'shots/103/cnn_kf_h3_v1/source_exact_with_audio.mp4'
LABEL = '玻璃片→卷积神经网络（代码绘制 v6：照原片第 12 帧对齐——板子侧边向左下斜、底边齐平、顶边向右下逐块降低，全部留在画面内；特征图由大到小、通道由少到多，卷积窗滑动；背景用原片；未经 H3）'
SS = 2  # supersampling
# final layout (frame 8 on): centre x, centre y, height, channel slices, cells per side
LAYERS = [(235, 285, 420, 1, 16), (495, 315, 340, 3, 12), (665, 345, 265, 4, 9), (790, 372, 200, 6, 7), (880, 398, 148, 8, 5),
          (948, 420, 105, 10, 4)]
CYAN = np.array([90, 235, 230], np.float32)
CARD = (840, 340)  # where the small card is in frame 0


def plate(src0):
    """Source frame 0 without the cyan card."""
    f = src0.astype(np.float32)
    card = (f[..., 1] > f[..., 0] + 40) & (f[..., 2] > f[..., 0] + 30) & (f[..., 1] > 90)
    # the card, its white rim, dark backing plate and faint glow: one ellipse around the cyan face, grown by 45 px (the glow and
    # the plate are too close to the dark sky to threshold), filled smoothly from the sky around it and feathered in
    ys, xs = np.nonzero(card)
    cy, cx = (ys.min() + ys.max()) / 2, (xs.min() + xs.max()) / 2
    ry, rx = (ys.max() - ys.min()) / 2 + 45, (xs.max() - xs.min()) / 2 + 45
    yy, xx = np.mgrid[0:576, 0:1024]
    hole = ((yy - cy) / ry) ** 2 + ((xx - cx) / rx) ** 2 <= 1
    known = (~hole).astype(np.float32)
    est = f.copy()
    for sigma in (80, 40):
        w = ndimage.gaussian_filter(known, sigma)
        e = np.stack([ndimage.gaussian_filter(f[..., c] * known, sigma) for c in range(3)], -1) / np.maximum(w, 1e-6)[..., None]
        est[hole] = e[hole]
    blend = ndimage.gaussian_filter(hole.astype(np.float32), 8)[..., None]
    return f * (1 - blend) + est * blend


def activations(n, seed):
    rng = np.random.default_rng(seed)
    a = ndimage.gaussian_filter(rng.random((n, n)), 0.9)
    a = (a - a.min()) / (np.ptp(a) + 1e-6)
    return a ** 1.6


# v3, the user on v2 (one perspective warp of the flat drawing): “这也太怪了，角度和原片不一样，显得好大好胖。我觉得应该更加“侧”过来” -
# like the source's glass panes, every map is its own plane turned well to the side: a narrow quad whose near (left) edge is
# taller than its far (right) edge, the maps stepping to the right and down, each smaller than the one before.
SIDE = 0.5    # apparent width / frontal width (the plane is turned about 60 degrees)
FAR = 0.8     # far edge height / near edge height
DROP = 0.06   # the far edge sits a little lower (the fan bends down to the right)
# per map: near-edge x, centre y, height, channel slices, cells per side (frame 8 on)
SIDE_LAYERS = [(130, 280, 430, 1, 16), (340, 300, 350, 3, 12), (505, 325, 275, 4, 9), (640, 350, 210, 6, 7), (750, 372, 155, 8, 5),
               (840, 392, 112, 10, 4)]


def quad(xn, cy, h):
    """Corners of a map turned to the side: near-top, far-top, far-bottom, near-bottom."""
    w = h * 0.78 * SIDE
    hf = h * FAR
    yc_far = cy + h * DROP
    return [(xn, cy - h / 2), (xn + w, yc_far - hf / 2), (xn + w, yc_far + hf / 2), (xn, cy + h / 2)]


def at(q, u, v):
    """Point at (u across, v down) in the quad, bilinear."""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = q
    top = (x0 + (x1 - x0) * u, y0 + (y1 - y0) * u)
    bot = (x3 + (x2 - x3) * u, y3 + (y2 - y3) * u)
    return top[0] + (bot[0] - top[0]) * v, top[1] + (bot[1] - top[1]) * v


def cell_poly(q, i, j, n, m=None):
    m = m or n
    return [tuple(c * SS for c in at(q, a / n, b / m)) for a, b in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))]


def draw_layer(draw, glow, xn, cy, h, slices, cells, k, t_appear, sky):
    """One feature map turned to the side: its channel slices step back to the right, each a grid of activation cells."""
    w = h * 0.78 * SIDE
    step = max(5, w * 0.12)
    for s in range(slices - 1, -1, -1):
        q = quad(xn + s * step, cy - s * step * 0.15, h)
        a = t_appear * (0.55 if s else 1.0)
        if k == 0 and s == 0:
            for i in range(cells):
                for j in range(cells):
                    v = sky[min(j * sky.shape[0] // cells, sky.shape[0] - 1), min(i * sky.shape[1] // cells, sky.shape[1] - 1)]
                    c = tuple(int(x) for x in np.clip(CYAN * (0.25 + 0.75 * v), 0, 255)) + (int(150 * a),)
                    draw.polygon(cell_poly(q, i, j, cells), fill=c)
        else:
            act = activations(cells, 1000 * k + s)
            for i in range(cells):
                for j in range(cells):
                    c = tuple(int(x) for x in np.clip(CYAN * (0.15 + 0.85 * act[j, i]), 0, 255)) + (int(110 * a),)
                    draw.polygon(cell_poly(q, i, j, cells), fill=c)
        grid = tuple(int(x) for x in CYAN) + (int(70 * a),)
        for t in range(cells + 1):
            draw.line([tuple(c * SS for c in at(q, t / cells, 0)), tuple(c * SS for c in at(q, t / cells, 1))], fill=grid, width=SS)
            draw.line([tuple(c * SS for c in at(q, 0, t / cells)), tuple(c * SS for c in at(q, 1, t / cells))], fill=grid, width=SS)
        edge = tuple(int(x) for x in CYAN) + (int(230 * a),)
        outline = [tuple(c * SS for c in pt) for pt in q]
        draw.line(outline + [outline[0]], fill=edge, width=2 * SS)
        glow.line(outline + [outline[0]], fill=edge, width=4 * SS)


def placed(k, f):
    """Near-edge x, centre y and height of map k at frame f: opening from the small card (frames 0-7), then a slow drift."""
    xn, cy, h, slices, cells = SIDE_LAYERS[k]
    u = min(f / 7, 1.0)
    e = 1 - (1 - u) ** 3
    drift = 1 + 0.004 * max(f - 7, 0)
    spread = min(max(e * 1.15 - k * 0.04, 0), 1)  # the back maps follow a little later
    sc = (0.12 + 0.88 * e) * drift
    w = h * 0.78 * SIDE
    x = CARD[0] - w * sc / 2 + (xn - (CARD[0] - w * sc / 2)) * spread
    y = CARD[1] + (cy - CARD[1]) * spread
    x, y = 512 + (x - 512) * drift, 288 + (y - 288) * drift
    return x, y, h * sc, max(1, round(slices * spread)), cells, spread


# v4, the user on v3 (side-on maps; screenshot beside the source): “你不觉得这个角度很怪吗？” - the source's panes are not turned to
# the side: they face the camera, lean slightly, and recede toward a vanishing point at the lower right, packed close and
# overlapping like a fanned deck. So every pane here is the front pane scaled about that vanishing point (front pane and point
# read off the source frame), the panes grouped into layers (1, 3, 4, 6, 8, 10 channels) with small gaps between layers, and
# each layer's grid coarsens (16 -> 4 cells).
# v5, the user on v4: “板子没有显示完整。小一点，然后再稍微旋转倾斜一点？很接近了” - smaller, and leaning like the source's panes
# (top edge level, sides slanting down to the right by ~13 degrees), every pane inside the frame at every frame
# v6, the user on v5: “等下。倾斜的方向又反了！你和原片对比一下呀” - checked against source frame 12: the panes' sides slant down to
# the LEFT (bottom edge shifted left of the top edge, ~8 degrees), their bottoms stay almost level while their tops step down
# toward a vanishing point at the lower right
FRONT = [(175, 45), (465, 40), (395, 525), (100, 535)]   # top-left, top-right, bottom-right, bottom-left
VP = (960, 560)
GROUPS = [(1.0, 1, 16), (0.80, 3, 12), (0.62, 4, 9), (0.47, 6, 7), (0.35, 8, 5), (0.26, 10, 4)]  # first depth, channels, cells
CH_STEP = 0.022  # depth step between the channels of one layer


def panes():
    """(layer, channel, depth, cells) back to front."""
    out = []
    for k, (d0, ch, cells) in enumerate(GROUPS):
        for c in range(ch):
            out.append((k, c, d0 - c * CH_STEP * d0, cells))
    return sorted(out, key=lambda t: t[2])


def pane_quad(d, f):
    """The front pane scaled about the vanishing point by depth d, opened from the small card over frames 0-7."""
    u = min(f / 7, 1.0)
    e = 1 - (1 - u) ** 3
    drift = 1 + 0.004 * max(f - 7, 0)
    final = [(VP[0] + (x - VP[0]) * d, VP[1] + (y - VP[1]) * d) for x, y in FRONT]
    card = [(CARD[0] - 28 + 56 * (x > 300), CARD[1] - 42 + 84 * (y > 300)) for x, y in FRONT]
    late = min(max(e * 1.15 - (1 - d) * 0.12, 0), 1)  # the back panes follow a little later
    q = [(cx + (fx - cx) * late, cy + (fy - cy) * late) for (cx, cy), (fx, fy) in zip(card, final)]
    return [(512 + (x - 512) * drift, 288 + (y - 288) * drift) for x, y in q], late


def draw_pane(draw, glow, q, k, c, cells, a, sky):
    if k == 0:
        for i in range(cells):
            for j in range(cells):
                v = sky[min(j * sky.shape[0] // cells, sky.shape[0] - 1), min(i * sky.shape[1] // cells, sky.shape[1] - 1)]
                col = tuple(int(x) for x in np.clip(CYAN * (0.25 + 0.75 * v), 0, 255)) + (int(85 * a),)
                draw.polygon(cell_poly(q, i, j, cells), fill=col)
    else:
        act = activations(cells, 1000 * k + c)
        for i in range(cells):
            for j in range(cells):
                col = tuple(int(x) for x in np.clip(CYAN * (0.15 + 0.85 * act[j, i]), 0, 255)) + (int(75 * a),)
                draw.polygon(cell_poly(q, i, j, cells), fill=col)
    grid = tuple(int(x) for x in CYAN) + (int(55 * a),)
    for t in range(cells + 1):
        draw.line([tuple(v * SS for v in at(q, t / cells, 0)), tuple(v * SS for v in at(q, t / cells, 1))], fill=grid, width=SS)
        draw.line([tuple(v * SS for v in at(q, 0, t / cells)), tuple(v * SS for v in at(q, 1, t / cells))], fill=grid, width=SS)
    edge = (225, 255, 255, int(200 * a))
    outline = [tuple(v * SS for v in pt) for pt in q]
    draw.line(outline + [outline[0]], fill=edge, width=SS + 1)
    glow.line(outline + [outline[0]], fill=(150, 250, 245, int(200 * a)), width=4 * SS)


def frame_image(f, bg, sky):
    big = Image.new('RGBA', (1024 * SS, 576 * SS), (0, 0, 0, 0))
    halo = Image.new('RGBA', (1024 * SS, 576 * SS), (0, 0, 0, 0))
    draw, glow = ImageDraw.Draw(big), ImageDraw.Draw(halo)
    for k, c, d, cells in panes():
        q, late = pane_quad(d, f)
        if late <= 0.02 and not (k == 0 and c == 0):
            continue
        draw_pane(draw, glow, q, k, c, cells, 1.0 if k == 0 else min(1.0, late * 1.3), sky)
    if f >= 8:
        q0, _ = pane_quad(GROUPS[0][0], f)
        cells0 = GROUPS[0][2]
        pos = (f - 8) * 2
        i, j = 2 + pos % (cells0 - 5), 4 + pos // (cells0 - 5)
        win = [tuple(v * SS for v in at(q0, a_ / cells0, b_ / cells0)) for a_, b_ in ((i, j), (i + 3, j), (i + 3, j + 3), (i, j + 3))]
        q1, _ = pane_quad(GROUPS[1][0], f)
        cells1 = GROUPS[1][2]
        tj = min(j * cells1 // cells0, cells1 - 1)
        tc = at(q1, (cells1 - 1.5) / cells1, (tj + 0.5) / cells1)  # on the part of the next layer that shows right of the input
        white = (235, 255, 255, 255)
        draw.polygon(win, fill=(160, 255, 250, 90))
        draw.line(win + [win[0]], fill=white, width=3 * SS)
        glow.line(win + [win[0]], fill=white, width=8 * SS)
        for pt in win:
            draw.line([pt, (tc[0] * SS, tc[1] * SS)], fill=(200, 255, 250, 200), width=SS)
            glow.line([pt, (tc[0] * SS, tc[1] * SS)], fill=(200, 255, 250, 200), width=3 * SS)
        draw.polygon(cell_poly(q1, cells1 - 2, tj, cells1), fill=(235, 255, 255, 230))
    layer = np.asarray(big.resize((1024, 576), Image.LANCZOS), np.float32)
    halo = np.asarray(halo.resize((1024, 576), Image.LANCZOS), np.float32)
    bloom = np.stack([ndimage.gaussian_filter(halo[..., ch] * halo[..., 3] / 255, 9) for ch in range(3)], -1)
    a = layer[..., 3:4] / 255
    out = bg * (1 - a) + layer[..., :3] * a + 0.7 * bloom
    if 3 <= f <= 5:  # the source flashes brighter while the card swings open
        out = out * (1 + 0.15 * (1 - abs(f - 4)))
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    src = frames(SRC)
    bg = plate(src[0])
    lum = bg.mean(-1)
    sky = (lum - lum.min()) / (np.ptp(lum) + 1e-6)
    result = [frame_image(f, bg, sky) for f in range(len(src))]
    out = PROD / 'shots' / UID / REV
    out.mkdir(parents=True, exist_ok=True)
    full = out / 'source_exact_with_audio.mp4'
    if not full.exists():
        shutil.copy2(SRC, full)
    silent = out / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(result)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(result).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = out / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    for k in (0, 4, 8, 16):
        Image.fromarray(result[k]).save(out / f'preview_f{k:03d}.png')
    if '--no-register' in sys.argv:
        print('PREVIEW', clip, flush=True)
        return
    runner.configure(out)
    check = runner.batch.validate_output(clip, len(result), True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    me = pathlib.Path(__file__).resolve()
    record = out / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), layers=LAYERS, recipe_text=(
        '代码绘制卷积网络：原片第 0 帧去掉小卡片作背景；小卡片在第 0–7 帧展开成 6 层特征图（高 470→120 像素逐层变小、通道 1→10 逐层加厚、'
        '格子 16→4 逐层变粗），第一层是背景云纹的像素化输入图；第 8 帧起 3×3 卷积窗在输入层上逐格滑动，光线连到下一层的一个格子；'
        '青色发光＋泛光。原片原音。未经 H3。')))
    p.write_json(out / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, flush=True)


if __name__ == '__main__':
    main()
