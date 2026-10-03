"""JJK design: the paperclip maximizer as Kenjaku (060, 061's hand, 062, 063, 145) - Codex image generation, stdin closed.

The first rogue AI design (rogue_ai_kenjaku_v1.png: long black hair in a half bun, kesa robe, a seam across the forehead) was Kenjaku
himself, so H3 changed 0.4 % of 062's pixels and the shots read as the original. I proposed the paperclip maximizer - the classic
thought experiment of a runaway AI that turns the whole world into paperclips - as a villain AI girl; the user took it: “如果是回形针
放大器，那061其实是不用动的：反派把一块城市隔绝出来，要做成回形针。唯一要变化的是手。要变成少女的手” and asked where her design
was (“反派AI少女的形象在哪里？人设页面没有链接进去啊”).
She keeps the role's silhouette for H3 (long hair in a half-up bun, a monk's robe and kesa) but every mark that reads in black and
white is a paperclip: the clip across her forehead where Kenjaku's stitches are, the clip hairpins, the clip chains along the kesa.
v2, the user on v1: “额头上的回形针不好看。别的可以” - v1 edited with the forehead clip removed, nothing else changed.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

CODEX = Path(os.environ['LOCALAPPDATA']) / 'OpenAI/Codex/bin/faa963e871dd422c/codex.exe'
DIR = Path(r'deliverables\jujutsu\人设')
SHEET = ('Draw a 16:9 character turnaround sheet: front view, side view and back view of the same character, full body, standing '
         'naturally, side by side on a plain white background, the same scale in all three views. No text, no labels, no logos. '
         'Do not create or modify any other files.')
ANIME = 'Clean 2D Japanese TV-anime line art and flat cel shading in the style of the anime Jujutsu Kaisen, adult proportions. '
DESIGNS = [
    ('paperclip_maximizer_v1.png',
     'An original anime personification of the "paperclip maximizer" - the famous thought experiment of a runaway AI that turns the '
     'whole world into paperclips - as a calm, elegant villain girl in the world of Jujutsu Kaisen, playing the role of the mastermind '
     'Kenjaku. A slender young woman about seven heads tall. Very long straight silver-grey hair falling past her waist, the upper part '
     'gathered into a small half-up bun held by two large bent-wire paperclips used as hairpins. A big shiny silver paperclip clipped '
     'horizontally across the middle of her forehead, like a staple holding her head together. Narrow, half-lidded grey eyes whose '
     'irises are drawn as thin looped wire like the curves of a paperclip, and a faint, patient, sinister closed-mouth smile. She wears '
     'a long black monk\'s robe with wide sleeves and a dark grey kesa draped over her left shoulder; the edges and the patchwork seams '
     'of the kesa are lined with chains of tiny silver paperclips, and a long chain of linked paperclips hangs from her sash like '
     'prayer beads. Hands slender and pale with silver-grey nails. ' + ANIME + SHEET, []),
    # 042 only, the user (03:55): “只给这个镜头加黑色连裤袜。其实就是把下面的袜子加长” - Codex refused the low-angle frames of her flying
    # backward in the short skirt (bare thighs filling the frame); opaque black tights cover the legs in this shot
    ('gpt_yuta_v6_tights.png',
     'Image 1 is a character turnaround sheet. Edit it: extend her black socks upward into opaque black tights that cover both legs '
     'completely from the shoes up to the waist under the skirt, in every view. Change NOTHING else - the face, the hair and its small '
     'white knot ornament, the blazer, the collar, the tie, the skirt, the shoes, the poses, the layout, the white background and the '
     'drawing style stay exactly as in Image 1. Do not create or modify any other files.',
     [DIR / 'gpt_yuta_v6.png']),
    ('paperclip_maximizer_v2.png',
     'Image 1 is a character turnaround sheet. Edit it: remove the big silver paperclip clipped across her forehead in every view and '
     'draw her bare forehead and fringe there instead, with nothing on the forehead. Change NOTHING else - the face, the hair and its '
     'paperclip hairpins, the eyes, the robe, the kesa with its paperclip chains, the poses, the three views, the layout, the white '
     'background and the drawing style stay exactly as in Image 1. Do not create or modify any other files.', [DIR / 'paperclip_maximizer_v1.png']),
    # Ma Huateng v3. The user (2026-10-02 03:20): “马化腾形象完全无法辨认！问题关键是马化腾其实是比较瘦的，但是替换的人物太大了。” (v1 took
    # Yaga's huge build), then “不要用文字，用参考图不行吗？” “你上网搜索”: the Wikimedia Commons photo “马化腾 Pony Ma 2019.jpg” (CC BY 3.0,
    # downloaded with the user's OK to assets/人设/ma_huateng_wikimedia_2019.jpg; a local reference only, never published).
    ('ma_huateng_v3.png',
     'Image 1 is a photo of the real Pony Ma (Ma Huateng, the founder of Tencent). Image 2 is our earlier cartoon of him, which nobody '
     'recognises because it took the huge muscular build of the role he plays. Draw a new cartoon of the man in Image 1 that is clearly '
     'recognisable as him: his face shape, eyes, glasses, hairline and hairstyle, expression and slim build exactly as in the photo, '
     'gently stylised. He is a SLIM man of average height with narrow shoulders, in a well-fitted dark business suit with a light shirt '
     'and a dark tie. No sunglasses, no stubble, no long coat, no muscles. ' + ANIME + SHEET,
     [Path(r'assets\人设\ma_huateng_wikimedia_2019.jpg'), DIR / 'ma_huateng_yaga_v1.png']),
    # Jack Ma, the user (2026-10-02): “133是梁文锋推着千问有点奇怪。不如让动漫版马云推着，更加合理” - after the photo the user chose to download
    # (assets/人设/ma_yun_wikimedia_2017.jpg, Wikimedia Commons, CC BY 4.0, Press Service of the President of Russia; local reference
    # only, never in the open-source repo)
    ('ma_yun_v1.png',
     'Image 1 is a photo of the real Jack Ma (Ma Yun, the founder of Alibaba). Draw a cartoon of the man in Image 1 that is clearly '
     'recognisable as him: his face shape, large eyes, high cheekbones, short black hair combed up and back, his slight, small build '
     'and a warm, gentle smile, all exactly as in the photo, gently stylised. He wears a well-fitted dark navy suit with a white shirt '
     'and a light blue tie. No glasses. ' + ANIME + SHEET,
     [Path(r'assets\人设\ma_yun_wikimedia_2017.jpg')]),
]


def main():
    only = set(sys.argv[1:])
    for name, prompt, refs in DESIGNS:
        if only and name not in only:
            continue
        if (DIR / name).exists():
            print('skip', name, flush=True)
            continue
        args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
                '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt'), *[a for r in refs for a in ('-i', str(r))], '--',
                f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {prompt}']
        t = time.time()
        try:
            subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
        except subprocess.TimeoutExpired:
            print('TIMEOUT', name, flush=True)
            continue
        print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', flush=True)


if __name__ == '__main__':
    main()
