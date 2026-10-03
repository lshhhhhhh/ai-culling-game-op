"""JJK designs, round 6: the Zenin twins redrawn, both still Gemini (Codex image generation, with timeout and retry).

User (2026-10-01): “gemini姐妹的人设我也想重画。现在这个身体太壮了不好看” (gemini_maki_v2 / gemini_mai_v1 look too muscular).
As with GPT v5 (“这个好看！”), drawn fresh in a square, symmetric front pose rather than edited from the old sheets; slender build.
The twins keep their small differences (the user: “微小差异（比如发型不同）”): Maki - high ponytail, glasses, Tokyo combat uniform, katana;
Mai - asymmetric shoulder-length bob, no glasses, Kyoto uniform with a long skirt, revolver. Maki is drawn first and passed to Mai.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

CODEX = Path(os.environ['LOCALAPPDATA']) / 'OpenAI/Codex/bin/faa963e871dd422c/codex.exe'
DIR = Path(r'deliverables\jujutsu\人设')
GEMINI = Path(r'assets\人设\GEMINI娘.jpg')
SHEET = ('Draw a 16:9 character turnaround sheet: front view, side view and back view of the same character, full body, standing '
         'naturally, side by side on a plain white background, the same scale in all three views. The front view faces the camera '
         'squarely and is symmetric left to right. No text, no labels, no logos. Do not create or modify any other files.')
STYLE = ('Slender, graceful build with slim arms and a narrow waist - not muscular, not stocky - adult proportions about seven and a half '
         'heads tall. Clean 2D Japanese TV-anime line art and cel shading in the style of the anime Jujutsu Kaisen. ')
FACE = ('Image 1 is the identity reference: the Gemini girl. Keep her pretty face, her amber eyes, her cat ears and her purple-to-pink '
        'gradient hair colours exactly. ')
DESIGNS = [
    ('gemini_maki_v3.png', [GEMINI],
     FACE + 'She is cast as Maki Zenin of Jujutsu Kaisen: her hair tied up in a high ponytail, thin rectangular dark-rimmed glasses, the '
     'dark navy Tokyo Jujutsu High uniform cut for fighting - a fitted high-collared jacket with the school\'s swirl buttons, slim dark '
     'trousers tucked into boots - and a long katana in a dark scabbard held in her right hand at her side. A cool, confident look. '
     + STYLE),
    ('gemini_mai_v2.png', [GEMINI, DIR / 'gemini_maki_v3.png'],
     FACE + 'Image 2 is her twin sister: give her the SAME face, eyes and hair colours as Image 2 so they are clearly twins, and the same '
     'slender build. She is cast as Mai Zenin of Jujutsu Kaisen. The small differences from her twin: a shoulder-length asymmetric bob, '
     'one side longer than the other with the longer side tucked behind her cat ear; no glasses; the dark navy Kyoto Jujutsu High '
     'uniform - a short fitted jacket and a long pleated skirt - and a small revolver held loosely in her right hand at her side. A cool, '
     'slightly haughty look. ' + STYLE),
]
# The user on v3/v2: “换成这样的黑色制服如何？然后领结是GOOGLE的渐变色。可能有点难，如果做不好就还是红色。真依的话，可以是长袖+长裙” with a
# photo of a black sailor uniform (ref_user_black_sailor.png). The v3/v2 sheets are already square front poses, so these are edits
# of them that change only the outfit.
BOW = ('a large soft bow at the centre of the collar whose ribbon shifts smoothly through Google\'s four colours - blue, red, yellow '
       'and green - like Google\'s 2025 gradient G logo')
UNIFORM = ('a black sailor uniform like the one in Image 2: a black top with a wide black sailor collar edged with three thin white '
           'stripes, lying flat and symmetric over both shoulders, and ' + BOW + '; a black pleated skirt')
EDITS = [
    ('gemini_maki_v4.png', [DIR / 'gemini_maki_v3.png', DIR / 'ref_user_black_sailor.png'],
     'Image 1 is a finished character turnaround sheet; Image 2 is a photo showing only the outfit to use. Edit Image 1, changing ONLY her '
     f'clothes in all three views: dress her in {UNIFORM} reaching just above the knee, short sleeves, black socks and black shoes. Keep '
     'EVERYTHING else exactly as in Image 1 - her face, glasses, ponytail, hair colours, cat ears, slender body, pose, the katana in her '
     'hand, the line art, layout and white background. Do not create or modify any other files.'),
    ('gemini_mai_v3.png', [DIR / 'gemini_mai_v2.png', DIR / 'ref_user_black_sailor.png', DIR / 'gemini_maki_v4.png'],
     'Image 1 is a finished character turnaround sheet; Image 2 is a photo showing the outfit; Image 3 is her twin sister in the same '
     f'uniform. Edit Image 1, changing ONLY her clothes in all three views: dress her in {UNIFORM}, matching Image 3, but with LONG '
     'sleeves and a LONG pleated skirt reaching her calves, black stockings and black shoes. Keep EVERYTHING else exactly as in Image 1 - '
     'her face, asymmetric bob, hair colours, cat ears, slender body, pose, the revolver in her hand, the line art, layout and white '
     'background. Do not create or modify any other files.'),
]


def run_edits():
    for name, images, prompt in EDITS:
        if (DIR / name).exists():
            print('skip', name, flush=True)
            continue
        args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
                '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt')]
        for i in images:
            args += ['-i', str(i)]
        args += ['--', f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {prompt}']
        for attempt in (1, 2):
            t = time.time()
            try:
                subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
            except subprocess.TimeoutExpired:
                print('TIMEOUT', name, 'attempt', attempt, flush=True)
                continue
            break
        print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', flush=True)
        if not (DIR / name).exists():
            return  # Mai is matched to Maki


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
        args += ['--', f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {prompt}{SHEET}']
        for attempt in (1, 2):  # Codex hung several times on 2026-10-01; a normal image takes 1-3 minutes
            t = time.time()
            try:
                subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
            except subprocess.TimeoutExpired:
                print('TIMEOUT', name, 'attempt', attempt, flush=True)
                continue
            break
        print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', flush=True)
        if not (DIR / name).exists():
            return  # Mai needs Maki


if __name__ == '__main__':
    run_edits() if '--uniform' in sys.argv else main()
