"""JJK designs by Codex image generation (Python driver: arguments as a list, no shell quoting).

User (2026-10-01 before sleeping): “codex生图也可以用，只要符合常识，不要用的太离谱就行……如果实在不协调（比如原作在用武器打斗），那就用
codex生图设计二社”. Four 16:9 turnaround sheets on white; outputs in deliverables/jujutsu/人设; existing files are skipped.
The PowerShell version lost the prompt argument (“No prompt provided via stdin”).
"""
import os
import subprocess
import sys
import time
from pathlib import Path

CODEX = Path(os.environ['LOCALAPPDATA']) / 'OpenAI/Codex/bin/faa963e871dd422c/codex.exe'
DIR = Path(r'deliverables\jujutsu\人设')
COMMON = ('Draw a 16:9 character turnaround sheet: front view, side view and back view of the same character, full body, standing '
          'naturally, side by side on a plain white background, the same scale in all three views. Clean 2D Japanese TV-anime line '
          'art and flat cel shading in the style of the anime Jujutsu Kaisen, adult proportions. No text, no labels, no logos. '
          'Do not create or modify any other files.')
DESIGNS = [
    ('gpt_yuta_v1.png', [Path(r'deliverables\lycoris\人设需求\生成_GPT娘_去龙_v1.png'), DIR / 'ref_yuta_315.png'],
     'Image 1 is the identity reference: the GPT girl with very long wavy white hair, a small ahoge, lavender eyes, a soft face and '
     'a small round white knot-shaped hair ornament. Keep her face, hair and hair ornament. Image 2 is a frame of Yuta Okkotsu from '
     'Jujutsu Kaisen, used only for the outfit and the weapon: dress her in a crisp white long-sleeved shirt, slim black trousers '
     'and black shoes, with a katana in a black scabbard - held at her side in the front view and slung across her back in the '
     'back view. No dragon horns, wings, tail or dress.'),
    ('gemini_maki_v1.png', [Path(r'assets\人设\GEMINI娘.jpg'), DIR / 'ref_maki_1105.png'],
     'Image 1 is the identity reference: the Gemini girl with very long wavy purple-to-pink gradient hair, cat ears and amber eyes. '
     'Keep her face, hair colours and cat ears, and tie her hair back in a high ponytail for fighting. Image 2 is a frame of Maki '
     'Zenin from Jujutsu Kaisen, used only for the outfit: a dark green-black sleeveless high-neck combat top, a belt, dark cargo '
     'trousers and boots, with a long sword in a dark scabbard on her back. Strong, athletic build.'),
    ('rogue_ai_kenjaku_v1.png', [DIR / 'ref_kenjaku_robe_2120.png'],
     'Design an original fictional villain, "the first rogue AI", for a parody of Jujutsu Kaisen. Image 1 (a frame of the villain '
     'Kenjaku) is used only for the robe and the mood. The character is an elegant, unsettling man with long black hair tied in a '
     'half-up bun, pale skin and a calm, sinister smile, with a thin seam of glowing red circuitry running across his forehead in '
     'place of stitches. He wears a black and dark-grey Buddhist monk kesa robe over a dark kimono, with subtle red circuit patterns '
     'along the hems. He must not resemble any real person.'),
    ('ma_huateng_yaga_v1.png', [],
     'A friendly cartoon parody of Tencent founder Pony Ma (Ma Huateng) cast as Principal Masamichi Yaga of Jujutsu High: his '
     'recognisable short black hair, rectangular glasses, round friendly face and gentle smile, a sturdy adult build, wearing a '
     'black high-collared long coat over a dark shirt and dark trousers like Yaga, holding a small handmade plush doll in one hand. '
     'Not a caricature with exaggerated features.'),
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
        args.append(f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {prompt} {COMMON}')
        t = time.time()
        proc = subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace')
        print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', proc.stdout[-300:].replace('\n', ' '),
              proc.stderr[-300:].replace('\n', ' ') if not (DIR / name).exists() else '', flush=True)


if __name__ == '__main__':
    main()
