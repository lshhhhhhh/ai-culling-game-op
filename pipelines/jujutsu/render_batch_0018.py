"""JJK batch 18: the user's review notes of 2026-10-02 02:08-02:14, run in the overnight queue (run_queue_1002.py).

User (02:15): “我准备睡觉了，开始推理队列吧。记得看我给的意见。” Notes and what each plan does:
- 087 “deepseek太壮了。需要重新跑，也许需要关键帧。” - keyframes 0/25: our own frames with DeepSeek slimmed (codex_keyframes_0007.py).
- 089 “最左边的claude应该是一脸不情愿的样子……另外几个人物也太壮了。也许需要关键帧。” - keyframes 0/26: Claude reluctant, the others slim.
- 091 “熊猫换成QQ企鹅吧。” - the doll beside Ma Huateng becomes a QQ penguin plush; keyframes 0/7.
- 103 “……做一个象征着convolution neural network的镜头？……如果模型效果不好，你可以自己用GPT画一个背景，然后自己用代码做特效。” -
  the glass panes become CNN feature maps; keyframes 8/16 (the CPU fallback is for later if this fails).
- 104 “光柱换成绿色黑客帝国式的数据流。” - no keyframe.
- 105 “改成巨大的回形针砸在地上。” - keyframes 0/12.
- 108 “这个场景没有人物。可以把白光换成数据流绿光。” - no keyframe.
- 140 “换成显卡。需要关键帧。可以用RTX3090作为模板。” - keyframes 0/8.
(084 “可以换成大肥鱼的背影。直接生图静止帧。” is a Codex still: codex_stills.py 084.)
Usage: render_batch_0018.py --queue UNIT@REV ... | render_batch_0018.py UNIT@REV ...
"""
import sys

from PIL import Image

import render_batch_0002 as b2
import copy

# first, before any other batch: batch 13 snapshots the job tables of batches 2/3/7/10/11 at import
import render_batch_0013  # noqa: F401  (GPT6 and 042's v6 plan; it sets b2.JOBS, b2.LOG and b2.AUTH_REQUEST, replaced below)
J042 = copy.deepcopy(b2.JOBS[('042', 'gpt6_h3_v1')])
J006 = copy.deepcopy(b2.JOBS[('006-016a', 'gpt6_h3_v1')])
J092 = copy.deepcopy(b2.JOBS[('092', 'gpt6_doubao_tint_h3_v3')])
import render_batch_0008  # noqa: E402,F401  (DSQ and 128's plan; it sets b2.JOBS, replaced below)
J128 = copy.deepcopy(b2.JOBS[('128', 'deepseek_army_h3_v1')])
J088 = copy.deepcopy(render_batch_0013.JOBS10[('088', 'deepseek_h3_v1')])
J116 = copy.deepcopy(render_batch_0013.JOBS10[('116', 'mistral_h3_v1')])
import render_batch_0012  # noqa: E402  (121-122's keyframe plan; it sets b2.JOBS, replaced below)
J121 = copy.deepcopy(b2.JOBS[('121-122', 'kf_qwen_h3_v2')])
J127 = copy.deepcopy(render_batch_0013.JOBS11[('127', 'doubao_zenin_group_h3_v1')])
J130 = copy.deepcopy(render_batch_0013.JOBS11[('130', 'ds_dsq_dance_h3_v1')])
J133 = copy.deepcopy(render_batch_0013.JOBS10[('133', 'liang_gpt_h3_v1')])
J133['subjects'] = [('QWEN', None, d) if k == 'GPT' else (k, *rest) for k, *rest in J133['subjects'] for d in [rest[-1]]]
import render_shot as runner
from common import PROD, ROOT, p
from gpu import wait_cool

KF = ROOT / 'deliverables/jujutsu/关键帧'


def kf(name, folder=KF):
    out = b2.REFS / name
    if not out.exists() and (folder / name).exists():
        Image.open(folder / name).convert('RGB').resize((1024, 576), Image.LANCZOS).save(out)
    return out


SLIM = 'slender and feminine, slim arms and narrow shoulders, no bulging muscles'
import render_batch_0009  # noqa: E402  (036's v1 plan; it sets b2.JOBS, replaced below)
J036 = dict(b2.JOBS[('036', 'claude_red_h3_v1')])
RB = 'drawn entirely in the red-and-black two-tone of the frame - only black and shades of red with pale pink highlights, no other colour on her'
# 036, the user (02:37, then “再把036加入队列”): “颜色不对。claude需要也变成红黑配色。” - v1 (red-black reference) still drew her in her own
# colours; keyframes per shot are our v1 frames with her recoloured red and black (codex_keyframes_0007.py)
J036.update(seed=2610018036, label='伏黑惠→Claude·红色家纹前跪地／走廊尽头（Claude 也画成红黑配色；关键帧第 2/9/15 帧）',
            extras=[f'She is {RB}, exactly like the young man of <Video 1>; her own hair and outfit colours never show.'],
            keyframes=[(kf('kf_036_f002_redblack_v2.png'), b2.t(2, '036'), 1, f'<A> crouching before the crest, {RB}'),
                       (kf('kf_036_f009_redblack_v2.png'), b2.t(9, '036'), 2, f'<A> kneeling inside the crest shape, {RB}'),
                       (kf('kf_036_f015_redblack_v2.png'), b2.t(15, '036'), 3, f'<A> small at the end of the red corridor, {RB}')])
KNOT = 'with the small white knot-shaped GPT hair ornament exactly as in her design, crisp and undistorted'
# 042, the user (03:08, on gpt6_h3_v1): “可能还是要关键帧。头上的GPT发饰经常会扭曲。” then “042还是要加入队列” - keyframes are frames
# of that run with only the ornament redrawn from the design (codex_keyframes_0007.py)
# Codex's image safety filter refused frames 0 and 7 (a low-angle view of her flying backward in a pleated skirt); only frame 13 is used
J042.update(seed=2610018042, label='乙骨→GPT（新设计v6）·被击飞（发饰按设定图修正；关键帧第 13 帧）',
            extras=J042.get('extras', []) + [f'She is always drawn {KNOT}; it never warps, melts or changes shape as she tumbles.'],
            keyframes=[(kf(f'kf_042_f{i:03d}_knot_v2.png'), b2.t(i, '042'), 1, f'<A> knocked flying backward, {KNOT}') for i in (13,)])
