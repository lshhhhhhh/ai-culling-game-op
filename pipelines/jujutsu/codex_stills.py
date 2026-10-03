"""Still shots done as one Codex-edited frame held for the whole unit (no H3).

User (2026-10-01), on 050 (H3 put DeepSeek in profile and Claude in her design-sheet pose): “050姿势明显不对。这个静止帧需要生图吧”.
A still unit has no motion to keep, so Codex edits the source frame directly (poses, framing and light kept, only the people
replaced), the frame is held for the unit's length with the source audio, and the clip goes to the review page.
Usage: codex_stills.py UNIT [UNIT ...]   (existing stills are reused; the clip is rebuilt)
"""
import json
import os
import pathlib
import subprocess
import sys
import time

import numpy as np
from PIL import Image

import render_shot as runner
import render_batch_0001 as b1
from common import PROD, ROOT, p
from codex_keyframes_0001 import source_frame

Path = pathlib.Path
CODEX = Path(os.environ['LOCALAPPDATA']) / 'OpenAI/Codex/bin/faa963e871dd422c/codex.exe'
DIR = ROOT / 'deliverables/jujutsu/静帧'
A, D = ROOT / 'assets/人设', ROOT / 'deliverables/jujutsu/人设'
KEEP = ('Keep EXACTLY the composition, camera angle, framing, background, props, light and the 2D TV-anime rendering of Image 1, and '
        'give every replaced character exactly the pose, gesture, facial expression, size and position of the person they replace. '
        'Only identities change: faces, hair and outfits come from the reference images. No text, no watermark. The output is a 16:9 '
        'image with the framing of Image 1. Do not create or modify any other files.')
