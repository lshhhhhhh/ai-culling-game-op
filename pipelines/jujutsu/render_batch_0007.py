"""JJK batch 7: the coloured-light line-up roles cast on 2026-10-01 afternoon (designs by codex_designs_0002.py).

Casting (user): Gakuganji = Elon Musk, Kusakabe = Liang Wenfeng (“学校的管理层用企业家”); every Zenin clan villain = Doubao in her
official avatar's 3D look with a different costume each (“反派用豆包吧……可以让她饰演全部禅院家反派，然后做出差异化设计”); Reggie = Grok.
Units: 092 v2 (Yuta + Ranta), 093 Gakuganji, 095-097 Kusakabe (batch 3 wrongly made it Yuta/GPT), 098 v2 (Reggie + Megumi +
Panda), 100 Jinichi, 101 (Hakari, Kirara, Tsukumo with her long shikigami, an unidentified 2-frame figure kept, Ogi).
Every shot is one coloured light on black, so each reference is tinted to the colour measured on that shot.
Run only after the user has seen the five designs.
"""
import sys

import render_batch_0003  # noqa: F401  (adds GLM to the cast)
import render_batch_0002 as b2
from common import PROD

D = b2.D
b2.CAST.update({
    'DB_OGI': (D / 'doubao_zenin_ogi_v1.png', 'a young woman with a smooth chocolate-brown chin-length bob, large glossy brown eyes and soft rounded 3D-rendered features, in a black formal crested kimono and grey striped hakama, holding a long katana wreathed in flame'),
    'DB_JIN': (D / 'doubao_zenin_jinichi_v1.png', 'a sturdy young woman with a smooth chocolate-brown chin-length bob, large glossy brown eyes and soft rounded 3D-rendered features, in a heavy dark-brown kimono with tied-back sleeves and huge grey stone fists'),
    'DB_RANTA': (D / 'doubao_zenin_ranta_v1.png', 'a young woman with a tousled chocolate-brown chin-length bob, large glossy brown eyes and soft rounded 3D-rendered features, in a white martial-arts gi with a red sash, dark red hakama and a white headband with an eye emblem'),
    'MUSK': (D / 'musk_gakuganji_v1.png', 'a man with short swept-back hair and a broad grin, in a dark formal kimono with a grey haori and hakama, with an electric guitar'),
    'LIANG': (D / 'liang_kusakabe_v1.png', 'a calm man with short black hair and glasses, in a long dark coat over a dark suit, with a katana at his hip'),
})
b2.NAMES.update({'DB_OGI': 'Doubao', 'DB_JIN': 'Doubao', 'DB_RANTA': 'Doubao', 'MUSK': 'the cartoon of Elon Musk',
                 'LIANG': 'the cartoon of Liang Wenfeng'})
b2.LOG = PROD / 'batch_0007'
b2.AUTH_REQUEST = '用户（2026-10-01 下午）：学校管理层用企业家；反派用豆包，饰演全部禅院家反派并差异化设计；可以生图'
t = b2.t
DOUBAO_LOOK = 'keeps the soft 3D-rendered look of <Picture {n}> - smooth CG shading and big glossy eyes - standing out from the 2D anime around her'

