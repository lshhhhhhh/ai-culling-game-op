"""JJK batch 5 (2026-10-01 afternoon): the coloured-light line-up units whose people are already cast.

The user first suggested chibi DeepSeek for 091-094, then: “等下，这些好像都是角色，不是无名路人。我的本意是无名路人可以这么干。”
The line-up order (animeexplained.com AIZO breakdown): Yaga, Yuta, Ranta Zenin, Gakuganji, Choso, Higuruma, Itadori,
Kusakabe, Reggie, Megumi, Panda, Maki, Jinichi Zenin, Hakari, Kirara, Yuki (, Ogi Zenin); it matches our cuts:
091 Yaga | 092 Yuta | Ranta (cut at 8) | 093 Gakuganji | 094 Choso | Higuruma (8) | Itadori (14) | 095-097 Kusakabe | 098 Reggie |
Megumi | Panda | 099 Maki | 100 Jinichi | 101 Hakari, Kirara, Yuki, Ogi (uncertain).
Here: 091 (Ma), 092 (GPT for Yuta; Ranta, not cast, stays), 094 (GLM, Claude, DeepSeek). Each shot is one coloured light on
black, so references are tinted to that light (tones.tint, same idea as the red-and-black references the user approved);
Itadori's shot is near full colour in orange light, so his reference stays in colour.
"""
import sys

import render_batch_0003  # noqa: F401  (adds GLM to the cast)
import render_batch_0002 as b2
from common import PROD

b2.LOG = PROD / 'batch_0005'
b2.AUTH_REQUEST = '用户（2026-10-01 下午）：等下，这些好像都是角色，不是无名路人（091-094 按已定选角做，未定的保留原样）'
t = b2.t

b2.JOBS = {
    ('091', 'ma_tint_h3_v1'): dict(seed=2610010091, label='夜蛾→马化腾·绿光登场',
        subjects=[('MA', 'tint_8FCC80', 'the big muscular man lit in green, with a small doll beside him (Yaga)')],
        preserve='the black background, the single green light, the small doll on the right and the slow movement',
        shots=[(None, 'a black background: <A> stands in the centre-left of the frame lit entirely in green light, shoulders squared, while a small doll floats on the right.')],
        extras=['His short black hair, glasses and long coat show in the green light, where <Video 1> shows the muscular man.']),
    ('092', 'gpt_tint_h3_v1'): dict(seed=2610010092, label='乙骨→GPT·蓝光登场（之后的兰太保留原样）',
        subjects=[('GPT', 'tint_70A1B9', 'the young man in a white shirt lit in blue in the first shot (Yuta)')],
        preserve='the black background, the blue light of the first shot, and the second shot exactly as it is: the wild-haired man in a white jacket and red belt lit in red, spreading his hands toward the camera',
        shots=[(None, 'a black background: <A> stands in the centre of the frame lit in pale blue light, her arms folded in front of her chest.'),
               (t(8, '092'), 'a hard cut: the wild-haired man in a white jacket lit in red light spreads both hands toward the camera, unchanged from <Video 1>.')],
        extras=['Her long wavy hair shows in the blue light, in place of the short dark hair of <Video 1>.']),
    ('094', 'glm_cl_ds_tint_h3_v1'): dict(seed=2610010094, label='胀相/日车/虎杖→GLM/Claude/DeepSeek·紫/青/橙光登场',
        subjects=[('GLM', 'tint_8758B9', 'the figure lit in violet spreading huge hands and wing-like shapes in the first shot (Choso)'),
                  ('CL', 'tint_4E8C98', 'the man in a suit raising a glowing sword in teal light in the second shot (Higuruma)'),
                  ('DS', None, 'the young man with spiky hair and a red scarf holding a burning fist in orange light in the third shot (Itadori)')],
        preserve='the black background and the single coloured light of each shot: violet, then teal, then orange with fire',
        shots=[(None, 'a black background: <A> is lit entirely in violet in the centre of the frame, spreading huge hands and wing-like shapes out to both sides.'),
               (t(8, '094'), 'a hard cut: <B> stands in the centre of the frame lit in teal, raising a glowing sword straight up in front of her.'),
               (t(14, '094'), 'a hard cut: <C> is lit in orange on the right of the frame, holding up a fist wrapped in fire on the left and looking at the camera.')]),
}

if __name__ == '__main__':
    if '--queue' in sys.argv:
        import review_queue
        units = [tuple(u.split('@')) for u in sys.argv[1:] if not u.startswith('--')]
        for uid, rev in units:
            spec = b2.JOBS[(uid, rev)]
            start, end = b2.b1.interval(uid)
            prompt, refs = b2.build(spec['subjects'], spec['preserve'], spec['shots'], spec.get('extras', []), b2.p.snap_frames(end - start))
            review_queue.add(PROD, uid, rev, spec['label'], note='彩光登场段，按已定选角（用户：这些都是角色，不是路人）', when='下午第五批',
                             script='pipelines/jujutsu/render_batch_0005.py', prompt=prompt, references=refs)
            print('QUEUED', uid, rev, flush=True)
    else:
        b2.main()
