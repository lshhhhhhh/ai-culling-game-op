"""053 with two people added: DeepSeek sitting on the veranda edge swinging her legs, GPT swinging her katana on the grass.

User (2026-10-01) on the moss-covered-computer still: “我想加入人物。比如deepseek坐在木头台阶上面晃动双腿……然后gpt在草地上挥剑”.
The source is 4 identical frames of an empty corridor and garden. The first frame is a Codex still with both girls added
(deliverables/jujutsu/静帧/still_053p_codex_people_v1.png, codex_stills.py '053p'); H3 starts on it as a keyframe and adds the motion.
The 4 output frames are spread over the 56-frame model sequence, so they show 4 different poses - fitting the flash-cut montage.
Characters are added, not replaced, so the prompt is written here in the official format instead of render_batch_0002.build.
"""
import sys

from PIL import Image

import render_batch_0013  # noqa: F401  (GPT6)
import render_batch_0002 as b2
import render_shot as runner
from common import PROD, ROOT, p
from gpu import wait_cool

# v2: the user on the v1 keyframe: “为什么gpt也有一个鲸鱼耳朵？而且如果静止帧就有“剑光”的特效（都弯曲了），我怕模型不能很好理解”
V2 = '--v2' in sys.argv
UID, REV = '053', 'people_kf_h3_v2' if V2 else 'people_kf_h3_v1'
STILL = ROOT / 'deliverables/jujutsu/静帧' / ('still_053p2_codex_people_v2.png' if V2 else 'still_053p_codex_people_v1.png')
SEED = 2610017054 if V2 else 2610017053
LABEL = '日式回廊与庭院：DeepSeek 坐在回廊边晃腿，GPT 在草地上挥刀（Codex 首帧＋H3）' + ('（v2：GPT 无鲸鱼耳、首帧无剑光）' if V2 else '')


def prompt(g):
    ds, gpt = b2.CAST['DS'][1], b2.CAST['GPT6'][1]
    return '\n'.join([
        'subject_definitions:',
        f'<Subject 1> is DeepSeek from <Picture 1>: {ds}.',
        f'<Subject 2> is GPT from <Picture 2>: {gpt}.',
        '<Picture 3> is the keyframe of [Shot 1] at 00:00.000: the first frame of the target video, with <Subject 1> sitting on the edge '
        'of the veranda floor and <Subject 2> ' + ('holding her katana raised, ready to swing' if V2 else 'swinging her katana') + ' on the grass.',
        '<Video 1> is the source video for the target video edit: a still view along a wooden veranda corridor out onto a garden.',
        '',
        'summary:',
        '[video editing + reference generation + keyframe completion] The target video is an edited version of <Video 1> that starts on '
        '<Picture 3>: two characters are added to the empty scene - <Subject 1> sits on the edge of the veranda floor swinging her legs and '
        '<Subject 2> practises sword swings on the grass - while the corridor, the garden, the old moss-covered computer, the light and the '
        'still camera stay as they are.',
        '',
        'retention_analysis:',
        '<Subject 1> (appears in [Shot 1]): fully_preserved - identity, face, hair and clothing come from <Picture 1>.',
        '<Subject 2> (appears in [Shot 1]): fully_preserved - identity, face, hair and clothing come from <Picture 2>.',
        '<Picture 3> ([Shot 1] first frame at 00:00.000): fully_preserved - the opening frame matches <Picture 3>: the positions, sizes and '
        'poses of both girls, the old computer and the whole scene.',
        '<Video 1> (source video editing): partially_preserved - the wooden corridor, the garden, the light and the still camera; the frame '
        'is never mirrored.',
        '',
        'detailed_description:',
        f'The target video keeps the soft, muted 2D anime look and the lighting of <Video 1> over this {g / 24:.3f}-second model sequence.',
        '[Shot 1] 2D-animated, the still camera looks along a dim wooden veranda corridor out onto a sunlit garden with an old moss-covered '
        'computer: <Subject 1> sits on the edge of the veranda floor in the lower middle-right, happily swinging both legs back and forth '
        'over the edge, and <Subject 2> stands on the grass to the right of the computer, swinging her katana in two quick strokes'
        + ('.' if V2 else ', a faint white streak trailing the blade.'),
        'The camera does not move; apart from the two girls only the leaves sway a little.',
        'The reference pictures <Picture 1> and <Picture 2> supply appearance only; <Picture 3> supplies the opening composition.',
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
    kf = b2.REFS / 'kf_053_people_v1.png'
    if not kf.exists():
        Image.open(STILL).convert('RGB').resize((1024, 576), Image.LANCZOS).save(kf)
    runner.REFERENCES[UID] = [b2.ref('DS'), b2.ref('GPT6'), kf]
    runner.SEEDS[UID], runner.LABELS[UID] = SEED, LABEL
    runner.SHOT_OVERRIDES[UID] = dict(id=UID, start=start, end=end, frames=end - start)
    with (PROD / 'batch.lock').open('a+b') as lock:
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        runner.prepare(UID, REV)
        p.write_json(job / 'authorization.json', dict(request='用户：053 加入人物，DeepSeek 坐在木头台阶上晃腿，GPT 在草地上挥剑（2026-10-01）',
                                                      references=[str(r) for r in runner.REFERENCES[UID]], visual_review='pending_user'))
        if '--prepare-only' in sys.argv:
            print('PREPARED', job, g, flush=True)
            return
        if not (job / 'validation.json').exists():
            wait_cool()
        sys.argv = [__file__, '--shot', UID, '--revision', REV]
        runner.main()
    print('DONE', job, flush=True)


if __name__ == '__main__':
    main()
