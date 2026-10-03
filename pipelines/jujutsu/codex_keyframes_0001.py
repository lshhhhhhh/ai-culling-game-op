"""JJK keyframes by Codex image editing (h3 keyframe anchor method, as on Fate 013-014).

User (2026-10-01): units whose output stayed a standing design sheet - 094 “claude那一幕动作完全不对啊，保持着立绘姿势没变过”,
098 “前两幕完全做坏了”, 101 “全是站着不动的人设图，不好看” / “人物对应是次要的，关键是好看”, 109-111a “完全就是人设图没有变化”,
111b-114 “依旧人设图没有变化”, 121-122 “这个就是人设图，需要更多设计”; then “生图任务直接去做”.
Each keyframe is the source frame (full 1280x720) with only the character replaced; pose, framing, lighting and background stay.
Outputs in deliverables/jujutsu/关键帧; existing files are skipped.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from common import PROD, ROOT, p
import render_batch_0001 as b1

CODEX = Path(os.environ['LOCALAPPDATA']) / 'OpenAI/Codex/bin/faa963e871dd422c/codex.exe'
DIR = ROOT / 'deliverables/jujutsu/关键帧'
A, D = ROOT / 'assets/人设', ROOT / 'deliverables/jujutsu/人设'
LOOK = {
    'CL': (A / 'claude娘.png', 'Claude: a young woman with very long flowing orange hair, amber eyes and an orange flower ornament with a black ribbon, in a white blouse with a black bow and a layered white, black and orange dress'),
    'GROK': (A / 'grok.jpg', 'Grok: a young woman with long blonde twin tails, blue eyes and small black horns, in a black-and-red gothic dress'),
    'KIMI': (A / 'KIMI娘.png', 'Kimi: a composed young woman with long wavy silver-white hair and blue eyes, in a white blouse and a dark blue coat'),
    'SPK': (A / 'spark娘.png', 'Spark: a girl with fluffy white curly hair, white animal ears and an oversized white hoodie with a blue infinity logo over a long white skirt'),
    'MIS': (A / 'mistral娘.jpg', 'Mistral: a young woman with long wavy golden-orange hair, cat ears, a wide red hat with a white feather and a red-and-white dress'),
    'DB_OGI': (D / 'doubao_zenin_ogi_v1.png', 'Doubao as Ogi Zenin: a young woman with a smooth chocolate-brown bob and big glossy brown eyes, in a black crested kimono and grey hakama with a flaming katana - keep her soft 3D-rendered CG look'),
    'DS': (A / '鲸鱼娘.png', 'DeepSeek: a slender young woman with very long wavy dark-blue hair, an ahoge, a white frilled maid headband, blue whale-fin ears, an off-shoulder navy maid dress with a white apron, white stockings and a large blue whale tail'),
    'GPT6': (D / 'gpt_yuta_v6.png', 'GPT as Yuta: a young woman with very long wavy white hair, a small white knot-shaped hair ornament, an off-white blazer-style school uniform with a black sailor collar with white stripes, a small dark green necktie, black cuffs and a black pleated skirt, with a katana'),
    'QWEN': (A / 'qwen娘.jpg', 'Qwen: a young woman with long wavy blue-violet hair, purple eyes and a navy beret, in a long blue-and-white robe'),
}
# (unit, local frame, cast key, who is replaced, light/rendering note)
KEYFRAMES = [
    ('094', 10, 'CL', 'the man in a suit raising a glowing sword', 'lit entirely in teal light on black, like the rest of Image 1'),
    ('098', 2, 'GROK', 'the figure wrapped in a skirt of fluttering paper receipts', 'lit entirely in violet light on black'),
    ('098', 8, 'CL', 'the young man making a hand sign', 'lit entirely in teal light on black'),
    ('101', 1, 'KIMI', 'the broad figure spreading his arms', 'lit entirely in blue light on black'),
    ('101', 5, 'SPK', 'the slim figure', 'lit entirely in pink light on black'),
    ('101', 9, 'MIS', 'the woman standing beneath the long spiked golden shikigami (keep the shikigami)', 'lit entirely in gold light on black'),
    ('101', 17, 'DB_OGI', 'the man in a kimono close to the camera on the right', 'lit in dim gold light on black'),
    ('109-111a', 1, 'SPK', 'the girl with purple-and-blue hair turning her head in close-up', 'in the same blue starlight'),
    ('109-111a', 10, 'SPK', 'the girl standing in the middle of the starry space', 'in the same blue starlight, the orbital rings kept'),
    ('111b-114', 2, 'KIMI', 'the man with spiky hair breathing blue flame', 'in the same dim green light with the blue flame and gold rays kept'),
    ('121-122', 6, 'QWEN', 'the grinning man with a tall pompadour in a fur coat', 'in the same colours, the collage stickers kept'),
    # 020-026a, the user: “这一帧明显虎杖。我觉得还是要用模型” - H3 had only turned Itadori blue (short hair, his face, his hoodie)
    ('020-026a', 11, 'DS', 'the young man falling face-down with his arms spread wide', 'lit by the same orange light against the dark city, seen from above'),
    ('020-026a', 23, 'DS', 'the small falling young man with the grey curse swooping at him (keep the curse)', 'lit by the same orange light, seen from above'),
    ('020-026a', 33, 'DS', 'the young man in close-up gritting his teeth', 'lit by the same warm orange light, her long blue hair whipping in the wind'),
    # 016b-019, the user on gpt6_h3_v1: “第一帧的脸部朝向不对，没有那种冲击感。要不还是用关键帧”
    ('016b-019', 0, 'GPT6', 'the young man seen from behind raising his sword in a flood of backlight; keep his head turned away to the right so the face stays hidden in shadow', 'a dark backlit silhouette against the blinding light, exactly like Image 1, her face turned away and not visible'),
    # v1 of frame 0 was wrong: I wrote “face hidden”, but the source shows a three-quarter face turned to the right, half in shadow,
    # with one fierce eye visible (the user: “你的参考帧是不是不对啊”)
    ('016b-019', 0, 'GPT6', 'the young man raising his sword in a flood of backlight', 'backlit like Image 1: her head turned to the right exactly like the young man in Image 1, her face in a three-quarter view half in shadow, one fierce narrowed eye visible glancing to the right, a tense, determined expression', 'v2', 'Copy the exact angle of the head and the direction of the gaze from Image 1.'),
    ('016b-019', 8, 'GPT6', 'the young man seen from behind dashing down the red street with his sword', 'seen from behind among the same red streaks and white light trails'),
    # user: “MISTRAL那个背景换成法棍正好” - the long spiked golden shikigami behind her becomes a giant baguette (Mistral is French)
    ('101', 9, 'MIS', 'the woman standing beneath the long spiked golden shikigami', 'lit entirely in gold light on black', 'v2',
     'Also replace the long spiked golden serpent-like shikigami that stretches across the frame with one giant golden French baguette '
     'lying across the frame in the same place and at the same size, its crust scored and glowing gold like the shikigami.'),
]


def source_frame(unit, local, out):
    inv = json.loads((PROD / 'source_inventory/inventory.json').read_text(encoding='utf-8'))
    n = b1.interval(unit)[0] + local
    if not out.exists():
        subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-i', inv['source'], '-vf', f'select=eq(n\\,{n})', '-frames:v', '1', str(out)], check=True)
    return out


def main():
    DIR.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for unit, local, key, who, light, *more in KEYFRAMES:
        version, extra = (more + ['v1', ''])[:2] if more else ('v1', '')
        name = f'kf_{unit}_f{local:02d}_{key.lower()}_{version}.png'
        if only and name not in only:
            continue
        if (DIR / name).exists():
            print('skip', name, flush=True)
            continue
        src = source_frame(unit, local, DIR / f'src_{unit}_f{local:02d}.png')
        ref, identity = LOOK[key]
        prompt = (f'Image 1 is a frame from an anime opening. Edit it: replace {who} with the character from Image 2 - {identity}. '
                  'Keep EXACTLY the same composition, camera angle and framing, the same size and position of the figure, the same pose '
                  f'and gesture, the same background and the same 2D anime rendering as Image 1; she is {light}. {extra} Only the identity changes: '
                  'face, hair and outfit come from Image 2. No text, no watermark. The output is a 16:9 image with the framing of Image 1. '
                  'Do not create or modify any other files.')
        args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
                '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt'), '-i', str(src), '-i', str(ref), '--',
                f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {prompt}']
        t = time.time()
        try:  # one 101 run hung for over an hour (2026-10-01); a normal image takes 1-3 minutes
            proc = subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
        except subprocess.TimeoutExpired:
            print('TIMEOUT', name, flush=True)
            continue
        print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s',
              proc.stderr[-300:].replace('\n', ' ') if not (DIR / name).exists() else '', flush=True)


if __name__ == '__main__':
    main()
