"""JJK batch 15: 020-026a again, with Codex keyframes (h3 keyframe anchor method). Registered as 待推理.

User (2026-10-01): “020大肥鱼出场的前几帧还是虎杖……远景没有替换”, then, on a frame of v1 where H3 had only turned Itadori blue (short
spiky hair, his face, his hoodie): “这一帧明显虎杖。我觉得还是要用模型”. Keyframes (codex_keyframes_0001.py): the source frames 11
(the fall, arms spread), 23 (the grey curse swooping in) and 33 (the close-up) with DeepSeek in Itadori's place. Shots follow the
source cuts: the continuous fall 0-29, the close-up 30-37 with two-frame impact jolts, the punch into the camera 38-43 with white flashes.
"""
import sys

from PIL import Image

import render_batch_0002 as b2
from common import PROD, ROOT

KF = ROOT / 'deliverables/jujutsu/关键帧'
b2.LOG = PROD / 'batch_0015'
b2.AUTH_REQUEST = '用户（2026-10-01 晚）：020 远景和这一帧明显虎杖，“我觉得还是要用模型”'
t = b2.t
U = '020-026a'


def kf(name):
    out = b2.REFS / name
    if not out.exists():
        Image.open(KF / name).convert('RGB').resize((1024, 576), Image.LANCZOS).save(out)
    return out


b2.JOBS = {
    (U, 'kf_deepseek_h3_v2'): dict(seed=2610015020, label='虎杖→DeepSeek·高空坠落、咒灵扑来、特写、出拳（关键帧锚定，远景也换）',
        subjects=[('DS', None, 'the young man with short spiky hair in an orange-lit hooded jacket who falls through the air and then punches (Itadori)')],
        preserve='the top-down view of the city drawn in flat orange and black, the dive of the camera past the building edge, the grey curse '
                 'swooping in, the two-frame impact jolts of the close-up, the white flashes of the final punch and the timing',
        shots=[(None, 'a top-down view from high above a city drawn in flat orange and black: the camera dives past a building edge over a red '
                      'ground; far below, <A> falls face-down, first a tiny speck, then larger and larger, her arms spread wide and her long hair '
                      'streaming upward; a grey curse swoops down at her from the upper left and she twists in the air to face it.'),
               (t(30, U), 'a hard cut: a close-up of <A>\'s face from above as she falls, gritting her teeth, her long hair whipping around her, '
                          'the frame jolting with two-frame impact cuts.'),
               (t(38, U), 'a hard cut: <A> punches straight at the camera, her fist filling the frame, and the image flashes white twice.')],
        extras=['She is DeepSeek in every frame, even while she is only a tiny speck far below: very long wavy dark-blue hair, the maid '
                'headband, whale-fin ears, the navy maid dress and the whale tail - never a short-haired boy in a hooded jacket.'],
        keyframes=[(kf('kf_020-026a_f11_ds_v1.png'), t(11, U), 1, '<A> falling face-down with her arms spread, seen from above'),
                   (kf('kf_020-026a_f23_ds_v1.png'), t(23, U), 1, '<A> falling small with the grey curse swooping at her'),
                   (kf('kf_020-026a_f33_ds_v1.png'), t(33, U), 2, 'the close-up of <A> gritting her teeth')]),
}

if __name__ == '__main__':
    if '--queue' in sys.argv:
        import review_queue
        for (uid, rev), spec in b2.JOBS.items():
            start, end = b2.b1.interval(uid)
            prompt, refs = b2.build(spec['subjects'], spec['preserve'], spec['shots'], spec.get('extras', []), b2.p.snap_frames(end - start),
                                    spec.get('keyframes', ()))
            review_queue.add(PROD, uid, rev, spec['label'], note='关键帧锚定重跑（远景和特写都要是 DeepSeek）', when='等你说开始',
                             script='pipelines/jujutsu/render_batch_0015.py', prompt=prompt, references=refs)
            print('QUEUED', uid, rev, [r.name for r in refs], flush=True)
    else:
        b2.main()