# unit -> (source frame, revision, label, [reference images], what to replace)
STILLS = {
    '050': (1, 'codex_still_v1', '森林餐桌：虎杖→DeepSeek，血涂→GLM·血涂，坏相→GLM·坏相（Codex 静帧）',
            [A / '鲸鱼娘.png', D / 'glm_kechizu_v1.png', D / 'glm_eso_v1.png'],
            'Image 1 is a frame from an anime opening: a banquet table in a sunlit forest. Replace the three people: the young man in a '
            'beige hoodie on the left, leaning on the table with a fierce grin, becomes the girl of Image 2 (DeepSeek: long wavy dark-blue '
            'hair, ahoge, white maid headband, whale-fin ears, navy maid dress) with the same lean and grin; the green creature hunched '
            'behind him with its arm around his shoulders becomes the girl of Image 3 (GLM Kechizu: fox ears, messy short black hair, a '
            'huge mischievous grin, pale green hooded jumpsuit), hunched the same way with her arm around DeepSeek\'s shoulders; the man '
            'on the right leaning in over the table with a knife and a grin becomes the girl of Image 4 (GLM Eso: fox ears, black-and-blue '
            'hair in two buns, dark green cropped top), leaning in the same way, holding the knife, grinning. '),
    # 053, the user: “没有人物。想想怎么重新设计。”, then “我想接下来处理一些没什么人物的镜头。比如053”: the standing stone in the garden
    # becomes an old computer left behind, overgrown with moss - a machine from the old era (the old clan / old guard of this OP)
    '053': (1, 'codex_still_v1', '日式回廊与庭院：庭中立石→长满青苔的旧电脑（Codex 静帧）', [],
            'Image 1 is a frame from an anime opening: a dim wooden veranda corridor on the left looking out onto a quiet garden, with a '
            'single standing stone in the garden. Replace ONLY that standing stone with an old beige desktop computer from the 1990s - a '
            'boxy CRT monitor sitting on an upright tower case - standing on the same spot at the same size, weathered, its plastic '
            'yellowed, overgrown with moss and small ferns at the base, the dark screen faintly reflecting the garden. It must look painted '
            'in the same soft, muted anime background style as the rest of Image 1. Nothing else changes. '),
    # 053 with people, the user on the computer version: “我想加入人物。比如deepseek坐在木头台阶上面晃动双腿……然后gpt在草地上挥剑”,
    # with two boxes on the frame: the edge of the veranda floor (lower middle-right) and the grass right of the stone. This still is the
    # first-frame keyframe of an H3 run (render_053_people.py) that adds the motion.
    '053p': (None, 'codex_people_v1', '日式回廊与庭院：DeepSeek 坐在回廊边晃腿，GPT 在草地上挥刀（关键帧）',
             [ROOT / 'deliverables/jujutsu/静帧/still_053_codex_still_v1.png', A / '鲸鱼娘.png', D / 'gpt_yuta_v6.png'],
             'Image 1 is a frame from an anime opening: a dim wooden veranda corridor on the left looking out onto a quiet garden with an '
             'old moss-covered computer standing in it. ADD two characters, keeping everything that is already there: (1) the girl of '
             'Image 2 (DeepSeek: very long wavy dark-blue hair, ahoge, white maid headband, whale-fin ears, navy maid dress with a white '
             'apron, white stockings, whale tail) sitting sideways on the edge of the wooden veranda floor in the lower middle-right of the '
             'frame, where the boards end above the garden, her legs dangling over the edge and swinging, a relaxed happy face; (2) the girl '
             'of Image 3 (GPT: very long wavy white hair, off-white blazer, black sailor collar, dark green tie, black pleated skirt) '
             'standing on the grass to the right of the old computer, smaller in the middle distance, in the middle of a sword swing with '
             'her katana, a faint white streak following the blade. Both are drawn in the same soft, muted 2D anime style and light as '
             'Image 1, at believable sizes for where they stand. '),
    # 056 (12 identical frames: a black sphere on orange-red, its upper-right edge crumbling): the user chose option 2 of three -
    # keep the black sun, but the crumbling edge breaks into square pixels and bits like corrupting data (“试试看2”)
    '056': (0, 'codex_still_v1', '黑太阳碎裂→边缘碎成方形像素（数据损坏）（Codex 静帧）', [],
            'Image 1 is a frame from an anime opening: a black sphere (a black sun) in front of a flat orange-red background, its '
            'upper-right edge crumbling into small irregular fragments. Keep EVERYTHING the same - the background, the sphere\'s size, '
            'position, colour and its round outline - and change ONLY the crumbling: the edge of the sphere at the upper right breaks '
            'apart into small square pixels and blocky digital fragments of different sizes, like corrupting data, drifting out from the '
            'same spot where the original fragments are, a few of them faintly glowing red at their edges. Flat 2D anime rendering, no '
            'text. '),
    # v2, the user on v1: “为什么gpt也有一个鲸鱼耳朵？而且如果静止帧就有“剑光”的特效（都弯曲了），我怕模型不能很好理解” - GPT took
    # DeepSeek's whale-fin ear, and the frozen slash streak would confuse the video model: no streak, a clean ready pose
    '053p2': (None, 'codex_people_v2', '日式回廊与庭院：DeepSeek 坐在回廊边，GPT 在草地上举刀（Codex 静帧，定格 4 帧；4 帧做不出动作，用户：还是用静止帧吧）',
              [ROOT / 'deliverables/jujutsu/静帧/still_053_codex_still_v1.png', A / '鲸鱼娘.png', D / 'gpt_yuta_v6.png'],
              'Image 1 is a frame from an anime opening: a dim wooden veranda corridor on the left looking out onto a quiet garden with '
              'an old moss-covered computer standing in it. ADD two characters, keeping everything that is already there: (1) the girl of '
              'Image 2 (DeepSeek: very long wavy dark-blue hair, ahoge, white maid headband, blue whale-fin ears, navy maid dress with a '
              'white apron, white stockings, whale tail) sitting sideways on the edge of the wooden veranda floor in the lower middle-right '
              'of the frame, where the boards end above the garden, her legs dangling over the edge, a relaxed happy face; (2) the girl of '
              'Image 3 (GPT) exactly as designed in Image 3 - very long wavy white hair with only the small white knot ornament, ordinary '
              'human ears hidden under her hair, NO whale-fin ears, NO animal ears, an off-white blazer, black sailor collar, dark green '
              'tie, black pleated skirt - standing on the grass to the right of the old computer, smaller in the middle distance, holding '
              'her katana raised in both hands, ready to swing. No motion effects at all: no slash streaks, no light trails, no speed lines - '
              'the blade is a plain straight katana. Both are drawn in the same soft, muted 2D anime style and light as Image 1, at '
              'believable sizes for where they stand. '),
    # the user (2026-10-02 03:20): “马化腾形象完全无法辨认！问题关键是马化腾其实是比较瘦的……” - 052 has 3 frames: a still with design v3
    '052': (1, 'codex_ma3_still_v1', '夜蛾（倒躺）→马化腾（瘦版 v3，照片参考；Codex 静帧）', [D / 'ma_huateng_v3.png'],
            'Image 1 is a frame from an anime opening: an upside-down close view in pale warm light of a man lying with his eyes closed, his '
            'face upside down in the frame, an X-shaped mark on the surface beside his face. Replace the man with the man of Image 2 (Pony Ma): '
            'his face, thin rimless glasses and short neat black hair from Image 2, a slim face, no sunglasses, no stubble, eyes closed, '
            'upside down exactly like the man in Image 1, in the same pale warm light. The X-shaped mark stays. '),
    # the user (2026-10-02 02:08, review note on 084): “可以换成大肥鱼的背影。直接生图静止帧。” (7 frames)
    '084': (3, 'codex_still_v1', '夜晚小巷：路上的人影→大肥鱼（DeepSeek）的背影（Codex 静帧）', [A / '鲸鱼娘.png'],
            'Image 1 is a frame from an anime opening: a painted night street that forks around an old brick building, lit by a few '
            'street lamps, with a tree, shop signs and a small dark figure walking away down the street on the left. Replace ONLY that '
            'figure with the girl of Image 2 (DeepSeek: very long wavy dark-blue hair, white maid headband, blue whale-fin ears, navy maid '
            'dress with a white apron, white stockings, a whale tail) seen from behind, walking away down the same street at the same '
            'small size and place, her hair and tail catching the lamplight. The buildings, the shop signs exactly as they are, the tree, '
            'the lamps and the painted texture stay exactly as in Image 1. '),
}


