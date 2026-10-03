"""002-004 on the CPU: the stove knob's scale becomes a “thinking level” scale (LOW / MEDIUM / HIGH / EXTRA).

User (2026-10-01): “就在这个基础上，把刻度改成thinking level如何？比如low medium high, extra。右边刻度可以加字” - on top of option A
(keep the source footage untouched, readable text added on the CPU), after rejecting the Codex temperature-dial keyframes (the
viewer could not read “temperature”, and a second keyframe that changed a knob the source never moves would force an abrupt jump).
The camera is still; only the hand moves. The small printed labels around the right knob are erased (normalized-convolution
fill, as in title_057), the new scale is drawn around the knob, and the text is hidden wherever the bright hand passes in front.
"""
import json
import pathlib
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

import render_shot as runner
import render_batch_0001 as b1
from common import PROD, p
from title_057 import fill

UID, REV = '002-004', 'thinking_cpu_v2'
OUT = PROD / 'shots' / UID / REV
LABEL = '煤气灶旋钮→Thinking level 刻度（原片不动，CPU 加字：LOW / MEDIUM / HIGH / EXTRA）'
CENTRE = (965, 228)            # right knob, 1024x576 frame
ERASE_BOXES = [(812, 336, 914, 424), (826, 8, 980, 98)]  # the original's small printed labels below-left and above the knob
FONT = 'C:/Windows/Fonts/arialbd.ttf'
INK, RED, DARK = (236, 230, 244), (236, 66, 58), (34, 26, 44)  # light print with a dark outline reads on the bright and the dark panel
# (text, angle in degrees measured counter-clockwise from +x on screen, ellipse radii, colour)
SCALE = [('LOW', 236, (205, 158), INK), ('MEDIUM', 200, (215, 160), INK), ('HIGH', 162, (210, 156), INK), ('EXTRA', 128, (205, 158), RED)]
TICKS_R = (176, 134)


def frames(path):
    raw = subprocess.run([str(p.FFMPEG), '-v', 'error', '-i', str(path), '-vsync', '0', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 576, 1024, 3)


def overlay():
    """RGBA layer with the new scale: ticks on the knob rim, words outside it, THINKING above."""
    layer = Image.new('RGBA', (1024, 576), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = CENTRE
    font = ImageFont.truetype(FONT, 30)
    for text, ang, (rx, ry), colour in SCALE:
        a = np.radians(ang)
        tx, ty = cx + rx * np.cos(a), cy - ry * np.sin(a)
        r0, r1 = (TICKS_R[0] - 16, TICKS_R[1] - 12), TICKS_R  # one bold tick per step
        line = [(cx + r0[0] * np.cos(a), cy - r0[1] * np.sin(a)), (cx + r1[0] * np.cos(a), cy - r1[1] * np.sin(a))]
        d.line(line, fill=DARK + (230,), width=8)
        d.line(line, fill=colour + (240,), width=4)
        w = d.textlength(text, font=font)
        d.text((tx - w / 2, ty - 16), text, font=font, fill=colour + (245,), stroke_width=3, stroke_fill=DARK + (235,))
    small = ImageFont.truetype(FONT, 26)
    title = 'THINKING'
    w = d.textlength(title, font=small)
    d.text((cx - 40 - w / 2, 34), title, font=small, fill=INK + (245,), stroke_width=3, stroke_fill=DARK + (235,))
    return np.asarray(layer).astype(np.float32)


def erase(fr):
    y = fr.astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
    mask = np.zeros(y.shape, bool)
    for x0, y0, x1, y1 in ERASE_BOXES:
        sub = y[y0:y1, x0:x1]
        mask[y0:y1, x0:x1] = sub > ndimage.median_filter(sub, size=15) + 14
    return fill(fr, ndimage.binary_dilation(mask, iterations=2))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    inv = json.loads((PROD / 'source_inventory/inventory.json').read_text(encoding='utf-8'))
    start, end = b1.interval(UID)
    fps = 24000 / 1001
    full = OUT / 'source_exact_with_audio.mp4'
    if not full.exists():
        p.run([p.FFMPEG, '-v', 'error', '-y', '-i', inv['source'], '-map', '0:v:0', '-map', '0:a:0',
               '-vf', f'trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS,scale=1024:576:flags=lanczos,setsar=1,format=yuv420p',
               '-af', f'atrim=start={start / fps:.9f}:end={end / fps:.9f},asetpts=PTS-STARTPTS',
               '-r', '24000/1001', '-c:v', 'libx264', '-crf', '12', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', full])
    src = frames(full)
    assert len(src) == end - start
    layer = overlay()
    alpha = layer[..., 3:] / 255
    lums = src.astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
    plate = np.median(lums, axis=0)  # still camera: the median is the bare panel wherever the hand only passes briefly
    result = []
    for fr, lum in zip(src, lums):
        out = erase(fr)
        # v1 hid the text wherever luma > 200, which also hid it on the bright top of the panel; now only what is brighter than the plate
        hand = ndimage.binary_dilation((lum > 170) & (lum > plate + 35), iterations=3)[..., None]
        a = alpha * (~hand)
        out = out * (1 - a) + layer[..., :3] * a
        result.append(np.clip(out, 0, 255).astype(np.uint8))
    silent = OUT / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(end - start), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(result).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    Image.fromarray(result[0]).save(OUT / 'preview_f00.png')
    Image.fromarray(result[10]).save(OUT / 'preview_f10.png')
    clip = OUT / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    runner.configure(OUT)
    check = runner.batch.validate_output(clip, end - start, True)
    record = OUT / 'title_compositing.json'
    builder = pathlib.Path(__file__).resolve()
    p.write_json(record, dict(kind='cpu_text', builder=str(builder), builder_sha256=p.sha(builder),
                              recipe_text='原片画面不动；右侧旋钮周围原有的小字擦掉，改成 THINKING 和 LOW / MEDIUM / HIGH / EXTRA 刻度（EXTRA 红色），'
                                          '手经过时字被手挡住。未经 H3。'))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, flush=True)


if __name__ == '__main__':
    main()
