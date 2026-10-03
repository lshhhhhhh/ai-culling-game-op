"""Keyframes for 061 (the paperclip maximizer's hand) and 070 (the toy-block tower built from paperclip wire), Codex image editing.

061 - the user on clip_hand_grey_h3_v1: “061的画面不行。手没有变化。需要关键帧。先记下来之后再推理”. The source hand is a huge white
bare hand; H3 kept it (3 % of the hand pixels changed). Frames 1 and 14: the hand redrawn as hers - slender, long silver-grey nails,
the hem of her wide black sleeve with a paperclip chain at the wrist (the black sleeve is what reads in black and white). Only the hand
area comes from Codex (inside the source hand's box grown by 40 px, where Codex differs from the source); the city is the source.
070 - the user took the paperclip tower: wooden toy blocks flying in and stacking into a tower become the same shapes bent from thick
silver wire. Frames 0, 14 and 28, used whole (the frame is all blocks). The user expects H3 may struggle (“这个画面和原版区别很大”);
the fallback is keyframes only, without the source video.
"""
import subprocess
import sys
import time

import numpy as np
from PIL import Image
from scipy import ndimage

from codex_keyframes_0001 import DIR, source_frame
from codex_keyframes_0003 import CODEX
from common import ROOT

DESIGN = ROOT / 'deliverables/jujutsu/人设/paperclip_maximizer_v2.png'
KEEP = ('Keep EVERYTHING else exactly as in Image 1 - the background, the light, the colours, the camera framing and the 2D anime '
        'rendering. The output is a 16:9 image with the framing of Image 1. Do not create or modify any other files.')
HAND = ('Image 1 is a frame from a black-and-white manga-style anime opening: a city skyline with mountains behind it and a tall black '
        'pillar in the middle; a giant white hand reaches in from the upper right. Image 2 is the character design of the hand\'s owner. '
        'Redraw ONLY the hand as her hand: a slender young woman\'s hand with long, elegant fingers and long pointed nails shaded light '
        'silver-grey, in exactly the same place, size, pose and gesture as the hand in Image 1; at the wrist, where it enters the frame, '
        'the edge of her wide black monk\'s-robe sleeve, its hem lined with a chain of small silver paperclips. Drawn in the same black, '
        'white and grey manga style as Image 1, no colour. ')
TOWER = ('Image 1 is a frame from a grey monochrome anime opening: wooden toy blocks - cubes, arches, half-circles and cylinders - fly in '
         'and stack up into a tower, with diagonal motion streaks. Redraw every wooden block as the same shape built from thick, bent '
         'silver wire like giant paperclips: each block\'s outline and edges are rounded loops of shiny silver wire, an open wireframe you '
         'can see through, at exactly the same place, size, angle and motion blur as that wooden block in Image 1. No wood grain anywhere. '
         'Keep the grey monochrome palette and the diagonal streaks. ')
EDITS = [('061', 1, 'kf_061_f001_clip_hand_v1.png', [DESIGN], HAND), ('061', 14, 'kf_061_f014_clip_hand_v1.png', [DESIGN], HAND),
         ('070', 0, 'kf_070_f000_clip_tower_v1.png', [], TOWER), ('070', 14, 'kf_070_f014_clip_tower_v1.png', [], TOWER),
         ('070', 28, 'kf_070_f028_clip_tower_v1.png', [], TOWER)]


def hand_composite(local, name):
    """Codex inside the source hand's box (grown by 40 px) where it differs from the source; the source elsewhere."""
    out = DIR / name.replace('_v1', '_v2')
    a = np.asarray(Image.open(DIR / name).convert('RGB').resize((1024, 576), Image.LANCZOS)).astype(np.float32)
    b = np.asarray(Image.open(DIR / f'src_061_f{local:03d}.png').convert('RGB').resize((1024, 576), Image.LANCZOS)).astype(np.float32)
    white = b.min(-1) > 215
    lab, n = ndimage.label(white)
    sizes = ndimage.sum(white, lab, range(1, n + 1))
    edge = set(np.unique(np.r_[lab[:, -1], lab[0, :]])) - {0}
    hand = lab == max(edge, key=lambda k: sizes[k - 1])
    ys, xs = np.nonzero(hand)
    box = np.zeros(hand.shape, bool)
    box[max(ys.min() - 40, 0):ys.max() + 41, max(xs.min() - 40, 0):] = True
    d = box & (np.abs(a - b).max(-1) > 35)
    lab, n = ndimage.label(ndimage.binary_closing(d, iterations=3))
    sizes = ndimage.sum(np.ones_like(d), lab, range(1, n + 1))
    m = np.isin(lab, [k + 1 for k, z in enumerate(sizes) if z >= 200]) | (hand & box)
    m = ndimage.binary_dilation(ndimage.binary_fill_holes(m), iterations=4) & ndimage.binary_dilation(box, iterations=4)
    w = ndimage.gaussian_filter(m.astype(np.float32), 2)[..., None]
    Image.fromarray((a * w + b * (1 - w)).round().clip(0, 255).astype(np.uint8)).save(out)
    print('composited', out.name, f'{100 * m.mean():.1f} % from Codex', flush=True)


def main():
    only = set(sys.argv[1:])
    for unit, local, name, refs, prompt in EDITS:
        if only and name not in only:
            continue
        if not (DIR / name).exists():
            src = source_frame(unit, local, DIR / f'src_{unit}_f{local:03d}.png')
            args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
                    '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt'), '-i', str(src), *[a for r in refs for a in ('-i', str(r))], '--',
                    f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {prompt}{KEEP}']
            t = time.time()
            try:
                subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
            except subprocess.TimeoutExpired:
                print('TIMEOUT', name, flush=True)
                continue
            print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', flush=True)
        if unit == '061' and (DIR / name).exists():
            hand_composite(local, name)


if __name__ == '__main__':
    main()