# 042 v3, the user (03:50): “042还是差了点” and, after Codex refused the low-angle frames, “只给这个镜头加黑色连裤袜。其实就是把下面的
# 袜子加长” - this shot only: design gpt_yuta_v6_tights (codex_designs_0007.py), keyframes 0/7/13 with tights and the fixed ornament
b2.CAST['GPT6T'] = (b2.D / 'gpt_yuta_v6_tights.png', b2.CAST['GPT6'][1].replace('a short black pleated skirt',
                    'a short black pleated skirt over opaque black tights'))
b2.NAMES['GPT6T'] = b2.NAMES.get('GPT6', 'GPT')
J042T = copy.deepcopy(J042)
J042T['subjects'] = [('GPT6T' if key == 'GPT6' else key, *rest) for key, *rest in J042T['subjects']]
TIGHTS = 'in opaque black tights that cover her legs completely'
J042T.update(seed=2610018142, label='乙骨→GPT（新设计v6，本镜头加黑色连裤袜）·被击飞（发饰修正；关键帧第 0/7/13 帧）',
             extras=J042T['extras'] + [f'Her legs are always {TIGHTS}, up under her skirt; no bare leg shows at any moment.'],
             keyframes=[(kf(f'kf_042_f{i:03d}_tights_v2.png'), b2.t(i, '042'), 1, f'<A> knocked flying backward {TIGHTS}, {KNOT}')
                        for i in (0, 7, 13)])
# 006, the user (03:15): “006的gpt发饰也有问题。如果042解决了那就用同样方法解决006” - queued right after 042 so both wait for review
J006.update(seed=2610018006, label=J006['label'] + '（发饰按设定图修正；关键帧第 48/54/61 帧）',
            extras=J006.get('extras', []) + [f'She is always drawn {KNOT}; it never warps, melts or changes shape as she falls.'],
            keyframes=[(kf(f'kf_006_f{i:03d}_knot_v2.png'), b2.t(i, '006-016a'), 1, f'<A> falling through the explosion with her katana, {KNOT}')
                       for i in (48, 54, 61)])
# Ma Huateng, the user (03:20): “马化腾形象完全无法辨认！问题关键是马化腾其实是比较瘦的，但是替换的人物太大了。” - design v3 from a photo
# (codex_designs_0007.py); keyframes are our frames with him slimmed (codex_keyframes_0007.py). 052 (3 frames) is a Codex still.
b2.CAST['MA3'] = (b2.D / 'ma_huateng_v3.png', 'the cartoon of Pony Ma: a slim man of average height with narrow shoulders, short neat '
                  'black hair, thin rimless glasses and a gentle reserved smile, in a dark business suit with a light shirt and a dark tie')
b2.NAMES['MA3'] = 'Ma'
# 140's falling graphics card as a cast member (the Codex sprite of sprite_140.py on white), so H3 replaces the bomb as it replaces a
# person: appearance from the picture, the whole motion from <Video 1>
b2.CAST['GPU3090'] = (ROOT / 'deliverables/jujutsu/人设/rtx3090_card_v1.png', 'a long, thick graphics card modelled on the GeForce RTX '
                      '3090 Founders Edition - a dark gunmetal shroud, a silver X-shaped metal frame, a large black fan and gold contacts, '
                      'no text and no logos')
b2.NAMES['GPU3090'] = 'the graphics card'
# Gemini in the black sailor design (as render_batch_0014, which is not imported here: it would reset b2.LOG and b2.AUTH_REQUEST)
b2.CAST['GEM_MAKI4'] = (b2.D / 'gemini_maki_v4.png', 'a slender young woman with long purple-to-pink gradient hair in a high ponytail, cat '
                        'ears, amber eyes and thin rectangular glasses, in a black sailor uniform - a black collar edged with three white '
                        'stripes, a large bow in Google\'s blue, red, yellow and green gradient, short sleeves and a black pleated skirt - '
                        'holding a katana')
b2.NAMES['GEM_MAKI4'] = 'Gemini'
MA_SLIM = 'He is slim and slightly built, much smaller and narrower than the big muscular man of <Video 1>; no sunglasses, no stubble.'
# 128, the user (03:30): “128的动作有问题，手做坏了。也许需要关键帧” “而且画风也不一样” - keyframes are SOURCE frames 0/7/14 with every
# ninja redrawn as a chibi DeepSeek in the source's flat cel style and colour wash, gripping the katana like him (codex_keyframes_0007.py)
STYLE128 = ('They are drawn in the flat 2D TV-anime cel shading, bold outlines and colour wash of <Video 1>, not in a soft glossy '
            'illustration style; every girl grips her katana with both hands closed around the hilt, with correct hands.')
J128.update(seed=2610018128, label='禅院家忍者阵列→一群Q版DeepSeek冲锋（手部与画风按原片修正；关键帧第 0/7/14 帧）',
            extras=J128.get('extras', []) + [STYLE128],
            keyframes=[(kf(f'kf_128_f{i:03d}_dsq_v2.png'), b2.t(i, '128'), 1,
                        'the formation of <A> charging with katanas, in the flat cel style and colour wash of the source') for i in (0, 7, 14)])
# 142, the user (11:00) “太夸张了，不好看。需要关键帧”; the Codex still was static (“142不是静止帧，是有动画效果的”) and the CPU shake
# “不太对……要不还是用视频模型” - H3 with the Codex still (cute surprised MiniMax) as the first-frame keyframe
J142 = dict(seed=2610018142, label='高羽→MiniMax·扁平卡通吃惊掉手机（Codex 静帧作首帧关键帧，表情改可爱，H3 做抖动）',
            subjects=[('MMX', None, 'the man drawn as a flat red-outlined cartoon face screaming as his phone falls (Takaba)')],
            preserve='the flat cartoon rendering with thick red outlines, the wavy pink and cream colour bands, the falling phone and the '
                     'comic shaking of the drawing',
            shots=[(None, "a flat cartoon: <A>'s face, drawn with thick red outlines, is caught in cute surprise with round wide eyes and a "
                          "small open mouth while her phone drops at the lower left, over wavy pink and cream colour bands; the whole drawing "
                          "shakes and its lines wobble from frame to frame exactly like <Video 1>.")],
            extras=['She keeps the cute surprised face of the keyframe the whole time - never the grotesque scream of <Video 1>.',
                    'She is drawn in the same flat cartoon style, keeping her short hair and cap as simple shapes.'],
            keyframes=[(kf('still_142_seg1_v2.png', ROOT / 'deliverables/jujutsu/静帧'), b2.t(0, '142'), 1,
                        "<A>'s cute surprised face with thick red outlines, her phone dropping at the lower left")])
