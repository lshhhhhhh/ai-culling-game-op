"""068: the bird gliding past the monolith becomes a drone, and the monolith gets faint glowing circuit lines - Codex art composited
on the CPU (no H3).

The user (2026-10-02): “讨论一下068怎么做。把飞过的鸟换成无人机怎么样？更有科技感”, then on my proposal “1用一架 2也要改动” (one drone; the
monolith changes too - faint glowing circuit lines).
Source (45 frames): seen from high above, a huge glossy black monolith hangs from the clouds over the land, wisps of cloud wrapping it;
the camera pushes in slowly (the monolith ~12 % larger by the end). From frame 7 a white bird glides away in front of the monolith,
drawn on threes, shrinking from a 75 px wingspan to a 10 px speck near the monolith's middle.
Here: the bird is found on the dark monolith and filled from around it; the circuit lines are drawn once by Codex on the clean frame 0,
taken as a glow layer and carried by the monolith's measured scale and shift in every frame, shown only where the monolith shows
(cloud wisps in front hide them); a Codex drone takes the bird's place, size and three-frame timing, with a blinking strobe.
Usage: drone_068.py draw | render [--no-register]
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

UID, REV = '068', 'drone_code_v2'
DIR = ROOT / 'deliverables/jujutsu/静帧'
OUT = PROD / 'shots' / UID / REV
SOURCE = ROOT / 'assets/jujutsu/op1_v1/review/source_units/068.mp4'
LABEL = '巨大黑色方碑：飞过的鸟→一架白色无人机（v2：从左上角进画面时就是无人机；航行灯闪烁），方碑表面加淡淡的发光电路纹路（Codex 画、代码合成，纹路随镜头推近固定在方碑上；未经 H3）'
LUMA = np.array([0.299, 0.587, 0.114], np.float32)
CIRCUIT = ('kf_068_f000_circuit_v1.png',
           'Image 1 is a frame from an anime opening: seen from high above, a huge glossy black monolith hangs down from the clouds over the '
           'land far below, wisps of cloud wrapping around it. Add ONLY faint glowing circuit lines on the monolith: thin cyan traces running '
           'along its surface like the paths on a circuit board - straight runs with right-angle turns and small round nodes - glowing '
           'softly, following the monolith\'s shape and perspective, fading toward its far end, and hidden where the cloud wisps pass in '
           'front of it. The monolith stays black and glossy. Keep EVERYTHING else exactly as in Image 1 - the clouds, the land, the '
           'light, the colours and the framing. The output is a 16:9 image with the framing of Image 1. No text. Do not create or modify '
           'any other files.')
DRONE = ('drone_068_v1.png',
         'Draw a small white quadcopter drone seen from above and slightly behind as it flies away from the viewer: four rotors on four '
         'arms in an X, a compact rounded white body with a small camera underneath, a tiny red light on the left arm tips and a tiny green '
         'light on the right arm tips. A clean illustration with crisp outlines and soft shading, lit from above by daylight. The drone '
         'fills most of the width of a landscape image. Background: flat pure magenta (#FF00FF) everywhere, no shadow, no text, no logos. '
         'Do not create or modify any other files.')


def fill(img, hole):
    """Fine-to-coarse normalized convolution (as sprite_140.fill)."""
    known = (~hole).astype(np.float32)
    est, todo = img.copy(), hole.copy()
    for sigma in (2, 4, 8, 16, 32):
        wgt = ndimage.gaussian_filter(known, sigma)
        e = np.stack([ndimage.gaussian_filter(img[..., c] * known, sigma) for c in range(3)], -1) / np.maximum(wgt, 1e-6)[..., None]
        ok = todo & (wgt > (0.15 if sigma < 32 else 1e-4))
        est[ok] = e[ok]
        todo &= ~ok
    return est


def track_bird(src):
    """Bounding box of the bird in each frame from 7 on: the largest bright blob on the dark monolith near its path, followed from the
    previous frame (a cloud wisp on the monolith's left edge and specks further down are not it)."""
    lum = src @ LUMA
    X0, Y0, X1, Y1 = 380, 240, 600, 380
    boxes, prev = {}, None
    for i in range(len(src)):
        w = lum[i][Y0:Y1, X0:X1]
        m = (w > 150) & (ndimage.median_filter(w, size=41) < 70)
        lab, n = ndimage.label(ndimage.binary_closing(m, iterations=1))
        best = None
        for k, sl in enumerate(ndimage.find_objects(lab), 1):
            ys, xs = np.nonzero(lab[sl] == k)
            if len(ys) < 6:
                continue
            box = (X0 + sl[1].start, Y0 + sl[0].start, X0 + sl[1].stop, Y0 + sl[0].stop)
            cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
            if prev is None and len(ys) < 300:  # the bird enters big (frame 7)
                continue
            if prev is not None and np.hypot(cx - prev[0], cy - prev[1]) > 45:
                continue
            if best is None or len(ys) > best[0]:
                best = (len(ys), box, (cx, cy))
        if best:
            boxes[i] = best[1]
            prev = best[2]
    return boxes


def track_early(src):
    """v2, the user on drone_code_v1: “68也不好。一开始鸟从左边进入画面的时候没有替换” - the bird enters huge at the top left at frame 3
    (cut by the frame's edges), sweeps across the clouds and land at 5-6 and only reaches the monolith at 7. Over that bright ground it is
    found as the largest change in the upper left against frame 1 (no bird yet) shifted by the camera's drift; the near clouds' parallax
    below is not it. Returns {frame: (box, mask, frame 1 aligned)}."""
    from pan_040 import shift
    u = np.clip(src, 0, 255).astype(np.uint8)
    out = {}
    for i in range(2, 7):
        dy, dx, _ = shift(u[1], u[i])
        ref = ndimage.shift(src[1], (-dy, -dx, 0), order=1, mode='nearest')
        m = ndimage.binary_opening(np.abs(src[i] - ref).max(-1) > 40, iterations=1)
        m[300:, :] = False
        m[:, 460:] = False
        lab, n = ndimage.label(ndimage.binary_closing(m, iterations=2))
        if not n:
            continue
        sz = ndimage.sum(np.ones_like(m), lab, range(1, n + 1))
        if sz.max() < 2000:
            continue
        bird = ndimage.binary_fill_holes(lab == 1 + int(np.argmax(sz)))
        ys, xs = np.nonzero(bird)
        out[i] = ((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1), ndimage.binary_dilation(bird, iterations=4), ref)
    return out


def erase_bird(frame, box):
    lum = frame @ LUMA
    x0, y0, x1, y1 = box
    win = np.zeros(lum.shape, bool)
    win[max(0, y0 - 14):y1 + 14, max(0, x0 - 14):x1 + 14] = True
    # the bird and its soft glow (a tighter mask left a faint ring of the glow round the filled hole)
    # - only over the dark monolith (where the left wing reaches the cloud at its edge, the cloud is not taken) and only what is joined
    # to the bird's bright body
    bg = ndimage.median_filter(lum, size=41)
    bird = win & (lum > bg + 8) & (bg < 60)
    core = win & (lum > 150) & (bg < 70)
    lab, n = ndimage.label(bird)
    if n:
        bird = np.isin(lab, np.unique(lab[core & bird]))
        bird &= lab > 0
    grown = ndimage.binary_dilation(bird, iterations=6) & (ndimage.binary_dilation(bg < 60, iterations=6))
    return fill(frame, grown)


def codex(item, image=None):
    name, prompt = item
    if (DIR / name).exists():
        return name, True
    args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
            '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt'), *(['-i', str(image)] if image else []), '--',
            f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {prompt}']
    t = time.time()
    try:
        subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
    except subprocess.TimeoutExpired:
        pass
    print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', flush=True)
    return name, (DIR / name).exists()


