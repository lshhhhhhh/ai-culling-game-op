"""056: GPT's pixel-fragment still, its fragments found as objects and animated on the CPU.

User (2026-10-01) on pixel_cpu_v1 (the source's fragments snapped to a grid): “太难看了。我的意思是，用GPT画的为基础，用算法找到一个个像素块
object，然后让它们移动。” Base: the Codex still (deliverables/jujutsu/静帧/still_056_codex_still_v1.png). Every dark connected blob
apart from the sphere is one fragment object (with its faint red glow); it is lifted off a cleaned background and drifts outward
from the sphere's centre - farther ones faster, the ones still touching the rim breaking away a few frames later - by whole pixels so
the blocks stay crisp. The sphere and the background stay as GPT drew them. 12 frames, the source audio.
"""
import json
import pathlib
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

import render_shot as runner
import render_batch_0001 as b1
from common import PROD, ROOT, p
from title_057 import fill

UID, REV = '056', 'pixel_particles_v7'
OUT = PROD / 'shots' / UID / REV
STILL = ROOT / 'deliverables/jujutsu/静帧/still_056_codex_still_v1.png'
LABEL = '黑太阳碎裂→GPT 画的像素块逐个飘散（CPU 粒子动画 v7：贴圆的阶梯方块按 12px 方块逐层剥落，每块完整）'
DARK = 75
LUMA = np.array([0.299, 0.587, 0.114], np.float32)
SEED = 56


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    still = np.asarray(Image.open(STILL).convert('RGB').resize((1024, 576), Image.LANCZOS)).astype(np.float32)
    lum = still @ LUMA
    # objects are everything that stands out from the orange ground - the dark blocks and the lighter outlined ones (v1 took only the
    # dark blocks, so the lighter ones stayed behind while the rest drifted away)
    bg_guess = ndimage.median_filter(still, size=(25, 25, 1))
    differs = (np.abs(still - bg_guess).max(-1) > 30) | (lum < DARK)
    lab, n = ndimage.label(differs)
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    sphere = int(np.argmax(sizes)) + 1
    # v3, the user: “贴近圆的像素点一动不动，是不是没有被识别出来？而且飞的太快了” - blocks touching the circle were part of the sphere's
    # blob. Fit the true circle on the intact lower-left boundary; everything of the blob outside it becomes separate block objects.
    body = lab == sphere
    edge = body & ~ndimage.binary_erosion(body)
    ys, xs = np.nonzero(edge)
    mx, my = xs.mean(), ys.mean()
    keep = (xs < mx) | (ys > my)  # the crumbling is at the upper right
    A = np.c_[2 * xs[keep], 2 * ys[keep], np.ones(keep.sum())]
    cx, cy, k0 = np.linalg.lstsq(A, xs[keep] ** 2 + ys[keep] ** 2, rcond=None)[0]
    radius = np.sqrt(k0 + cx ** 2 + cy ** 2)
    centre = np.array([cx, cy])
    yy, xx = np.mgrid[0:576, 0:1024]
    dist_c = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    # v7, the user on v6: “现在方块完整了，但是贴近圆的像素点又不动了”. GPT drew the crumbling rim as a packed staircase of 10-14 px
    # squares that all touch the sphere, so no connected-component test separates them. The outer 16 px of the sphere in the crumbling
    # sector are tiled into 12 px squares, the grid offset chosen so tile edges line up best with the staircase's own edges; each tile
    # with enough of the rim in it moves as one solid square, the outermost first, peeling the rim off layer by layer.
    sector = ((xx - cx) > -0.25 * radius) & ((yy - cy) < 0.25 * radius)
    # only where GPT drew crumbling (blocks sticking out, square bites taken out); the first v7 tiled the whole quarter-arc
    protrude = body & (dist_c > radius + 1.5)
    bites = ~body & (dist_c < radius - 1.5) & (dist_c > radius - 30)
    crumble = ndimage.binary_dilation(protrude | bites, iterations=10)
    band = body & sector & crumble & (dist_c > radius - 16)
    glow = differs & (lum >= DARK)
    T = 12
    zone = ndimage.binary_dilation(band, iterations=3)
    grad = np.hypot(ndimage.sobel(lum, 0), ndimage.sobel(lum, 1)) * zone
    best = max(((grad[:, ox::T].sum() + grad[oy::T, :].sum(), oy, ox) for oy in range(T) for ox in range(T)))
    _, goy, gox = best
    tiles = []
    for ty in range(goy - T, 576, T):
        for tx in range(gox - T, 1024, T):
            y0, x0 = max(ty, 0), max(tx, 0)
            y1, x1 = min(ty + T, 576), min(tx + T, 1024)
            cell = band[y0:y1, x0:x1]
            if cell.size == 0 or cell.mean() < 0.45:
                continue
            tiles.append((y0, x0, y1, x1, None))
    tile_mask = np.zeros(body.shape, bool)
    for y0, x0, y1, x1, _ in tiles:
        tile_mask[y0:y1, x0:x1] = True
    free = [k for k in range(1, n + 1) if k != sphere and sizes[k - 1] >= 3]
    allfree = np.isin(lab, free)
    # the ground is orange: fill the sphere, every block and every glow from the orange around them, then put back the sphere minus
    # the band - a tile that leaves shows orange behind it (band pixels too thin for a tile simply go)
    background = fill(still.astype(np.uint8), ndimage.binary_dilation(body | allfree | glow, iterations=2))
    rest = body & ~tile_mask
    background[rest] = still[rest]
    objects = []
    for y0, x0, y1, x1, _ in tiles:
        # GPT's own pixels of the tile (sphere and glow, not the orange), so frame 0 is exactly GPT's picture; the tile edges follow
        # the staircase, so what moves is still a square block
        piece = np.zeros(body.shape, bool)
        piece[y0:y1, x0:x1] = (body | glow)[y0:y1, x0:x1]
        oy, ox = np.nonzero(piece)
        if len(oy) == 0:
            continue
        colour_px = still[oy, ox]
        d = np.array([ox.mean(), oy.mean()]) - centre
        dist = np.linalg.norm(d)
        direction = d / (dist + 1e-6) + np.array([0.15, -0.35])
        direction /= np.linalg.norm(direction)
        depth = max(radius + 4 - dist, 0)  # 0 at the outer edge, larger further in: the outer tiles leave first
        delay = int(min(depth / 2.5, 9)) + int(rng.integers(0, 3))
        objects.append(dict(ys=oy, xs=ox, colours=colour_px, v=direction * rng.uniform(0.3, 0.8), delay=delay))
    for k in free:
        m = lab == k
        m = m | (glow & ndimage.binary_dilation(m, iterations=1) & ~body)
        oy, ox = np.nonzero(m)
        c = np.array([ox.mean(), oy.mean()])
        d = c - centre
        dist = np.linalg.norm(d)
        direction = d / (dist + 1e-6) + np.array([0.15, -0.35])  # outward, with a slight drift up and to the right like the source
        direction /= np.linalg.norm(direction)
        out_of_rim = dist - radius
        speed = rng.uniform(0.3, 0.8) * (1 + max(out_of_rim, 0) / 80)  # v2 used 0.8-1.8: “飞的太快了”
        delay = int(rng.integers(0, 10)) if out_of_rim < 12 else 0
        objects.append(dict(ys=oy, xs=ox, colours=still[oy, ox], v=direction * speed, delay=delay))
    start, end = b1.interval(UID)
    frames = []
    for t in range(end - start):
        canvas = background.copy()
        for o in objects:
            s = max(t - o['delay'], 0)
            dx, dy = np.round(o['v'] * s).astype(int)
            y, x = o['ys'] + dy, o['xs'] + dx
            ok = (y >= 0) & (y < 576) & (x >= 0) & (x < 1024)
            canvas[y[ok], x[ok]] = o['colours'][ok]
        frames.append(np.clip(canvas, 0, 255).astype(np.uint8))
    frames = np.stack(frames)
    inv = json.loads((PROD / 'source_inventory/inventory.json').read_text(encoding='utf-8'))
    fps = 24000 / 1001
    full = OUT / 'source_exact_with_audio.mp4'
    if not full.exists():
        p.run([p.FFMPEG, '-v', 'error', '-y', '-i', inv['source'], '-map', '0:v:0', '-map', '0:a:0',
               '-vf', f'trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS,scale=1024:576:flags=lanczos,setsar=1,format=yuv420p',
               '-af', f'atrim=start={start / fps:.9f}:end={end / fps:.9f},asetpts=PTS-STARTPTS',
               '-r', '24000/1001', '-c:v', 'libx264', '-crf', '12', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', full])
    silent = OUT / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(frames)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=frames.tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    x0, x1 = int(centre[0] - 40), int(min(centre[0] + radius + 160, 1024))
    y0, y1 = int(max(centre[1] - radius - 120, 0)), int(centre[1] + 40)
    strip = np.concatenate([frames[i][y0:y1, x0:x1] for i in (0, 5, 11)], axis=1)
    Image.fromarray(strip).resize((strip.shape[1] * 2, strip.shape[0] * 2), Image.NEAREST).save(OUT / 'preview_f00_f05_f11.png')
    clip = OUT / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    runner.configure(OUT)
    check = runner.batch.validate_output(clip, len(frames), True)
    record = OUT / 'title_compositing.json'
    builder = pathlib.Path(__file__).resolve()
    p.write_json(record, dict(kind='cpu_text', builder=str(builder), builder_sha256=p.sha(builder),
                              recipe_text=f'以 GPT 画的静帧为底（{STILL.name}），找出球体以外的 {len(objects)} 个像素块（含微弱红光），从干净背景上取下，'
                                          '逐帧向外飘散（离得远的更快，贴着边缘的晚几帧才脱落，整像素移动保持方块锐利）。球体和背景不动。未经 H3。'))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    if '--no-register' not in sys.argv:
        entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
        if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
            runner.review.register(UID, str(clip), record, LABEL)
    moving = [int((np.abs(frames[i + 1].astype(int) - frames[i].astype(int)).max(-1) > 20).sum()) for i in range(len(frames) - 1)]
    print('READY', clip, '| objects', len(objects), '| frame-to-frame motion', moving, flush=True)


if __name__ == '__main__':
    main()
