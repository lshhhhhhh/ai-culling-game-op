"""JJK batch 10: roles identified on 2026-10-01 evening that already have designs.

User: “124-125就是乐岩寺嘉伸 129随便安排一点角色吧不深究了 133应该是日下部和他的妹妹 141就是高羽史彦 102是禅院直哉”; earlier
notes: 088 “虎杖没有替换”, 116 “这个应该是要替换成mistral的金发女性吧”, 126 “这个是乙骨忧太啊”, 143 “伏黑惠”. The AIZO character list
(JJK Fandom wiki, via search snippets) gave 073 Itadori's mother Kaori with baby Itadori (“婴儿可以换成Q版deepseek”) and 076
Kusakabe's sister with her son Takeru. Minor roles nobody had claimed follow the user's rule (“角色不够用了就让热门角色…替换”):
Kusakabe's sister = GPT (whose long white hair matches the woman in 133's wheelchair), her son = chibi DeepSeek; 129's two
unnamed players = Grok and Mistral; 142 is Takaba again. 085 shows only Megumi small in the street; Remi is not visible.
"""
import sys

import render_batch_0006  # noqa: F401  (chibi DeepSeek key DSQ)
import render_batch_0007  # noqa: F401  (MUSK, LIANG and the Doubao keys)
import render_batch_0002 as b2
from common import PROD

b2.LOG = PROD / 'batch_0010'
b2.AUTH_REQUEST = '用户（2026-10-01 晚）：124-125 乐岩寺、129 随便安排、133 日下部和妹妹、141 高羽；审阅页备注 088、116、126、143'
t = b2.t
FLAT = 'the flat cartoon style of <Video 1>: thick coloured outlines, flat fills and the wavy colour-band background'

