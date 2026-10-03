"""JJK batch 4 (2026-10-01 afternoon): the three remaining units whose people are all cast already.

058 is the Ghost in the Shell 2nd GIG line-up: left to right Maki, Yuta, Itadori, Tengen, Tsukumo, Megumi, Choso, all seven
replaced (experimental: Lycoris 021 worked with 7 pictures and 5 replacements, 8 broke it). 098 has hard cuts at local
frames 6 and 12 (violet figure kept, Megumi, Panda). 130: Takaba in his blue-and-yellow tights, as in 081.
Usage: render_batch_0004.py --queue UNIT@REV ... | render_batch_0004.py UNIT@REV ...
"""
import sys

import render_batch_0003  # noqa: F401  (adds GLM to the cast)
import render_batch_0002 as b2
from common import PROD, ROOT

b2.CAST['JENSEN'] = (ROOT / 'deliverables/jujutsu/人设/tengen_jensen_v1.png',
                     'a smiling man with short swept-back black-and-grey hair and glasses, wearing a black leather jacket under a long white hooded robe with a thin green trim')
b2.LOG = PROD / 'batch_0004'
b2.AUTH_REQUEST = '用户（2026-10-01 白天）：现在生成的都还可以，为什么不继续做了'
t = b2.t

b2.JOBS = {
    ('058', 'lineup7_h3_v1'): dict(seed=2610010058, label='高专群像七人→Gemini/GPT/DeepSeek/黄仁勋/Mistral/Claude/GLM（实验）',
        subjects=[('GEM_MAKI', None, 'the young woman on the far left with short dark hair and glasses in a black outfit (Maki)'),
                  ('GPT', None, 'the young man second from the left in a white jacket with a long bag over his shoulder (Yuta)'),
                  ('DS', None, 'the young man third from the left with short light hair in a black hoodie (Itadori)'),
                  ('JENSEN', None, 'the tall figure in the middle in a white robe with an elongated face, arms folded (Tengen)'),
                  ('MIS', None, 'the tall woman third from the right with long blonde hair in a black leather jacket (Yuki Tsukumo)'),
                  ('CL', None, 'the young man second from the right with spiky black hair in a dark uniform (Megumi)'),
                  ('GLM', None, 'the young man on the far right with spiky tied-up hair, arms crossed, in a white top and baggy white trousers (Choso)')],
        preserve='the pale grey-white background, the long shadows cast to the left, the even spacing of the seven figures and the still camera',
        shots=[(None, 'a pale grey-white background with long shadows: seven figures stand side by side in one row facing the camera, full body, from left to right <A>, <B>, <C>, <D>, <E>, <F>, <G>; the image holds still.')],
        extras=['Each figure keeps the place, the height in the frame and the stance of the person they replace: <A> with one hand on her hip, '
                '<B> with the long bag over her shoulder, <D> with his arms folded inside the white robe, <G> with her arms crossed.',
                'All seven are drawn in the clean, softly shaded TV-anime style of <Video 1>, in muted cool tones.']),
    ('098', 'claude_hy_h3_v1'): dict(seed=2610010098, label='伏黑惠与熊猫→Claude与HY·黑底彩光登场（紫光人物保留）',
        subjects=[('CL', None, 'the young man with spiky dark hair making a hand sign in teal light (Megumi)'),
                  ('HY', None, 'the panda raising both arms in green light (Panda)')],
        preserve='the black background, the violet-lit figure of the first shot exactly as it is, and the coloured rim light of each shot',
        shots=[(None, 'a black background: a figure lit in violet stands in the centre of the frame, unchanged from <Video 1>.'),
               (t(6, '098'), 'a hard cut: <A> stands in the centre of the frame lit in teal, her hands pressed together in a hand sign in front of her chest.'),
               (t(12, '098'), 'a hard cut: <B> raises both arms high in the centre of the frame, lit in bright green, with a wide open-mouthed grin.')],
        extras=['<B> is a girl with long black-blue hair and a red scarf, where <Video 1> shows the panda.']),
    ('130', 'minimax_h3_v1'): dict(seed=2610010130, label='高羽→MiniMax·霓虹舞台群舞',
        subjects=[('MMX', None, 'the man in the centre in blue-and-yellow tights dancing (Takaba)')],
        preserve='the neon disco stage, the crowd of muscular dancers in red, the coloured lights and the camera',
        shots=[(None, 'a neon disco stage full of coloured lights: <A> dances in the centre of the frame in the middle of a crowd of muscular men in red, throwing her arms up in a comic pose.')],
        extras=['She wears blue-and-yellow tights like <Video 1>, with her short orange hair and white cap.']),
}

if __name__ == '__main__':
    if '--queue' in sys.argv:
        import review_queue
        units = [tuple(u.split('@')) for u in sys.argv[1:] if not u.startswith('--')]
        for uid, rev in units:
            spec = b2.JOBS[(uid, rev)]
            start, end = b2.b1.interval(uid)
            prompt, refs = b2.build(spec['subjects'], spec['preserve'], spec['shots'], spec.get('extras', []), b2.p.snap_frames(end - start))
            review_queue.add(PROD, uid, rev, spec['label'], note='白天第四批（选角都已定的剩余单元）', when='白天第四批',
                             script='pipelines/jujutsu/render_batch_0004.py', prompt=prompt, references=refs)
            print('QUEUED', uid, rev, flush=True)
    else:
        b2.main()
