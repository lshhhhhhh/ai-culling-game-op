"""JJK batch 12 - keyframe plans (registered as 待推理; run only when the user says so).

Units whose output stayed a standing design sheet: 094 “claude那一幕动作完全不对啊，保持着立绘姿势没变过”, 098 “前两幕完全做坏了”,
101 “全是站着不动的人设图，不好看” (“人物对应是次要的，关键是好看”), 109-111a “完全就是人设图没有变化”, 111b-114 “依旧人设图没有变化”,
121-122 “这个就是人设图，需要更多设计”. Fix: the h3 keyframe anchor method (Fate 013-014) - Codex-edited source frames
(codex_keyframes_0001.py; the user: “生图任务直接去做”) anchored at their exact model timestamps, plus every source action named.
101: the user, “MISTRAL那个背景换成法棍正好” - Tsukumo's long spiked golden shikigami becomes a giant golden baguette.
"""
import sys

from PIL import Image

import render_batch_0007  # noqa: F401  (DB_OGI and friends; imports batch 3 for GLM)
import render_batch_0002 as b2
from common import PROD, ROOT

KF = ROOT / 'deliverables/jujutsu/关键帧'
b2.LOG = PROD / 'batch_0012'
b2.AUTH_REQUEST = '用户（2026-10-01 晚）：生图任务直接去做；关键帧方案先挂待推理，现在不要直接推理'
t = b2.t


def kf(name):
    """Keyframe resized to the 1024x576 model frame, stored next to the other references."""
    out = b2.REFS / name
    if not out.exists():
        Image.open(KF / name).convert('RGB').resize((1024, 576), Image.LANCZOS).save(out)
    return out