# 071, the user (10:53): “应该是很多个HY跑过去，和原镜头对应” - about ten tiny pandas on a moonlit clearing, moving on twos; H3 skips
# tiny far figures, so source frames 0/10/19 with every panda redrawn as a tiny chibi HY anchor the run (“试试1”)
J071 = dict(seed=2610018071, label='熊猫群→一群小 HY·夜森林空地里跑动（关键帧第 0/10/19 帧）',
            subjects=[('HY', None, 'every one of the tiny pandas running and wandering on the clearing (Panda)')],
            preserve='the dark forest at night, the small moonlit clearing, the deep green palette, the fixed camera, the number, places '
                     'and paths of the tiny figures and their stepping rhythm',
            shots=[(None, 'a dark forest at night around a small moonlit green clearing: about ten tiny chibi <A> run and wander about the '
                          'clearing in different directions, exactly where and how the tiny pandas of <Video 1> move, small and lit in pale green.')],
            extras=['Every tiny figure is <A>, a little chibi girl with long black-blue hair and a red scarf; no panda remains at any moment.',
                    'The figures stay tiny, as small as the pandas of <Video 1>.'],
            keyframes=[(kf(f'kf_071_f{i:03d}_hys_v2.png'), b2.t(i, '071'), 1, 'the tiny chibi <A> scattered over the moonlit clearing')
                       for i in (0, 10, 19)])
# 116 v3, the user on mistral_kf_h3_v2: “116完全不对啊 没有变成mistral，原型人物特征太多了” - five keyframes (0/4/7/10/14) redrawn
# completely as Mistral (wavy orange hair, cat ears, musketeer hat, puffy white sleeve, red-and-white dress), with a soft front light
J116B = copy.deepcopy(J116)
MIS_LOOK = ('Mistral\'s long, voluminous wavy orange-gold hair fading to red, her cat ears, her red musketeer hat with a white feather, '
            'her raised arm in a puffy white sleeve with a white glove, and the red-and-white corseted top of her dress')
J116B.update(seed=2610018216, label='金发女性→Mistral·红色逆光举手（v3：完全换成 Mistral 的特征＋正面补光；关键帧第 0/4/7/10/14 帧）',
             shots=[(None, 'deep red backlight with a soft warm light on her front: <A> stands in the centre of the frame with one arm raised '
                           'high and her head slightly bowed, eyes closed, ' + MIS_LOOK + ' clearly visible, rim light along her edges.')],
             extras=[f'She shows {MIS_LOOK} in every frame. Nothing of the woman of <Video 1> remains: no straight centre-parted hair, '
                     'no bare arm, no black sleeveless top; only her pose, the slow sway and the red backlight come from <Video 1>.'],
             keyframes=[(kf(f'kf_116_f{i:03d}_mis3_v2.png'), b2.t(i, '116'), 1, f'<A> with one arm raised, {MIS_LOOK}')
                        for i in (0, 4, 7, 10, 14)])
# 116 v4, the user on v3: “116有点奇怪，衣服和细节有微妙的变化。大概是因为关键帧用多了。然后每个关键帧之间有微妙的区别（比如衣服帽子的
# 褶皱）” - three keyframes: frame 7's as the master, frames 0 and 14 redrawn by Codex to match it exactly
J116C = copy.deepcopy(J116B)
J116C.update(seed=2610018316, label='金发女性→Mistral·红色逆光举手（v4：关键帧减为 3 张且以第 7 帧为母版统一细节）',
             extras=J116C['extras'] + ['Her hat, its folds and feather, her hair, sleeve, glove and dress keep exactly the same details in '
                                       'every frame; only her pose sways as in <Video 1>.'],
             # Codex's whole frames (v1): pasting only the changed area left dark blotches in the red glow and on the sleeve
             keyframes=[(kf(name), b2.t(i, '116'), 1, f'<A> with one arm raised, {MIS_LOOK}') for i, name in (
                 (0, 'kf_116_f000_mis4_v1.png'), (7, 'kf_116_f007_mis3_v1.png'), (14, 'kf_116_f014_mis4_v1.png'))])
# 121-122, the user (10:59): “表情有点狰狞，不好看，没必要用原版的表情。” - our kf_qwen_h3_v2 frames 4/8/12 with only the expression
# redrawn as a confident, pleasant smile; the prompt no longer asks for the source's grin
SMILE = 'a confident, pleasant smile with her lips closed or only slightly parted, no bared teeth'
J121['shots'] = [(s, text.replace('with a wide, cocky grin', f'with {SMILE}').replace('while she keeps grinning', 'while she keeps smiling'))
                 for s, text in J121['shots']]
J121.update(seed=2610018121, label='石流龙→Qwen·拼贴前微笑（表情改为自信的微笑；关键帧第 4/8/12 帧）',
            extras=J121.get('extras', []) + [f'Her expression is always {SMILE} - never the fierce, toothy grin of <Video 1>.'],
            keyframes=[(kf(f'kf_121_f{i:03d}_smile_v2.png'), b2.t(i, '121-122'), 1, f'<A> among the collage stickers with {SMILE}')
                       for i in (4, 8, 12)])
# 116, the user (10:59): “完全没有替换” - source frames 0/7/14 with the blonde woman redrawn as Mistral in the red backlight
J116.update(seed=2610018116, label='金发女性→Mistral·红色逆光举手（关键帧第 0/7/14 帧）',
            extras=J116.get('extras', []) + ['She is the girl of her reference picture in every frame - her own face, hair and outfit - never '
                                             'the blonde woman of <Video 1>; only the red backlight and rim light come from <Video 1>.'],
            keyframes=[(kf(f'kf_116_f{i:03d}_mis_v2.png'), b2.t(i, '116'), 1, '<A> with one arm raised in the deep red backlight, rim-lit')
                       for i in (0, 7, 14)])
# 092, the user (10:56): “这个有用关键帧吗？怎么头饰还是看不清楚” - frames 2/6 of our run with the ornament redrawn (the 006 method)
J092.update(seed=2610018092, label=J092['label'] + '（发饰按设定图修正；关键帧第 2/6 帧）',
            extras=J092.get('extras', []) + [f'<A> is always drawn {KNOT}, clearly readable in the blue light.'],
            keyframes=[(kf(f'kf_092_f{i:03d}_knot_v2.png'), b2.t(i, '092'), 1, f'<A> lit in pale blue with her arms folded, {KNOT}')
                       for i in (2, 6)])
