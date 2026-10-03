"""JJK imagery redesign keyframes by Codex image editing.

002-004 (the user: “这里原版好像是一个转动煤气灶旋钮” -> chose option 1, “试试1.让我看看关键帧效果”): the gas-stove knob becomes an LLM
“temperature” dial turned all the way up (the next shots are the title and the city exploding). The hand stays a plain hand.
No readable text on the dial (H3 garbles text): tick marks only, red at the high end, a ring of indicator lights.
Outputs in deliverables/jujutsu/关键帧; existing files are skipped.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

from codex_keyframes_0001 import DIR, source_frame

CODEX = Path(os.environ['LOCALAPPDATA']) / 'OpenAI/Codex/bin/faa963e871dd422c/codex.exe'
DIAL = ('Replace the round gas-stove knob and the stove panel with its small printed labels by a sleek modern control dial: a smooth '
        'round knob with a thin glowing indicator line, set in a dark brushed-metal panel with a circular scale of evenly spaced tick '
        'marks that turn from white to red toward the high end, and a thin ring of small indicator lights around the knob. No letters, '
        'no numbers, no words, no logos anywhere. ')
KEEP = ('Keep EXACTLY the hand - its pose, fingers, size and position - and the camera angle, framing, lighting, the cold black-and-white '
        'colour grading with its purple tint, and the 2D anime rendering of Image 1. The output is a 16:9 image with the framing of '
        'Image 1. Do not create or modify any other files.')
# (unit, local frame, version, state of the dial in this frame)
EDITS = [
    ('002-004', 0, 'v1', 'Image 1 shows a hand gripping the knob. The dial is near the low end: its indicator line points at the white ticks and only the first few indicator lights are lit. '),
    ('002-004', 10, 'v1', 'Image 1 shows the hand after it has let go, opening palm up, with the knob on the right. The dial is now turned all the way to the maximum: its indicator line points into the red zone and the whole ring of indicator lights glows. '),
]
# The user rejected the dial keyframes (unreadable, and the second changed a knob the source never moves), chose “thinking level”
# (“把刻度改成thinking level如何？比如low medium high, extra。右边刻度可以加字”), found the CPU text overlay ugly and asked:
# “可以用codex生图吗？现在这个好难看”. One still of the static panel; thinking_002_004_codex.py composites it under the moving hand.
PRINT = ('Image 1 is a frame from an anime opening: a close-up of a hand on a stove panel; on the right there is a dark round knob. Edit '
         'ONLY the small printed markings on the panel around that right knob: replace them with a printed dial scale, as if it was '
         'silk-screened on the metal panel - the word THINKING printed above the knob, and around the left side of the knob a scale '
         'with short tick marks labelled LOW, MEDIUM, HIGH, EXTRA going clockwise from the lower left up to the top, EXTRA printed in '
         'red, everything else in the same pale grey print as the original markings, following the tilted perspective of the panel, '
         'slightly worn. Keep EXACTLY everything else - the hand, both knobs, the panel, the camera angle, framing, light, the cold '
         'black-and-white colour grading with its purple tint and the 2D anime rendering of Image 1. The output is a 16:9 image with '
         'the framing of Image 1. Do not create or modify any other files.')


def main():
    DIR.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    if not only or 'kf_002-004_f00_thinking_v1.png' in only:
        name = 'kf_002-004_f00_thinking_v1.png'
        if not (DIR / name).exists():
            src = source_frame('002-004', 0, DIR / 'src_002-004_f00.png')
            args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
                    '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt'), '-i', str(src), '--',
                    f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {PRINT}']
            t = time.time()
            try:
                subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
            except subprocess.TimeoutExpired:
                print('TIMEOUT', name, flush=True)
            print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', flush=True)
        if only:
            return
    for unit, local, version, state in EDITS:
        name = f'kf_{unit}_f{local:02d}_dial_{version}.png'
        if only and name not in only:
            continue
        if (DIR / name).exists():
            print('skip', name, flush=True)
            continue
        src = source_frame(unit, local, DIR / f'src_{unit}_f{local:02d}.png')
        prompt = (f'Image 1 is a frame from an anime opening: a close-up of a hand turning a round gas-stove knob. Edit it. {DIAL}{state}{KEEP}')
        args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
                '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt'), '-i', str(src), '--',
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
