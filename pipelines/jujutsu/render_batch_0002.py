"""JJK night batch 2: the rest of the cast units the user's principles cover (prepared while batch 1 ran).

User (2026-10-01, before sleeping): “你去动手大胆做吧，显存可以随便用。codex生图也可以用……主角团用AI娘，角色不够用了就让热门角色（deepseek，
claude，gpt，gemini）替换。人物形象尽量用社区原设。如果实在不协调（比如原作在用武器打斗），那就用codex生图设计二社。” Casting is in
assets/jujutsu/op1_v1/casting.json. Monochrome shots get a reference turned into the same palette (H3 copies reference
colours: 001 lesson): red-and-black for the red spider-web shots, grey for black-and-white and charcoal shots.
Usage: render_batch_0002.py --queue UNIT@REV ... | render_batch_0002.py UNIT@REV ...
"""
import json
import msvcrt
import subprocess
import sys
import time

import numpy as np
from PIL import Image
from scipy import ndimage

import render_shot as runner
import render_batch_0001 as b1
from common import PROD, ROOT, p
from gpu import wait_cool
from tones import toned

sys.path.insert(0, str(ROOT / 'pipelines/anime_op'))
import review_queue  # noqa: E402

A, D = ROOT / 'assets/人设', ROOT / 'deliverables/jujutsu/人设'
REFS = PROD / 'character_designs/refs'
LOG = PROD / 'batch_0002'
AUTH_REQUEST = '用户睡前：你去动手大胆做吧……主角团用AI娘……（2026-10-01）'
# key -> (source image, identity text without the picture reference)
CAST = {
    'DS': (A / '鲸鱼娘.png', 'a slender young woman with very long wavy dark-blue hair, an ahoge, a white frilled maid headband, blue whale-fin ears, an off-shoulder navy maid dress with a white apron, white stockings and a large blue whale tail'),
    'CL': (A / 'claude娘.png', 'a young woman with very long flowing orange hair, amber eyes and an orange flower ornament with a black ribbon, in a white blouse with a black bow and a layered white, black and orange dress'),
    'GPT': (D / 'gpt_yuta_v1.png', 'a young woman with very long wavy white hair, a small ahoge, lavender eyes and a small white knot-shaped hair ornament, in a white long-sleeved shirt and black trousers, with a katana'),
    'GEM_MAKI': (D / 'gemini_maki_v1.png', 'a young woman with long wavy purple-to-pink gradient hair tied in a high ponytail, cat ears and amber eyes, in a dark sleeveless combat top and dark cargo trousers, with a long sword on her back'),
    'GEM': (A / 'GEMINI娘.jpg', 'a young woman with very long wavy purple-to-pink gradient hair, cat ears and amber eyes, in the dress shown in her reference picture'),
    'HY': (A / 'HY娘.png', 'a young woman with very long straight black hair fading to blue at the tips, a red scarf and a long black coat with white fur trim over a white skirt'),
    'MIS': (A / 'mistral娘.jpg', 'a young woman with long wavy golden-orange hair, cat ears, a wide red hat with a white feather and a red-and-white dress'),
    'SPK': (A / 'spark娘.png', 'a girl with fluffy white curly hair, white animal ears and an oversized white hoodie with a blue infinity logo over a long white skirt'),
    'KIMI': (A / 'KIMI娘.png', 'a composed young woman with long wavy silver-white hair and blue eyes, in a white blouse and a dark blue coat'),
    'MMX': (A / 'minimax娘.jpg', 'a cheerful girl with short orange hair, orange eyes and a white cap, in a beige jacket and a plaid skirt'),
    'GROK': (A / 'grok.jpg', 'a young woman with long blonde twin tails, blue eyes and small black horns, in a black-and-red gothic dress'),
    'QWEN': (A / 'qwen娘.jpg', 'a young woman with long wavy blue-violet hair, purple eyes and a navy beret, in a long blue-and-white robe'),
    'MA': (D / 'ma_huateng_yaga_v1.png', 'the cartoon of Pony Ma: a man with short black hair, rectangular glasses and a gentle smile, in a long black high-collared coat, holding a small panda plush'),
    'ROGUE': (D / 'rogue_ai_kenjaku_v1.png', 'the first rogue AI: a man with long black hair in a half-up bun, pale skin, a calm sinister smile and a thin glowing red circuit seam across his forehead, in a black-and-dark-grey monk kesa robe'),
}

