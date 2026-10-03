"""JJK designs, round 4: the minor roles identified on 2026-10-01 evening (Codex image generation; same driver as before).

Identification: the AIZO character list on the JJK Fandom wiki (read through search snippets) plus the user's own answers
(“124-125就是乐岩寺嘉伸 129随便安排一点角色吧不深究了 133应该是日下部和他的妹妹 141就是高羽史彦 102是禅院直哉”).
Casting followed the user's rules and, for the rest, the proposals the user did not object to:
- every Zenin clan villain is Doubao in her official avatar's 3D look, each with a different costume: Naoya (102, 115, 127),
  Chojuro, Nobuaki, Naobito (115 front row, 127);
- Eso and Kechizu, Choso's younger brothers (050, 132): two GLM variants, as Choso is GLM;
- the twins' mother (077-080): Bard, Gemini's predecessor.
Outputs in deliverables/jujutsu/人设; existing files are skipped.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

CODEX = Path(os.environ['LOCALAPPDATA']) / 'OpenAI/Codex/bin/faa963e871dd422c/codex.exe'
DIR = Path(r'deliverables\jujutsu\人设')
AVATAR = Path(r'assets\fate_zero\op1_v1\character_designs\references\doubao_official_avatar.jpg')
GLM = Path(r'assets\人设\GLM娘.png')
SHEET = ('Draw a 16:9 character turnaround sheet: front view, side view and back view of the same character, full body, standing '
         'naturally, side by side on a plain white background, the same scale in all three views. No text, no labels, no logos. '
         'Do not create or modify any other files.')
ANIME = 'Clean 2D Japanese TV-anime line art and flat cel shading in the style of the anime Jujutsu Kaisen, adult proportions. '
DOUBAO_3D = ('Image 1 is Doubao\'s official app avatar, the identity reference: a young woman with a smooth chocolate-brown chin-length '
             'bob with an off-centre side part, large glossy dark-brown eyes, soft rounded features and pale skin. Keep her face, hair '
             'and especially her soft 3D-rendered look - smooth CG shading like an animated 3D film character, NOT 2D anime line art. '
             'Adult proportions, about seven heads tall. ')
DESIGNS = [
    ('doubao_zenin_naoya_v1.png', [AVATAR],
     DOUBAO_3D + 'She is cast as Naoya Zenin, the arrogant young heir of the Zenin clan from Jujutsu Kaisen: the ends of her bob dyed '
     'blond, several small earrings along one ear, a smug, sneering half-smile, a dark grey kimono worn loosely with a black haori '
     'over it, hands in her sleeves, a fast, light-footed stance.'),
    ('doubao_zenin_chojuro_v1.png', [AVATAR],
     DOUBAO_3D + 'She is cast as Chojuro Zenin, a big brawling elder of the Zenin clan from Jujutsu Kaisen: a broad, heavy build, a '
     'sleeveless dark olive kimono top with a thick rope belt over dark hakama, bandaged forearms, a fierce grin and a scar across '
     'her cheek.'),
    ('doubao_zenin_nobuaki_v1.png', [AVATAR],
     DOUBAO_3D + 'She is cast as Nobuaki Zenin, captain of the Zenin clan\'s foot soldiers (the Kukuru unit) in Jujutsu Kaisen: the '
     'unit\'s white gi with black hakama, a black cloth mask pulled down around her neck, white arm wraps, a long katana held at '
     'her side, a stern, disciplined look.'),
    ('doubao_zenin_naobito_v1.png', [AVATAR],
     DOUBAO_3D + 'She is cast as Naobito Zenin, the old head of the Zenin clan in Jujutsu Kaisen: grey streaks through her bob, a '
     'plain dark brown kimono with a grey haori bearing the clan crest, a gourd of sake hanging from her sash, holding a small sake '
     'cup, a relaxed, slightly tipsy, knowing smile.'),
    ('glm_eso_v1.png', [GLM],
     'Image 1 is the identity reference: the GLM girl with very long black hair with dark-blue streaks, black fox ears with white '
     'inner fur and a large black fox tail with a white tip. Draw her as a younger sister playing Eso, one of the Death Painting '
     'brothers from Jujutsu Kaisen: keep her face, fox ears and tail; her hair tied in two buns with long strands falling, a dark '
     'green cropped sleeveless top that leaves her back bare with a stylised red blood-splash pattern painted across it, loose dark '
     'green trousers, a confident, theatrical pose. ' + ANIME),
    ('glm_kechizu_v1.png', [GLM],
     'Image 1 is the identity reference: the GLM girl with very long black hair with dark-blue streaks, black fox ears with white '
     'inner fur and a large black fox tail with a white tip. Draw her as the youngest sister playing Kechizu, one of the Death '
     'Painting brothers from Jujutsu Kaisen: keep her face, fox ears and tail; shorter and rounder, her hair in a short messy bob, '
     'a pale green hooded jumpsuit, a huge mischievous grin showing teeth, slightly hunched and bouncy. ' + ANIME),
    ('bard_twins_mother_v1.png', [],
     'An original personification of Google Bard, the AI assistant that came before Gemini, as a gentle, tired adult mother in the '
     'world of Jujutsu Kaisen: she is the mother of twin girls in the old, strict Zenin clan. Long straight hair in a soft gradient '
     'from deep blue to violet, worn in a low loose bun, calm violet eyes with a sad, patient expression, a small four-pointed '
     'sparkle hair ornament, a plain muted lavender kimono with a dark obi, hands folded in front of her. ' + ANIME),
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
        print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', proc.stdout[-160:].replace('\n', ' '),
              proc.stderr[-300:].replace('\n', ' ') if not (DIR / name).exists() else '', flush=True)


if __name__ == '__main__':
    main()
