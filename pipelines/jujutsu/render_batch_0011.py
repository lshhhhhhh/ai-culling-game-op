"""JJK batch 11 - PLANS ONLY (registered as 待推理; the user: “所有有了修改方案的镜头都应该是待推理状态。然后现在不要直接推理”).

User, 2026-10-01 evening: “新形象可以。074我觉得是gemini姐妹。086左边随便换一个，deepseek也行。101这个镜头人物对应是次要的，关键是好看，
好几个镜头就是人设图站在那边，没有动作。106后面的小弟可以用小deepseek。130也可以用小deepseek。甚至搞笑艺人也可以换成deepseek，因为后面
有一幕是转身晃屁股，如果是别的角色就很出戏，如果是deepseek那只是晃动鲸鱼尾巴。”
Earlier review notes answered here: 058/064/065-067/099/135 Gemini redesign; 072/083 twins; 089 “最左边的claude应该是一脸不情愿的样子”;
090 “后面炸弹的一幕没有了”; 136-138 “嘴巴张的太大了，好吓人”; 145 “完全没做啊”; 071 the panda wanders, it does not lie down.
New designs (approved): gemini_maki_v2, gemini_mai_v1, doubao_zenin_{naoya,chojuro,nobuaki,naobito}_v1, glm_eso_v1, glm_kechizu_v1,
bard_twins_mother_v1. Units whose output stayed a standing design sheet (094, 098, 101, 109-111a, 111b-114, 121-122) are in
KEYFRAME_PLANS: they need Codex-edited source keyframes first (h3 keyframe anchor method), so they are queued as drafts.
Usage: render_batch_0011.py --queue (all plans) | render_batch_0011.py UNIT@REV ... (only after the user says to run)
"""
import sys

import render_batch_0004  # noqa: F401  (JENSEN)
import render_batch_0006  # noqa: F401  (DSQ)
import render_batch_0007  # noqa: F401  (MUSK, LIANG, DB_OGI, DB_JIN, DB_RANTA; imports batch 3 for GLM)
import render_batch_0002 as b2
from common import PROD

D, A = b2.D, b2.A
DOUBAO = 'a young woman with a smooth chocolate-brown chin-length bob, large glossy brown eyes and soft rounded 3D-rendered features'
b2.CAST.update({
    'GEM_MAKI2': (D / 'gemini_maki_v2.png', 'a young woman with long purple-to-pink gradient hair in a high ponytail, cat ears, amber eyes and rectangular glasses, in a dark navy high-collared jujutsu school combat uniform, with a katana on her back'),
    'GEM_MAI': (D / 'gemini_mai_v1.png', 'a young woman with a shoulder-length asymmetric purple-to-pink bob, cat ears and amber eyes, no glasses, in a dark navy Kyoto jujutsu school uniform with a long pleated skirt, with a revolver at her hip'),
    'DB_NAOYA': (D / 'doubao_zenin_naoya_v1.png', DOUBAO + ', the ends of her bob dyed blond, small earrings, a smug half-smile, a loose dark grey kimono with a black haori'),
    'DB_CHOJURO': (D / 'doubao_zenin_chojuro_v1.png', DOUBAO + ', a broad heavy build, a sleeveless dark olive kimono top with a rope belt, bandaged forearms and a scar on her cheek'),
    'DB_NOBUAKI': (D / 'doubao_zenin_nobuaki_v1.png', DOUBAO + ', in a white gi and black hakama with a black mask around her neck, holding a katana'),
    'DB_NAOBITO': (D / 'doubao_zenin_naobito_v1.png', DOUBAO + ', grey streaks in her bob, a dark brown kimono with a grey crested haori and a sake gourd at her sash'),
    'GLM_ESO': (D / 'glm_eso_v1.png', 'a young woman with black fox ears and a black fox tail, her black-and-blue hair in two buns, in a dark green cropped top that bares her back, painted with a red blood-splash pattern'),
    'GLM_KECHIZU': (D / 'glm_kechizu_v1.png', 'a short, round girl with black fox ears and a fox tail, a messy short bob and a huge mischievous grin, in a pale green hooded jumpsuit'),
    'BARD': (D / 'bard_twins_mother_v1.png', 'a gentle, tired woman with long straight blue-to-violet hair in a low bun, a small four-pointed sparkle hair ornament and a muted lavender kimono'),
})
b2.NAMES.update({'GEM_MAKI2': 'Gemini', 'GEM_MAI': 'Gemini', 'DB_NAOYA': 'Doubao', 'DB_CHOJURO': 'Doubao', 'DB_NOBUAKI': 'Doubao',
                 'DB_NAOBITO': 'Doubao', 'GLM_ESO': 'GLM', 'GLM_KECHIZU': 'GLM', 'BARD': 'Bard'})