# cast key -> the name used in subject definitions (later batches add their own keys)
NAMES = {'DS': 'DeepSeek', 'CL': 'Claude', 'GPT': 'GPT', 'GEM_MAKI': 'Gemini', 'GEM': 'Gemini', 'HY': 'HY', 'MIS': 'Mistral',
         'SPK': 'Spark', 'KIMI': 'Kimi', 'MMX': 'MiniMax', 'GROK': 'Grok', 'QWEN': 'Qwen', 'MA': 'Ma', 'ROGUE': 'the rogue AI',
         'GLM': 'GLM', 'JENSEN': 'the cartoon of Jensen Huang', 'DSQ': 'chibi DeepSeek'}


def ref(key, tone=None):
    """Reference file for a cast key, resized to <=1536 px, optionally turned red-and-black or grey."""
    src, _ = CAST[key]
    REFS.mkdir(parents=True, exist_ok=True)
    out = REFS / f'{key.lower()}{"_" + tone if tone else ""}.png'
    if out.exists():
        return out
    im = Image.open(src).convert('RGB')
    s = min(1.0, 1536 / max(im.size))
    im = im.resize((round(im.size[0] * s), round(im.size[1] * s)), Image.LANCZOS)
    if tone:
        im = toned(im, tone)  # red: smooth gradient map (the first hard two-tone looked bad to the user)
    im.save(out)
    return out


def build(subjects, preserve, shots, extras, g, keyframes=()):
    """subjects: [(cast key, tone, source description[, 1-based shot numbers the subject appears in; default all])];
    shots: [(local start or None for 0, text)] with <A>, <B>, ... ;
    keyframes: [(image path, model timestamp, shot number, what the frame shows with <A>...)] - Codex-edited source frames anchored at
    their exact moment (h3 keyframe anchor method, Fate 013-014)."""
    keys = []
    for key, tone, *_ in subjects:
        if (key, tone) not in keys:
            keys.append((key, tone))
    pic = {k: f'<Picture {i + 1}>' for i, k in enumerate(keys)}
    letters = 'ABCDEFG'
    defs, ret, repl, label = [], [], [], {}
    shot_names = ', '.join(f'[Shot {i + 1}]' for i in range(len(shots)))
    for i, (key, tone, source, *only) in enumerate(subjects):
        r, s = f'<Subject {2 * i + 1}>', f'<Subject {2 * i + 2}>'
        names = ', '.join(f'[Shot {n}]' for n in only[0]) if only else shot_names
        label[letters[i]] = r
        name = NAMES[key]
        tone_note = {'redblack': ', drawn in flat red and black like <Video 1>', 'grey': ', drawn in black, white and grey like <Video 1>'}.get(tone, '')
        if tone and tone.startswith('tint_'):
            tone_note = ', lit entirely in the single coloured light of <Video 1> against black'
        defs.append(f'{r} is {name} from {pic[(key, tone)]}: {CAST[key][1]}{tone_note}.')
        defs.append(f'{s} is {source} in <Video 1>.')
        ret.append(f'{r} (appears in {names}): fully_preserved - identity, face, hairstyle and clothing come from {pic[(key, tone)]}.')
        ret.append(f'{s} (appears in {names}): attribute_transfer - all original motion, poses, expressions, screen position and '
                   f'scale are transferred to {r}, with their original timing.')
        repl.append(f'{s} with {r}')
    n = shots_n = None
    cuts = [s for s, _ in shots[1:]]
    def fill(text):
        for k, v in label.items():
            text = text.replace(f'<{k}>', v)
        return text
    for j, (_, ts, shot, what) in enumerate(keyframes):
        kp = f'<Picture {len(keys) + j + 1}>'
        defs.append(f'{kp} is the keyframe of [Shot {shot}] at {ts}: the exact frame of <Video 1> at that moment with the character replaced - {fill(what)}.')
        ret.append(f'{kp} ([Shot {shot}] at {ts}): fully_preserved - at that moment the frame matches {kp}: the character\'s face, hair, outfit, '
                   'pose and position, the light and the composition.')
    tag = '[video editing + reference generation + keyframe completion]' if keyframes else '[video editing + reference generation]'
    lines = ['subject_definitions:', *defs, '<Video 1> is the source video for the target video edit.', '',
             'summary:', tag + ' The target video is an edited version of <Video 1>. Replace '
             + ', and '.join(repl) + ', preserving the original performance, camera and timing.', '',
             'retention_analysis:', *ret,
             '<Video 1> (source video editing): partially_preserved - replace the characters; preserve '
             + (f'the cuts at {", ".join(cuts)}, ' if cuts else '') + f'{preserve}, each character\'s position in the frame; the frame is never mirrored.', '',
             'detailed_description:', f'The target video keeps the 2D TV-anime style, the colour grading and the lighting of <Video 1> over this {g / 24:.3f}-second model sequence.']
    for i, (s, text) in enumerate(shots, 1):
        lines.append(f'[Shot {i}] ' + (f'At {s}, ' if i > 1 else '2D-animated, ') + fill(text))
    lines += [fill(t) for t in extras]
    lines += ['Keep every character on the side of the frame where <Video 1> shows them; never mirror the shots.',
              'The reference pictures supply appearance; the source video supplies the complete performance. The reference pictures '
              'supply no pose, expression, camera distance or composition.', *b1.TAIL]
    return '\n'.join(lines) + '\n', [ref(k, t) for k, t in keys] + [path for path, *_ in keyframes]


