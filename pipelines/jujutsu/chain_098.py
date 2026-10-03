"""098: the violet shot drawn frame by frame by Codex, each drawing made from the one before it (CPU compositing, no H3).

The user (2026-10-02) on grok_twos_splice_v6: “感觉动作还是不连贯啊。要不这样，让codex生成4帧动作，每一张都用之前的生成，确保一致性”.
The source's violet shot (frames 0-5) is animated on ones: the figure sweeps an arm across and points. Frames 0 and 1 are grok_ref_h3_v4's
whole-Grok frames; frames 2-5 are drawn in order, each from the source frame's pose (Image 1) and the previous drawing (Image 2), so the
girl stays the same from drawing to drawing. The teal and green shots are v4's moving frames, with the cuts on the source's frames
(6 shows v4's 7, 12 shows v4's 13), as in splice_098.py.
Usage: chain_098.py draw | render [--no-register]
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
from title_057 import frames

UID, REV = '098', 'grok_chain_v7'
OUT = PROD / 'shots' / UID / REV
V4 = PROD / 'shots/098/grok_ref_h3_v4'
DIR = ROOT / 'deliverables/jujutsu/关键帧'
DRAWN = (2, 3, 4, 5)
LABEL = '雷吉/伏黑惠/熊猫→Grok/Claude/HY·彩光登场（紫光段第 2–5 帧由 Codex 逐帧画、每张以上一张为参考；后两段用 H3 v4 的动态画面）'
PROMPT = ('Image 1 is a frame from an anime opening: on a black background, a figure lit entirely in a single violet light, wrapped in a '
          'big coat of fluttering paper strips, caught in the middle of an arm movement. Image 2 is the previous frame of the same shot, '
          'already redrawn: the girl who replaces that figure. Redraw the figure of Image 1 as exactly the girl of Image 2 - the same '
          'face, twin tails, small crown and horns, the same gothic dress and full skirt, the same violet light, line style and colours, '
          'the same size and place - changing only her pose to match the figure of Image 1 at this moment (the same arm positions and the '
          'same turn of the head), as the next drawing of the same animation. Nothing of the original figure remains: no coat of paper '
          'strips, no long straight hair, no beard. Keep the black background. The output is a 16:9 image with the framing of Image 1. '
          'No text. Do not create or modify any other files.')


def name(i):
    return f'kf_098_f{i:03d}_chain_v1.png'


def draw():
    src = frames(V4 / 'source_exact_with_audio.mp4')
    v4 = frames(V4 / 'native_fullframe.mp4')
    prev = DIR / 'h3_098_grok_ref_h3_v4_f001.png'
    if not prev.exists():
        Image.fromarray(v4[1]).save(prev)
    for i in DRAWN:
        pose = DIR / f'src_098_chain_f{i:03d}.png'
        if not pose.exists():
            Image.fromarray(src[i]).save(pose)
        if not (DIR / name(i)).exists():
            args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
                    '-o', str(DIR / f'codex_last_message_{name(i)[:-4]}.txt'), '-i', str(pose), '-i', str(prev), '--',
                    f'Use your image generation tool to create ONE image and save it in the current directory as {name(i)}. {PROMPT}']
            t = time.time()
            subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
            print('done' if (DIR / name(i)).exists() else 'FAILED', name(i), f'{time.time() - t:.0f} s', flush=True)
            if not (DIR / name(i)).exists():
                raise SystemExit(f'Codex failed on frame {i}')
        prev = DIR / name(i)


def render():
    v4 = frames(V4 / 'native_fullframe.mp4')
    drawn = {i: np.asarray(Image.open(DIR / name(i)).convert('RGB').resize((1024, 576), Image.LANCZOS)) for i in DRAWN}
    shot1 = [v4[0], v4[1]] + [drawn[i] for i in DRAWN]
    out = shot1 + [v4[7]] + [v4[i] for i in range(7, 12)] + [v4[13]] + [v4[i] for i in range(13, 17)]
    assert len(out) == len(v4) == 17, len(out)
    OUT.mkdir(parents=True, exist_ok=True)
    full = OUT / 'source_exact_with_audio.mp4'
    if not full.exists():
        shutil.copy2(V4 / 'source_exact_with_audio.mp4', full)
    silent = OUT / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(out)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(out).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = OUT / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    if '--no-register' in sys.argv:
        print('PREVIEW', clip, flush=True)
        return
    runner.configure(OUT)
    check = runner.batch.validate_output(clip, len(out), True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    me = pathlib.Path(__file__).resolve()
    record = OUT / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), base=str(V4),
                              drawings=[name(i) for i in DRAWN], recipe_text=(
        '紫光段：第 0、1 帧用 H3 grok_ref_h3_v4 的完整 Grok；第 2–5 帧由 Codex 依次逐帧画，每张以原片该帧的姿势（图 1）和上一张'
        '（图 2，第 2 帧以 v4 第 1 帧为准）为参考，保证前后一致。第二、三段用 v4 的动态画面，切镜按原片（第 6 帧用 v4 第 7 帧、第 12 帧用'
        ' v4 第 13 帧）。原片原音。\nCodex 提示词：' + PROMPT)))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, flush=True)


if __name__ == '__main__':
    {'draw': draw, 'render': render}[sys.argv[1]]()
