"""JJK designs, round 3: the Zenin twins, both Gemini (Codex image generation; same driver as codex_designs_0001).

User (2026-10-01 evening): “我觉得姐妹可以都是gemini，但是两者的形象要重新设计。要符合世界观，而且也要微小差异（比如发型不同）”.
Earlier: 058/064 “gemini的形象不好看” (gemini_maki_v1), 072/083 “这是真希和真依，怎么变成了两个Gemini” (Maki redesign + Mai in the
community dress did not read as a twin pair). Both keep the Gemini girl's face, purple-to-pink hair, cat ears and amber eyes,
dressed as Jujutsu Kaisen sorcerers; they differ in small, readable ways: Maki has a high ponytail, glasses, the Tokyo school
combat uniform and a katana; Mai has a shoulder-length asymmetric bob, no glasses, the Kyoto school uniform and a revolver.
Maki is drawn first and passed to Mai's call so the twins share one face. Outputs in deliverables/jujutsu/人设; existing files
are skipped. (copilot_maki_v1 from round 2 is no longer cast.)
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
         'naturally, side by side on a plain white background, the same scale in all three views. No text, no labels, no logos. '
         'Do not create or modify any other files.')
ANIME = ('Clean 2D Japanese TV-anime line art and flat cel shading in the style of the anime Jujutsu Kaisen, adult proportions, '
         'a believable jujutsu sorcerer who fits that world - practical clothes, no fantasy frills. ')
FACE = ('Image 1 is the identity reference: the Gemini girl. Keep her face, her amber eyes, her cat ears and her long purple-to-pink '
        'gradient hair colours exactly. ')
DESIGNS = [
    ('gemini_maki_v2.png', [GEMINI, DIR / 'ref_maki_1105.png', DIR / 'ref_twins_072.png'],
     FACE + 'She is cast as Maki Zenin from Jujutsu Kaisen (Image 2 is a frame of Maki and Image 3 shows the twins, used only for the '
     'role and the mood). Her hair is tied up in a high ponytail, and she wears Maki\'s rectangular dark-rimmed glasses and the dark '
     'navy Tokyo Jujutsu High uniform adapted for combat: a high-collared fitted jacket with the school\'s swirl buttons, dark '
     'trousers tucked into boots, fingerless gloves, a long katana in a dark scabbard slung across her back. A sharp, confident, '
     'slightly fierce look. ' + ANIME),
    ('gemini_mai_v1.png', [GEMINI, DIR / 'gemini_maki_v2.png', DIR / 'ref_mai_041.png'],
     FACE + 'Image 2 is her twin sister (our new Maki design): give her the SAME face and the same hair colours, so they are clearly '
     'twins. She is cast as Mai Zenin from Jujutsu Kaisen (Image 3 is a frame of Mai, used only for the role). The small differences '
     'from her twin: a shoulder-length asymmetric bob, one side longer than the other, with the longer side tucked behind her cat '
     'ear; no glasses; the dark navy Kyoto Jujutsu High uniform with a long pleated skirt and a short fitted jacket; a revolver in a '
     'holster at her hip. A cool, slightly haughty look. ' + ANIME),
]


def main():
    only = set(sys.argv[1:])
    for name, images, prompt in DESIGNS:
        if only and name not in only:
            continue
        if (DIR / name).exists():
            print('skip', name, flush=True)
            continue
        missing = [i for i in images if not i.exists()]
        if missing:
            print('FAILED', name, 'missing input', missing, flush=True)
            continue
        args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
                '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt')]
        for i in images:
            args += ['-i', str(i)]
        args.append('--')  # -i takes several files; without this the prompt is read as one more image
        args.append(f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {prompt} {SHEET}')
        t = time.time()
        proc = subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace')
        print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', proc.stdout[-200:].replace('\n', ' '),
              proc.stderr[-300:].replace('\n', ' ') if not (DIR / name).exists() else '', flush=True)


if __name__ == '__main__':
    main()