b2.LOG = PROD / 'batch_0011'
b2.AUTH_REQUEST = '用户（2026-10-01 晚）：新形象可以；074、086、101、106、130 的意见；有修改方案的镜头都设为待推理，现在不要直接推理'
t = b2.t
RED = 'the red-and-black two-tone rendering and the black background'
DOUBAO_LOOK = 'Every Doubao keeps her soft 3D-rendered look - smooth CG shading and big glossy eyes - standing out from the 2D anime around her.'
TWINS = 'They are twins with the same face and the same purple-to-pink hair: <A> has a high ponytail and glasses, <B> a shoulder-length asymmetric bob and no glasses.'

b2.JOBS = {
    # --- the twins, new designs ---
    ('035', 'gemini_maki2_h3_v1'): dict(seed=2610011035, label='真希→Gemini新二设·火焰中的剪影',
        subjects=[('GEM_MAKI2', None, 'the dark-haired fighter whirling through the stylised orange flames (Maki)')],
        preserve='the stylised orange, black and white flame animation, the fast fluid motion and the camera',
        shots=[(None, 'stylised orange, black and white flames swirl across the frame: <A> whirls and slashes through them, her ponytail and her katana trailing streaks of flame, her figure breaking up into the flame shapes and re-forming.')],
        extras=['She is drawn in the same flat orange, black and white flame style as the rest of the frame.']),
    ('041', 'gemini_mai_ds_h3_v2'): dict(seed=2610011041, label='真依→Gemini新二设·暗场紫光中舞动；之后虎杖→DeepSeek',
        subjects=[('GEM_MAI', None, 'the dark-haired woman in a black outfit swaying with her arms raised in violet light in the first shot (Mai)', (1,)),
                  ('DS', None, 'the young man with short light hair in black thrown through grey smoke in the second shot (Itadori)', (2,))],
        preserve='the dark scene, the thin violet beam of light and city lights of the first shot, the grey smoke of the second shot and the camera movement',
        shots=[(None, 'a dark scene lit by a thin violet beam of light, city lights far below: <A> on the left of the frame sways and leans back with her arms raised, her bob swinging.'),
               (t(13, '041'), 'a hard cut: in thick grey smoke, <B> is thrown backward through the air, arms flung out.')]),
    ('046', 'gemini_mai_red_h3_v2'): dict(seed=2610011046, label='真依→Gemini新二设·红黑蛛网横握巨刃',
        subjects=[('GEM_MAI', 'redblack', 'the figure at the top holding a huge serrated blade sideways (Mai)')],
        preserve='the red spider-web lines, ' + RED + ', and the huge serrated blade across the frame',
        shots=[(None, 'a red-and-black two-tone image crossed by red spider-web lines: <A> leans over the top of the frame gripping a huge serrated blade that stretches sideways across the whole frame.')],
        extras=['She is drawn entirely in shades of red on black like the rest of the frame; her cat ears and bob show in her silhouette.']),
    ('058', 'lineup7_h3_v2'): dict(seed=2610011058, label='高专群像七人（真希换Gemini新二设）',
        subjects=[('GEM_MAKI2', None, 'the young woman on the far left with short dark hair and glasses in a black outfit (Maki)'),
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
    ('064', 'gemini_maki2_h3_v1'): dict(seed=2610011064, label='真希→Gemini新二设·光柱中走来（腿部）',
        subjects=[('GEM_MAKI2', None, 'the person walking, seen from the knees down (Maki)')],
        preserve='the underground space with tall pillars of light, the cold light and the low camera',
        shots=[(None, 'an underground space full of tall pillars of light: <A> walks past the low camera, seen from the knees down, in dark uniform trousers and boots.')]),
    ('065-067', 'gemini_maki2_h3_v1'): dict(seed=2610011065, label='真希→Gemini新二设·光柱中站立',
        subjects=[('GEM_MAKI2', None, 'the young woman with short dark hair, scarred arms and a sleeveless top (Maki)')],
        preserve='the underground space with pillars of light, the cold green light and the upward camera tilt',
        shots=[(None, 'an underground space full of tall pillars of light: the camera tilts up <A> as she stands tall in the centre of the frame in her dark combat uniform, arms at her sides, looking down at the camera through her glasses.')],
        extras=['Her purple-to-pink ponytail and cat ears take the place of the short dark hair of <Video 1>.']),
    ('072', 'gemini_twins2_h3_v1'): dict(seed=2610011072, label='真希真依→Gemini姐妹新二设·麦田牵手奔跑',
        subjects=[('GEM_MAKI2', None, 'the girl on the left with dark green hair and red marks (Maki)'), ('GEM_MAI', None, 'the girl on the right with dark green hair in a black dress (Mai)')],
        preserve='the over-saturated wheat field, the red and green palette, the redrawn flicker of every frame and the camera',
        shots=[(None, 'an over-saturated field of red and green grass, every frame redrawn with a slight flicker: <A> on the left and <B> on the right run hand in hand toward the camera, laughing, their hair flying.')],
        extras=[TWINS]),
    ('083', 'gemini_twins2_h3_v1'): dict(seed=2610011083, label='真希真依→Gemini姐妹新二设·夜间石桥',
        subjects=[('GEM_MAKI2', None, 'the girl on the left in dark clothes (Maki)'), ('GEM_MAI', None, 'the girl on the right in a black dress (Mai)')],
        preserve='the dark stone bridge at night, the railings, the cold blue light and the high camera',
        shots=[(None, 'a dark stone bridge at night seen from above: <A> on the left and <B> on the right walk across it side by side.')],
        extras=[TWINS]),
    ('099', 'gemini_maki2_tint_h3_v1'): dict(seed=2610011099, label='真希→Gemini新二设·紫光张臂',
        subjects=[('GEM_MAKI2', 'tint_8758B9', 'the woman crouching with both arms spread in violet light (Maki)')],
        preserve='the black background, the violet glow along the arms and the camera pulling back',
        shots=[(None, 'a black background: <A> crouches in a wide stance in the centre of the frame and spreads both arms out wide, violet light glowing along her arms, as the camera pulls back.')]),
    ('134', 'gemini_maki2_red_h3_v1'): dict(seed=2610011134, label='真希→Gemini新二设·红光中挥刃',
        subjects=[('GEM_MAKI2', 'redblack', 'the fighter swinging blades through the red darkness (Maki)')],
        preserve=RED + ', the swinging blades and the fast motion fading into the red darkness',
        shots=[(None, 'red darkness: <A> spins and swings a long blade in a wide arc on the left of the frame, then vanishes into the red shadows as the blade trails off.')],
        extras=['She is drawn in shades of red on black; her ponytail and glasses show in her silhouette.']),
    ('135', 'gemini_mai_h3_v1'): dict(seed=2610011135, label='真依→Gemini新二设·奥菲利亚（漂在水中）',
        subjects=[('GEM_MAI', None, 'the short-haired girl floating face up in the water holding flowers (Mai)')],
        preserve='the painting in the style of Millais\' Ophelia, the blue-green water, the floating flowers and the still camera',
        shots=[(None, 'in the style of Millais\' Ophelia: <A> floats face up in blue-green water among floating flowers, her eyes half closed, holding a bunch of flowers in one hand.')]),
    ('074', 'gemini_twin_babies_h3_v1'): dict(seed=2610011074, label='婴儿真希真依→Gemini姐妹的婴儿版·鲁本斯',
        subjects=[('GEM_MAKI2', None, 'the baby sleeping on the left (baby Maki)'), ('GEM_MAI', None, 'the baby sleeping on the right (baby Mai)')],
        preserve='the warm oil painting in the style of Rubens, the golden blanket and the still frame',
        shots=[(None, 'a warm oil painting in the style of Rubens: two babies sleep side by side under a golden blanket, <A> on the left and <B> on the right; the image holds still.')],
        extras=['They are babies: chubby baby versions of the twins with tiny cat ears and soft purple-to-pink baby hair, painted in the same oil style.']),
    ('123', 'gemini_uro_h3_v2'): dict(seed=2610011123, label='乌鹭→Gemini新形象·仰视与拼贴（棱镜、手、烟花）',
        subjects=[('GEM_MAI', None, 'the woman with swept-back purple hair, big gold earrings and a choker looking up with a smirk (Uro)')],
        preserve='the dark background with a white light streak, the collage that appears around her - a pale hand, a prism splitting light into a rainbow, a sparkler and a splash painting - and the fixed camera',
        shots=[(None, 'a dark background crossed by a streak of white light: <A> looks up and to the left with a confident smirk, her hair swept back by wind, while a collage appears around her - a pale reaching hand, a prism splitting a beam of light into a rainbow, a bright sparkler and a splash painting.')],
        extras=['She wears big round gold earrings and a black choker as in <Video 1>; her purple-to-pink hair is swept back by the wind.']),
    # --- Zenin clan (Doubao), Eso and Kechizu (GLM sisters), the twins' mother (Bard) ---
    ('102', 'doubao_naoya_tint_h3_v1'): dict(seed=2610011102, label='禅院直哉→豆包（直哉造型）·蓝色虚影',
        subjects=[('DB_NAOYA', 'tint_7FA6E8', 'the young man glowing in blurred blue-white light (Naoya)')],
        preserve='the black background, the blurred blue-white glow and the ghostly motion blur',
        shots=[(None, 'a black background: <A> glows in blurred blue-white light in the centre-left of the frame, turning her head with a smug look, her image smearing like a ghost.')],
        extras=[DOUBAO_LOOK]),
    ('115', 'doubao_deepseek_photo_h3_v2'): dict(seed=2610011115, label='禅院家合影：前排→豆包（各造型），后排→Q版DeepSeek',
        subjects=[('DB_NAOBITO', 'tint_C5A584', 'the clan head seated in the middle of the front row (Naobito)'),
                  ('DB_JIN', 'tint_C5A584', 'the big man with wild hair seated in the front row (Jinichi)'),
                  ('DB_NAOYA', 'tint_C5A584', 'the young man in white standing at the front left (Naoya)'),
                  ('DSQ', 'tint_C5A584', 'every person standing in the rows behind the front row')],
        preserve='the old sepia photograph look, the traditional Japanese hall and its tiled roof, the stone steps, the trees and the still frame',
        shots=[(None, 'an old sepia group photograph in front of a traditional Japanese hall: the front row of clan elders sits and stands in front - <A> in the middle, <B> beside her, <C> standing at the left, and the rest of the front row also Doubao in other clan kimonos - while rows upon rows of identical <D> fill the steps behind them; the image holds still.')],
        extras=['The front row is all Doubao in different clan costumes; every person in the rows behind is a small chibi DeepSeek girl, evenly spaced like the people of <Video 1>.',
                'Everyone is tinted in the same faded sepia as the rest of the photograph.', DOUBAO_LOOK]),
    ('127', 'doubao_zenin_group_h3_v1'): dict(seed=2610011127, label='禅院家众人摆姿势→豆包（长寿郎／直毘人／甚壹／直哉造型）',
        subjects=[('DB_CHOJURO', None, 'the white-haired muscular shirtless man on the left (Chojuro)'),
                  ('DB_NAOBITO', None, 'the white-haired figure in white fur second from the left'),
                  ('DB_JIN', None, 'the tanned muscular man flexing in the middle (Jinichi)'),
                  ('DB_NAOYA', None, 'the woman in a purple dress with a string of big black beads on the right')],
        preserve='the blue-and-white sunburst sky, the white flash at the start, the comic posing and the zoom-out',
        shots=[(None, 'a white flash with a huge arm swinging away, then a blue-and-white sunburst sky as the camera zooms out on four figures striking comic poses in a row: <A> on the left, <B> next to her, <C> flexing both arms in the middle, and <D> on the right with one arm raised behind her head.')],
        extras=[DOUBAO_LOOK]),
    ('132', 'glm_sisters_red_h3_v1'): dict(seed=2610011132, label='坏相与血涂→GLM的两个妹妹·夜空红日',
        subjects=[('GLM_ESO', 'tint_D04A3A', 'the taller red-tinted figure flying on the left (Eso)'), ('GLM_KECHIZU', 'tint_D04A3A', 'the round red-tinted figure flying on the right (Kechizu)')],
        preserve='the night city far below, the red-and-black sun, the red-tinted cartoon rendering of the two figures and the slow drift',
        shots=[(None, 'a night city far below, a red-and-black sun in the sky: <A> on the left and <B> on the right fly across the sky, both drawn in flat red tones, trailing red streaks.')]),
    ('050', 'ds_glm_sisters_h3_v1'): dict(seed=2610011050, label='森林餐桌：虎杖→DeepSeek，坏相与血涂→GLM的两个妹妹',
        subjects=[('DS', None, 'the young man in a beige jacket sitting on the left (Itadori)'),
                  ('GLM_KECHIZU', None, 'the hunched green creature in the middle (Kechizu)'),
                  ('GLM_ESO', None, 'the man in a dark coat leaning in on the right (Eso)')],
        preserve='the sunlit forest banquet table with red roses, candles, wine glasses and plates, and the still camera',
        shots=[(None, 'a sunlit banquet table in a forest, set with red roses, candles and wine glasses: <A> sits on the left, <B> hunches over the table in the middle, and <C> leans in on the right.')]),
    ('077-080', 'bard_h3_v1'): dict(seed=2610011077, label='真希真依的母亲→Bard·蒙克式尖叫（眼睛黑条）',
        subjects=[('BARD', None, 'the screaming woman clutching her head with a black bar over her eyes (the twins\' mother)')],
        preserve='the rough expressionist oil painting in the style of Munch and Francis Bacon, the black bar over the eyes, the jerky zooms and the dark orange palette',
        shots=[(None, 'a rough expressionist oil painting: <A> clutches her head with both hands and screams, a black bar covering her eyes, as the view jerks closer in small jumps.')],
        extras=['She keeps the black bar over her eyes for the whole shot; her blue-violet hair and sparkle ornament are painted in the same rough strokes.']),
    # --- nameless people -> DeepSeek, per the user ---
    ('086', 'claude_ds_grey_h3_v1'): dict(seed=2610011086, label='日车→Claude；左边倒下的人→DeepSeek·炭笔法庭',
        subjects=[('CL', 'grey', 'the man slumped over the blood-stained desk in the middle (Higuruma)'),
                  ('DS', 'grey', 'the figure collapsed across the left end of the desk')],
        preserve='the charcoal drawing in the style of Daumier\'s Three Judges, the blood-stained desk, the grey wall and the still camera',
        shots=[(None, 'a rough charcoal drawing of a courtroom: <A> slumps over the blood-stained desk in the middle with her long hair falling over it, and <B> lies collapsed across the left end of the desk.')],
        extras=['Both are drawn in the same rough charcoal strokes and greys.']),
    ('106', 'grok_dsq_h3_v1'): dict(seed=2610011106, label='雷吉→Grok；身后的小弟→Q版DeepSeek',
        subjects=[('GROK', None, 'the man with red hair sitting spread on the sofa (Reggie)'), ('DSQ', None, 'every henchman standing behind the sofa')],
        preserve='the dim room, the patterned sofa, the old-photo colour grading and the still camera',
        shots=[(None, 'a dim room: <A> lounges on a patterned sofa in the middle, legs wide apart, while a row of <B> stand behind the sofa like henchmen.')]),
    ('130', 'ds_dsq_dance_h3_v1'): dict(seed=2610011130, label='高羽→DeepSeek（转身晃鲸鱼尾巴）；伴舞→Q版DeepSeek',
        subjects=[('DS', None, 'the comedian in blue-and-yellow tights dancing in the middle, who turns around and shakes his hips (Takaba)'),
                  ('DSQ', None, 'every muscular dancer in red behind and around him')],
        preserve='the neon disco stage, the coloured lights, the crowd of dancers and the camera',
        shots=[(None, 'a neon disco stage full of coloured lights: <A> dances in the middle in blue-and-yellow tights, then turns her back to the camera and wiggles her big whale tail from side to side, while a crowd of <B> dance around her.')],
        extras=['Where <Video 1> shakes his hips, <A> wags her whale tail instead.']),
    # --- other review notes ---
    ('089', 'gym_trio_h3_v2'): dict(seed=2610011089, label='健身房三人：Claude一脸不情愿（修表情）',
        subjects=[('CL', None, 'the young man in an orange hoodie on the left, joining in reluctantly (Megumi)'),
                  ('MMX', None, 'the comedian in blue-and-yellow tights in the middle (Takaba)'),
                  ('DS', None, 'the young man in a white T-shirt with an orange towel on the right (Itadori)')],
        preserve='the bright yellow gym, the dumbbell racks and the fist-raising rhythm',
        shots=[(None, 'a bright yellow gym: three people raise their fists in rhythm - <A> on the left half-heartedly, <B> in the middle with gusto, <C> on the right cheerfully.')],
        extras=['<A> looks thoroughly unwilling the whole time: a flat, embarrassed scowl, eyes looking away, raising her fist only halfway, exactly like the reluctant young man of <Video 1>.']),
    ('090', 'gpt_klimt_bomb_h3_v2'): dict(seed=2610011090, label='乙骨→GPT·克林姆特金色画；之后炸弹镜头（补回）',
        subjects=[('GPT', None, 'the young man with a sword inside the golden Klimt-style painting (Yuta)', (1,))],
        preserve='the gold-leaf painting in the style of Klimt\'s The Kiss with the dark curse creature, and the second shot exactly as it is: a bomb falling through a red sky',
        shots=[(None, 'a gold-leaf painting in the style of Klimt\'s The Kiss: <A> holds a long sword among the golden patterns, wrapped together with a dark curse creature.'),
               (t(16, '090'), 'a hard cut: a red sky streaked with dark clouds, a single bomb falling down the middle of the frame; no person.')]),
    ('136-138', 'kimi_spark_h3_v2'): dict(seed=2610011136, label='秤与绮罗罗→Kimi与Spark·霓虹拥抱（嘴巴别张太大）',
        subjects=[('KIMI', None, 'the tall blond man on the left hugging (Hakari)'), ('SPK', None, 'the girl with purple-and-blue hair on the right (Kirara)')],
        preserve='the neon bokeh lights, the pink and purple palette and the push-in',
        shots=[(None, 'neon bokeh lights in pink and purple: <A> on the left throws an arm around <B> on the right and they laugh together as the camera pushes in.')],
        extras=['They laugh with natural, friendly smiles - mouths only slightly open, never stretched wide.']),
    ('145', 'rogue_grey_h3_v2'): dict(seed=2610011145, label='羂索→初代失控AI·白色光圈（加强替换）',
        subjects=[('ROGUE', 'grey', 'the long-haired man in a black robe laughing upward inside the white circle of light (Kenjaku)')],
        preserve='the black-and-white rendering, the black frames at the start, the white circle of light with shattered edges and the black background',
        shots=[(None, 'black and white: after a moment of darkness a circle of white light with shattered edges opens, and inside it <A> throws back her head and laughs, her long hair falling behind her, the red circuit seam on her forehead showing as a pale line.')],
        extras=['The figure in the circle is fully <A>: her face, hair in a half bun and monk robe replace the man of <Video 1> completely.']),
    ('071', 'hy_walk_h3_v2'): dict(seed=2610011071, label='熊猫→HY·夜森林空地里徘徊（不是躺着）',
        subjects=[('HY', None, 'the panda wandering slowly on all fours across the clearing (Panda)')],
        preserve='the dark forest clearing at night, the deep green palette and the fixed camera',
        shots=[(None, 'a dark forest clearing at night in deep green tones: <A> wanders slowly across the clearing in the centre of the frame, small and lit in pale green, pausing and looking around.')],
        extras=['She walks; she does not lie down. Her long black-blue hair and red scarf show in the pale green light.']),
}

# Static-sheet failures: need Codex keyframes (the source frame with the character replaced, pose and lighting kept) before H3.
KEYFRAME_PLANS = {
    '094': '胀相（紫）、日车（青）、虎杖（橙）三段；日车那段保持立绘姿势没动 → 用 Codex 改原片第 10 帧做关键帧，写明举剑动作',
    '098': '雷吉、伏黑、熊猫三段；前两段做坏了 → 用 Codex 改原片第 2、8 帧做关键帧',
    '101': '秤、绮罗罗、九十九、扇依次登场；都是人设图站着不动 → 每段一张 Codex 关键帧（第 1、5、9、17 帧），人物对应次要，重在好看和动作',
    '109-111a': '绮罗罗→Spark：星空中回头、站立，结果是人设图没变化 → Codex 关键帧（回头那一刻）',
    '111b-114': '秤→Kimi：结果依旧人设图没变化 → Codex 关键帧',
    '121-122': '石流龙→Qwen：结果就是人设图 → Codex 关键帧（狞笑那一刻）',
}

if __name__ == '__main__':
    if '--queue' in sys.argv:
        import review_queue
        for (uid, rev), spec in b2.JOBS.items():
            start, end = b2.b1.interval(uid)
            prompt, refs = b2.build(spec['subjects'], spec['preserve'], spec['shots'], spec.get('extras', []), b2.p.snap_frames(end - start))
            review_queue.add(PROD, uid, rev, spec['label'], note='修改方案已定，等你说开始再推理', when='第十一批（未排期）',
                             script='pipelines/jujutsu/render_batch_0011.py', prompt=prompt, references=refs)
            print('QUEUED', uid, rev, flush=True)
        for uid, note in KEYFRAME_PLANS.items():
            review_queue.add(PROD, uid, 'keyframe_plan_v1', '关键帧方案（先做 Codex 关键帧）', note=note, when='需先生成 Codex 关键帧',
                             script='pipelines/jujutsu/render_batch_0011.py', prompt='（关键帧生成后再写完整提示词）', references=())
            print('QUEUED', uid, 'keyframe_plan_v1', flush=True)
    else:
        b2.main()