# 088, the user (10:55): “虎杖没有替换” then “可以，就这么干” - the close tilt up (hands, face, raised hands) kept the young man;
# keyframes are source frames 4/10/18 with that part of him redrawn as DeepSeek (codex_keyframes_0007.py)
J088.update(seed=2610018088, label='虎杖→DeepSeek·双手合十举过头顶（关键帧第 4/10/18 帧）',
            extras=J088.get('extras', []) + ['Her navy maid dress with the white apron bib replaces the dark hoodie of <Video 1>, her hands '
                                             'are slender girl\'s hands with white frilled cuffs, and when her face appears her eyes are '
                                             'closed under her white maid headband, her whale-fin ears beside it.'],
            keyframes=[(kf(f'kf_088_f{i:03d}_ds_v2.png'), b2.t(i, '088'), 1, what) for i, what in (
                (4, '<A>\'s slender hands pressed together in front of her navy maid dress'),
                (10, '<A>\'s face with her eyes closed behind her pressed hands'),
                (18, '<A>\'s slender hands raised high, outlined in pale green against violet'))])
b2.LOG = PROD / 'batch_0018'
b2.AUTH_REQUEST = '用户（2026-10-02 02:15）：“我准备睡觉了，开始推理队列吧。记得看我给的意见。”（按 02:08-03:08 的审阅意见做的方案）'
b2.JOBS = {
    ('075', 'ma3_hy_kf_h3_v2'): dict(seed=2610018075, label='夜蛾与熊猫→马化腾（瘦版 v3）与HY·莫奈花园（关键帧第 0/8 帧）',
        subjects=[('MA3', None, 'the man in sunglasses sitting at the garden table on the left (Yaga)'), ('HY', None, 'the panda sitting on the right (Panda)')],
        preserve='the impressionist oil-painting rendering in the style of Monet, the flower garden and the white garden table',
        shots=[(None, 'an impressionist oil painting of a sunny flower garden: <A> sits at a small white garden table on the left and <B> sits on the right, both painted with soft visible brush strokes.')],
        extras=['Both keep the oil-painting brush strokes of <Video 1>.', MA_SLIM],
        keyframes=[(kf(f'kf_075_f{i:03d}_ma3_v2.png'), b2.t(i, '075'), 1, '<A>, slim, at the garden table on the left and <B> on the right') for i in (0, 8)]),
    ('091', 'ma3_qq_kf_tint_h3_v3'): dict(seed=2610018191, label='夜蛾→马化腾（瘦版 v3）·绿光登场，身旁的玩偶→QQ 企鹅（关键帧第 0/7 帧）',
        subjects=[('MA3', 'tint_8FCC80', 'the big muscular man lit in green, with a small doll beside him (Yaga)')],
        preserve='the black background, the single green light and the slow movement',
        shots=[(None, 'a black background: <A> stands in the centre-left of the frame lit entirely in green light, while a small plush of the QQ penguin floats on the right.')],
        extras=[MA_SLIM, 'The small doll of <Video 1> is a plush of the QQ penguin, Tencent\'s mascot: a round chibi black-and-white penguin with '
                'a white belly, a yellow beak and feet, a red scarf and three little tufts on its head, lit by the same green light.'],
        keyframes=[(kf(f'kf_091_f{i:03d}_ma3qq_v2.png'), b2.t(i, '091'), 1, '<A>, slim, in green light and the QQ penguin plush floating beside him') for i in (0, 7)]),
    ('042', 'gpt6_kf_h3_v2'): J042,
    ('042', 'gpt6t_kf_h3_v3'): J042T,
    ('128', 'dsq_army_kf_h3_v2'): J128,
    # 127, the user (2026-10-02): “最右边的角色没有替换（前几帧没有替换）” - the woman in purple entering on the right at frame 6 stayed
    # the source's; keyframes 7/12/19 are our frames with only her redrawn as Doubao in the Naoya costume (codex_keyframes_0007.py)
    ('127', 'doubao_naoya_kf_h3_v2'): dict(J127, seed=2610018127,
        label='禅院家众人摆姿势→豆包（最右边的紫裙女子也换成直哉造型豆包；关键帧第 7/12/19 帧）',
        keyframes=[(kf(f'kf_127_f{i:03d}_naoya_v2.png'), b2.t(i, '127'), 1,
                    'the Doubao girls posing in a row, the one on the right in the dark grey kimono and black haori, one arm raised behind '
                    'her head') for i in (7, 12, 19)]),
    # 133, the user (2026-10-02): “轮椅上的换成千问吧。” - the girl in the wheelchair is Qwen; keyframes 0/11/22 are our liang_gptgirl
    # frames with only her redrawn (codex_keyframes_0007.py)
    ('133', 'liang_qwen_kf_h3_v2'): dict(J133, seed=2610018133, label='日下部与妹妹→梁文锋推着坐轮椅的千问·林间（关键帧第 0/11/22 帧）',
        keyframes=[(kf(f'kf_133_f{i:03d}_qwen_v2.png'), b2.t(i, '133'), s, '<A> pushing the wheelchair in which <B> sits quietly, '
                    'her hands in her lap') for i, s in ((0, 1), (11, 1), (22, 2))]),
    # 130, the user (2026-10-02): “最前面的搞笑艺人没有替换” - keyframes 0/5/10 are our frames with only the comedian redrawn as DeepSeek
    # (facing us, turning, back turned wagging her whale tail; codex_keyframes_0007.py)
    ('130', 'ds_dance_kf_h3_v2'): dict(J130, seed=2610018130,
        label='高羽→DeepSeek（转身晃鲸鱼尾巴；关键帧第 0/5/10 帧）；伴舞→Q版DeepSeek',
        keyframes=[(kf(f'kf_130_f{i:03d}_ds_v2.png'), b2.t(i, '130'), 1, w) for i, w in (
            (0, '<A> in her maid dress dancing in the middle, facing the camera, among the chibi <B>'),
            (5, '<A> turning her back to the camera, her whale tail swinging out, among the chibi <B>'),
            (10, '<A> with her back to the camera, looking back over her shoulder and wagging her whale tail, among the chibi <B>'))]),
    # 130 v3: v2 matched only its first keyframe and copied the source from frame 2 on (Takaba and the muscle dancers back). Now
    # <Video 1> is our ds_dsq_dance_h3_v1 (the chibi DeepSeek dancers already right), the keyframes are edits of exactly those frames,
    # and the only change asked is the comedian; the last frame (14) is a keyframe too, and the old “blue-and-yellow tights” is gone
    ('130', 'ds_dance_kf_h3_v3'): dict(seed=2610018330, reference=PROD / 'shots/130/ds_dsq_dance_h3_v1/native_fullframe.mp4',
        label='高羽→DeepSeek（女仆装，转身摇鲸鱼尾巴；以 ds_dsq_dance_h3_v1 为参考视频只换她，关键帧第 0/5/10/14 帧）',
        subjects=[('DS', None, 'the comedian in blue-and-yellow tights dancing in the middle, who turns around and shakes his hips (Takaba)')],
        preserve='the crowd of chibi maid girls dancing around him exactly as they are, the neon disco stage, the coloured lights and the camera',
        shots=[(None, 'a neon disco stage full of coloured lights: <A> dances in the middle in her navy maid dress, then turns her back to '
                      'the camera and wags her big whale tail from side to side, while the crowd of chibi maid girls dance around her.')],
        extras=['Where <Video 1> shakes his hips, <A> wags her whale tail instead.'],
        keyframes=[(kf(f'kf_130_f{i:03d}_ds_v2.png'), b2.t(i, '130'), 1, w) for i, w in (
            (0, '<A> in her maid dress dancing in the middle, facing the camera, among the chibi maid girls'),
            (5, '<A> turning her back to the camera, her whale tail swinging out, among the chibi maid girls'),
            (10, '<A> with her back to the camera, looking back over her shoulder and wagging her whale tail, among the chibi maid girls'),
            (14, '<A> with her back to the camera, her whale tail swung to the other side, among the chibi maid girls'))]),
    # 140 v3, the user on gpu_spin_h3_v2 (2026-10-02): “你是不是用提示词在要求140“旋转”？其实这个词不恰当，更加类似于“翻转”。也许你不要用提示词
    # 限定显卡的运动，而是让模型自己去理解” - the bomb tips over as it falls (side view first, then nose down toward the city, seen more and
    # more end-on). <Video 1> is the source again, the card is a cast member with its own picture, and the text names no motion: the
    # bomb's whole motion transfers to the card (v1, a keyframes-only object edit, turned back into the bomb from frame 1)
    ('140', 'gpu_follow_h3_v3'): dict(seed=2610018340, label='落向城市的炸弹→RTX 3090（显卡作为角色配参考图，动作完全照原片炸弹，提示词不描述动作；第 0 帧关键帧）',
        subjects=[('GPU3090', None, 'the dark bomb that falls away from the camera toward the city')],
        preserve='the aerial view of the city, the camera and the timing',
        shots=[(None, 'an aerial view of a city seen from straight above: <A> falls away from the camera toward the city exactly as the '
                      'bomb of <Video 1> does.')],
        extras=['<A> is a graphics card at every moment, never a bomb: no fins, no rounded nose, no cylinder; it carries no text and no '
                'logos.'],
        keyframes=[(kf('kf_140_f000_sprite_v1.png'), b2.t(0, '140'), 1, '<A> large at the top of the frame, just starting to fall')]),
    # 098 v4, the user (2026-10-02) on the hold fix (frames 1-5 held on frame 0): “098现在完全就是静止帧了，不好看。要不还是用视频模型生成
    # 动态的。” - <Video 1> is our kf_grok_claude_hy_h3_v3 with its two late cuts fixed (6 = 7, 12 = 13; hold_frames.py --out
    # kf_grok_claude_hy_h3_v3_cutfix), whose teal and green shots are already right; Grok is pinned at 0, 3 and 5 (frame 0 of v3, and
    # frames 3 and 5 redrawn after it by Codex), the other two shots by their own frames 9 and 14
    ('098', 'grok_ref_h3_v4'): dict(seed=2610018098, reference=PROD / 'shots/098/kf_grok_claude_hy_h3_v3_cutfix/native_fullframe.mp4',
        label='雷吉/伏黑惠/熊猫→Grok/Claude/HY·彩光登场（以修好切镜的 v3 为参考视频，Grok 关键帧第 0/3/5 帧，动态）',
        subjects=[('GROK', 'tint_985CB6', 'the man lit in violet wrapped in a big coat of fluttering paper strips in the first shot (Reggie)', (1,))],
        preserve='the black background, the single coloured light of each shot (violet, teal, then green) and the girls of the second and '
                 'third shots exactly as they are',
        shots=[(None, 'a black background, violet light: <A> stands in the centre of the frame, sweeps one arm across her body and then '
                      'points ahead, her full skirt and twin tails fluttering.'),
               (b2.t(6, '098'), 'a hard cut, teal light: the orange-haired girl in white brings her hands together in front of her chest '
                                'into a hand sign.'),
               (b2.t(12, '098'), 'a hard cut, bright green light: the girl with long hair and a red scarf throws both arms up high with a '
                                 'wide grin.')],
        keyframes=[(kf('h3_098_kf_grok_claude_hy_h3_v3_f000.png'), b2.t(0, '098'), 1, '<A> in violet light, one arm across her body'),
                   (kf('kf_098_f003_grokfull_v2.png'), b2.t(3, '098'), 1, '<A> in violet light, her arm swept across her body'),
                   (kf('kf_098_f005_grokfull_v2.png'), b2.t(5, '098'), 1, '<A> in violet light, pointing ahead'),
                   (kf('h3_098_cutfix_f009.png'), b2.t(9, '098'), 2, 'the orange-haired girl in white making the hand sign in teal light'),
                   (kf('h3_098_cutfix_f014.png'), b2.t(14, '098'), 3, 'the girl with the red scarf, both arms up, in green light')]),
    # 134 v4, the user (2026-10-02) on the Codex compositing fog_codex_v3: “位置对了，但是有一闪一闪的颜色变化”, “我感觉特效还是不太行。
    # 要不试试视频路线” - <Video 1> is fog_codex_v3 itself (Gemini in the right design, frozen, the fog eating her on the source's
    # timing), so H3 only redraws it as one coherent animation; frames 0, 12 and 22 of it are keyframes. The text names no new motion
    # (gemini_maki4_red_h3_v1 had turned the frozen figure into a spinning swing).
    ('134', 'fog_ref_h3_v4'): dict(seed=2610018134, reference=PROD / 'shots/134/fog_codex_v3/native_fullframe.mp4',
        label='真希→Gemini黑水手服·静止的挥刀姿势被红雾吞没（以 Codex 合成版为参考视频，H3 重画成连贯动画；关键帧第 0/12/22 帧）',
        subjects=[('GEM_MAKI4', 'redblack', 'the girl with cat ears and a long ponytail frozen mid-swing with her sword in the red darkness')],
        preserve='the red darkness, the red and black fog that churns over her and swallows her piece by piece, and the timing',
        shots=[(None, 'red darkness: <A> stays frozen mid-swing with her sword, completely still, while red and black fog churns over her '
                      'and swallows her piece by piece exactly as in <Video 1>.')],
        extras=['She is drawn in shades of red on black like <Video 1>, in her short pleated skirt, black knee socks and loafers, with her '
                'cat tail; she does not move at all - only the fog moves.'],
        keyframes=[(kf(f'h3_134_fog_codex_v3_f{k:03d}.png'), b2.t(k, '134'), 1, w) for k, w in (
            (0, '<A> frozen mid-swing in the red darkness, the fog around her'),
            (12, '<A> frozen, half swallowed by the fog'),
            (22, '<A> almost swallowed by the fog, only her hands and sword still showing'))]),
    # 133 v3: liang_qwen_kf_h3_v2 ignored all three keyframes and brought back the source's white-haired sister. As 130 v3: <Video 1> is
    # our liang_gptgirl_h3_v1 (Liang already right) and only the girl in the wheelchair changes, to Qwen
    ('133', 'liang_qwen_ref_h3_v3'): dict(seed=2610018333, reference=PROD / 'shots/133/liang_gptgirl_h3_v1/native_fullframe.mp4',
        label='日下部与妹妹→梁文锋推着坐轮椅的千问·林间（以 liang_gptgirl_h3_v1 为参考视频只换轮椅上的人，关键帧第 0/11/22 帧）',
        subjects=[('QWEN', None, 'the white-haired girl in a pale hooded robe sitting in the wheelchair')],
        preserve='the man in a dark suit and glasses pushing the wheelchair exactly as he is, the sunlit green forest, the wheelchair, the slow '
                 'walk toward the camera, the slow push-in and the cut',
        shots=[(None, 'a sunlit green forest: a man in a dark suit and glasses slowly pushes a wheelchair toward the camera, and <A> sits in '
                      'it quietly, her hands in her lap.'),
               (b2.t(21, '133'), 'a hard cut: a closer view of the two of them in the same forest.')],
        keyframes=[(kf(f'kf_133_f{i:03d}_qwen_v2.png'), b2.t(i, '133'), s, '<A> sitting quietly in the wheelchair, her hands in her lap, '
                    'pushed by the man in the dark suit') for i, s in ((0, 1), (11, 1), (22, 2))]),
    ('142', 'mmx_cute_kf_h3_v2'): J142,
    ('071', 'hys_kf_h3_v3'): J071,
    ('088', 'ds_kf_h3_v2'): J088,
    ('092', 'gpt6_doubao_kf_h3_v4'): J092,
    ('116', 'mistral_kf_h3_v2'): J116,
    ('116', 'mistral_full_kf_h3_v3'): J116B,
    ('116', 'mistral_master_kf_h3_v4'): J116C,
    ('121-122', 'qwen_smile_kf_h3_v3'): J121,
    ('006-016a', 'gpt6_kf_h3_v2'): J006,
    ('036', 'claude_redblack_kf_h3_v2'): J036,
    ('087', 'ds_slim_kf_h3_v2'): dict(seed=2610018087, label='高羽与虎杖→MiniMax与DeepSeek·健身房（DeepSeek 改纤细；关键帧第 0/25 帧）',
        subjects=[('MMX', None, 'the man in the blue-and-yellow costume with red gloves (Takaba)'),
                  ('DS', None, 'the boy with pink hair and an orange towel on the right (Itadori)')],
        preserve='the bright yellow gym, the exercise machines, the poses and the comic energy',
        shots=[(None, 'a bright yellow gym: <A> in the centre-left and <B> on the right work out side by side with comic energy.')],
        extras=[f'<B> is {SLIM}, where the boy of <Video 1> is muscular; she keeps his poses and gestures.'],
        keyframes=[(kf('kf_087_f000_ds_slim_v2.png'), b2.t(0, '087'), 1, f'<A> on the left and <B> on the right, {SLIM}'),
                   (kf('kf_087_f025_ds_slim_v2.png'), b2.t(25, '087'), 1, f'<A> on the left and <B> on the right, {SLIM}')]),
    ('089', 'gym_trio_kf_h3_v3', ): dict(seed=2610018089, label='健身房三人举拳：Claude 一脸不情愿，MiniMax 与 DeepSeek 改纤细（关键帧第 0/26 帧）',
        subjects=[('CL', None, 'the young man in an orange hoodie on the left, joining in reluctantly (Megumi)'),
                  ('MMX', None, 'the comedian in blue-and-yellow tights in the middle (Takaba)'),
                  ('DS', None, 'the young man in a white T-shirt with an orange towel on the right (Itadori)')],
        preserve='the bright yellow gym, the dumbbell racks and the fist-raising rhythm',
        shots=[(None, 'a bright yellow gym: three people raise their fists in rhythm - <A> on the left half-heartedly, <B> in the middle with gusto, <C> on the right cheerfully.')],
        extras=['<A> looks thoroughly unwilling the whole time: a flat, embarrassed scowl, eyes looking away, raising her fist only halfway, '
                'exactly like the reluctant young man of <Video 1>.', f'<B> and <C> are {SLIM}, where the men of <Video 1> are muscular.'],
        keyframes=[(kf('kf_089_f000_trio_v2.png'), b2.t(0, '089'), 1, f'<A> unwilling on the left, <B> and <C> {SLIM}, raising their fists'),
                   (kf('kf_089_f026_trio_v2.png'), b2.t(26, '089'), 1, f'<A> unwilling on the left, <B> and <C> {SLIM}, raising their fists')]),
    ('091', 'ma_qq_kf_tint_h3_v2'): dict(seed=2610018091, label='夜蛾→马化腾·绿光登场（身旁的玩偶→QQ 企鹅；关键帧第 0/7 帧）',
        subjects=[('MA', 'tint_8FCC80', 'the big muscular man lit in green, with a small doll beside him (Yaga)')],
        preserve='the black background, the single green light and the slow movement',
        shots=[(None, 'a black background: <A> stands in the centre-left of the frame lit entirely in green light, shoulders squared, while a '
                      'small plush of the QQ penguin floats on the right.')],
        extras=['His short black hair, glasses and long coat show in the green light, where <Video 1> shows the muscular man.',
                'The small doll of <Video 1> is a plush of the QQ penguin, Tencent\'s mascot: a round chibi black-and-white penguin with a '
                'white belly, a yellow beak and feet, a red scarf and three little tufts on its head, lit by the same green light.'],
        keyframes=[(kf('kf_091_f000_qq_v2.png'), b2.t(0, '091'), 1, '<A> in green light and the QQ penguin plush floating beside him'),
                   (kf('kf_091_f007_qq_v2.png'), b2.t(7, '091'), 1, '<A> in green light and the QQ penguin plush floating beside him')]),
}

