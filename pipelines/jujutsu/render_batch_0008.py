"""JJK batch 8: the nameless Zenin foot soldiers (masked ninjas) -> chibi DeepSeek armies.

User rule (2026-10-01): nameless crowds may become chibi DeepSeek (“我的本意是无名路人可以这么干”; 115 note “可以替换成一片deepseek。”).
128: a continuous charge of masked ninjas in white gi and black hakama with katanas, the palette sliding into a yellow wash.
131: black-and-white masked swordsmen in a dojo, one close to the camera on the right.
"""
import sys

import render_batch_0006  # noqa: F401  (adds the chibi DeepSeek cast key DSQ)
import render_batch_0002 as b2
from common import PROD

b2.LOG = PROD / 'batch_0008'
b2.AUTH_REQUEST = '用户规则：无名路人可以换成 Q 版 DeepSeek（2026-10-01）'
ARMY = ('Every soldier is replaced by <A>: a crowd of identical chibi DeepSeek girls with big heads, long wavy hair and maid '
        'headbands, each holding a katana in the same stance and place as the soldier of <Video 1>, with her face uncovered.')

b2.JOBS = {
    ('128', 'deepseek_army_h3_v1'): dict(seed=2610010128, label='禅院家忍者阵列→一群Q版DeepSeek冲锋',
        subjects=[('DSQ', None, 'every masked ninja soldier in white gi and black hakama charging with a katana')],
        preserve='the wooden dojo, the charging formation, the camera movement and the palette sliding from natural colours into a yellow wash',
        shots=[(None, 'a wooden dojo: a whole formation of <A> charges toward the camera with katanas raised, crowding the frame from edge to edge, while the colours slide into a strong yellow wash.')],
        extras=[ARMY]),
    ('131', 'deepseek_army_grey_h3_v1'): dict(seed=2610010131, label='禅院家持刀忍者（黑白）→一群Q版DeepSeek',
        subjects=[('DSQ', 'grey', 'every masked swordsman in white gi in the black-and-white dojo, including the one close to the camera on the right')],
        preserve='the black-and-white manga rendering, the dojo with paper screens, the low camera angle and the slow movement',
        shots=[(None, 'black and white: in a dojo with paper screens, rows of <A> stand ready with long katanas, one of them close to the camera on the right raising her blade, as the camera drifts.')],
        extras=[ARMY, 'They are drawn in black, white and grey like the rest of the frame.']),
}

if __name__ == '__main__':
    if '--queue' in sys.argv:
        import review_queue
        units = [tuple(u.split('@')) for u in sys.argv[1:] if not u.startswith('--')]
        for uid, rev in units:
            spec = b2.JOBS[(uid, rev)]
            start, end = b2.b1.interval(uid)
            prompt, refs = b2.build(spec['subjects'], spec['preserve'], spec['shots'], spec.get('extras', []), b2.p.snap_frames(end - start))
            review_queue.add(PROD, uid, rev, spec['label'], note='无名路人→Q版DeepSeek（按你的规则）', when='第八批',
                             script='pipelines/jujutsu/render_batch_0008.py', prompt=prompt, references=refs)
            print('QUEUED', uid, rev, flush=True)
    else:
        b2.main()
