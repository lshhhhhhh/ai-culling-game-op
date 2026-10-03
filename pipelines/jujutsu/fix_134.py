"""134: H3's fog_ref_h3_v4 fixed on the CPU - Gemini toned into the source's red and black, and her ponytail and tail eaten with her.

The user (2026-10-02) on fog_ref_h3_v4: “现在的134是模型生成的？没有特效吗？感觉有点怪异啊”, then on my two fixes “试试看修v4”.
v4 keeps the hands still (v3's flicker is gone) but (1) draws Gemini in her own colours - purple hair, a colour bow - where the source
draws Maki, like everything else, in red and black; (2) never eats her ponytail and cat tail: ~18-20k purple pixels in every frame,
while the source's figure is gone by frame 16 except the hands and sword.
(1) A ramp from luminance to colour is learned from the source (median colour per luminance bin over all its frames) and applied to
every pixel of v4 in proportion to how far that pixel is off the ramp (red and black pixels are already on it and stay).
(2) The purple pixels (her hair and tail) are eaten in the order the fog reaches each place in the source (the first frame its colour
changes by more than 22 from frame 0, smoothed into blobs), at the pace of the source figure (its pale pixels, running minimum, 0 left
by frame 16); what they leave is fog from fog_codex_v3, which is the source's fog in red and black there.
Usage: fix_134.py [--no-register]
"""
import pathlib
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

import render_shot as runner
from common import PROD, p
from title_057 import frames

UID, REV = '134', 'fog_h3_tint_v5'  # (first try toned only the hair and ate only purple pixels: her legs and arms stayed to the end)
OUT = PROD / 'shots' / UID / REV
V4 = PROD / 'shots/134/fog_ref_h3_v4'
V3 = PROD / 'shots/134/fog_codex_v3'
LABEL = '真希→Gemini黑水手服·静止的挥刀姿势被红雾吞没（H3 v4 加代码修正：人物压成原片的红黑单色，马尾和猫尾巴跟着雾一起被吞；手不闪）'
LUMA = np.array([0.299, 0.587, 0.114], np.float32)


def ramp(src):
    """Median colour of the source per luminance bin (0..255), empty bins interpolated."""
    px = src.reshape(-1, 3)
    lum = np.clip((px @ LUMA).round(), 0, 255).astype(int)
    table = np.full((256, 3), np.nan, np.float32)
    for v in range(256):
        sel = px[lum == v]
        if len(sel) >= 30:
            table[v] = np.median(sel, axis=0)
    good = ~np.isnan(table[:, 0])
    for c in range(3):
        table[:, c] = np.interp(np.arange(256), np.nonzero(good)[0], table[good, c])
    return table


def main():
    src = frames(V4 / 'source_exact_with_audio.mp4').astype(np.float32)
    v4 = frames(V4 / 'native_fullframe.mp4').astype(np.float32)
    v3 = frames(V3 / 'native_fullframe.mp4').astype(np.float32)
    n = len(src)
    table = ramp(src[::2])
    print('ramp at luminance 20/60/120/200:', [table[v].round().tolist() for v in (20, 60, 120, 200)], flush=True)
    # (2) where and when the fog arrives in the source
    touched = np.full(src.shape[1:3], n + 4, np.float32)
    for i in range(n - 1, 0, -1):
        hit = np.abs(src[i] - src[0]).max(-1) > 22
        touched[hit] = i
    order = ndimage.gaussian_filter(touched, 6) + np.random.default_rng(134).random(touched.shape) * 0.01
    # the source figure's pace: its pale (skin, highlight) pixels, running minimum, all gone by frame 16
    pale = np.array([float(((f[..., 1] > 0.5 * f[..., 0]) & (f.max(-1) > 90)).sum()) for f in src])
    left = np.minimum.accumulate(pale / pale[0])
    keep = np.clip((left - 0.1) / 0.9, 0, 1)
    keep[16:] = 0
    print('hair kept per frame:', np.round(keep, 2).tolist(), flush=True)
    result = []
    for i in range(n):
        f = v4[i]
        r, g, b = f[..., 0], f[..., 1], f[..., 2]
        L = f @ LUMA
        purple = ndimage.binary_closing((b > g + 6) & (b > 35), iterations=2)  # the tail darkens later on (105, 66, 94)
        # her light pixels - hair, skin, the white socks of light - are what keeps her readable; dark uniform melts into the black fog
        figure = ndimage.binary_dilation(purple | ((g > 0.45 * r) & (L > 100)), iterations=3)
        # (1) tone into the source's palette; the light purple hair looked up darker, so it reads as red hair, not pale pink
        lum = np.clip((L * np.where(purple, 0.65, 1.0)).round(), 0, 255).astype(int)
        target = table[lum]
        off = np.linalg.norm(f - target, axis=-1)
        w = np.clip((off - 25) / 35, 0, 1)
        w = np.maximum(w, ndimage.gaussian_filter(purple.astype(np.float32), 1.0))[..., None]
        toned = f * (1 - w) + target * w
        # (2) eat her: the share of her light pixels the fog has reached, in the order it reaches them - except near what the source
        # itself still shows of Maki in this frame (in the end his hands and sword)
        s_i = src[i]
        sr, sg, sb = s_i[..., 0], s_i[..., 1], s_i[..., 2]
        sl = s_i @ LUMA
        s_pale = ndimage.binary_opening((sg > 0.45 * sr) & (sl > 100), iterations=1)
        s_grey = ndimage.binary_opening((np.abs(sr - sg) < 35) & (np.abs(sg - sb) < 25) & (sl > 55) & (sl < 210), iterations=1)
        # her skin stays only close to what the source still shows (8 px); her hair and tail only round the source's face - a 14 px
        # reach round any figure pixel kept the tail floating beside the source's blade fragments to the end, and a leg by the hands
        still = np.where(ndimage.binary_dilation(purple, iterations=3), ndimage.binary_dilation(s_pale, iterations=10),
                         ndimage.binary_dilation(s_pale | s_grey, iterations=8))
        if figure.any() and keep[i] < 1:
            cut = np.quantile(order[figure], 1 - keep[i]) if keep[i] > 0 else np.inf
            gone = figure & (order <= cut) & ~still
            gw = ndimage.gaussian_filter(gone.astype(np.float32), 1.5)[..., None]
            toned = toned * (1 - gw) + v3[i] * gw
        result.append(np.clip(toned, 0, 255).astype(np.uint8))
    OUT.mkdir(parents=True, exist_ok=True)
    full = OUT / 'source_exact_with_audio.mp4'
    if not full.exists():
        shutil.copy2(V4 / 'source_exact_with_audio.mp4', full)
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
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), base=str(V4), recipe_text=(
        '在 H3 fog_ref_h3_v4 上用 CPU 修：①从原片学“亮度→颜色”的红黑映射，偏离原片色系的像素（紫发、彩色领结等）按偏离程度压成红黑；'
        '②她的浅色像素（头发、皮肤）按原片里雾到达各处的先后、以原片人物被吞的进度逐帧消失（第 16 帧起只留原片同帧仍有人物的地方，即手和刀），'
        '空出的地方用 fog_codex_v3 同帧的雾。原片原音。')))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, flush=True)


if __name__ == '__main__':
    main()