# object edits (no characters): hand-written prompts in the official format, as render_070_kf.py
OBJ = {
    ('103', 'cnn_kf_h3_v1'): dict(seed=2610018103, label='玻璃片→卷积神经网络的特征图（关键帧第 8/16 帧）',
        video='on a dark red background a small cyan glass card appears, then a row of translucent cyan glass panes fans out in perspective, '
              'showing faint clouds',
        change='the glass panes are the feature maps of a convolutional neural network: glowing cyan grids of small square cells with '
               'brighter and darker activations, smaller toward the back like successive layers, a bright square kernel window on the '
               'front pane with thin glowing lines to the next pane',
        keep='the dark red background, the appearance of the first card, the fanning-out motion, the perspective, the cyan glow and the timing',
        keyframes=[('kf_103_f008_cnn_v2.png', 8, 'the panes as glowing CNN feature maps with the kernel window on the front pane'),
                   ('kf_103_f016_cnn_v2.png', 16, 'the full row of feature maps receding into the distance')],
        detail='on a dark red background a small cyan card appears and a row of translucent cyan feature maps fans out in perspective: each '
               'is a glowing grid of small square cells with soft bright and dark activations, the maps growing smaller toward the back like '
               'successive layers of a convolutional neural network, a bright square kernel window sliding on the front map with thin '
               'glowing lines running to the next map.',
        rule='No clouds or photos show inside the panes; every pane is a grid of activation cells.'),
    ('104', 'matrix_h3_v1'): dict(seed=2610018104, label='蓝色光柱→黑客帝国式绿色数据流',
        video='a low-angle night view up between neon-lit skyscrapers; a thin blue beam of light shoots up into the purple sky, with rings of light around it',
        change='the beam is a column of green Matrix-style digital rain: streams of small falling green glyphs and digits forming the '
               'column, with green rings of glyphs around it',
        keep='the skyscrapers, the camera, the beam\'s position, path and growth, the rings and the timing',
        keyframes=[],
        detail='a low-angle night view up between neon-lit skyscrapers; a column of bright green digital rain - streams of tiny glowing '
               'green glyphs and digits, unreadable - shoots up into the sky, rings of green glyphs expanding around it, the green glow '
               'spilling onto the building edges.',
        rule='The beam is green digital rain at every moment, never a blue beam; the glyphs are too small to read.'),
    ('105', 'clip_kf_h3_v1'): dict(seed=2610018105, label='巨大方碑砸地→巨大回形针砸在地上（旧照片色；关键帧第 0/12 帧）',
        video='an anime frame drawn like an old sepia photograph: a giant stone cube crashes down onto the ground, raising huge clouds of '
              'dust and debris, mountains behind',
        change='the stone cube is a giant silver paperclip slamming down into the ground',
        keep='the sepia old-photo rendering, the dust clouds, the debris, the mountains, the camera and the timing',
        keyframes=[('kf_105_f000_clip_v2.png', 0, 'the giant paperclip slamming into the ground in a cloud of dust'),
                   ('kf_105_f012_clip_v2.png', 12, 'the giant paperclip in the ground with the dust rising around it')],
        detail='in a sepia old-photo look, a giant silver paperclip slams down into the ground at an angle, its lower end buried as huge '
               'clouds of dust and debris billow up around it, mountains behind.',
        rule='The falling object is a giant paperclip at every moment, never a stone cube.'),
    ('108', 'green_data_h3_v1'): dict(seed=2610018108, label='海面上的白色光束→绿色数据流光',
        video='a dim sea under a cloudy sky, shafts of white light falling from the clouds onto the water, glittering on the surface',
        change='the shafts of light are green data streams: columns of falling green glyphs like digital rain, green glints on the water',
        keep='the sea, the clouds, the camera, the positions and flicker of the shafts and the timing',
        keyframes=[],
        detail='a dim sea under a cloudy sky; shafts of green light made of falling streams of tiny green glyphs and digits, like digital '
               'rain, pour from the clouds onto the water, green glints flickering on the surface.',
        rule='The shafts are green digital rain at every moment, never white light; the glyphs are too small to read.'),
    ('140', 'gpu3090_kf_h3_v1'): dict(seed=2610018140, label='落向城市的炸弹→RTX 3090 显卡（关键帧第 0/8 帧）',
        video='an aerial view of a city seen from straight above; a dark bomb falls away from the camera toward the city, shrinking to a dot',
        change='the bomb is a graphics card modelled on the GeForce RTX 3090 Founders Edition (dark gunmetal shroud, silver X-shaped frame, '
               'a large fan, no text or logos)',
        keep='the city, the camera, the fall of the object and its shrinking, and the timing',
        keyframes=[('kf_140_f000_gpu_v2.png', 0, 'the graphics card large in the frame, just starting to fall away'),
                   ('kf_140_f008_gpu_v2.png', 8, 'the graphics card smaller, falling toward the city')],
        detail='an aerial view of a city seen from straight above; a big graphics card with a dark gunmetal shroud, a silver X-shaped frame '
               'and a large fan falls away from the camera toward the city, shrinking until it is a tiny dot.',
        rule='The falling object is the graphics card at every moment, never a bomb; it carries no text and no logos.'),
    # 140 v2, the user (2026-10-02) on the CPU sprite version gpu_sprite_v1: “140其实还应该有一个旋转的效果，我想试一下视频模型，如果视频模型
    # 处理不好再回退” - <Video 1> is that CPU composite (sprite_140.py), so there is no bomb left for H3 to fall back to (v1 kept the bomb
    # from frame 1 on); its frame 0 is the keyframe for the card's look; the edit asked for is the spin
    ('140', 'gpu_spin_h3_v2'): dict(seed=2610018240, label='落向城市的 RTX 3090 加旋转（以 CPU 贴图版为参考视频，H3 只加旋转；第 0 帧关键帧）',
        reference=PROD / 'shots/140/gpu_sprite_v1/native_fullframe.mp4',
        video='an aerial view of a city seen from straight above; a graphics card with a dark gunmetal shroud, a silver X-shaped frame and a '
              'large fan falls away from the camera toward the city, shrinking to a speck, without turning',
        change='the graphics card spins around its long axis as it falls, like a falling bomb spinning on its axis: it keeps turning from its '
               'fan side to its thin edge to its back plate and round again, about one and a half turns over the shot',
        keep='the city, the camera, the path of the falling card, its size at every moment, and the timing',
        keyframes=[('kf_140_f000_sprite_v1.png', 0, 'the graphics card large at the top of the frame, fan side up, just starting to fall away')],
        detail='an aerial view of a city seen from straight above; a big graphics card with a dark gunmetal shroud, a silver X-shaped frame '
               'and a large fan falls away from the camera toward the city, spinning around its long axis as it shrinks - its fan side, '
               'its edge and its back plate flashing by in turn - until it is a tiny spinning speck.',
        rule='The falling object is the same graphics card at every moment, never a bomb, and it keeps spinning the whole time; it carries '
             'no text and no logos.',
        kf_note='The keyframe supplies the look of the card; <Video 1> supplies its path, size and timing; the spin is new.'),
}


