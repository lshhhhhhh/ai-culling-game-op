"""070: the toy-block tower built from paperclip wire - H3 with three Codex keyframes (PLAN; registered as 待推理, run only when asked).

Source (frames 1188-1217, 29 frames): grey monochrome; wooden toy blocks - cubes, arches, half-circles, cylinders - fly in from all
sides and stack up into a tower while the camera rises along it, with diagonal motion streaks and flying debris.
The user took my proposal (the paperclip maximizer builds her tower: every block the same shape bent from thick silver wire) and said:
“你先把070的方案记下来，变成待推理。但是这个画面和原版区别很大，我担心模型会处理不好，如果不好可以考虑别的方案，比如纯粹的图生视频，
完全用关键帧不用参考视频”. Keyframes 0, 14 and 28 (codex_keyframes_0006.py) serve both this plan and that fallback (first/last
frame to video without the source; our pipeline has no such workflow yet).
Usage: render_070_kf.py --queue | render_070_kf.py (only after the user says to run)
"""
import sys

from PIL import Image

import render_batch_0002 as b2
import render_shot as runner
from common import PROD, ROOT, p
from gpu import wait_cool

UID, REV = '070', 'clip_tower_kf_h3_v1'
KF = ROOT / 'deliverables/jujutsu/关键帧'
SEED = 2610017070
LABEL = '积木搭塔→回形针银丝搭的塔（形状、运动不变；Codex 关键帧第 0/14/28 帧）'
KEYFRAMES = [('kf_070_f000_clip_tower_v1.png', 0), ('kf_070_f014_clip_tower_v1.png', 14), ('kf_070_f028_clip_tower_v1.png', 28)]


def prompt(g):
    t = [b2.t(local, UID) for _, local in KEYFRAMES]
    return '\n'.join([
        'subject_definitions:',
        f'<Picture 1> is the keyframe of [Shot 1] at {t[0]}: the exact first frame of <Video 1> with every wooden block rebuilt from bent '
        'silver wire - open wireframe cubes, arches, half-circles and cylinders made of looped wire like giant paperclips.',
        f'<Picture 2> is the keyframe of [Shot 1] at {t[1]}: the exact frame of <Video 1> at that moment with every block rebuilt from bent silver wire.',
        f'<Picture 3> is the keyframe of [Shot 1] at {t[2]}: the exact last frame of <Video 1> with every block rebuilt from bent silver wire.',
        '<Video 1> is the source video for the target video edit: grey monochrome; wooden toy blocks - cubes, arches, half-circles and '
        'cylinders - fly in from all sides and stack up into a tower while the camera rises along it, with diagonal motion streaks and flying debris.',
        '',
        'summary:',
        '[video editing + keyframe completion] The target video is an edited version of <Video 1> in which every wooden toy block is the same '
        'shape built from thick bent silver wire like giant paperclips, so the tower that stacks up is a tower of paperclip wire; the motion, '
        'the camera and the timing preserve <Video 1>.',
        '',
        'retention_analysis:',
        *[f'<Picture {i + 1}> ([Shot 1] at {ts}): fully_preserved - at that moment the frame matches <Picture {i + 1}>: every wire block, its '
          'shape, place, size and angle, the grey palette and the streaks.' for i, ts in enumerate(t)],
        '<Video 1> (source video editing): partially_preserved - replace the material of every block; preserve each block\'s shape, path, '
        'spin and timing, the stacking of the tower, the rising camera, the diagonal motion streaks, the debris and the grey monochrome '
        'palette; the frame is never mirrored.',
        '',
        'detailed_description:',
        f'The target video keeps the 2D anime look, the grey monochrome palette and the lighting of <Video 1> over this {g / 24:.3f}-second model sequence.',
        '[Shot 1] 2D-animated, grey monochrome: blocks bent from thick, shiny silver wire - open wireframe cubes, arches, half-circles and '
        'cylinders whose edges are rounded loops of wire like giant paperclips - fly in from all sides along diagonal motion streaks, spin, '
        'and lock onto one another, stacking up into a tall see-through tower of paperclip wire while the camera rises along it.',
        'No block is wooden at any moment and there is no wood grain anywhere; every block keeps the shape, path and timing of its wooden '
        'counterpart in <Video 1>.',
        'The keyframes supply the wire blocks; the source video supplies all motion and the timing.',
        *b2.b1.TAIL]) + '\n'


def refs():
    out = []
    for name, _ in KEYFRAMES:
        ref = b2.REFS / name
        if not ref.exists():
            Image.open(KF / name).convert('RGB').resize((1024, 576), Image.LANCZOS).save(ref)
        out.append(ref)
    return out


def main():
    import msvcrt
    start, end = b2.b1.interval(UID)
    g = p.snap_frames(end - start)
    text = prompt(g)
    if '--queue' in sys.argv:
        sys.path.insert(0, str(ROOT / 'pipelines/anime_op'))
        import review_queue
        review_queue.add(PROD, UID, REV, LABEL, note='用户担心与原版差别大；若模型处理不好，备选：只用关键帧（首末帧生成），不用参考视频',
                         when='未排期', script='pipelines/jujutsu/render_070_kf.py', prompt=text, references=refs())
        print('QUEUED', UID, REV, flush=True)
        return
    job = PROD / 'shots' / UID / REV
    job.mkdir(parents=True, exist_ok=True)
    if (job / 'prompt.txt').exists():
        assert (job / 'prompt.txt').read_text(encoding='utf-8') == text
    else:
        (job / 'prompt.txt').write_text(text, encoding='utf-8')
    runner.REFERENCES[UID] = refs()
    runner.SEEDS[UID], runner.LABELS[UID] = SEED, LABEL
    runner.SHOT_OVERRIDES[UID] = dict(id=UID, start=start, end=end, frames=end - start)
    with (PROD / 'batch.lock').open('a+b') as lock:
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        runner.prepare(UID, REV)
        p.write_json(job / 'authorization.json', dict(request='用户（2026-10-02）：070 回形针搭塔方案', references=[str(r) for r in runner.REFERENCES[UID]],
                                                      visual_review='pending_user'))
        if not (job / 'validation.json').exists():
            wait_cool()
        sys.argv = [__file__, '--shot', UID, '--revision', REV]
        runner.main()
    print('DONE', job, flush=True)


if __name__ == '__main__':
    main()