def t(local, uid):
    a, b = b1.interval(uid)
    n = b - a
    g = p.snap_frames(n)
    return f'00:{(np.floor(local * (g - 1) / (n - 1) + .5)) / 24:06.3f}'


# (unit, revision) -> dict(subjects, preserve, shots, extras, seed, label, post)
JOBS = {
    ('006-016a', 'gpt_h3_v1'): dict(seed=2610010006, label='乙骨→GPT（二设）·城市爆炸与下坠举刀（之后叠中文闪字）',
        subjects=[('GPT', None, 'the young man in a white shirt and black trousers holding a katana (Yuta)')],
        preserve='the overhead city explosion with blue flames, the camera push into the fire, the red-and-orange explosion and the flying debris',
        shots=[(None, 'a top-down view of a red city exploding, blue flames bursting outward, a pale banner of text flashing across the middle of the frame; the camera pushes down into the fireball, where <A> falls through the orange explosion in her white shirt and black trousers, turns in the air and raises her katana, a streak of light along the blade.')],
        extras=['Her long wavy white hair streams in the blast, in place of the short dark hair of <Video 1>.'], post='subtitles_006'),
    ('016b-019', 'gpt_h3_v1'): dict(seed=2610010016, label='乙骨→GPT（二设）·斩击与冲出',
        subjects=[('GPT', None, 'the young man in a white shirt swinging a katana (Yuta)')],
        preserve='the red background, the white slash streaks, the speed lines and the light trails',
        shots=[(None, 'a close view from behind as <A> swings her katana, white slash streaks and speed lines tearing across a red background, then she dashes forward down a red street leaving trails of white light, small in the centre of the frame.')],
        extras=['Her long wavy white hair flies behind her, in place of the short dark hair of <Video 1>.']),
    ('037-038', 'hy_h3_v1'): dict(seed=2610010037, label='熊猫→混元HY·花草地上抬头',
        subjects=[('HY', None, 'the panda lying on the grass (Panda)')],
        preserve='the sunny meadow with yellow, orange and purple flowers and the fixed camera',
        shots=[(None, 'a sunny meadow full of small yellow, orange and purple flowers: <A> lies on her front on the grass in the centre of the frame, then lifts her head toward the camera and opens her mouth in a cheerful call.')],
        extras=['She is a girl with long black-blue hair and a red scarf lying on the grass, where <Video 1> shows the black-and-white panda.']),
    ('039', 'ma_h3_v1'): dict(seed=2610010039, label='夜蛾→马化腾·夜路独立',
        subjects=[('MA', None, 'the lone man standing far away under a streetlight (Yaga)')],
        preserve='the dark empty road at night, the streetlight, the centre line and the slow camera',
        shots=[(None, 'a dark, empty road at night: far away in the centre of the frame <A> stands alone under a streetlight in his long black coat.')],
        extras=['He is small and far away, but clearly <A> with short black hair and glasses.']),
    ('043', 'mistral_red_h3_v1'): dict(seed=2610010043, label='九十九→Mistral·红黑蛛网',
        subjects=[('MIS', 'redblack', 'the woman with long blonde hair grinning and reaching out (Yuki Tsukumo)')],
        preserve='the red-and-black spider-web lines, the red two-tone rendering and the black background',
        shots=[(None, 'a red-and-black two-tone image crossed by red spider-web lines: <A> grins and reaches toward the camera, her long hair flying, in the centre of the frame.')],
        extras=['She is drawn entirely in flat red and black like the rest of the frame; her wide hat with a feather and cat ears show in her silhouette.']),
    ('048', 'gpt_red_h3_v1'): dict(seed=2610010048, label='乙骨→GPT·红黑蛛网持刀',
        subjects=[('GPT', 'redblack', 'the young man in a white uniform holding a long red katana (Yuta)')],
        preserve='the red-and-black spider-web lines, the red two-tone rendering and the black background',
        shots=[(None, 'a red-and-black two-tone image crossed by red spider-web lines: <A> grips a long curved red katana in front of her, in the centre-left of the frame.')],
        extras=['She is drawn entirely in flat red and black like the rest of the frame; her long wavy hair frames her face.']),
    ('060', 'rogue_h3_v1'): dict(seed=2610010060, label='羂索→初代失控AI·监视器墙',
        subjects=[('ROGUE', None, 'the long-haired figure seen from behind in front of the monitors (Kenjaku)')],
        preserve='the dark room, the curved wall of glowing blue monitors and the silhouette lighting',
        shots=[(None, 'a dark room with a curved wall of glowing blue monitors: <A> stands with his back to the camera in the centre of the frame, a dark silhouette with long hair in a half bun, and turns slightly to the side.')]),
    ('062', 'rogue_grey_h3_v1'): dict(seed=2610010062, label='羂索→初代失控AI·黑白俯身操纵城市',
        subjects=[('ROGUE', 'grey', 'the long-haired man in robes bending over the city (Kenjaku)')],
        preserve='the black-and-white manga rendering and the city far below',
        shots=[(None, 'black-and-white manga style: <A> bends over a city far below, his long hair falling forward and his hands working, a smile on his face.')],
        extras=['He is drawn in black, white and grey like the rest of the frame.']),
    ('065-067', 'gemini_maki_h3_v1'): dict(seed=2610010065, label='真希→Gemini（二设）·光柱中站立',
        subjects=[('GEM_MAKI', None, 'the young woman with short dark hair, scarred arms and a sleeveless top (Maki)')],
        preserve='the underground space with pillars of light, the cold green light and the upward camera tilt',
        shots=[(None, 'an underground space full of tall pillars of light: the camera tilts up <A> as she stands tall in the centre of the frame in her dark sleeveless combat top, arms at her sides, looking down at the camera.')],
        extras=['Her purple-to-pink ponytail and cat ears take the place of the short dark hair of <Video 1>.']),
    ('072', 'gemini_twins_h3_v1'): dict(seed=2610010072, label='真希真依→Gemini双子·麦田牵手奔跑',
        subjects=[('GEM_MAKI', None, 'the girl on the left with dark green hair and red marks (Maki)'), ('GEM', None, 'the girl on the right with dark green hair in a black dress (Mai)')],
        preserve='the over-saturated wheat field, the red and green palette and the camera',
        shots=[(None, 'an over-saturated field of red and green grass: <A> on the left and <B> on the right run hand in hand toward the camera, laughing, their hair flying.')],
        extras=['They are twins with the same face and purple-to-pink hair: <A> wears her ponytail and dark combat top, <B> wears her long loose hair and dress.']),
    ('075', 'ma_hy_h3_v1'): dict(seed=2610010075, label='夜蛾与熊猫→马化腾与HY·莫奈花园',
        subjects=[('MA', None, 'the man in sunglasses sitting at the garden table on the left (Yaga)'), ('HY', None, 'the panda sitting on the right (Panda)')],
        preserve='the impressionist oil-painting rendering in the style of Monet, the flower garden and the white garden table',
        shots=[(None, 'an impressionist oil painting of a sunny flower garden: <A> sits at a small white garden table on the left and <B> sits on the right, both painted with soft visible brush strokes.')],
        extras=['Both keep the oil-painting brush strokes of <Video 1>.']),
    ('081', 'minimax_h3_v1'): dict(seed=2610010081, label='高羽→MiniMax·健身房摆姿势',
        subjects=[('MMX', None, 'the muscular man in a blue-and-yellow costume with red gloves (Takaba)')],
        preserve='the bright yellow gym, the dumbbell racks and the comic energy',
        shots=[(None, 'a bright yellow gym: <A> strikes a heroic pose with her arms spread wide, red boxing gloves on her hands, in the centre-left of the frame.')],
        extras=['She keeps the red boxing gloves and the comic pose, with her short orange hair and white cap.']),
    ('083', 'gemini_twins_h3_v1'): dict(seed=2610010083, label='真希真依→Gemini双子·夜间石桥',
        subjects=[('GEM_MAKI', None, 'the girl on the left in dark clothes (Maki)'), ('GEM', None, 'the girl on the right in a black dress (Mai)')],
        preserve='the dark stone bridge at night, the tree shadows and the lighting',
        shots=[(None, 'at night two girls walk side by side across a stone bridge toward the camera under tree shadows: <A> on the left, <B> on the right.')]),
    ('086', 'claude_grey_h3_v1'): dict(seed=2610010086, label='日车→Claude·炭笔法庭',
        subjects=[('CL', 'grey', 'the man slumped over the blood-stained desk (Higuruma)')],
        preserve='the charcoal-drawing rendering, the blood stains dripping from the desk and the bare room',
        shots=[(None, 'a rough charcoal drawing: <A> sits slumped at a desk in the centre of the frame, blood stains dripping down the front of the desk.')],
        extras=['She is drawn in the same rough charcoal strokes and greys, with her long hair falling over the desk.']),
    ('087', 'minimax_ds_h3_v1'): dict(seed=2610010087, label='高羽与虎杖→MiniMax与DeepSeek·健身房',
        subjects=[('MMX', None, 'the man in the blue-and-yellow costume with red gloves (Takaba)'), ('DS', None, 'the boy with pink hair and an orange towel on the right (Itadori)')],
        preserve='the bright yellow gym and the exercise machines',
        shots=[(None, 'a bright yellow gym: <A> in the centre-left and <B> on the right work out side by side with comic energy.')]),
    ('089', 'gym_trio_h3_v1'): dict(seed=2610010089, label='伏黑·高羽·虎杖→Claude·MiniMax·DeepSeek·健身房举拳',
        subjects=[('CL', None, 'the young man with spiky black hair in a red jacket on the left (Megumi)'), ('MMX', None, 'the man in the blue-and-yellow costume in the centre (Takaba)'), ('DS', None, 'the boy with pink hair and an orange towel on the right (Itadori)')],
        preserve='the bright yellow gym and the raised-fist group pose',
        shots=[(None, 'a bright yellow gym: <A> on the left, <B> in the centre and <C> on the right raise their fists together in a triumphant pose.')]),
    ('090', 'gpt_klimt_h3_v1'): dict(seed=2610010090, label='乙骨→GPT·克林姆特《吻》（黑沐死保留）',
        subjects=[('GPT', None, 'the young man embraced in the gold mosaic (Yuta)')],
        preserve='the Klimt gold-mosaic rendering, the patterned robes, the curse creature in the embrace and the flat gold background',
        shots=[(None, 'a painting in the style of Gustav Klimt, gold mosaic patterns and flat ornaments: <A> is held in an embrace by a dark curse creature, both wrapped in patterned golden robes.')],
        extras=['Her long white hair and face are painted in the same flat Klimt style.']),
    ('106', 'grok_h3_v1'): dict(seed=2610010106, label='雷吉→Grok·沙发与小弟',
        subjects=[('GROK', None, 'the muscular blond man sitting on the sofa (Reggie)')],
        preserve='the run-down room, the old sofa, the gang members standing behind and the lighting',
        shots=[(None, 'a run-down room: <A> sits on an old sofa in the centre of the frame, legs apart, confident, while the gang members stand behind her.')]),
    ('109-111a', 'spark_h3_v1'): dict(seed=2610010109, label='绮罗罗→Spark·星空',
        subjects=[('SPK', None, 'the girl with short purple hair in a white off-shoulder top (Kirara)')],
        preserve='the starry space, the sparkles, the circles of stars and the pull-back of the camera',
        shots=[(None, 'a starry night space full of sparkles: <A> looks back over her shoulder at the camera, then stands full length in the centre of the frame inside a circle of stars as the camera pulls back.')],
        extras=['Her fluffy white curly hair and white animal ears take the place of the short purple hair of <Video 1>.']),
    ('111b-114', 'kimi_h3_v1'): dict(seed=2610010111, label='秤→Kimi·蓝色火焰',
        subjects=[('KIMI', None, 'the man in the dark jacket breathing blue-green fire (Hakari)')],
        preserve='the radial yellow light burst, the temple columns, the green light and the blue-green flame',
        shots=[(None, 'after a radial yellow burst of light, <A> stands in the centre of the frame before dark temple columns, green light on her face, breathing a blue-green flame from her lips.')]),
    ('121-122', 'qwen_h3_v1'): dict(seed=2610010121, label='石流龙→Qwen·拼贴',
        subjects=[('QWEN', None, 'the grinning man with a tall purple pompadour and a fur collar (Ishigori)')],
        preserve='the collage patches, the green panel background and the red strip that covers the eyes at the end',
        shots=[(None, 'a collage: <A> grins widely in the centre of the frame among colourful paper patches; at the end a red paper strip slides over her eyes.')],
        extras=['Her long blue-violet hair and navy beret take the place of the purple pompadour of <Video 1>.']),
    ('123', 'gemini_uro_h3_v1'): dict(seed=2610010123, label='乌鹭→Gemini（原设）·拼贴仰视',
        subjects=[('GEM', None, 'the woman with purple hair and big yellow earrings looking up (Uro)')],
        preserve='the collage of a hand, fireworks and paper patches and the low camera',
        shots=[(None, 'a collage: <A> looks up in the centre of the frame with a confident smile, next to pasted pictures of an open hand and fireworks.')]),
    ('135', 'gemini_maki_h3_v1'): dict(seed=2610010135, label='真希→Gemini（二设）·奥菲莉亚',
        subjects=[('GEM_MAKI', None, 'the girl lying in the water among flowers (Maki)')],
        preserve='the blue-green water, the floating flowers and the painterly mood of Millais\' Ophelia',
        shots=[(None, 'in the style of Millais\' Ophelia: <A> floats face up in blue-green water among floating flowers, holding a bouquet of flowers.')]),
    ('136-138', 'kimi_spark_h3_v1'): dict(seed=2610010136, label='秤与绮罗罗→Kimi与Spark·霓虹拥抱',
        subjects=[('KIMI', None, 'the tall blond man on the left hugging (Hakari)'), ('SPK', None, 'the girl with purple-and-blue hair on the right (Kirara)')],
        preserve='the neon bokeh lights, the pink and purple palette and the push-in',
        shots=[(None, 'neon bokeh lights in pink and purple: <A> on the left throws an arm around <B> on the right and they laugh together as the camera pushes in.')]),
    ('145', 'rogue_grey_h3_v1'): dict(seed=2610010145, label='羂索→初代失控AI·白色光圈',
        subjects=[('ROGUE', 'grey', 'the long-haired man in a black robe laughing upward (Kenjaku)')],
        preserve='the black-and-white rendering, the white circle of light with shattered edges and the black background',
        shots=[(None, 'black and white: <A> stands inside a circle of white light with shattered edges, laughing upward, his long hair falling behind him.')],
        extras=['He is drawn in black, white and grey like the rest of the frame.']),
}