b2.JOBS = {
    ('092', 'gpt_doubao_tint_h3_v2'): dict(seed=2610010192, label='乙骨→GPT，兰太→豆包·蓝光/红光登场',
        subjects=[('GPT', 'tint_70A1B9', 'the young man in a white shirt lit in blue in the first shot (Yuta)', (1,)),
                  ('DB_RANTA', 'tint_C78579', 'the wild-haired man in a white jacket and red belt lit in red, spreading his hands in the second shot (Ranta)', (2,))],
        preserve='the black background and the single coloured light of each shot: pale blue, then red',
        shots=[(None, 'a black background: <A> stands in the centre of the frame lit in pale blue light, her arms folded in front of her chest.'),
               (t(8, '092'), 'a hard cut: <B> is lit in red in the centre of the frame and spreads both hands wide toward the camera, staring hard.')],
        extras=['<B> ' + DOUBAO_LOOK.format(n=2) + '.']),
    ('093', 'musk_tint_h3_v1'): dict(seed=2610010093, label='乐岩寺→马斯克·金光弹电吉他',
        subjects=[('MUSK', 'tint_B0AB74', 'the bald old man in a white kimono playing an electric guitar in gold light (Gakuganji)')],
        preserve='the black background, the gold light, the red-orange electric guitar and the strumming',
        shots=[(None, 'a black background: <A> is lit in gold in the centre-left of the frame, playing a red-orange electric guitar with wild energy, leaning into the strum.')],
        extras=['His short swept-back hair and grin take the place of the bald head and beard of <Video 1>.']),
    ('095-097', 'liang_tint_h3_v1'): dict(seed=2610010295, label='日下部→梁文锋·青光中披风转身（替换误认的 GPT 版）',
        subjects=[('LIANG', 'tint_55BBB4', 'the dark-haired man in a pale long coat turning in cyan light (Kusakabe)')],
        preserve='the cyan light on black, the swirling coat and the quick two-frame smears',
        shots=[(None, 'cyan light on a black background: <A> turns sharply on the left of the frame, his long coat swirling around him, glasses glinting.')]),
    ('098', 'grok_claude_hy_tint_h3_v2'): dict(seed=2610010198, label='雷吉→Grok，伏黑惠→Claude，熊猫→HY·紫/青/绿光登场',
        subjects=[('GROK', 'tint_985CB6', 'the figure lit in violet wrapped in a skirt of fluttering paper receipts in the first shot (Reggie)', (1,)),
                  ('CL', 'tint_5C9B8F', 'the young man with spiky dark hair making a hand sign in teal light in the second shot (Megumi)', (2,)),
                  ('HY', 'tint_6CCB5A', 'the panda raising both arms in green light in the third shot (Panda)', (3,))],
        preserve='the black background and the single coloured light of each shot: violet, teal, then green',
        shots=[(None, 'a black background: <A> stands in the centre of the frame lit in violet, a skirt of fluttering paper receipts swirling around her.'),
               (t(6, '098'), 'a hard cut: <B> stands in the centre of the frame lit in teal, her hands pressed together in a hand sign in front of her chest.'),
               (t(12, '098'), 'a hard cut: <C> raises both arms high in the centre of the frame, lit in bright green, with a wide open-mouthed grin.')],
        extras=['<C> is a girl with long hair and a scarf, where <Video 1> shows the panda.']),
    ('100', 'doubao_jinichi_tint_h3_v1'): dict(seed=2610010100, label='甚壹→豆包·粉色骷髅墙前跃起',
        subjects=[('DB_JIN', 'tint_B73BA1', 'the figure leaping across the wall of pink skulls (Jinichi)')],
        preserve='the wall of glowing pink skulls, the magenta light and the diagonal motion',
        shots=[(None, 'a wall of glowing pink skulls: <A> leaps diagonally across the centre of the frame, lit in magenta, her huge stone fists swinging.')],
        extras=['<A> ' + DOUBAO_LOOK.format(n=1) + '.']),
    ('101', 'kimi_spark_mis_doubao_tint_h3_v1'): dict(seed=2610010101, label='秤/绮罗罗/九十九/扇→Kimi/Spark/Mistral/豆包·彩光依次登场',
        subjects=[('KIMI', 'tint_3C7495', 'the broad figure lit in blue spreading his arms in the first shot (Hakari)', (1,)),
                  ('SPK', 'tint_B15FA4', 'the slim figure lit in pink in the second shot (Kirara)', (2,)),
                  ('MIS', 'tint_9D9248', 'the woman lit in gold standing beneath a long spiked serpent-like shikigami in the third shot (Yuki Tsukumo)', (3,)),
                  ('DB_OGI', 'tint_AFA84D', 'the man in a kimono lit in gold who stands far away and then close to the camera in the last shot (Ogi)', (5,))],
        preserve='the black background, the single coloured light of each shot, the long spiked golden shikigami of the third shot, and the small lavender-lit figure of the fourth shot exactly as it is',
        shots=[(None, 'a black background: <A> stands in the centre of the frame lit in blue, arms spread wide.'),
               (t(4, '101'), 'a hard cut: <B> stands small in the centre of the frame lit in pink.'),
               (t(7, '101'), 'a hard cut: <C> stands lit in gold in the centre of the frame beneath a long, spiked, serpent-like golden shikigami stretching across the frame.'),
               (t(12, '101'), 'a hard cut: a small figure lit in lavender stands in the centre of the frame, unchanged from <Video 1>.'),
               (t(14, '101'), 'a hard cut: <D> stands far away in the centre of the frame lit in dim gold, then appears close on the right of the frame, gripping her katana.')],
        extras=['<D> ' + DOUBAO_LOOK.format(n=4) + '.']),
}

if __name__ == '__main__':
    if '--queue' in sys.argv:
        import review_queue
        units = [tuple(u.split('@')) for u in sys.argv[1:] if not u.startswith('--')]
        for uid, rev in units:
            spec = b2.JOBS[(uid, rev)]
            start, end = b2.b1.interval(uid)
            prompt, refs = b2.build(spec['subjects'], spec['preserve'], spec['shots'], spec.get('extras', []), b2.p.snap_frames(end - start))
            review_queue.add(PROD, uid, rev, spec['label'], note='彩光登场段：企业家／豆包／Grok（等你看过设计图）', when='第七批',
                             script='pipelines/jujutsu/render_batch_0007.py', prompt=prompt, references=refs)
            print('QUEUED', uid, rev, flush=True)
    else:
        b2.main()
