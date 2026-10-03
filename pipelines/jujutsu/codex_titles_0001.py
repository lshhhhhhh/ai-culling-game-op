"""JJK title redesign by Codex image generation (same driver as codex_designs_0001).

User (2026-10-01): “标题也需要重新设计”; chose main title 「模型回战」 and keeping the subtitle 「死滅回游 前編」.
- title_057_logo_v1.png: the 057 logo alone (gold outline brush glyphs, small kana もけいかいせん above), on pure black, for
  frame-by-frame compositing over the source (the original subtitle stays in the frame).
- title_005_frame_v1.png: the whole 005 frame (giant red melting glitch calligraphy over the psychedelic swirl) reading 模型回战;
  animated on the CPU afterwards.
Outputs in deliverables/jujutsu/标题; existing files are skipped.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

CODEX = Path(os.environ['LOCALAPPDATA']) / 'OpenAI/Codex/bin/faa963e871dd422c/codex.exe'
DIR = Path(r'deliverables\jujutsu\标题')
TAIL = 'No other text, no watermark, no signature. Do not create or modify any other files.'
DESIGNS = [
    ('title_057_logo_v1.png', [DIR / 'ref_057_f40.png'],
     'Image 1 is a frame from an anime opening: its title logo 呪術廻戦 is drawn as thin, hollow, double-outlined brush calligraphy '
     'in gold, with a small line of gold kana above its right end. Create a new title logo in exactly this style - the same gold '
     'colour, the same thin hollow outline strokes, the same rough brush character and letter spacing - that reads 模型回战 '
     '(four simplified Chinese characters, left to right), with the small kana line もけいかいせん above the right end like the '
     'original. Draw ONLY the logo, centred, on a pure black background, 16:9 image, the logo about two thirds of the image width. '
     'Do not draw the subtitle or the city.'),
    ('title_005_frame_v1.png', [DIR / 'ref_005_f8.png'],
     'Image 1 is a frame from an anime opening: the title 呪術廻戦 as giant, bright red, melting, dripping, glitchy brush calligraphy '
     'filling the whole frame, over a swirling psychedelic background of dark blue, white, cyan and orange light. Recreate this '
     'image at 16:9 with the title replaced by 模型回战 (four simplified Chinese characters, left to right) in the identical red '
     'melting, dripping, glitchy style, the same size and layout filling the frame, over the same kind of swirling background.'),
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
        args.append(f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {prompt} {TAIL}')
        t = time.time()
        proc = subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace')
        print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', proc.stdout[-300:].replace('\n', ' '),
              proc.stderr[-300:].replace('\n', ' ') if not (DIR / name).exists() else '', flush=True)


if __name__ == '__main__':
    main()