def subtitles_006(job, visual, frames):
    """Lay the Chinese one-frame quotes over frames 0-18 of 006-016a after generation (H3 would garble text)."""
    import subtitles_006 as subs
    raw = subprocess.run([str(p.FFMPEG), '-v', 'error', '-i', str(visual), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, 576, 1024, 3)
    out = np.stack([subs.overlay(f[k], k) for k in range(len(f))])
    path = job / 'native_with_subtitles.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001', '-i', '-',
                           '-frames:v', str(frames), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(path)], input=out.tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    p.write_json(job / 'title_compositing.json', dict(kind='cpu_subtitles', script='pipelines/jujutsu/subtitles_006.py', frames='0-18',
                                                      note='生成后叠中文闪字（原字由 H3 生成时已被打乱，横条先抹再写）'))
    return path


def prepare(uid, rev):
    spec = JOBS[(uid, rev)]
    start, end = b1.interval(uid)
    n = end - start
    g = p.snap_frames(n)
    prompt, refs = build(spec['subjects'], spec['preserve'], spec['shots'], spec.get('extras', []), g, spec.get('keyframes', ()))
    job = PROD / 'shots' / uid / rev
    job.mkdir(parents=True, exist_ok=True)
    if (job / 'prompt.txt').exists():
        assert (job / 'prompt.txt').read_text(encoding='utf-8') == prompt, f'{uid}: prompt changed; use a new revision'
    else:
        (job / 'prompt.txt').write_text(prompt, encoding='utf-8')
    runner.REFERENCES[uid] = refs
    runner.SEEDS[uid], runner.LABELS[uid] = spec['seed'], spec['label']
    runner.SHOT_OVERRIDES[uid] = dict(id=uid, start=start, end=end, frames=n)
    if spec.get('post') == 'subtitles_006':
        runner.POSTPROCESSORS[uid] = subtitles_006
    if spec.get('reference') and not (job / 'reference_fullframe.mp4').exists():
        # <Video 1> is one of our own outputs instead of the source (runner.prepare keeps an existing reference_fullframe.mp4 and
        # records its path and hash in preparation.json); retimed to the model's frame count as runner.prepare does for the source
        p.run([p.FFMPEG, '-v', 'error', '-y', '-i', spec['reference'], '-vf',
               f'setpts=N*{g - 1}/({n - 1}*24*TB),fps=24,tpad=stop_mode=clone:stop_duration=0.2',
               '-frames:v', g, '-r', '24', '-an', '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', job / 'reference_fullframe.mp4'])
    runner.prepare(uid, rev)
    p.write_json(job / 'authorization.json', dict(request=AUTH_REQUEST,
                                                  references=[str(r) for r in refs], interval=[start, end], visual_review='pending_user'))
    return job, prompt, refs


