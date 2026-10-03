"""JJK batch 9: fixes from the user's review-page notes (2026-10-01 15:29-15:39).

Notes used here: 026b-029 “这个应该是胀相”; 036 “是伏黑惠”; 041 “禅院真依” (v1 wrongly made it Kenjaku); 046 “是禅院真依”;
047 “手部动作不对。” (the source holds both hands pressed together in front of the chest; v1 never said so); 050 “左边虎杖，右边
不认识，换成claude也行”; 051 “不认识的路人角色。随便找一个吧。” (-> Qwen, whose long blue-violet hair matches the woman in the bed);
052 “好像是管理层人物，我没认出是谁。” (upside-down man with sunglasses and stubble: Yaga, already Ma Huateng); 054 “这是被宿傩夺舍的虎杖”.
Mai is Gemini in her community design (casting.json); the Maki redesign the user asked for is separate.
"""
import sys

import render_batch_0003  # noqa: F401  (adds GLM to the cast)
import render_batch_0002 as b2
from common import PROD

b2.LOG = PROD / 'batch_0009'
b2.AUTH_REQUEST = '用户审阅页备注（2026-10-01 15:29-15:39）：026b-029、036、041、046、047、050、051、052、054'
t = b2.t
RED = 'the red-and-black two-tone rendering and the black background'

