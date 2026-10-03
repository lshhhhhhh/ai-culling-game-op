"""JJK designs, round 2 (Codex image generation; same driver as codex_designs_0001).

User (2026-10-01 afternoon):
- “学校的管理层用企业家可以吗？梁文峰，达里奥，杨植麟，马斯克，奥特曼。” Agreed pairing: Gakuganji (Kyoto principal,
  electric guitar in 093) = Elon Musk; Kusakabe (Tokyo teacher, 095-097) = Liang Wenfeng.
- “反派用豆包吧。这个形象也是有梗的，画风明显不一样。可以让她饰演全部禅院家反派，然后做出差异化设计。可以生图”:
  Doubao plays Ogi, Jinichi and Ranta Zenin. She keeps the soft 3D look of her official app avatar (the joke is that she does
  not look like the 2D anime cast); the three differ by costume and props.
Added later: copilot_maki_v1 - user on 072/083 “这是真希和真依，怎么变成了两个Gemini” and on 058/064 “gemini的形象不好看”;
with no preference given, Mai keeps Gemini (community design) and Maki goes to the Copilot girl in a combat redesign.
Outputs in deliverables/jujutsu/人设; existing files are skipped.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

CODEX = Path(os.environ['LOCALAPPDATA']) / 'OpenAI/Codex/bin/faa963e871dd422c/codex.exe'
DIR = Path(r'deliverables\jujutsu\人设')
FATE = Path(r'assets\fate_zero\op1_v1\character_designs')
SHEET = ('Draw a 16:9 character turnaround sheet: front view, side view and back view of the same character, full body, standing '
         'naturally, side by side on a plain white background, the same scale in all three views. No text, no labels, no logos. '
         'Do not create or modify any other files.')
ANIME = 'Clean 2D Japanese TV-anime line art and flat cel shading in the style of the anime Jujutsu Kaisen, adult proportions. '
DOUBAO_3D = ('Image 1 is Doubao\'s official app avatar, the identity reference: a young woman with a smooth chocolate-brown chin-length '
             'bob with an off-centre side part, large glossy dark-brown eyes, soft rounded features and pale skin. Keep her face, hair '
             'and especially her soft 3D-rendered look - smooth CG shading like an animated 3D film character, NOT 2D anime line art. '
             'Adult proportions, about seven heads tall. ')
DESIGNS = [
    ('doubao_zenin_ogi_v1.png', [FATE / 'references/doubao_official_avatar.jpg'],
     DOUBAO_3D + 'She is cast as Ogi Zenin, the proud sword-wielding clan elder from Jujutsu Kaisen: a black formal montsuki kimono '
     'with white family crests over grey striped hakama, a long katana whose blade is wreathed in orange flame, a stern, haughty '
     'frown and a straight, arrogant posture.'),
    ('doubao_zenin_jinichi_v1.png', [FATE / 'references/doubao_official_avatar.jpg'],
     DOUBAO_3D + 'She is cast as Jinichi Zenin, the hulking brute of the Zenin clan from Jujutsu Kaisen: a heavy dark-brown kimono '
     'with the sleeves tied back, a broad, sturdy build, huge grey stone fists like gauntlets over her hands, arms crossed and a '
     'scowl.'),
    ('doubao_zenin_ranta_v1.png', [FATE / 'references/doubao_official_avatar.jpg'],
     DOUBAO_3D + 'She is cast as Ranta Zenin, the young retainer of the Zenin clan from Jujutsu Kaisen: a white martial-arts gi '
     'jacket with a red sash belt and dark red hakama trousers, a white headband with a single stylised eye emblem on the '
     'forehead, her bob slightly tousled, and an intense, unblinking stare.'),
    ('musk_gakuganji_v1.png', [FATE / 'outputs/elon_kariya_v1.png', FATE / 'references/elon_musk_photo.jpg'],
     'A friendly cartoon parody of Elon Musk cast as Principal Yoshinobu Gakuganji of Kyoto Jujutsu High. Image 1 is our earlier '
     'cartoon design of him (keep this face and hair style); Image 2 is a photo for likeness only. His recognisable face, short '
     'swept-back hair and broad grin, wearing a dark formal kimono with a grey haori and hakama like Gakuganji, an electric guitar '
     'slung over his shoulder. Not a caricature with exaggerated features. ' + ANIME),
    ('liang_kusakabe_v1.png', [FATE / 'outputs/liang_kiritsugu_blue_v2.png', FATE / 'references/liang_wenfeng_photo.jpg'],
     'A friendly cartoon parody of Liang Wenfeng (the founder of DeepSeek) cast as Atsuya Kusakabe, the laid-back teacher of Tokyo '
     'Jujutsu High. Image 1 is our earlier cartoon design of him (keep this face, glasses and hair style); Image 2 is a photo for '
     'likeness only. His short black hair, glasses and calm face, wearing a long dark coat over a dark suit like Kusakabe, with a '
     'katana in a black scabbard at his hip and a lollipop stick in his mouth. Not a caricature with exaggerated features. ' + ANIME),
    ('copilot_maki_v1.png', [FATE / 'outputs/copilot_aoi_v1.png', DIR / 'ref_maki_1105.png'],
     'Image 1 is the identity reference: our original Copilot girl with long softly waved deep indigo hair with teal inner strands, '
     'teal eyes, a kind composed face and a small folded loop-ribbon hair ornament. Keep her face, hair colours and the ribbon motif. '
     'She is now cast as Maki Zenin from Jujutsu Kaisen (Image 2 is a frame of Maki, used only for the role): give her Maki\'s '
     'rectangular glasses, tie her hair up in a high ponytail, and dress her for fighting in a dark navy high-collared sleeveless '
     'combat top, fingerless gloves, a belt, dark cargo trousers and boots, with a long katana in a dark scabbard on her back and the '
     'small loop-ribbon brooch at her collar. Strong, athletic adult build, a fierce confident look. ' + ANIME),
]


def main():
    only = set(sys.argv[1:])
    for name, images, prompt in DESIGNS:
        if only and name not in only:
            continue
        if (DIR / name).exists():
            print('skip', name, flush=True)
            continue
        args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
                '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt')]
        for i in images:
            args += ['-i', str(i)]
        args.append('--')  # -i takes several files; without this the prompt is read as one more image
        args.append(f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {prompt} {SHEET}')
        t = time.time()
        proc = subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace')
        print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', proc.stdout[-300:].replace('\n', ' '),
              proc.stderr[-300:].replace('\n', ' ') if not (DIR / name).exists() else '', flush=True)


if __name__ == '__main__':
    main()
