"""057 title v3: the title 「模型回战」 and the subtitle 「死滅回游 前編」 laid over H3's text-free clip (render_057_kf.py).

User (2026-10-02): “让模型去掉字，直接你来写？” - H3 removes all text, so nothing has to be erased; this only composites.
- Title: one fixed drawing (title_057_logo_v1.png, the dark fill inside its strokes as in v2), placed on title_057.track()'s fitted box.
- Subtitle: set in Yu Mincho Demibold on the six glyph cells found at source frame 40 (against the text-free keyframe of that frame,
  kf_057_f040_clean_v2.png), moved and scaled with the title box.
- Opacity: the title fade measured on the source as the colour contrast between the old glyph outline and a ring around it (v2 used
  the gold-pixel count, which drops to zero at frame 98 while the title is still faintly there until frame 100); the subtitle's
  fade-in is measured the same way on its own glyphs.
Used as render_shot's POSTPROCESSORS['057']; `python title_057_v3.py <job dir>` reruns it on an existing H3 job without registering.
"""
import json
import pathlib
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

from common import PROD, ROOT, p
from title_057 import LOGO, frames, gold, logo, track

UID = '057'
T0 = 40
CLEAN40 = ROOT / 'deliverables/jujutsu/关键帧/kf_057_f040_clean_v2.png'
FONT = Path(r'C:\Windows\Fonts\yumindb.ttf')
SUB = '死滅回游前編'


def warp(mask_crop, origin, box, i):
    """Place a crop taken at frame T0 (top-left `origin`) into frame i, following the fitted title box."""
    s = (box[i][2] - box[i][0]) / (box[T0][2] - box[T0][0])
    h, w = mask_crop.shape[:2]
    W, H = max(1, round(w * s)), max(1, round(h * s))
    X, Y = round(box[i][0] + (origin[0] - box[T0][0]) * s), round(box[i][1] + (origin[1] - box[T0][1]) * s)
    return X, Y, W, H


def paste(out, X, Y, colour, alpha):
    H, W = alpha.shape
    sx0, sy0 = max(0, -X), max(0, -Y)
    dx0, dy0, dx1, dy1 = max(0, X), max(0, Y), min(1024, X + W), min(576, Y + H)
    if dx1 > dx0 and dy1 > dy0:
        c = colour[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0]
        a = alpha[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0, None]
        out[dy0:dy1, dx0:dx1] = out[dy0:dy1, dx0:dx1] * (1 - a) + c * a


def resized(arr, W, H, nearest=False):
    mode = Image.NEAREST if nearest else Image.LANCZOS
    if arr.ndim == 2:
        return np.asarray(Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).resize((W, H), mode)).astype(np.float32) / 255
    return np.asarray(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize((W, H), mode)).astype(np.float32)


def contrast(fr, mask):
    ring = ndimage.binary_dilation(mask, iterations=6) & ~ndimage.binary_dilation(mask, iterations=2)
    f = fr.astype(np.float32)
    return float(np.linalg.norm(f[mask].mean(0) - f[ring].mean(0))) if mask.any() and ring.any() else 0.0


def visibility(src, box, crop, origin, first, last, absent):
    """Per-frame visibility of a T0 glyph mask: its outline contrast, from the median over the frames `absent` (the text not there
    yet or any more: the contrast of the background alone) to the median over frames first..last (fully there)."""
    c = []
    for i in range(len(src)):
        X, Y, W, H = warp(crop, origin, box, i)
        m = np.zeros((576, 1024), np.float32)
        paste(m[..., None], X, Y, np.ones((H, W, 1), np.float32), resized(crop.astype(np.float32), W, H, nearest=True))
        c.append(contrast(src[i], m > 0.5))
    c = np.array(c)
    floor = np.median(c[absent[0]:absent[1] + 1])
    return np.clip(ndimage.uniform_filter1d((c - floor) / (np.median(c[first:last + 1]) - floor), 3), 0, 1), c


def subtitle_matte(src40, clean40, title_box):
    """The white subtitle glyphs at frame T0: brighter than the text-free plate, in the band under the title."""
    x0, y0, x1, y1 = (round(v) for v in title_box)
    band = np.zeros((576, 1024), bool)
    band[y1 + 2:min(y1 + 110, 576), x0:x1] = True
    s, c = src40.astype(np.float32), clean40.astype(np.float32)
    d = s.min(-1) - c.min(-1)
    core = band & (s.min(-1) > 190) & (d > 40)
    lab, n = ndimage.label(ndimage.binary_dilation(core, iterations=1))
    sizes = ndimage.sum(core, lab, range(1, n + 1))
    core &= np.isin(lab, [k + 1 for k, z in enumerate(sizes) if z >= 6])  # specks of the city that Codex redrew are not glyphs
    # The matte itself also catches city whites that Codex redrew darker (the camera moves, so frames cannot be differenced either);
    # it is used only to locate the six glyph cells - its columns split cleanly into six runs - and the glyphs are set in Yu Mincho
    # Demibold, each centred on its run, ink top on the matte's top row, white like the source's text.
    cols = core.sum(0) > 0
    runs, start = [], None
    for x in range(1025):
        on = x < 1024 and cols[x]
        if on and start is None:
            start = x
        if not on and start is not None:
            if x - start >= 20:
                runs.append((start, x))
            start = None
    assert len(runs) == len(SUB), runs
    top = int(np.nonzero(core.any(1))[0].min())
    white = np.median(s[core], axis=0)
    size = round(np.median([b - a for a, b in runs]) * 1.08)  # ink about 92 % of the em
    font = ImageFont.truetype(str(FONT), size * 4)
    glyphs = []
    for ch in SUB:
        im = Image.new('L', (size * 8, size * 8), 0)
        ImageDraw.Draw(im).text((size * 4, size * 4), ch, font=font, fill=255, anchor='mm')
        a = np.asarray(im.resize((size * 2, size * 2), Image.LANCZOS)).astype(np.float32) / 255
        ys, xs = np.nonzero(a > 0.05)
        glyphs.append((a, xs.min(), xs.max() + 1, ys.min()))
    ink_top = min(g[3] for g in glyphs)
    X0, X1 = runs[0][0] - 4, runs[-1][1] + 4
    canvas = np.zeros((size * 2, X1 - X0), np.float32)
    for (a, ix0, ix1, _), (r0, r1) in zip(glyphs, runs):
        x = round((r0 + r1) / 2 - (ix0 + ix1) / 2) - X0
        crop = a[ink_top:, max(0, -x):]
        x = max(x, 0)
        w = min(crop.shape[1], canvas.shape[1] - x)
        canvas[:crop.shape[0], x:x + w] = np.maximum(canvas[:crop.shape[0], x:x + w], crop[:, :w])
    ys = np.nonzero(canvas.max(1) > 0.05)[0]
    alpha = canvas[:ys.max() + 2]
    return np.full(alpha.shape + (3,), white, np.float32), alpha, (X0, top)


