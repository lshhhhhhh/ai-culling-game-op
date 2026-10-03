"""005 title on the CPU: the giant red melting 「呪術廻戦」 frame -> 「模型回战」, animated like the source.

User (2026-10-01): “标题也需要重新设计”; chose 「模型回战」. The still is a Codex redraw of the source frame
(deliverables/jujutsu/标题/title_005_frame_v1.png, codex_titles_0001.py). The source does not move (phase correlation 0,0 over
its 17 frames); the glyphs and the background only “boil”. Here each frame gets its own smooth random displacement, with the
amplitude tuned so the mean frame-to-frame change matches the source.
"""
import json
import pathlib
import subprocess

import numpy as np
from PIL import Image
from scipy import ndimage

import render_shot as runner
from common import PROD, ROOT, p

UID, REV = '005', 'title_cpu_v1'
START, END = 252, 269
STILL = ROOT / 'deliverables/jujutsu/标题/title_005_frame_v1.png'
LABEL = '标题→「模型回战」（Codex 重画整帧＋CPU 逐帧沸腾抖动）'
OUT = PROD / 'shots' / UID / REV
SIGMA = 14  # px, smoothness of the displacement field


def frames(path):
    raw = subprocess.run([str(p.FFMPEG), '-v', 'error', '-i', str(path), '-vsync', '0', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 576, 1024, 3)


def boil(img, amp, rng):
    h, w = img.shape[:2]
    dy, dx = (ndimage.gaussian_filter(rng.standard_normal((h, w)), SIGMA) for _ in range(2))
    dy, dx = dy / (dy.std() + 1e-9) * amp, dx / (dx.std() + 1e-9) * amp
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    return np.stack([ndimage.map_coordinates(img[..., c], [yy + dy, xx + dx], order=1, mode='reflect') for c in range(3)], -1)


def mean_change(seq):
    return float(np.mean([np.abs(seq[i + 1].astype(np.float32) - seq[i]).mean() for i in range(len(seq) - 1)]))


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
    target = mean_change(src)
    still = np.asarray(Image.open(STILL).convert('RGB').resize((1024, 576), Image.LANCZOS)).astype(np.float32)
    amp, result = 2.0, None
    for _ in range(4):  # tune the amplitude to the source's frame-to-frame change
        rng = np.random.default_rng(2610010005)
        result = [np.clip(boil(still, amp, rng), 0, 255).astype(np.uint8) for _ in range(END - START)]
        change = mean_change(result)
        if abs(change - target) / target < 0.15:
            break
        amp *= target / max(change, 1e-3)
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
                              recipe_text=f'Codex 按原帧重画「模型回战」整帧（{STILL.name}），CPU 逐帧加平滑随机位移模拟原片的沸腾抖动（幅度 {amp:.2f} px，帧间变化 {mean_change(result):.2f}，原片 {target:.2f}）。未经 H3。'))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, 'amp', round(amp, 2), 'change', round(mean_change(result), 2), 'source', round(target, 2), flush=True)


if __name__ == '__main__':
    main()