def object_prompt(uid, spec, g):
    ks = spec['keyframes']
    ts = [b2.t(local, uid) for _, local, _ in ks]
    tag = '[video editing + keyframe completion]' if ks else '[video editing]'
    return '\n'.join([
        'subject_definitions:',
        *[f'<Picture {i + 1}> is the keyframe of [Shot 1] at {t}: the exact frame of <Video 1> at that moment edited - {what}.'
          for i, ((_, _, what), t) in enumerate(zip(ks, ts))],
        f'<Video 1> is the source video for the target video edit: {spec["video"]}.',
        '',
        'summary:',
        f'{tag} The target video is an edited version of <Video 1> in which {spec["change"]}; everything else preserves <Video 1>, its motion and its timing.',
        '',
        'retention_analysis:',
        *[f'<Picture {i + 1}> ([Shot 1] at {t}): fully_preserved - at that moment the frame matches <Picture {i + 1}>.' for i, t in enumerate(ts)],
        f'<Video 1> (source video editing): partially_preserved - make that change; preserve {spec["keep"]}; the frame is never mirrored.',
        '',
        'detailed_description:',
        f'The target video keeps the 2D anime style, the colour grading and the lighting of <Video 1> over this {g / 24:.3f}-second model sequence.',
        f'[Shot 1] 2D-animated, {spec["detail"]}',
        spec['rule'],
        *([spec.get('kf_note', 'The keyframes supply the new look; the source video supplies all motion and the timing.')] if ks else []),
        *b2.b1.TAIL]) + '\n'


