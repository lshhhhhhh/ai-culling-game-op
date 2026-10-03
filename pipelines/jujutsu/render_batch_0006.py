"""JJK batch 6 (2026-10-01 afternoon): two units from the user's review-page notes.

044 note “panda”: the roaring white face in the red web is Panda -> HY with the red gradient reference.
115 note “可以替换成一片deepseek。”: the sepia group photo of the Zenin clan (100+ people on the steps) -> a crowd of chibi
DeepSeek (assets/人设/鲸鱼娘-小.jpg). The user, on 091-094: chibi DeepSeek is for nameless crowds (“我的本意是无名路人可以这么干”).
The reference is tinted to the photo's sepia (#C5A584, measured on the source's light tones).
"""
import sys

import render_batch_0003  # noqa: F401  (adds GLM to the cast)
import render_batch_0002 as b2
from common import PROD

b2.CAST['DSQ'] = (b2.A / '鲸鱼娘-小.jpg', 'a chibi girl about two and a half heads tall with a big round head, very long wavy dark-blue hair, an ahoge, a white frilled maid headband, small whale-fin ears and a navy maid dress with a white apron')
b2.LOG = PROD / 'batch_0006'
b2.AUTH_REQUEST = '用户审阅页备注：044“panda”；115“可以替换成一片deepseek。”（2026-10-01）'

b2.JOBS = {
    ('044', 'hy_red_h3_v1'): dict(seed=2610010044, label='熊猫→混元HY·红黑蛛网张嘴怒吼',
        subjects=[('HY', 'redblack', 'the panda roaring with its mouth wide open in the upper left (Panda)')],
        preserve='the red-and-black spider-web lines, the red two-tone rendering, the black background and the still frame',
        shots=[(None, 'a red-and-black two-tone image crossed by red spider-web lines: <A> roars with her mouth wide open in the upper left of the frame, head thrown back, her body sweeping down toward the lower right; the image holds still.')],
        extras=['She is drawn entirely in shades of red on black like the rest of the frame, with pale highlights on her face where <Video 1> shows the white panda face; her long hair and scarf show in her silhouette.']),
    ('115', 'deepseek_crowd_h3_v1'): dict(seed=2610010115, label='禅院家合影→一片Q版DeepSeek（旧照片）',
        subjects=[('DSQ', 'tint_C5A584', 'every person in the old group photograph: the rows of standing clan members and the seated men in the front row')],
        preserve='the old sepia photograph look, the traditional Japanese hall and its tiled roof, the stone steps, the trees and the still frame',
        shots=[(None, 'an old sepia group photograph in front of a traditional Japanese hall: rows upon rows of identical <A> fill the steps in the same neat formation as <Video 1>, all facing the camera, the front row seated on chairs; the image holds still.')],
        extras=['Every single person in the photograph is replaced by <A>: well over a hundred chibi DeepSeek girls with big heads, long wavy hair and maid headbands, small and evenly spaced like the people of <Video 1>.',
                'They are tinted in the same faded sepia as the rest of the photograph.']),
}

if __name__ == '__main__':
    if '--queue' in sys.argv:
        import review_queue
        units = [tuple(u.split('@')) for u in sys.argv[1:] if not u.startswith('--')]
        for uid, rev in units:
            spec = b2.JOBS[(uid, rev)]
            start, end = b2.b1.interval(uid)
            prompt, refs = b2.build(spec['subjects'], spec['preserve'], spec['shots'], spec.get('extras', []), b2.p.snap_frames(end - start))
            review_queue.add(PROD, uid, rev, spec['label'], note='按你在审阅页的备注', when='下午第六批',
                             script='pipelines/jujutsu/render_batch_0006.py', prompt=prompt, references=refs)
            print('QUEUED', uid, rev, flush=True)
    else:
        b2.main()
