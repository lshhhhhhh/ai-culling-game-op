"""056: the black sun crumbling into square pixels - the Codex still as the first-frame keyframe, H3 keeps the source's motion.

The user chose option 2 (“试试看2”: keep the black sun, the crumbling edge breaks into square pixels like corrupting data). I first held
the Codex still for 12 frames, judging the unit static from the mean frame difference; the user: “可是这个镜头不是静止帧啊？有一个碎开的
过程” - about 200 px change per frame inside the crumbling area (x 526-619, y 168-281), which the full-frame mean rounds to zero.
Here H3 takes the source's crumbling motion and continues it in the pixel style from <Picture 1> (no characters, so a hand-written
prompt in the official format).
"""
import sys

from PIL import Image

import render_batch_0002 as b2
import render_shot as runner
from common import PROD, ROOT, p
from gpu import wait_cool

UID, REV = '056', 'pixel_kf_h3_v1'
STILL = ROOT / 'deliverables/jujutsu/静帧/still_056_codex_still_v1.png'
SEED = 2610018056
LABEL = '黑太阳碎裂→边缘碎成方形像素并持续飘散（Codex 首帧＋H3 动起来）'


def prompt(g):
    return '\n'.join([
        'subject_definitions:',
        '<Picture 1> is the keyframe of [Shot 1] at 00:00.000: the first frame of the target video - the black sun on an orange-red '
        'background with its upper-right edge breaking apart into small square pixels and blocky digital fragments.',
        '<Video 1> is the source video for the target video edit: the same black sun, its upper-right edge crumbling into small irregular '
        'fragments that keep breaking off and drifting.',
        '',
        'summary:',
        '[video editing + keyframe completion] The target video is an edited version of <Video 1> that starts on <Picture 1>: the crumbling '
        'happens exactly as in <Video 1>, but every fragment is a small square pixel or blocky digital fragment, like corrupting data.',
        '',
        'retention_analysis:',
        '<Picture 1> ([Shot 1] first frame at 00:00.000): fully_preserved - the opening frame matches <Picture 1>: the black sun, its size, '
        'position and round outline, the orange-red background and the square pixel fragments.',
        '<Video 1> (source video editing): partially_preserved - the timing, speed and direction of the crumbling at the upper-right edge, '
        'the still camera, the black sun and the background; the frame is never mirrored.',
        '',
        'detailed_description:',
        f'The target video keeps the flat 2D anime rendering of <Video 1> over this {g / 24:.3f}-second model sequence.',
        '[Shot 1] 2D-animated, a black sun hangs in front of a flat orange-red background; at its upper-right edge, small square pixels and '
        'blocky fragments keep breaking away from the sphere and drifting slowly outward to the upper right, a few glowing faintly red at '
        'their edges, at the same pace as the crumbling in <Video 1>.',
        'The camera does not move. The rest of the sphere and the background stay perfectly still; no organic shards, only square pixels.',
        *b2.b1.TAIL]) + '\n'


def main():
    import msvcrt
    job = PROD / 'shots' / UID / REV
    job.mkdir(parents=True, exist_ok=True)
    start, end = b2.b1.interval(UID)
    g = p.snap_frames(end - start)
    text = prompt(g)
    if (job / 'prompt.txt').exists():
        assert (job / 'prompt.txt').read_text(encoding='utf-8') == text
    else:
        (job / 'prompt.txt').write_text(text, encoding='utf-8')
    kf = b2.REFS / 'kf_056_pixel_v1.png'
    if not kf.exists():
        Image.open(STILL).convert('RGB').resize((1024, 576), Image.LANCZOS).save(kf)
    runner.REFERENCES[UID] = [kf]
    runner.SEEDS[UID], runner.LABELS[UID] = SEED, LABEL
    runner.SHOT_OVERRIDES[UID] = dict(id=UID, start=start, end=end, frames=end - start)
    with (PROD / 'batch.lock').open('a+b') as lock:
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        runner.prepare(UID, REV)
        p.write_json(job / 'authorization.json', dict(request='用户：056 选方案 2；“可是这个镜头不是静止帧啊？有一个碎开的过程”（2026-10-01）',
                                                      references=[str(kf)], visual_review='pending_user'))
        if not (job / 'validation.json').exists():
            wait_cool()
        sys.argv = [__file__, '--shot', UID, '--revision', REV]
        runner.main()
    print('DONE', job, flush=True)


if __name__ == '__main__':
    main()