def draw():
    src = frames(SOURCE).astype(np.float32)
    clean0 = DIR / 'src_068_f000_clean.png'
    Image.fromarray(src[0].astype(np.uint8)).save(clean0)  # the bird is not there yet in frame 0
    with ThreadPoolExecutor(2) as pool:
        print(list(pool.map(lambda a: codex(*a), [(CIRCUIT, clean0), (DRONE, None)])))


def monolith_motion(src):
    """Per frame (scale, dy, dx) taking frame-0 point p to frame-i point c + s * (p - d - c): searched on gradient images of the
    monolith's box (scale step 0.005, shift by phase correlation), then smoothed by a quadratic fit over the frames."""
    lum = src @ LUMA
    grad = lambda a: np.hypot(ndimage.sobel(a, 0), ndimage.sobel(a, 1))
    x0, y0, x1, y1 = 380, 40, 660, 470
    win = np.outer(np.hanning(y1 - y0), np.hanning(x1 - x0))
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    g0 = grad(lum[0])[y0:y1, x0:x1] * win
    meas = []
    for i in range(len(src)):
        gi = grad(lum[i])
        best = None
        for s in np.arange(0.98, 1.16, 0.005):
            w = ndimage.map_coordinates(gi, [C[1] + s * (yy - C[1]), C[0] + s * (xx - C[0])], order=1) * win
            F = np.fft.fft2(g0) * np.conj(np.fft.fft2(w))
            r = np.fft.ifft2(F / (np.abs(F) + 1e-6)).real
            k = np.unravel_index(r.argmax(), r.shape)
            if best is None or r.max() > best[0]:
                dy = k[0] if k[0] < r.shape[0] // 2 else k[0] - r.shape[0]
                dx = k[1] if k[1] < r.shape[1] // 2 else k[1] - r.shape[1]
                best = (r.max(), s, dy, dx)
        meas.append(best[1:])
    meas = np.array(meas, np.float32)
    f = np.arange(len(src))
    fit = np.stack([np.polyval(np.polyfit(f, meas[:, c], 2), f) for c in range(3)], -1)
    fit[0] = (1, 0, 0)
    print('monolith scale / shift at 0, 22, 44:', [tuple(np.round(fit[k], 3)) for k in (0, 22, 44)], flush=True)
    return fit