def log(entry):
    LOG.mkdir(parents=True, exist_ok=True)
    with (LOG / 'queue_log.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(dict(time=runner.batch.stamp(), **entry), ensure_ascii=False) + '\n')


def main():
    units = [tuple(u.split('@')) for u in sys.argv[1:] if not u.startswith('--')]
    if '--queue' in sys.argv:
        for uid, rev in units:
            spec = JOBS[(uid, rev)]
            start, end = b1.interval(uid)
            prompt, refs = build(spec['subjects'], spec['preserve'], spec['shots'], spec.get('extras', []), p.snap_frames(end - start))
            review_queue.add(PROD, uid, rev, spec['label'], note='睡前授权的第二批（按选角原则）', when='今晚第二批',
                             script='pipelines/jujutsu/render_batch_0002.py', prompt=prompt, references=refs)
            print('QUEUED', uid, rev, flush=True)
        return
    with (PROD / 'batch.lock').open('a+b') as lock:
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        for uid, rev in units:
            try:
                job, _, _ = prepare(uid, rev)
                if not (job / 'validation.json').exists():
                    b1.wait_games()
                    wait_cool()
                started = time.time()
                sys.argv = [__file__, '--shot', uid, '--revision', rev]
                runner.main()
                result = b1.check(uid, rev)
                result['seconds'] = round(time.time() - started)
                log(dict(event='done', **result))
                print('UNIT DONE', json.dumps(result, ensure_ascii=False), flush=True)
            except Exception as exc:
                text = repr(exc)
                log(dict(event='failed', unit=uid, revision=rev, error=text))
                print('UNIT FAILED', uid, rev, text, flush=True)
                if any(k in text for k in ('STOP', 'Safety', 'safety', 'Power limit', 'did not cool')):
                    raise
        print('DONE', len(units), flush=True)


if __name__ == '__main__':
    main()