b2.JOBS = {
    ('124-125', 'musk_h3_v1'): dict(seed=2610010124, label='乐岩寺→马斯克·拼贴前正面（替换误认的羂索版）',
        subjects=[('MUSK', None, 'the large hooded figure facing the camera in a dark robe patterned with thin red lines (Gakuganji)')],
        preserve='the white sunburst background of the first shot, the collage of the second shot with flat poster colour blocks, a red rising sun and paper cut-outs, and the fixed camera',
        shots=[(None, 'a white sunburst background: <A> stands facing the camera in the centre of the frame in a dark robe patterned with thin red lines, a small emblem above his head.'),
               (t(7, '124-125'), 'a hard cut: the same framing of <A>, now in front of a collage of flat poster-like colour blocks, a red rising sun and paper cut-outs that keep appearing around him.')],
        extras=['His face is visible beneath the hood: short swept-back hair and a broad grin, where <Video 1> hides the face.']),
    ('133', 'liang_gpt_h3_v1'): dict(seed=2610010133, label='日下部与妹妹→梁文锋推着坐轮椅的GPT·林间',
        subjects=[('LIANG', None, 'the man in black pushing the wheelchair (Kusakabe)'),
                  ('GPT', None, 'the white-haired woman in a pale hooded robe sitting in the wheelchair (Kusakabe\'s sister)')],
        preserve='the sunlit green forest, the wheelchair, the slow walk toward the camera and the slow push-in',
        shots=[(None, 'a sunlit green forest: <A> slowly pushes a wheelchair toward the camera, and <B> sits in it wrapped in a pale hooded robe, her hands in her lap.'),
               (t(21, '133'), 'a hard cut: a closer view of the two of them in the same forest.')]),
    ('141', 'minimax_flat_h3_v1'): dict(seed=2610010141, label='高羽→MiniMax·扁平卡通看手机',
        subjects=[('MMX', None, 'the man drawn as a flat blue-outlined cartoon face looking at his phone (Takaba)')],
        preserve=FLAT + ', the phone at the lower left and the blue and lilac palette',
        shots=[(None, 'a flat cartoon: <A>\'s face, drawn with thick blue outlines, looks down at a phone at the lower left with half-closed eyes, over wavy blue and lilac colour bands.')],
        extras=['She is drawn in the same flat cartoon style, keeping her short hair and cap as simple shapes.']),
    ('142', 'minimax_flat_h3_v1'): dict(seed=2610010142, label='高羽→MiniMax·扁平卡通惊叫掉手机',
        subjects=[('MMX', None, 'the man drawn as a flat red-outlined cartoon face screaming as his phone falls (Takaba)')],
        preserve=FLAT + ', the falling phone at the lower left and the pink and cream palette',
        shots=[(None, 'a flat cartoon: <A>\'s face, drawn with thick red outlines, screams in shock with wide eyes and an open mouth while her phone drops at the lower left, over wavy pink and cream colour bands.')],
        extras=['She is drawn in the same flat cartoon style, keeping her short hair and cap as simple shapes.']),
    ('073', 'ds_mother_baby_h3_v1'): dict(seed=2610010073, label='虎杖香织与婴儿虎杖→DeepSeek母亲与Q版DeepSeek婴儿·席勒',
        subjects=[('DS', None, 'the dark, gaunt mother wrapped around the baby (Kaori Itadori)'), ('DSQ', None, 'the baby curled in the middle (baby Itadori)')],
        preserve='the dark expressionist painting style of Egon Schiele\'s Dead Mother, the black surroundings, the bony hands and the still frame',
        shots=[(None, 'a dark expressionist painting in the style of Egon Schiele: <A> curls around a glowing baby, her pale face in shadow at the left and her bony hands at the right, and in the middle the baby <B> sleeps curled up; the image holds still.')],
        extras=['Both are painted with the same rough brush strokes and dark palette as <Video 1>.']),
    ('076', 'gpt_takeru_h3_v1'): dict(seed=2610010076, label='日下部的妹妹与儿子武→GPT与Q版DeepSeek·珂勒惠支铅笔素描',
        subjects=[('GPT', None, 'the mother hugging the child tightly (Kusakabe\'s sister)'), ('DSQ', None, 'the small child held in her arms (Takeru)')],
        preserve='the pencil sketch style of Kathe Kollwitz on beige paper, the trembling redrawn lines and the slow push-in',
        shots=[(None, 'a pencil sketch on beige paper in the style of Kathe Kollwitz, its lines redrawn every frame: <A> hugs the small child <B> tightly against her cheek, eyes closed, as the camera slowly pushes in.')],
        extras=['Both are drawn in the same grey pencil lines on beige paper as <Video 1>.']),
    ('085', 'claude_h3_v1'): dict(seed=2610010085, label='伏黑惠→Claude·夜晚Y字路口（横尾忠则）',
        subjects=[('CL', None, 'the small figure standing in the street at the fork (Megumi)')],
        preserve='the oil-painting look of Tadanori Yokoo\'s Y-junction series, the night street, the tall narrow building at the fork and the still camera',
        shots=[(None, 'an oil-painted night street splitting in a Y around a tall narrow building: <A> stands small in the street on the right, under the street light.')]),
    ('129', 'grok_mistral_h3_v1'): dict(seed=2610010129, label='死灭回游玩家二人→Grok与Mistral·彩色天空飞跃',
        subjects=[('GROK', None, 'the shirtless wild-haired man leaping on the left'), ('MIS', None, 'the man in a white top leaping on the right')],
        preserve='the colourful pastel sky with pink, yellow and green clouds, the town far below and the leap',
        shots=[(None, 'a colourful pastel sky over a town: <A> on the left and <B> on the right leap through the air side by side, fists forward.')]),
    ('088', 'deepseek_h3_v1'): dict(seed=2610010088, label='虎杖→DeepSeek·双手合十举过头顶（绿描边紫底）',
        subjects=[('DS', None, 'the young man pressing his hands together and raising them above his head (Itadori)', (1,))],
        preserve='the magenta-to-violet background, the pale green outline light, the upward tilt and the final cut to the dark sphere on red',
        shots=[(None, 'a magenta background turning violet, the figure outlined in pale green light: the camera tilts up from <A>\'s chest as she presses her hands together in front of her and raises them high above her head, her long hair and headband in silhouette.'),
               (t(29, '088'), 'a hard cut: a dark sphere hangs in a red field; no person.')]),
    ('116', 'mistral_h3_v1'): dict(seed=2610010116, label='金发女性→Mistral·红色逆光举手',
        subjects=[('MIS', None, 'the blonde woman in a sleeveless top silhouetted in red backlight with one arm raised')],
        preserve='the deep red backlight, the rim light on her hair and arm and the slow movement',
        shots=[(None, 'deep red backlight: <A> stands in silhouette in the centre of the frame with one arm raised high, her long golden hair lit at the edges, her head slightly bowed.')]),
    ('126', 'gpt_grey_h3_v1'): dict(seed=2610010126, label='乙骨→GPT·黑白持刀与拼贴',
        subjects=[('GPT', 'grey', 'the young man in white drawing a long sword (Yuta)')],
        preserve='the black-and-white manga rendering, the long sword across the frame and the collage panels that keep appearing',
        shots=[(None, 'black and white: <A> holds a long sword across the frame with a fierce look, while small collage panels - an empty chair, a pair of hands, a black frame - pop up one by one around her.')],
        extras=['She is drawn in black, white and grey like the rest of the frame.']),
    ('143', 'claude_red_h3_v1'): dict(seed=2610010143, label='伏黑惠→Claude·红光中掩面',
        subjects=[('CL', 'redblack', 'the young man covering his face with his hands in red light in the third shot (Megumi)', (3,))],
        preserve='the dark space with the small cube, the burst of debris, the red light, the red gears and the final orange light',
        shots=[(None, 'darkness: a small cube floats among rays of light.'),
               (t(5, '143'), 'a hard cut: debris bursts outward around a blue-white light.'),
               (t(11, '143'), 'a hard cut: red light: <A> covers her face with both hands, staring through her fingers.'),
               (t(20, '143'), 'a hard cut: huge red and dark gears turn; no person.'),
               (t(25, '143'), 'a hard cut: an orange light glows at the centre of a dark tunnel; no person.')],
        extras=['In the third shot she is drawn in shades of red on black like the frame.']),
}

if __name__ == '__main__':
    if '--queue' in sys.argv:
        import review_queue
        units = [tuple(u.split('@')) for u in sys.argv[1:] if not u.startswith('--')]
        for uid, rev in units:
            spec = b2.JOBS[(uid, rev)]
            start, end = b2.b1.interval(uid)
            prompt, refs = b2.build(spec['subjects'], spec['preserve'], spec['shots'], spec.get('extras', []), b2.p.snap_frames(end - start))
            review_queue.add(PROD, uid, rev, spec['label'], note='按你的识别与备注', when='第十批',
                             script='pipelines/jujutsu/render_batch_0010.py', prompt=prompt, references=refs)
            print('QUEUED', uid, rev, flush=True)
    else:
        b2.main()
