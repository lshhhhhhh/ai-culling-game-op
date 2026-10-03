"""JJK design, round 5: GPT as Yuta, v2 (Codex image generation; same driver as before, with a timeout).

User (2026-10-01): “GPT/乙骨的形象有点不好看。我想重新设计一下。参考这个如何？当然还要保留GPT原版的特征（比如发型，GPT的LOGO），可以上网找一下GPT
最新的LOGO作为参考。” The reference (deliverables/jujutsu/人设/ref_user_toji_uniform.png, a card the user supplied) is used for the
uniform, the katana and the clean look. GPT girl identity: the dragon-free design from Lycoris. Logo: OpenAI's “blossom”, as refreshed
in February 2025 (thicker strokes of one width, a larger open centre) - described in words, no logo file downloaded.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

CODEX = Path(os.environ['LOCALAPPDATA']) / 'OpenAI/Codex/bin/faa963e871dd422c/codex.exe'
DIR = Path(r'deliverables\jujutsu\人设')
GPT = Path(r'deliverables\lycoris\人设需求\生成_GPT娘_去龙_v1.png')
LOGO = ('OpenAI\'s current “blossom” logo: six identical rounded strokes interlocked into a hexagonal knot around a large open hexagon in '
        'the centre, every stroke the same thickness, a single flat colour')
SHEET = ('Draw a 16:9 character turnaround sheet: front view, side view and back view of the same character, full body, standing '
         'naturally, side by side on a plain white background, the same scale in all three views. No text, no labels, no wordmarks. '
         'Do not create or modify any other files.')
DESIGNS = [
    ('gpt_yuta_v2.png', [GPT, DIR / 'ref_user_toji_uniform.png'],
     'Image 1 is the identity reference: the GPT girl - very long wavy white hair, a small ahoge, lavender eyes, a soft face and a small '
     'white knot-shaped hair ornament. Keep her face, her eyes and her very long wavy white hair exactly. Image 2 is the style and outfit '
     'reference: dress her like the girl in Image 2, adapted as Yuta Okkotsu\'s white jujutsu school uniform - a fitted off-white '
     'blazer-style jacket with a deep purple sailor-style collar and purple cuff trim, a small tie, a short dark purple pleated skirt with '
     'white stripes, dark socks and shoes, and a long katana held upright in front of her in both hands like Image 2, a black sword case '
     f'on her back. Work the GPT logo into the design: her hair ornament is {LOGO}, in white; the katana\'s round sword guard (tsuba) is '
     'shaped like the same blossom knot; a small silver pin of the blossom knot on her collar. Calm, composed expression. Clean 2D '
     'Japanese TV-anime line art and cel shading in the style of the anime Jujutsu Kaisen, slender adult proportions. '),
    # the user on v2: “我感觉gpt标志只要头发上有就够了。放到衣领和刀上都有点奇怪” - an edit of v2, so everything else stays the same
    ('gpt_yuta_v3.png', [DIR / 'gpt_yuta_v2.png'],
     # and: “三视图是错的，从身后来看刀鞘都是断的” - the black sword case is broken into pieces in the back view
     'Image 1 is a finished character turnaround sheet. Edit it, changing only these details: (1) remove the small logo pin from her '
     'collar in all views (plain collar there); (2) replace the logo-shaped sword guard of her katana with an ordinary dark round iron '
     'tsuba; (3) fix the black sword case on her back so that it is ONE continuous straight case in every view - in the back view it runs '
     'unbroken diagonally from above her shoulder down past her hip, hanging from a strap across her chest, consistent with the front and '
     'side views, never cut into pieces by her hair. Keep the knot-shaped logo hair ornament and EVERYTHING else exactly as in Image 1 - '
     'her face, hair, uniform, pose, katana, colours, line art, layout and white background. '),
    # the user on v3: “gpt的衣领是歪的！可能是因为参考图的角度误导了。要不用这个” + a front-view picture of the same uniform (not saved to
    # disk, so described in words): a symmetric navy sailor collar with two white stripes, a white shirt collar with an orange tie, a
    # cream blazer with one row of brown buttons, navy cuffs with buttons, a navy pleated skirt with white stripes and tassels at the hips
    ('gpt_yuta_v4.png', [DIR / 'gpt_yuta_v3.png'],
     'Image 1 is a finished character turnaround sheet. Edit only her uniform so that it is drawn correctly and symmetrically in every '
     'view: in the front view a symmetric navy sailor collar with two thin white stripes lies flat over both shoulders and meets in a V at '
     'the chest, over a white shirt collar with an orange necktie; a cream blazer that closes in the middle with one straight row of '
     'brown buttons; navy cuffs with two small buttons; a plain navy pleated skirt with two white stripes near the hem, with nothing '
     'hanging from it - no tassels, cords or charms at the hips (the user: “裙子上两边垂下的东西……不要”). In the side and back views the same sailor collar is a square navy flap with white stripes lying flat on her '
     'upper back, consistent with the front. Keep EVERYTHING else exactly as in Image 1 - her face, very long wavy white hair, the '
     'knot-shaped logo hair ornament, her pose, the katana with its plain round guard, the continuous black sword case, the line art, the '
     'layout and the white background. '),
    # the user on v4: “衣领还是歪的呀，有点奇怪。而且我想把紫色的部分（衣领，裙子）换成黑色，看看效果（符合gpt的黑白配色）”. Every version so
    # far was an edit of v2, whose angled pose came from the first reference, so v5 is drawn fresh in a square, symmetric front pose.
    ('gpt_yuta_v5.png', [GPT],
     'Image 1 is the identity reference: the GPT girl - very long wavy white hair, a small ahoge, lavender eyes, a soft face. Keep her '
     f'face, eyes and very long wavy white hair exactly; her hair ornament is {LOGO}, in white, on one side of her head. She is cast as '
     'Yuta Okkotsu of Jujutsu Kaisen in a black-and-white school uniform: an off-white fitted blazer that closes in the middle with one '
     'straight row of buttons; a BLACK sailor collar with two thin white stripes, perfectly symmetric, lying flat over both shoulders and '
     'meeting in a neat V at the centre of her chest, over a white shirt collar with a small orange necktie; black cuffs with two small '
     'buttons; a plain BLACK pleated skirt with two thin white stripes near the hem, nothing hanging from it; black socks and black '
     'shoes. She holds a katana in a plain black scabbard in her left hand, hanging straight down at her side (plain round guard, no '
     'logo); no straps across her chest. The front view faces the camera squarely and is symmetric left to right - the collar, the '
     'buttons and the hem are level. Calm, composed expression. Clean 2D Japanese TV-anime line art and cel shading in the style of the '
     'anime Jujutsu Kaisen, slender adult proportions. '),
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
        args += ['--', f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {prompt}'
                 + ('Do not create or modify any other files.' if name.endswith(('_v3.png', '_v4.png')) else SHEET)]
        for attempt in (1, 2):  # Codex hung twice on 2026-10-01; a normal image takes 1-3 minutes
            t = time.time()
            try:
                subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
            except subprocess.TimeoutExpired:
                print('TIMEOUT', name, 'attempt', attempt, flush=True)
                continue
            break
        print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', flush=True)


if __name__ == '__main__':
    main()