def object_refs(spec):
    return [kf(name) for name, _, _ in spec['keyframes']]


def run_object(uid, rev):
    import msvcrt
    spec = OBJ[(uid, rev)]
    start, end = b2.b1.interval(uid)
    g = p.snap_frames(end - start)
    text = object_prompt(uid, spec, g)
    job = PROD / 'shots' / uid / rev
    job.mkdir(parents=True, exist_ok=True)
    if (job / 'prompt.txt').exists():
        assert (job / 'prompt.txt').read_text(encoding='utf-8') == text
    else:
        (job / 'prompt.txt').write_text(text, encoding='utf-8')
    refs = object_refs(spec)
    assert all(r.exists() for r in refs), refs
    runner.REFERENCES[uid] = refs
    runner.SEEDS[uid], runner.LABELS[uid] = spec['seed'], spec['label']
    runner.SHOT_OVERRIDES[uid] = dict(id=uid, start=start, end=end, frames=end - start)
    if 'reference' in spec and not (job / 'reference_fullframe.mp4').exists():
        # <Video 1> is our own composite instead of the source (render_shot.prepare keeps an existing reference_fullframe.mp4 and records
        # its path and hash in preparation.json); the same retiming to the model's frame count as prepare does for the source
        n = end - start
        p.run([p.FFMPEG, '-v', 'error', '-y', '-i', spec['reference'], '-vf',
               f'setpts=N*{g - 1}/({n - 1}*24*TB),fps=24,tpad=stop_mode=clone:stop_duration=0.2',
               '-frames:v', g, '-r', '24', '-an', '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', job / 'reference_fullframe.mp4'])
    with (PROD / 'batch.lock').open('a+b') as lock:
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        runner.prepare(uid, rev)
        p.write_json(job / 'authorization.json', dict(request=b2.AUTH_REQUEST, references=[str(r) for r in refs], visual_review='pending_user'))
        if not (job / 'validation.json').exists():
            wait_cool()
        sys.argv = [__file__, '--shot', uid, '--revision', rev]
        runner.main()
    print('UNIT DONE', uid, rev, flush=True)


