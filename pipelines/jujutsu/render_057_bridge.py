"""057 clean_gpu_h3_v1 + a bridge: regenerate only frames 92-114 so the falling object is the graphics card from its first appearance.

User (2026-10-02) on clean_gpu_h3_v1: “哪里有显卡？显卡只有最后一帧出现了，前面完全没变。除了这个以外，标题什么的几乎完美”.
As 001's bridge (render_001_bridge.py): keep that clip's frames 0-91, regenerate 92-114 (23 frames, 56 model frames, present mode)
with that clip's own frame 92 as the first keyframe and its frame 114 (already the card) as the last, plus the card at 98, 104 and
109 (codex_keyframes_0005.py); crossfade 92-94 into the bridge, then lay the title over the joined clip again (title_057_v3.py).
v2: the user on v1: “还是有炸弹的画面啊？是不是你关键帧的位置放晚了？” - yes: the bomb is there from about frame 87 (dark red, which
my black-pixel test missed), so frames 87-91 kept it and v1's first keyframe (frame 92) still showed it. v2 starts at 82, before the
bomb, with the card at 88, 93, 98 and 109 (104 dropped to keep six pictures) and crossfades 82-84.
"""
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image

import render_batch_0002 as b2
import render_shot as runner
import title_057_v3
from common import PROD, ROOT, p
from gpu import wait_cool
from title_057 import frames

UID, REV = '057', 'gpu_bridge_h3_v2'
B0, B1 = 82, 115
FADE = (82, 85)
MAIN = PROD / 'shots/057/clean_gpu_h3_v1'
KF = ROOT / 'deliverables/jujutsu/关键帧'
KEYFRAMES = [('base_057_f082.png', 82), ('kf_057_f088_bridge_gpu_v2.png', 88), ('kf_057_f093_bridge_gpu_v2.png', 93),
             ('kf_057_f098_bridge_gpu_v2.png', 98), ('kf_057_f109_bridge_gpu_v2.png', 109), ('base_057_f114.png', 114)]
SEED = 2610019082
LABEL = '标题→「模型回战」＋炸弹→显卡（无字底片＋第 82–114 帧桥接重做 v2：炸弹第 87 帧就出现，桥接提前到出现之前；标题 CPU 叠加）'


def ts(local, g):
    n = B1 - B0
    return f'00:{np.floor((local - B0) * (g - 1) / (n - 1) + .5) / 24:06.3f}'


def prompt(g):
    t = [ts(local, g) for _, local in KEYFRAMES]
    return '\n'.join([
        'subject_definitions:',
        f'<Picture 1> is the keyframe of [Shot 1] at {t[0]}: the exact first frame of the target video - the city dissolving into the '
        'dark red sky with black cloud streaks and the black eclipsed sun, with no text and nothing falling yet.',
        f'<Picture 2> is the keyframe of [Shot 1] at {t[1]}: a black graphics card with round fans, tiny and far away, appearing in the upper '
        'right where <Video 1> shows the bomb.',
        f'<Picture 3> is the keyframe of [Shot 1] at {t[2]}: the same graphics card, a little larger.',
        f'<Picture 4> is the keyframe of [Shot 1] at {t[3]}: the same graphics card, larger and closer.',
        f'<Picture 5> is the keyframe of [Shot 1] at {t[4]}: the same graphics card, larger still, diving toward the lower left.',
        f'<Picture 6> is the last frame of [Shot 1] at {t[5]}: the same graphics card, huge and close to the camera.',
        '<Video 1> is the source video for the target video edit: a gold title over a city dissolving into a dark red sky with a black '
        'eclipsed sun; a bomb appears in the upper right and dives toward the camera while the title fades out.',
        '',
        'summary:',
        '[video editing + keyframe completion] The target video is an edited version of <Video 1> without any text, in which the falling bomb '
        'is a black graphics card with round fans in every frame where it is visible; [Shot 1] starts on <Picture 1> and ends on <Picture 6>.',
        '',
        'retention_analysis:',
        f'<Picture 1> ([Shot 1] first frame at {t[0]}): fully_preserved - the opening frame matches <Picture 1>: the sky, the clouds, the sun.',
        *[f'<Picture {k + 2}> ([Shot 1] at {t[k + 1]}): fully_preserved - at that moment the frame matches <Picture {k + 2}>: the graphics '
          'card, its size, place and angle, and the sky.' for k in range(4)],
        f'<Picture 6> ([Shot 1] last frame at {t[5]}): fully_preserved - the final frame matches <Picture 6>: the huge graphics card and the sky.',
        '<Video 1> (source video editing): partially_preserved - remove the text and replace the bomb; preserve the end of the dissolve, the red sky, the black cloud '
        'streaks, the eclipsed sun, the path, speed, tumbling and growth of the falling object, and the timing; the frame is never mirrored.',
        '',
        'detailed_description:',
        f'The target video keeps the 2D TV-anime style, the colour grading and the lighting of <Video 1> over this {g / 24:.3f}-second model sequence.',
        '[Shot 1] 2D-animated, the last of the city dissolves into a dark red sky streaked with black clouds and a black eclipsed sun ringed '
        'in glowing red at the left, with no text. A tiny black graphics card appears in the upper right and falls toward the camera, growing larger and larger as it tumbles '
        'toward the lower left, its round fans, metal bracket and gold contacts catching the dark red light, until it fills the right half of the frame.',
        'There is no text anywhere in the frame. The falling object is the graphics card of the keyframes from its very first appearance - '
        'never a bomb: no fins, no rounded nose, no cylinder.',
        'The keyframes supply the graphics card; the source video supplies the motion and the timing.',
        *b2.b1.TAIL]) + '\n'