b2.JOBS = {
    ('094', 'kf_glm_cl_ds_h3_v2'): dict(seed=2610012094, label='胀相/日车/虎杖→GLM/Claude/DeepSeek·彩光登场（日车段用关键帧）',
        subjects=[('GLM', 'tint_8758B9', 'the figure lit in violet spreading huge hands and wing-like shapes in the first shot (Choso)', (1,)),
                  ('CL', 'tint_4E8C98', 'the man in a suit raising a glowing sword in teal light in the second shot (Higuruma)', (2,)),
                  ('DS', None, 'the young man with spiky hair and a red scarf holding a burning fist in orange light in the third shot (Itadori)', (3,))],
        preserve='the black background and the single coloured light of each shot: violet, then teal, then orange with fire',
        shots=[(None, 'a black background, violet light: <A> thrusts both huge hands toward the camera, then pulls back and spreads them out to both sides like wings, her body tensing.'),
               (t(8, '094'), 'a hard cut, teal light: <B> stands in the centre of the frame and raises a glowing sword straight up in front of her face with both hands, the blade flaring as she lifts it, her hair stirring.'),
               (t(14, '094'), 'a hard cut, orange light: <C> on the right turns her face to the camera and holds up her fist wrapped in flickering fire on the left.')],
        keyframes=[(kf('kf_094_f10_cl_v1.png'), t(10, '094'), 2, '<B> raising the glowing sword in teal light')]),
    ('098', 'kf_grok_claude_hy_h3_v3'): dict(seed=2610012098, label='雷吉/伏黑惠/熊猫→Grok/Claude/HY·彩光登场（前两段用关键帧）',
        subjects=[('GROK', 'tint_985CB6', 'the figure lit in violet wrapped in a skirt of fluttering paper receipts in the first shot (Reggie)', (1,)),
                  ('CL', 'tint_5C9B8F', 'the young man with spiky dark hair making a hand sign in teal light in the second shot (Megumi)', (2,)),
                  ('HY', 'tint_6CCB5A', 'the panda raising both arms in green light in the third shot (Panda)', (3,))],
        preserve='the black background and the single coloured light of each shot: violet, teal, then green',
        shots=[(None, 'a black background, violet light: <A> stands in the centre of the frame as a skirt of paper receipts flutters and swirls around her, her head turning slightly.'),
               (t(6, '098'), 'a hard cut, teal light: <B> stands in the centre of the frame and brings her hands together in front of her chest, fingers interlocking into a hand sign, her eyes narrowing.'),
               (t(12, '098'), 'a hard cut, bright green light: <C> throws both arms up high in the centre of the frame with a wide open-mouthed grin.')],
        extras=['<C> is a girl with long hair and a scarf, where <Video 1> shows the panda.'],
        keyframes=[(kf('kf_098_f02_grok_v1.png'), t(2, '098'), 1, '<A> in the skirt of receipts in violet light'),
                   (kf('kf_098_f08_cl_v1.png'), t(8, '098'), 2, '<B> making the hand sign in teal light')]),
    ('101', 'kf_lineup_baguette_h3_v2'): dict(seed=2610012101, label='秤/绮罗罗/九十九/扇→Kimi/Spark/Mistral/豆包·彩光登场（关键帧；九十九的式神→法棍）',
        subjects=[('KIMI', 'tint_3C7495', 'the broad figure lit in blue spreading his arms in the first shot (Hakari)', (1,)),
                  ('SPK', 'tint_B15FA4', 'the slim figure lit in pink in the second shot (Kirara)', (2,)),
                  ('MIS', 'tint_9D9248', 'the woman lit in gold standing beneath a long spiked shikigami in the third shot (Yuki Tsukumo)', (3,)),
                  ('DB_OGI', 'tint_AFA84D', 'the man in a kimono lit in gold who stands far away and then close to the camera in the last shot (Ogi)', (5,))],
        preserve='the black background, the single coloured light of each shot, and the small lavender-lit figure of the fourth shot exactly as it is',
        shots=[(None, 'a black background, blue light: <A> lands in the centre of the frame with her arms spread wide, then draws them in and squares her shoulders.'),
               (t(4, '101'), 'a hard cut, pink light: <B> strikes a playful pose in the centre of the frame, one hand raised, her hoodie swaying.'),
               (t(7, '101'), 'a hard cut, gold light: <C> stands in the centre of the frame with one hand on her hip, while a giant golden French baguette with a scored, glowing crust stretches across the whole frame above her, where <Video 1> shows the long spiked shikigami.'),
               (t(12, '101'), 'a hard cut: a small figure lit in lavender stands in the centre of the frame, unchanged from <Video 1>.'),
               (t(14, '101'), 'a hard cut, dim gold light: <D> stands far away in the centre of the frame, then appears close on the right, drawing her flaming katana and turning a haughty glare on the camera.')],
        extras=['<D> keeps the soft 3D-rendered look of her reference - smooth CG shading and big glossy eyes - standing out from the 2D anime around her.'],
        keyframes=[(kf('kf_101_f01_kimi_v1.png'), t(1, '101'), 1, '<A> with her arms spread in blue light'),
                   (kf('kf_101_f05_spk_v1.png'), t(5, '101'), 2, '<B> in pink light'),
                   (kf('kf_101_f09_mis_v2.png'), t(9, '101'), 3, '<C> in gold light beneath the giant golden baguette'),
                   (kf('kf_101_f17_db_ogi_v1.png'), t(17, '101'), 5, '<D> close on the right in dim gold light')]),
    ('109-111a', 'kf_spark_h3_v2'): dict(seed=2610012109, label='绮罗罗→Spark·星空回头与站立（关键帧）',
        subjects=[('SPK', None, 'the girl with purple-and-blue hair who turns her head in close-up and then stands in the starry space (Kirara)')],
        preserve='the starry space, the sparkles, the orbital rings that open around her, the stepwise zoom-out and the blue palette',
        shots=[(None, 'starry space: a close-up of <A> as she turns her head toward the camera with a teasing smile, her hair swinging.'),
               (t(4, '109-111a'), 'a cut: <A> stands full length in the middle of the starry space, arms loose at her sides, swaying slightly, as the camera pulls back in steps and glowing orbital rings open around her.')],
        keyframes=[(kf('kf_109-111a_f01_spk_v1.png'), t(1, '109-111a'), 1, 'the close-up of <A> turning her head'),
                   (kf('kf_109-111a_f10_spk_v1.png'), t(10, '109-111a'), 2, '<A> standing full length among the stars and rings')]),
    ('111b-114', 'kf_kimi_h3_v2'): dict(seed=2610012111, label='秤→Kimi·神殿前口吐蓝焰（关键帧）',
        subjects=[('KIMI', None, 'the man with spiky hair breathing blue flame in front of a temple (Hakari)')],
        preserve='the dark Greek temple behind, the dim green light, the blue flame and the bursts of gold light rays from both sides',
        shots=[(None, 'in front of a dark Greek temple in dim green light: <A> throws her head back and breathes a jet of blue flame from her mouth while bursts of golden light rays shoot out from both sides of the frame and fade.')],
        keyframes=[(kf('kf_111b-114_f02_kimi_v1.png'), t(2, '111b-114'), 1, '<A> breathing blue flame with the gold rays bursting')]),
    ('121-122', 'kf_qwen_h3_v2'): dict(seed=2610012121, label='石流龙→Qwen·拼贴前狞笑（关键帧）',
        subjects=[('QWEN', None, 'the grinning man with a tall pompadour in a white fur coat (Ryu Ishigori)')],
        preserve='the dark green background with white lines, the collage stickers that pop up one by one, the red striped bar that covers the eyes in the second shot and the fixed camera',
        shots=[(None, 'a dark green background with thin white lines: <A> leans in from the right with a wide, cocky grin, her fur-trimmed coat around her shoulders, as collage stickers pop up one by one around her - a green splash, a painted face, a blue panel, a red-and-black picture.'),
               (t(13, '121-122'), 'a cut: a red striped bar slaps across her eyes like a censor sticker while she keeps grinning.')],
        keyframes=[(kf('kf_121-122_f06_qwen_v1.png'), t(6, '121-122'), 1, '<A> grinning among the collage stickers')]),
}


def build_job(uid, rev):
    spec = b2.JOBS[(uid, rev)]
    start, end = b2.b1.interval(uid)
    return b2.build(spec['subjects'], spec['preserve'], spec['shots'], spec.get('extras', []), b2.p.snap_frames(end - start),
                    spec.get('keyframes', ()))


if __name__ == '__main__':
    if '--queue' in sys.argv:
        import review_queue
        for (uid, rev), spec in b2.JOBS.items():
            prompt, refs = build_job(uid, rev)
            review_queue.add(PROD, uid, rev, spec['label'], note='关键帧锚定方案（Codex 关键帧已生成）；等你说开始再推理', when='第十二批（未排期）',
                             script='pipelines/jujutsu/render_batch_0012.py', prompt=prompt, references=refs)
            print('QUEUED', uid, rev, len(refs), 'pictures', flush=True)
    else:
        b2.main()  # only when the user has said to run
