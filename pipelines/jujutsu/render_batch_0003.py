"""JJK batch 3 (2026-10-01 daytime): the identified cast units batches 1 and 2 did not cover.

User, after batches 1 and 2 finished: “现在生成的都还可以，为什么不继续做了”. Same principles and machinery as batch 2
(render_batch_0002: CAST, ref, build, prepare, main); the units come from a contact sheet of the remaining source units.
Left for later: 026b-029 (small tumbling figure, cast unclear), 058 (seven-person line-up), 098 (three-character flash montage).
Usage: render_batch_0003.py --queue UNIT@REV ... | render_batch_0003.py UNIT@REV ...
"""
import sys

import render_batch_0002 as b2
from common import PROD

b2.CAST['GLM'] = (b2.A / 'GLM娘.png', 'a young woman with very long black hair with dark-blue streaks, black fox ears with white inner fur, a white frilled headband, a black capelet with blue lining over a white blouse, a long black pleated skirt and a large black fox tail with a white tip')
b2.LOG = PROD / 'batch_0003'
b2.AUTH_REQUEST = '用户（2026-10-01 白天，第一二批跑完后）：现在生成的都还可以，为什么不继续做了'

RED = 'the red spider-web lines, the red two-tone rendering and the black background'
b2.JOBS = {
    ('040', 'gpt_ukiyoe_h3_v1'): dict(seed=2610010040, label='乙骨→GPT（二设）·国芳武者绘大战巨兽',
        subjects=[('GPT', None, 'the young man with short black hair swinging a sword (Yuta)')],
        preserve='the ukiyo-e woodblock-print rendering in the style of Utagawa Kuniyoshi, the giant tiger-striped monster, its claws and the camera moves',
        shots=[(None, 'an ukiyo-e woodblock print in the style of Utagawa Kuniyoshi, in muted beige, black and red: a giant striped monster fills the frame and <A> fights it with her katana, slashing down at its huge claws in the middle of the frame.')],
        extras=['She is drawn with the same woodblock outlines and flat muted colours as the rest of the print; her long wavy white hair takes the place of the short black hair of <Video 1>.']),
    ('041', 'rogue_h3_v1'): dict(seed=2610010041, label='羂索→初代失控AI·暗场仰身伸手',
        subjects=[('ROGUE', None, 'the long-haired man in dark clothes leaning back and reaching out (Kenjaku)')],
        preserve='the dark scene, the thin violet beam of light and the camera movement',
        shots=[(None, 'a dark scene lit by a thin violet beam of light: <A> on the left of the frame leans back with one arm reaching out, then twists away into the shadows as the camera follows.')]),
    ('042', 'gpt_h3_v1'): dict(seed=2610010042, label='乙骨→GPT（二设）·被击飞',
        subjects=[('GPT', None, 'the young man with short black hair in a white shirt knocked flying backward (Yuta)')],
        preserve='the low angle, the dark grey sky with streaks of motion and the speed of the fall',
        shots=[(None, 'a low-angle view against a dark grey sky full of motion streaks: <A> is knocked backward through the air in her white shirt and black trousers, arms flung out, travelling from the lower left toward the upper right of the frame.')],
        extras=['Her long wavy white hair whips around her, in place of the short black hair of <Video 1>.']),
    ('045', 'glm_red_h3_v1'): dict(seed=2610010045, label='脹相→GLM·红黑蛛网血带',
        subjects=[('GLM', 'redblack', 'the figure with both arms spread and ribbons of blood around the neck (Choso)')],
        preserve=RED,
        shots=[(None, 'a red-and-black two-tone image crossed by red spider-web lines: <A> stands in the centre of the frame with both arms spread wide, ribbons of blood swirling around her like a scarf.')],
        extras=['She is drawn entirely in shades of red on black like the rest of the frame; her fox ears and long hair show in her silhouette.']),
    ('047', 'glm_red_h3_v1'): dict(seed=2610010047, label='脹相→GLM·红黑血线放射',
        subjects=[('GLM', 'redblack', 'the figure in the centre with lines of blood radiating outward (Choso)')],
        preserve=RED,
        shots=[(None, 'a red-and-black two-tone image: <A> stands in the centre of the frame as glowing red lines of blood radiate outward from her across the black.')],
        extras=['She is drawn entirely in shades of red on black like the rest of the frame; her fox ears and long hair show in her silhouette.']),
    ('049', 'deepseek_red_h3_v1'): dict(seed=2610010049, label='虎杖→DeepSeek·红黑伸手',
        subjects=[('DS', 'redblack', 'the figure with spiky hair on the right reaching out (Itadori)')],
        preserve=RED,
        shots=[(None, 'a red-and-black two-tone image crossed by red spider-web lines: <A> on the right of the frame reaches one arm out toward the left.')],
        extras=['She is drawn entirely in shades of red on black like the rest of the frame; her long wavy hair and maid headband show in her silhouette.']),
    ('055', 'mistral_h3_v1'): dict(seed=2610010055, label='九十九→Mistral·楼顶边缘俯瞰城市',
        subjects=[('MIS', None, 'the woman with long blonde hair standing at the roof edge (Yuki Tsukumo)')],
        preserve='the skyscraper roof edge, the city far below in daylight, the upward camera movement and the white flash at the end',
        shots=[(None, 'the edge of a skyscraper roof high above a city in daylight: the camera rises from <A>\'s feet at the edge to her back as she stands looking down over the city, her long hair blowing in the wind, then the frame flashes white.')]),
    ('064', 'gemini_maki_h3_v1'): dict(seed=2610010064, label='真希→Gemini（二设）·光柱中走来（腿部）',
        subjects=[('GEM_MAKI', None, 'the person walking, seen from the knees down (Maki)')],
        preserve='the underground space with tall pillars of light, the cold light and the low camera',
        shots=[(None, 'an underground space full of tall pillars of light: <A> walks past the low camera, seen from the knees down, in dark cargo trousers and boots.')]),
    ('071', 'hy_h3_v1'): dict(seed=2610010071, label='熊猫→混元HY·夜森林空地',
        subjects=[('HY', None, 'the panda lying in the clearing (Panda)')],
        preserve='the dark forest clearing at night, the deep green palette and the fixed camera',
        shots=[(None, 'a dark forest clearing at night in deep green tones: <A> lies on the ground in the centre of the frame, small and lit in pale green.')],
        extras=['She is a girl with long black-blue hair and a red scarf, where <Video 1> shows the panda.']),
    ('082', 'deepseek_h3_v1'): dict(seed=2610010082, label='虎杖→DeepSeek·灰底翻身飞出',
        subjects=[('DS', None, 'the young man in a red hooded top flipping through the air (Itadori)')],
        preserve='the pale grey background, the dark diagonal shadow and the motion',
        shots=[(None, 'a pale grey background with a dark diagonal shadow: <A> flips through the air from the upper left toward the right of the frame, her navy maid dress and long hair flying.')]),
    ('095-097', 'gpt_h3_v1'): dict(seed=2610010095, label='乙骨→GPT（二设）·青光中披风转身',
        subjects=[('GPT', None, 'the dark-haired figure in a pale cloak turning (Yuta)')],
        preserve='the cyan light on black, the swirling cloak and the quick cuts',
        shots=[(None, 'cyan light on a black background: <A> turns sharply on the left of the frame with a pale cloak swirling around her.')],
        extras=['Her long wavy white hair takes the place of the short dark hair of <Video 1>.']),
    ('099', 'gemini_maki_h3_v1'): dict(seed=2610010099, label='真希→Gemini（二设）·紫光张臂',
        subjects=[('GEM_MAKI', None, 'the woman crouching with both arms spread in violet light (Maki)')],
        preserve='the black background, the violet glow along the arms and the camera pulling back',
        shots=[(None, 'a black background: <A> crouches in a wide stance in the centre of the frame and spreads both arms out wide, violet light glowing along her arms, as the camera pulls back.')]),
    ('124-125', 'rogue_h3_v1'): dict(seed=2610010124, label='羂索→初代失控AI·拼贴前正面',
        subjects=[('ROGUE', None, 'the robed figure facing the camera with red lines on the robe (Kenjaku)')],
        preserve='the collage background with flat poster colour blocks, the red rising sun and the paper cut-outs, and the fixed camera',
        shots=[(None, 'a collage: <A> stands facing the camera in the centre of the frame in a black robe patterned with thin red lines, while flat poster-like colour blocks, a red rising sun and paper cut-outs appear behind him.')]),
}

if __name__ == '__main__':
    if '--queue' in sys.argv:
        import review_queue
        units = [tuple(u.split('@')) for u in sys.argv[1:] if not u.startswith('--')]
        for uid, rev in units:
            spec = b2.JOBS[(uid, rev)]
            start, end = b2.b1.interval(uid)
            prompt, refs = b2.build(spec['subjects'], spec['preserve'], spec['shots'], spec.get('extras', []), b2.p.snap_frames(end - start))
            review_queue.add(PROD, uid, rev, spec['label'], note='白天第三批（按选角原则，用户：为什么不继续做了）', when='白天第三批',
                             script='pipelines/jujutsu/render_batch_0003.py', prompt=prompt, references=refs)
            print('QUEUED', uid, rev, flush=True)
    else:
        b2.main()