def composite(src, base, clean40):
    box, _ = track(src)
    colour, alpha = logo()
    # the title glyphs at T0 (outline + fill) for the visibility measurement
    g0 = gold(src[T0])
    glyph0 = ndimage.binary_fill_holes(ndimage.binary_closing(g0, iterations=4)) | g0
    gy, gx = np.nonzero(g0)
    tcrop, torigin = g0[gy.min():gy.max() + 1, gx.min():gx.max() + 1], (gx.min(), gy.min())
    title_vis, title_c = visibility(src, box, tcrop, torigin, 76, 86, (104, 114))
    title_vis[:86] = 1.0
    title_vis = np.minimum.accumulate(title_vis)  # the title only fades out
    ink = np.median(src[T0][ndimage.binary_dilation(glyph0, iterations=2) & ~ndimage.binary_dilation(g0, iterations=2)], axis=0).astype(np.float32)
    outline = alpha > 0.15
    inside = ndimage.binary_fill_holes(ndimage.binary_closing(outline, iterations=2)) & ~outline
    colour = np.where(inside[..., None], ink, colour)
    alpha = np.where(inside, 1.0, alpha)
    scol, salpha, sorigin = subtitle_matte(src[T0], clean40, box[T0])
    sub_vis, sub_c = visibility(src, box, salpha > 0.5, sorigin, 36, 44, (0, 4))
    on = int(np.argmax(sub_vis > 0.5))  # the first frame the subtitle is half there
    sub_vis[on + 8:] = np.maximum(sub_vis[on + 8:], 1.0)  # fully there after its fade-in ...
    sub_vis[86:] = np.minimum(sub_vis[86:], title_vis[86:])  # ... until it fades out with the title
    result = []
    for i, fr in enumerate(base):
        out = fr.astype(np.float32)
        if title_vis[i] > 0.03:
            x0, y0, x1, y1 = box[i]
            W = max(1, round(x1 - x0))
            H = max(1, round(W * alpha.shape[0] / alpha.shape[1]))
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            paste(out, round(cx - W / 2), round(cy - H / 2), resized(colour, W, H), resized(alpha, W, H) * title_vis[i])
        if sub_vis[i] > 0.03:
            X, Y, W, H = warp(salpha, sorigin, box, i)
            paste(out, X, Y, resized(scol, W, H), resized(salpha, W, H) * sub_vis[i])
        result.append(np.clip(out, 0, 255).astype(np.uint8))
    return result, dict(title_visibility=[round(float(v), 3) for v in title_vis], title_contrast=[round(float(v), 1) for v in title_c],
                        subtitle_visibility=[round(float(v), 3) for v in sub_vis], subtitle_contrast=[round(float(v), 1) for v in sub_c],
                        subtitle_px=int((salpha > 0.5).sum()), subtitle_first_half_visible=on)


def postprocess(job, visual, n):
    job = pathlib.Path(job)
    src = frames(job / 'source_exact_with_audio.mp4')
    base = frames(visual)
    assert len(src) == len(base) == int(n), (len(src), len(base), n)
    clean40 = np.asarray(Image.open(CLEAN40).convert('RGB').resize((1024, 576), Image.LANCZOS))
    result, measured = composite(src, base, clean40)
    out = job / 'titled_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(result)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(out)],
                          input=np.stack(result).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    me = pathlib.Path(__file__).resolve()
    p.write_json(job / 'title_compositing.json', dict(
        kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), base=str(visual), logo=str(LOGO), subtitle_plate=str(CLEAN40),
        recipe_text='H3 生成无字底片（关键帧去字）；叠 Codex 画的「模型回战」标志（同一张图，笔画内填深棕色），位置大小按原标题逐帧拟合；'
                    '副标题「死滅回游 前編」用游明朝 Demibold 按原片第 40 帧测得的六个字位排字，随标题框缩放；淡入淡出按原片字形轮廓对比度逐帧测量。',
        **measured))
    for k in (0, 40, 88, 96):
        Image.fromarray(result[k]).save(job / f'preview_f{k:03d}.png')
    return out


if __name__ == '__main__':
    job = pathlib.Path(sys.argv[1])
    print('WROTE', postprocess(job, job / 'native_fullframe.mp4', len(frames(job / 'source_exact_with_audio.mp4'))))
    print(json.dumps({k: v for k, v in json.loads((job / 'title_compositing.json').read_text(encoding='utf-8')).items()
                      if k in ('subtitle_px', 'subtitle_first_half_visible')}))