C = (510.0, 250.0)  # the centre the monolith is scaled about


def glow_layer(clean0):
    """What Codex added on the monolith: brighter than frame 0 and cyan (G and B well above R), inside the monolith's dark silhouette."""
    a = np.asarray(Image.open(DIR / CIRCUIT[0]).convert('RGB').resize((1024, 576), Image.LANCZOS), np.float32)
    lum0 = clean0 @ LUMA
    mono = np.zeros(lum0.shape, bool)
    mono[0:445, 400:620] = True
    lab, _ = ndimage.label(ndimage.binary_closing((lum0 < 45) & mono, iterations=3))
    mono = ndimage.binary_dilation(ndimage.binary_fill_holes(lab == lab[250, 510]), iterations=6)
    add = (a @ LUMA) - lum0
    cyan = (a[..., 1] + a[..., 2]) / 2 - a[..., 0]
    alpha = np.clip((add - 6) / 50, 0, 1) * np.clip((cyan - 10) / 30, 0, 1) * mono
    colour = np.where(alpha[..., None] > 0, a, 0)
    print('glow pixels', int((alpha > 0.3).sum()), flush=True)
    return alpha, colour


def drone_sprite():
    a = np.asarray(Image.open(DIR / DRONE[0]).convert('RGB')).astype(np.float32)
    alpha = np.clip((np.linalg.norm(a - np.array([255, 0, 255], np.float32), axis=-1) - 60) / 80, 0, 1)
    ys, xs = np.nonzero(alpha > 0.5)
    a, alpha = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], alpha[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    a = np.where(alpha[..., None] < 1, a - np.array([255, 0, 255], np.float32) * (1 - alpha[..., None]) * 0.6, a)
    return np.clip(a, 0, 255), alpha


def render():
    OUT.mkdir(parents=True, exist_ok=True)
    full = OUT / 'source_exact_with_audio.mp4'
    if not full.exists():
        shutil.copy2(SOURCE, full)
    src = frames(full).astype(np.float32)
    boxes = track_bird(src)
    early = track_early(src)
    print('bird from frame', min(boxes), 'to', max(boxes), {k: boxes[k] for k in sorted(boxes)[::3]}, flush=True)
    print('entering bird', {k: v[0] for k, v in early.items()}, flush=True)
    boxes.update({k: v[0] for k, v in early.items()})
    motion = monolith_motion(src)
    alpha0, colour0 = glow_layer(src[0])
    rgb, al = drone_sprite()
    asp = rgb.shape[0] / rgb.shape[1]
    # the drone keeps the bird's three-frame timing: one place, size and tilt per drawing (a drawing = frames whose box is unchanged)
    keys = sorted(boxes)
    drawings, cur = [], [keys[0]]
    for k in keys[1:]:
        if np.abs(np.subtract(boxes[k], boxes[cur[0]])).max() <= 3:
            cur.append(k)
        else:
            drawings.append(cur)
            cur = [k]
    drawings.append(cur)
    # its width: from frame 10 on the bird's wingspan changes with every flap, so a straight-line fit of the log wingspan over those
    # drawings; the three nearest drawings (3-4 cut by the frame, 5-6, 7-9) shrink too fast for it and keep the measured span
    mids = np.array([np.mean(d) for d in drawings])
    spans = np.array([boxes[d[0]][2] - boxes[d[0]][0] for d in drawings], np.float32)
    far = mids >= 10
    k1, k0 = np.polyfit(mids[far], np.log(spans[far]), 1)
    pose = {}
    for j, d in enumerate(drawings):
        x0, y0, x1, y1 = boxes[d[0]]
        cut = x0 <= 3 or y0 <= 3  # entering at the top left, partly outside the frame
        if mids[j] >= 10:
            width = float(np.exp(k1 * mids[j] + k0)) * 0.9
        elif cut:
            width = 1.5 * float(spans[j + 1])  # nearer than the next drawing; its true span is outside the frame
        else:
            width = float(spans[j]) * 0.9
        tilt = -12 if cut else -8 if mids[j] < 7 else (-4, 3, -2, 4, -3, 2)[j % 6]  # it swoops in banked, then glides with a gentle sway
        H = width * asp
        cx, cy = ((x1 - width / 2, y1 - H / 2) if cut else ((x0 + x1) / 2, (y0 + y1) / 2))  # cut: its lower right on the bird's
        for k in d:
            pose[k] = (cx, cy, width, tilt)
    yy, xx = np.mgrid[0:576, 0:1024].astype(np.float32)
    result = []
    for i in range(len(src)):
        frame = src[i]
        if i in early:  # over the bright ground: frame 1 (no bird yet), aligned, fills the bird's place
            _, m, ref = early[i]
            w = ndimage.gaussian_filter(m.astype(np.float32), 1.5)[..., None]
            frame = frame * (1 - w) + ref * w
        elif i in boxes:
            frame = erase_bird(frame, boxes[i])
        # circuit lines: frame-i point q came from frame-0 point p = C + (q - C) / s + d
        s, dy, dx = motion[i]
        py, px = C[1] + (yy - C[1]) / s + dy, C[0] + (xx - C[0]) / s + dx
        a = ndimage.map_coordinates(alpha0, [py, px], order=1)
        col = np.stack([ndimage.map_coordinates(colour0[..., c], [py, px], order=1) for c in range(3)], -1)
        # back from premultiplied; where the warped alpha is tiny the ratio blew up into white specks (frame 44, top of the monolith)
        col = np.where(a[..., None] > 0.02, np.clip(col / np.maximum(a[..., None], 1e-3), 0, 255), 0)
        lum = frame @ LUMA
        visible = np.clip((60 - lum) / 25, 0, 1)  # only on the dark monolith: cloud wisps in front hide the lines
        pulse = 0.85 + 0.15 * np.sin(2 * np.pi * i / 30)
        g = (a * visible * pulse)[..., None]
        frame = 255 - (255 - frame) * (1 - g * col / 255)  # screen: light added, never darkening
        if i in pose:
            cx, cy, width, tilt = pose[i]
            W = max(3, round(width))
            H = max(2, round(W * asp))
            spr = Image.fromarray(rgb.astype(np.uint8)).resize((W, H), Image.LANCZOS).rotate(tilt, Image.BICUBIC, expand=True)
            sa = Image.fromarray((al * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS).rotate(tilt, Image.BICUBIC, expand=True)
            c = np.asarray(spr, np.float32)
            m = np.asarray(sa, np.float32)[..., None] / 255
            X, Y = round(cx - c.shape[1] / 2), round(cy - c.shape[0] / 2)
            sx0, sy0, dx0, dy0 = max(0, -X), max(0, -Y), max(0, X), max(0, Y)  # it enters partly outside the frame
            dx1, dy1 = min(1024, X + c.shape[1]), min(576, Y + c.shape[0])
            if dx1 > dx0 and dy1 > dy0:
                cc, mm = c[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0], m[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0]
                frame[dy0:dy1, dx0:dx1] = frame[dy0:dy1, dx0:dx1] * (1 - mm) + cc * mm
            # a red strobe under its tail: two frames lit in every eight, a soft dot at least 2 px across
            if i % 8 < 2:
                r = max(1.0, W / 14)
                d = np.hypot(xx - cx, yy - (cy + H * 0.25))
                glow = np.clip(1.2 - d / r, 0, 1)[..., None] + 0.5 * np.exp(-(d / (2.5 * r)) ** 2)[..., None]
                frame = 255 - (255 - frame) * (1 - np.clip(glow, 0, 1) * np.array([1.0, 0.25, 0.2], np.float32))
        result.append(np.clip(frame, 0, 255).astype(np.uint8))
    silent = OUT / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(result)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(result).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = OUT / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    for k in (0, 8, 22, 44):
        Image.fromarray(result[k]).save(OUT / f'preview_f{k:03d}.png')
    if '--no-register' in sys.argv:
        print('PREVIEW', clip, flush=True)
        return
    runner.configure(OUT)
    check = runner.batch.validate_output(clip, len(result), True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    me = pathlib.Path(__file__).resolve()
    record = OUT / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), art=[CIRCUIT[0], DRONE[0]], recipe_text=(
        '原片的鸟（第 7 帧起，一拍三）在方碑暗面上找出并抹掉；Codex 在第 0 帧给方碑画发光电路纹路，取出发光层，按逐帧测得的方碑缩放与位移'
        '贴回每一帧，只在方碑露出的暗处显示（云挡住的地方不显示），亮度缓慢脉动；Codex 画的白色无人机按鸟每张画的位置、平滑后的大小与'
        '一拍三的节奏贴上，尾部红色频闪。原片原音。未经 H3。\nCodex 提示词（纹路）：' + CIRCUIT[1] + '\n（无人机）：' + DRONE[1])))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, flush=True)


if __name__ == '__main__':
    {'draw': draw, 'render': render}[sys.argv[1]]()
