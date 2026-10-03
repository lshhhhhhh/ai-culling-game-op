"""JJK batch 16: 016b-019 with the GPT v6 design and Codex keyframes (h3 keyframe anchor method).

User (2026-10-01) on gpt6_h3_v1: “第一帧的脸部朝向不对，没有那种冲击感。要不还是用关键帧” - the source opens backlit, the head turned to the
right, a three-quarter face half in shadow with a fierce glance; H3 gave a clean, lit profile looking up. (kf v1 wrongly hid the face:
“你的参考帧是不是不对啊”.) Keyframes (codex_keyframes_0001.py): source frame 0 (backlit,
three-quarter face glancing right; v2) and 8 (the dash from behind). Shots follow the source cuts: 0-1 the backlit swing, 2-3 the hands on the hilt with sparks,
4-6 the white slash, 7-17 the dash down the red street.
"""
import sys

from PIL import Image

import render_batch_0013  # noqa: F401  (GPT6)
import render_batch_0002 as b2
from common import PROD, ROOT

KF = ROOT / 'deliverables/jujutsu/关键帧'
b2.LOG = PROD / 'batch_0016'
b2.AUTH_REQUEST = '用户（2026-10-01 晚）：016b 第一帧脸部朝向不对，没有冲击感，“要不还是用关键帧”'
t = b2.t
U = '016b-019'


def kf(name):
    out = b2.REFS / name
    if not out.exists():
        Image.open(KF / name).convert('RGB').resize((1024, 576), Image.LANCZOS).save(out)
    return out


b2.JOBS = {
    (U, 'kf_gpt6_h3_v3'): dict(seed=2610016017, label='乙骨→GPT（新设计v6）·逆光举刀、握柄火花、白色斩击、冲出（关键帧锚定v2：第0帧侧脸怒视）',
        subjects=[('GPT6', None, 'the young man in a white shirt who raises and swings a sword and then dashes forward (Yuta)')],
        preserve='the red background, the blinding backlight of the first shot, the sparks, the white slash streaks, the speed lines, the '
                 'light trails, the cuts and the timing',
        shots=[(None, 'in a flood of blinding backlight against a dark red background: <A> raises her katana high, her head turned to the right, '
                      'her face in a three-quarter view half in shadow with one fierce narrowed eye glancing to the right, her long white hair lit at the edges.'),
               (t(2, U), 'a hard cut: an extreme close-up of her hands gripping the katana\'s hilt as sparks and white light burst along the blade.'),
               (t(4, U), 'a hard cut: a huge white slash streaks across the frame, her figure blurred white inside it.'),
               (t(7, U), 'a hard cut: seen from behind, <A> dashes forward down a red street drawn with streaking lines, her katana low, leaving '
                         'trails of white light as she shrinks toward the centre of the frame.')],
        extras=["In the first shot her head and gaze point exactly where the young man's do in <Video 1>: a tense three-quarter face, half in shadow, with a fierce glance to the right."],
        keyframes=[(kf('kf_016b-019_f00_gpt6_v2.png'), t(0, U), 1, '<A> backlit with her katana raised, her three-quarter face half in shadow glancing fiercely to the right'),
                   (kf('kf_016b-019_f08_gpt6_v1.png'), t(8, U), 4, '<A> dashing down the red street, seen from behind')]),
}

if __name__ == '__main__':
    b2.main()