def compose(bridge_dir):
    base = frames(MAIN / 'native_fullframe.mp4')
    bridge = frames(bridge_dir / 'native_fullframe.mp4')
    n = len(base)
    assert n == B1 and len(bridge) == B1 - B0, (n, len(bridge))
    out = []
    for i in range(n):
        if i < FADE[0]:
            out.append(base[i])
        elif i < FADE[1]:
            w = (i - FADE[0] + 1) / (FADE[1] - FADE[0] + 1)
            out.append(np.clip(base[i] * (1 - w) + bridge[i - B0] * w, 0, 255).astype(np.uint8))
        else:
            out.append(bridge[i - B0])
    dest = PROD / 'shots' / UID / f'{REV}_joined'
    dest.mkdir(parents=True, exist_ok=True)
    full = dest / 'source_exact_with_audio.mp4'
    if not full.exists():
        shutil.copy2(MAIN / 'source_exact_with_audio.mp4', full)
    silent = dest / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(n), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(out).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    titled = title_057_v3.postprocess(dest, silent, n)
    clip = dest / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', titled, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    runner.configure(dest)
    check = runner.batch.validate_output(clip, n, True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    parts = [dict(label='H3 无字底片：第 0–91 帧（关键帧第 0/40/88 帧去字）', workflow=str(MAIN / 'workflow.json'), workflow_sha256=p.sha(MAIN / 'workflow.json')),
             dict(label=f'H3 显卡桥接 v2：第 {B0}–{B1 - 1} 帧（首帧＝底片第 82 帧，末帧＝底片第 114 帧，第 88/93/98/109 帧 Codex 显卡关键帧）',
                  workflow=str(bridge_dir / 'workflow.json'), workflow_sha256=p.sha(bridge_dir / 'workflow.json'))]
    record = dest / 'multistage.json'
    p.write_json(record, dict(kind='h3_multistage', parts=parts, postprocessing=str(dest / 'title_compositing.json'), note=(
        f'第 0–{B0 - 1} 帧为无字底片；第 {FADE[0]}–{FADE[1] - 1} 帧淡入桥接；之后为桥接。标题「模型回战」与副标题由 CPU 叠加'
        '（title_057_v3.py，参数见同目录 title_compositing.json），原片原音。')))
    p.write_json(dest / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    return clip


def main():
    import msvcrt
    job = PROD / 'shots' / UID / REV
    start, _ = b2.b1.interval(UID)
    g = p.snap_frames(B1 - B0)
    text = prompt(g)
    if '--prompt-only' in sys.argv:
        print(text)
        return
    job.mkdir(parents=True, exist_ok=True)
    if (job / 'prompt.txt').exists():
        assert (job / 'prompt.txt').read_text(encoding='utf-8') == text
    else:
        (job / 'prompt.txt').write_text(text, encoding='utf-8')
    refs = []
    for name, _ in KEYFRAMES:
        out = b2.REFS / name
        if not out.exists():
            Image.open(KF / name).convert('RGB').resize((1024, 576), Image.LANCZOS).save(out)
        refs.append(out)
    runner.REFERENCES[UID] = refs
    runner.SEEDS[UID], runner.LABELS[UID] = SEED, LABEL
    runner.SHOT_OVERRIDES[UID] = dict(id=UID, start=start + B0, end=start + B1, frames=B1 - B0)
    runner.register = lambda job, sid: None  # registered only as the joined 115-frame unit
    with (PROD / 'batch.lock').open('a+b') as lock:
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        runner.prepare(UID, REV)
        p.write_json(job / 'authorization.json', dict(request='用户（2026-10-02）：057 “哪里有显卡？显卡只有最后一帧出现了，前面完全没变。除了这个以外，标题什么的几乎完美”',
                                                      references=[str(r) for r in refs], interval=[B0, B1], visual_review='pending_user'))
        if not (job / 'validation.json').exists():
            wait_cool()
        sys.argv = [__file__, '--shot', UID, '--revision', REV]
        runner.main()
    print('DONE', compose(job), flush=True)


if __name__ == '__main__':
    main()