def queue(keys):
    sys.path.insert(0, str(ROOT / 'pipelines/anime_op'))
    import review_queue
    for uid, rev in keys:
        start, end = b2.b1.interval(uid)
        g = p.snap_frames(end - start)
        if (uid, rev) in OBJ:
            spec = OBJ[(uid, rev)]
            text, refs = object_prompt(uid, spec, g), object_refs(spec)
        else:
            spec = b2.JOBS[(uid, rev)]
            text, refs = b2.build(spec['subjects'], spec['preserve'], spec['shots'], spec.get('extras', []), g, spec.get('keyframes', ()))
        assert all(r.exists() for r in refs), refs
        review_queue.add(PROD, uid, rev, spec['label'], note='按用户 10-02 02:08-02:14 的审阅意见', when='10-02 夜间队列',
                         script='pipelines/jujutsu/render_batch_0018.py', prompt=text, references=refs)
        print('QUEUED', uid, rev, [r.name for r in refs], flush=True)


if __name__ == '__main__':
    keys = [tuple(a.split('@')) for a in sys.argv[1:] if '@' in a]
    if '--queue' in sys.argv:
        queue(keys)
    else:
        for uid, rev in keys:
            if (uid, rev) in OBJ:
                run_object(uid, rev)
            else:
                sys.argv = [__file__, f'{uid}@{rev}']
                b2.main()
