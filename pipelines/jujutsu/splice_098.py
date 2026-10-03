"""098: the moving teal and green shots of grok_ref_h3_v4 with a violet shot animated on twos from three whole-Grok drawings (CPU).

The user (2026-10-02) on the hold fix: “098现在完全就是静止帧了，不好看。要不还是用视频模型生成动态的。” grok_ref_h3_v4 (our v3 as
<Video 1>, Grok keyframes at 0, 3 and 5) moves well in the second and third shots, but its violet shot went back to Reggie again from
frame 2 (it copied its reference, which has Reggie there). Here the violet shot is three whole-Grok drawings in the source's action -
v4's frames 0 and 1 (arm across her body), the Codex keyframe of frame 3 (the arm sweeping), that of frame 5 (pointing) - held on twos
like the anime around it: 0, 1, 3, 3, 5, 5. H3 put each cut one frame late (frame 6 still violet, 12 still teal): frame 6 shows v4's
frame 7 and frame 12 its frame 13.
v6, the user on v5: “可以把快结束的时候“伸出手臂”的动作延长一点（往前面延长），这样动作更加明显” - the sweep (frame 3's drawing) is
one frame and the pointing arm (frame 5's) starts at frame 3: 0, 1, 3, 5, 5, 5.
Usage: splice_098.py [--v6] [--no-register]
"""
import pathlib
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image

import render_shot as runner
from common import PROD, ROOT, p
from title_057 import frames

UID, REV = '098', 'grok_twos_splice_v5'
V6 = '--v6' in sys.argv
if V6:
    REV = 'grok_twos_splice_v6'
OUT = PROD / 'shots' / UID / REV
V4 = PROD / 'shots/098/grok_ref_h3_v4'
KF = ROOT / 'deliverables/jujutsu/关键帧'
LABEL = '雷吉/伏黑惠/熊猫→Grok/Claude/HY·彩光登场（后两段用 H3 v4 的动态画面；紫光段由三张完整 Grok 一拍二接成：v4 第 0–1 帧、Codex 第 3、5 帧）'
if V6:
    LABEL = '雷吉/伏黑惠/熊猫→Grok/Claude/HY·彩光登场（后两段用 H3 v4 的动态画面；紫光段三张完整 Grok，伸出手臂从第 3 帧起延长到三帧）'


def main():
    v4 = frames(V4 / 'native_fullframe.mp4')
    kf = {k: np.asarray(Image.open(KF / f'kf_098_f{k:03d}_grokfull_v2.png').convert('RGB').resize((1024, 576), Image.LANCZOS))
          for k in (3, 5)}
    shot1 = [v4[0], v4[1], kf[3], kf[5], kf[5], kf[5]] if V6 else [v4[0], v4[1], kf[3], kf[3], kf[5], kf[5]]
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
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), base=str(V4), recipe_text=(
        '第二、三段（Claude、HY）用 H3 grok_ref_h3_v4 的动态画面；紫光段 v4 从第 2 帧起又变回雷吉，改由三张完整的 Grok 一拍二接成：'
        + ('v4 第 0、1 帧，Codex 关键帧第 3 帧（手臂横扫）×1，第 5 帧（伸出手臂前指）×3（v6：按用户要求把伸手往前延长）。' if V6 else 'v4 第 0、1 帧，Codex 关键帧第 3 帧（手臂横扫）×2，第 5 帧（前指）×2。') + 'H3 把两个切镜各晚了一帧：第 6 帧用 v4 第 7 帧，'
        '第 12 帧用 v4 第 13 帧。原片原音。')))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, flush=True)


if __name__ == '__main__':
    main()