b2.JOBS = {
    ('026b-029', 'glm_grey_h3_v1'): dict(seed=2610010026, label='胀相→GLM·昏暗大厅翻滚（黑白冷调）',
        subjects=[('GLM', 'grey', 'the figure in a white top and dark baggy trousers tumbling through the hall (Choso)')],
        preserve='the dim traditional Japanese hall with paper screens, the round ceiling lamp, the cold black-and-white rendering, the wide camera and the tumbling motion',
        shots=[(None, 'a dim traditional Japanese hall in cold black and white, a round lamp glowing on the ceiling: <A> flips and tumbles through the air in the middle of the hall, small in the wide frame, and lands rolling across the floor.')],
        extras=['She is drawn in the same cold greys as the hall; her long hair and fox tail swing as she tumbles.']),
    ('036', 'claude_red_h3_v1'): dict(seed=2610010036, label='伏黑惠→Claude·红色家纹前跪地／走廊尽头',
        subjects=[('CL', 'redblack', 'the young man crouching beneath the glowing red crest symbols (Megumi)', (1, 2, 3, 4))],
        preserve=RED + ', the glowing red clan crest symbols, the red corridor and the final crest wheel without any person',
        shots=[(None, 'red and black: <A> crouches low in front of a large glowing red crest symbol, one hand on the floor.'),
               (t(4, '036'), 'a hard cut: <A> kneels inside a different glowing red crest shape in the centre of the frame.'),
               (t(14, '036'), 'a hard cut: <A> stands small at the far end of a long red corridor beneath a huge hood-shaped red symbol.'),
               (t(18, '036'), 'a hard cut: a red wheel-shaped crest symbol glows in a dark hall; no person.')],
        extras=['She is drawn entirely in shades of red on black like the rest of the frame; her long hair shows in her silhouette.']),
    ('041', 'gemini_mai_ds_h3_v1'): dict(seed=2610010141, label='真依→Gemini（原设）·暗场紫光中舞动；之后虎杖→DeepSeek',
        subjects=[('GEM', None, 'the dark-haired woman in a black outfit swaying with her arms raised in violet light in the first shot (Mai)', (1,)),
                  ('DS', None, 'the young man with short light hair in black thrown through grey smoke in the second shot (Itadori)', (2,))],
        preserve='the dark scene, the thin violet beam of light and city lights of the first shot, the grey smoke of the second shot and the camera movement',
        shots=[(None, 'a dark scene lit by a thin violet beam of light, city lights far below: <A> on the left of the frame sways and leans back with her arms raised, her hair flowing.'),
               (t(13, '041'), 'a hard cut: in thick grey smoke, <B> is thrown backward through the air, arms flung out.')]),
    ('046', 'gemini_mai_red_h3_v1'): dict(seed=2610010046, label='真依→Gemini（原设）·红黑蛛网横握巨刃',
        subjects=[('GEM', 'redblack', 'the figure at the top holding a huge serrated blade sideways (Mai)')],
        preserve='the red spider-web lines, ' + RED + ', and the huge serrated blade across the frame',
        shots=[(None, 'a red-and-black two-tone image crossed by red spider-web lines: <A> leans over the top of the frame gripping a huge serrated blade that stretches sideways across the whole frame.')],
        extras=['She is drawn entirely in shades of red on black like the rest of the frame; her cat ears and long hair show in her silhouette.']),
    ('047', 'glm_red_h3_v2'): dict(seed=2610010247, label='胀相→GLM·红黑血线汇聚，双手合于胸前（修手部动作）',
        subjects=[('GLM', 'redblack', 'the figure in the centre holding both hands pressed together in front of the chest as lines of blood converge (Choso)')],
        preserve='the red spider-web lines, ' + RED + ', and the glowing knot of blood between the hands',
        shots=[(None, 'a red-and-black two-tone image: <A> stands in the centre of the frame with both hands pressed together palm to palm in front of her chest, and glowing red lines of blood radiate outward from her joined hands across the black.')],
        extras=['Her hands stay pressed together in front of her chest for the whole shot, exactly as in <Video 1>; she is drawn in shades of red on black, her fox ears and long hair in silhouette.']),
    ('050', 'ds_claude_h3_v1'): dict(seed=2610010050, label='森林餐桌：虎杖→DeepSeek（左），右边男人→Claude',
        subjects=[('DS', None, 'the young man in a beige jacket sitting on the left (Itadori)'),
                  ('CL', None, 'the man in a dark coat leaning in on the right')],
        preserve='the sunlit forest banquet table with red roses, candles, wine glasses and plates, the green cursed creature in the middle, and the still camera',
        shots=[(None, 'a sunlit banquet table in a forest, set with red roses, candles and wine glasses: <A> sits on the left and <B> leans in on the right, with a hunched green creature between them.')]),
    ('051', 'qwen_h3_v1'): dict(seed=2610010051, label='病床上的路人→Qwen',
        subjects=[('QWEN', None, 'the long-haired woman lying asleep in the hospital bed')],
        preserve='the pale hospital room, the white sheets and bed rails, and the tilted still camera',
        shots=[(None, 'a pale hospital room: <A> lies asleep in a white hospital bed, her long hair spread over the pillow, seen at a tilted angle.')]),
    ('052', 'ma_h3_v1'): dict(seed=2610010052, label='夜蛾（倒躺）→马化腾',
        subjects=[('MA', None, 'the man with sunglasses and stubble lying upside down with an X-shaped mark beside his face (Yaga)')],
        preserve='the upside-down framing, the pale warm light, the X-shaped mark and the still camera',
        shots=[(None, 'an upside-down close view in pale warm light: <A> lies with his eyes closed, his face upside down in the frame, an X-shaped mark on the surface beside his face.')]),
    ('054', 'deepseek_sukuna_red_h3_v1'): dict(seed=2610010054, label='宿傩夺舍的虎杖→DeepSeek（宿傩纹）·红暗',
        subjects=[('DS', 'redblack', 'the young man possessed by Sukuna, with black markings under his eyes, glaring down behind glass (Itadori as Sukuna)')],
        preserve='the dark red light, the glass in front, the bloody hands at the bottom of the frame and the still camera',
        shots=[(None, 'dark red light: <A> glares down at the camera from behind a pane of glass with a cruel smile, bloody hands pressed at the bottom of the frame.')],
        extras=['She is possessed: black curse markings under her eyes and across her cheeks, and a cruel grin, in place of her gentle look.',
                'She is drawn in shades of red on black like the rest of the frame.']),
}

if __name__ == '__main__':
    if '--queue' in sys.argv:
        import review_queue
        units = [tuple(u.split('@')) for u in sys.argv[1:] if not u.startswith('--')]
        for uid, rev in units:
            spec = b2.JOBS[(uid, rev)]
            start, end = b2.b1.interval(uid)
            prompt, refs = b2.build(spec['subjects'], spec['preserve'], spec['shots'], spec.get('extras', []), b2.p.snap_frames(end - start))
            review_queue.add(PROD, uid, rev, spec['label'], note='按你在审阅页的备注修改', when='第九批',
                             script='pipelines/jujutsu/render_batch_0009.py', prompt=prompt, references=refs)
            print('QUEUED', uid, rev, flush=True)
    else:
        b2.main()
