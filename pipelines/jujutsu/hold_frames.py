"""Hold one good frame of a finished version over its bad frames (CPU), and register the result as a new version.

098, the user (2026-10-02 10:57): “第一个人物替换失败，有几帧人物切成原版了。可以用CPU修复，把替换成功的最后一帧拉长。” In
kf_grok_claude_hy_h3_v3 the first shot is frames 0-5: frames 1-2 show Grok in the fluttering receipt skirt, frames 3-5 are Reggie
again (output vs source 2.5-6.4 against 16.3 on frame 0), so frame 2 is held over 3-5.
Correction (2026-10-02, the user: “098还要修改”): judged by those numbers alone that was wrong - frames 1-2 have only Grok's head on
Reggie's receipt coat; only frame 0 is all Grok. Also each cut came one frame late (frame 6 still the purple shot, 12 still Claude).
v2 rules: 1-5=0 6-6=7 12-12=13, written to their own folder (--out) so the first hold version's files stay as registered.
Usage: hold_frames.py UNIT REV FIRST-LAST=GOOD [...] [--out FOLDER] [--no-register]
"""
import pathlib
import shutil
import subprocess
import sys

import numpy as np

import render_shot as runner
from common import PROD, p
from title_057 import frames


def main():
    uid, rev = sys.argv[1], sys.argv[2]
    rules = []
    for a in sys.argv[3:]:
        if '=' in a:
            span, good = a.split('=')
            first, last = (int(x) for x in span.split('-'))
            rules.append((first, last, int(good)))
    job = PROD / 'shots' / uid / rev
    base = frames(job / 'native_fullframe.mp4')
    out_frames = [f for f in base]
    for first, last, good in rules:
        for i in range(first, last + 1):
            out_frames[i] = base[good]
    tag = '_'.join(f'{a}-{b}={g}' for a, b, g in rules)
    out = PROD / 'shots' / uid / (sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else f'{rev}_hold')
    out.mkdir(parents=True, exist_ok=True)
    full = out / 'source_exact_with_audio.mp4'
    if not full.exists():
        shutil.copy2(job / 'source_exact_with_audio.mp4', full)
    silent = out / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(out_frames)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(out_frames).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = out / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    runner.configure(out)
    check = runner.batch.validate_output(clip, len(out_frames), True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    me = pathlib.Path(__file__).resolve()
    record = out / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), base=str(job), rules=rules, recipe_text=(
        f'在 {rev} 上用 CPU 修：' + '；'.join(f'第 {a}–{b} 帧换成第 {g} 帧（定格）' for a, b, g in rules) + '。其余帧不变，原片原音。')))
    p.write_json(out / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == uid)
    label = next((v.get('label', '') for v in entry['versions'] if rev in v.get('id', '') or rev in str(v.get('video', ''))), uid)
    if '--no-register' not in sys.argv and not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(uid, str(clip), record, f'{label}（CPU：{tag} 定格，盖住切回原版的帧）')
    print('READY', clip, flush=True)


if __name__ == '__main__':
    main()