def codex(unit):
    local, rev, label, refs, what = STILLS[unit]
    DIR.mkdir(parents=True, exist_ok=True)
    name = f'still_{unit}_{rev}.png'
    if (DIR / name).exists():
        return DIR / name
    args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
            '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt')]
    if local is not None:  # None: the first reference is already the frame to edit (e.g. 053p builds on the 053 still)
        args += ['-i', str(source_frame(unit, local, DIR / f'src_{unit}_f{local:02d}.png'))]
    for r in refs:
        args += ['-i', str(r)]
    args += ['--', f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {what}{KEEP}']
    for attempt in (1, 2):  # Codex hung twice on 2026-10-01; a normal image takes 1-3 minutes
        t = time.time()
        try:
            subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
        except subprocess.TimeoutExpired:
            print('TIMEOUT', name, 'attempt', attempt, flush=True)
            continue
        if (DIR / name).exists():
            print('done', name, f'{time.time() - t:.0f} s', flush=True)
            return DIR / name
    raise SystemExit('Codex failed for ' + name)


def clip(unit, still, key=None):
    """Hold the still for the unit; key picks another STILLS entry for the revision and label (e.g. '053p2' held as unit 053)."""
    local, rev, label, refs, what = STILLS[key or unit]
    out = PROD / 'shots' / unit / rev
    out.mkdir(parents=True, exist_ok=True)
    inv = json.loads((PROD / 'source_inventory/inventory.json').read_text(encoding='utf-8'))
    start, end = b1.interval(unit)
    fps = 24000 / 1001
    full = out / 'source_exact_with_audio.mp4'
    if not full.exists():
        p.run([p.FFMPEG, '-v', 'error', '-y', '-i', inv['source'], '-map', '0:v:0', '-map', '0:a:0',
               '-vf', f'trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS,scale=1024:576:flags=lanczos,setsar=1,format=yuv420p',
               '-af', f'atrim=start={start / fps:.9f}:end={end / fps:.9f},asetpts=PTS-STARTPTS',
               '-r', '24000/1001', '-c:v', 'libx264', '-crf', '12', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', full])
    frame = np.asarray(Image.open(still).convert('RGB').resize((1024, 576), Image.LANCZOS))
    silent = out / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(end - start), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.repeat(frame[None], end - start, axis=0).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    video = out / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', video])
    runner.configure(out)
    check = runner.batch.validate_output(video, end - start, True)
    record = out / 'title_compositing.json'
    builder = pathlib.Path(__file__).resolve()
    p.write_json(record, dict(kind='cpu_text', builder=str(builder), builder_sha256=p.sha(builder),
                              recipe_text=(f'静止镜头：Codex 直接改原片第 {local} 帧' if local is not None else '静止镜头：Codex 在已有静帧上修改')
                                          + f'（{still.name}），保留构图，定格 {end - start} 帧，原片原音。未经 H3。\n'
                                          f'Codex 提示词：{what}{KEEP}'))
    p.write_json(out / 'validation.json', dict(video=str(video), sha256=p.sha(video), validation=check, still=str(still), visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == unit)
    if not any(v['video_sha256'] == p.sha(video) for v in entry['versions']):
        runner.review.register(unit, str(video), record, label)
    print('READY', video, flush=True)


if __name__ == '__main__':
    for unit in sys.argv[1:]:
        clip(unit, codex(unit))
