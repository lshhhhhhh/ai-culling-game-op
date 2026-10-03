"""124-125: Gakuganji -> cartoon Musk, the crow -> a Starship silhouette, the landscape card -> a Cybertruck card. Codex stills and
CPU compositing, no H3.

The user (2026-10-02): on musk_h3_v1 “替换失败。需要关键帧。”, then “其实我还想增加设计。背景里的鸟换成星舰的简剪影，然后右边的风景图变成
cyber truck。全部用静止帧和算法做，不用视频生成”.
Source (22 frames): a hard cut at 7; the camera barely drifts (under 2 px). Shot 1 (0-6): the hooded Gakuganji as a frame-filling bust
on a grey paper sunburst. Shot 2 (7-21): the same bust in front of a red banner (a gold sun with a crow on a branch at the left); paper
cards pop in on top - a fiery landscape at 12 (right), a gold texture over its bottom at 14, a dark card with a red triangle and a
noise strip at 17 (bottom left).
Here: one Codex still per shot (shot 2's drawn with shot 1's Musk as the reference so he stays the same), moved with the measured
drift and carrying the source's grain; the landscape card's slot gets a Codex-redrawn Cybertruck card; every other card is the source,
frame by frame.
Usage: collage_124.py draw | render [--no-register]
"""
import pathlib
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image
from scipy import ndimage

import render_shot as runner
from codex_keyframes_0003 import CODEX
from common import PROD, ROOT, p
from pan_040 import shift
from title_057 import frames

UID, REV = '124-125', 'collage_code_v1'
DIR = ROOT / 'deliverables/jujutsu/静帧'
OUT = PROD / 'shots' / UID / REV
SOURCE = PROD / 'shots' / UID / 'musk_h3_v1' / 'source_exact_with_audio.mp4'
MUSK = ROOT / 'deliverables/jujutsu/人设/musk_gakuganji_v1.png'
LABEL = '乐岩寺→马斯克（卡通）；乌鸦→星舰剪影；右边风景拼贴→Cybertruck（Codex 静帧＋代码拼贴，其余卡片用原片逐帧；未经 H3）'
CUT = 7            # first frame of shot 2
K1, K2 = 3, 8      # the frames Codex edits for shot 1 and shot 2
CARD_FROM = 12     # the landscape card lands here and stays put
CARD = (711, 255, 967, 446)  # its slot (x0, y0, x1, y1), inside its thin paper edge
PIECES = (14, 17)  # the later cards (gold texture; dark card + noise strip): measured on their entrance frames, they then stay put
KEEP = (' Keep EVERYTHING else exactly as in Image 1 - the background, the light, the colours, the framing and the 2D anime '
        'rendering. The output is a 16:9 image with the framing of Image 1. No text. Do not create or modify any other files.')
MAN = ('short swept-back brown hair, a broad confident grin, a grey haori over a black kimono with a silver tassel cord, the neck of '
       'an electric guitar over his shoulder')
STILL1 = ('still_124_musk_s1_v1.png', lambda: [DIR / f'src_124_f{K1:03d}.png', MUSK],
          'Image 1 is a frame from a 2D anime opening: a huge hooded old man seen from the front as an extreme close-up bust that fills '
          'the frame - a dark hood and robe drawn with thin red lines, his face hidden in shadow, a white emblem of a meditating figure '
          'on the hood - in front of a pale grey paper sunburst. Image 2 is the character design of a man: ' + MAN + '. Replace the '
          'hooded old man completely with the man of Image 2: no hood, no emblem, no red-lined robe - his own face fully visible and '
          'lit, his brown hair, his grey haori and black kimono - seen from the front as a close bust at exactly the same place and '
          'size: his head as big as the old man\'s hooded head and where it is, his shoulders spreading out to the bottom edge of the '
          'frame like the robe. An imposing, smug half-smile, looking straight at the camera, drawn in the same 2D anime style with the '
          'same dark, dramatic shading. Keep the pale grey paper sunburst background.' + KEEP)
STILL2 = ('still_124_musk_s2_v1.png', lambda: [DIR / f'src_124_f{K2:03d}.png', DIR / STILL1[0]],
          'Image 1 is a frame from a 2D anime opening: a huge hooded old man as a close bust in front of a red collage banner - at the '
          'left a golden sun with a black crow perched on a bare branch, at the right black and olive shapes - with a red emblem and a '
          'yellow halo on his hood, a pale grey paper sunburst below the banner. Image 2 is the same camera with the man who must '
          'replace him. Make exactly two changes. (1) Replace the hooded old man completely with the man of Image 2, copied exactly '
          'from Image 2 - his face, hair, smile, grey haori and black kimono, at the same place, size and lighting as in Image 2; no '
          'hood, no emblem, no halo. (2) Replace the black crow in front of the golden sun with a simple flat black silhouette of a '
          'SpaceX Starship rocket - a tall slim cylinder with a rounded pointed nose, two small flaps near the nose and two larger fins '
          'at the base - standing upright in front of the sun, a little taller than the crow, in the same flat silhouette style as the '
          'crow. Keep the sun, the branches, the red banner, the black and olive shapes at the right and the grey sunburst exactly as '
          'in Image 1.' + KEEP)
TRUCK = ('card_124_cybertruck_v1.png', lambda: [DIR / 'src_124_card.png'],
         'Image 1 is a small printed collage card: a fiery red sky with dark red clouds and magenta at the top, orange and yellow '
         'flames along the ridge of black hills. Redraw it as the same kind of card in the same palette and the same flat, grainy '
         'screen-print look: the same fiery red sky with dark red clouds and magenta at the top, the orange-yellow glow at the horizon, '
         'and in front of it the black silhouette of a Tesla Cybertruck - the angular, wedge-shaped stainless-steel pickup with one '
         'sharp triangular roofline - seen from the side, parked on the black hills, large, filling most of the card\'s width, a thin '
         'bright line of light along its sharp roof edge. Same framing and landscape aspect ratio as Image 1, no border, no text, no '
         'logos. Do not create or modify any other files.')


# v2, the user on collage_code_v1: “左上角的星舰在树上很怪。应该在发射塔架上。左下角和右上角右下角都是原版的元素，想想替换成什么。先讨论再动手”,
# then “124按照你的方案”: the launch tower with Starship in front of the sun, Optimus at the top right, Mars and a Starlink train for the
# bottom-left cards, Dogecoin for the gold card. Shot 2's still is edited once more (only the two banner areas are taken, Musk stays the
# v1 pixels); the cards are new art pasted in their measured places - nothing of the source's cards remains.
V2 = '--v2' in sys.argv
if V2:
    REV = 'collage_code_v2'
    OUT = PROD / 'shots' / UID / REV
    LABEL = ('乐岩寺→马斯克（卡通）；太阳前是发射塔架上的星舰，右上→Optimus 机器人，左下→火星＋星链卫星列车，右下→狗狗币，右边风景→Cybertruck'
             '（Codex 静帧＋代码拼贴，未经 H3）')
STILL2B = ('still_124_musk_s2_v2.png', lambda: [DIR / STILL2[0]],
           'Image 1 is a frame from a 2D anime opening: a grinning man in a grey haori in front of a red collage banner - at the left a '
           'golden sun with a black rocket silhouette and bare black branches in front of it, at the right black and olive-green geometric '
           'shapes. Make exactly two changes, both in the same flat cut-paper silhouette style as the banner (flat black shapes with a few '
           'olive-green accents, on the same red textured paper): (1) At the left, replace the bare branches and the rocket with a black '
           'silhouette of a SpaceX launch tower - a tall lattice steel tower with two long horizontal "chopstick" catch arms near its top - '
           'with the Starship rocket (a tall slim cylinder with a rounded nose and small flaps) standing on its launch mount right beside '
           'the tower, both in front of the golden sun and rising from the bottom edge of the banner. (2) At the right, replace the black '
           'and olive shapes with the Tesla Optimus humanoid robot - its sleek helmet-like head with a dark face visor, its shoulders and one '
           'raised hand - as a big flat black silhouette with olive-green panel lines, filling the same area. Keep the man, his guitar, the '
           'golden sun, the red banner texture and the grey sunburst below exactly as in Image 1.' + KEEP)
DARK = (26, 375, 231, 552)    # the black card of frame 17 (on top) ...
STRIP = (165, 335, 272, 490)  # ... and the grey noise strip behind its top right
ART2 = {
    'mars': ('card_124_mars_v1.png', DARK,
             'Image 1 is a small printed collage card: on black, a grainy red triangle and a thin white outline. Draw a new card of the same '
             'shape in the same grainy screen-print look and the same colours (grainy red and thin white lines on black): the red planet Mars '
             'as a big grainy red disc, and a thin white dotted flight path curving to it from a small Earth in a corner. No border, no text, '
             'no logos. The same aspect ratio as Image 1. Do not create or modify any other files.'),
    'starlink': ('card_124_starlink_v1.png', STRIP,
                 'Image 1 is a narrow printed collage strip of grainy grey-blue noise like TV static (ignore the black card covering its lower '
                 'left). Draw a new strip of the same tall, narrow shape: a dark blue night sky in the same grainy grey-blue static texture, '
                 'crossed by one long straight diagonal line of small, evenly spaced bright white dots - a Starlink satellite train. No '
                 'border, no text, no logos. A tall portrait image. Do not create or modify any other files.'),
    'doge': ('card_124_doge_v1.png', None,
             'Image 1 is a small printed collage card of grainy gold and brown texture. Draw a new card of the same shape in the same '
             'grainy gold-and-brown print look: a heap of shiny gold coins filling the whole card, each coin stamped with the face of a cute '
             'Shiba Inu dog, like Dogecoin - no letters, no logos, no border. The same wide aspect ratio as Image 1. Do not create or modify '
             'any other files.'),
}
GOLD_FROM = 14


def draw_v2():
    src = frames(SOURCE)
    def crop(name, box, k):
        x0, y0, x1, y1 = box
        Image.fromarray(src[k][y0:y1, x0:x1]).resize(((x1 - x0) * 4, (y1 - y0) * 4), Image.LANCZOS).save(DIR / name)
        return DIR / name
    jobs = [STILL2B]
    for key, (name, box, prompt) in ART2.items():
        ref = crop(f'src_124_{key}.png', box or (768, 402, 1004, 522), 20)
        jobs.append((name, lambda r=ref: [r], prompt))
    with ThreadPoolExecutor(len(jobs)) as pool:
        print(list(pool.map(codex, jobs)))


def still2_v2():
    """Shot 2's still: v1 with only the two banner areas taken from Codex's edit (the guitar neck and Musk stay v1's pixels)."""
    a = cover(DIR / STILL2B[0], 1024, 576)
    b = cover(DIR / STILL2[0], 1024, 576)
    d = np.abs(a - b).max(-1) > 35
    lab, n = ndimage.label(ndimage.binary_closing(d, iterations=3))
    sizes = ndimage.sum(np.ones_like(d), lab, range(1, n + 1))
    m = ndimage.binary_dilation(ndimage.binary_fill_holes(np.isin(lab, [k + 1 for k, z in enumerate(sizes) if z >= 300])), iterations=4)
    region = np.zeros((576, 1024), bool)
    region[0:300, 0:345] = True
    region[0:300, 645:1024] = True
    region[215:300, 265:365] = False  # the guitar's head
    w = ndimage.gaussian_filter((m & region).astype(np.float32), 2)[..., None]
    return a * w + b * (1 - w)


def codex(item):
    name, refs, prompt = item
    if (DIR / name).exists():
        return name, True
    args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
            '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt'), *[a for r in refs() for a in ('-i', str(r))], '--',
            f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {prompt}']
    t = time.time()
    try:
        subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
    except subprocess.TimeoutExpired:
        pass
    print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', flush=True)
    return name, (DIR / name).exists()


def draw():
    src = frames(SOURCE)
    for k in (K1, K2):
        Image.fromarray(src[k]).save(DIR / f'src_124_f{k:03d}.png')
    x0, y0, x1, y1 = CARD
    Image.fromarray(src[CARD_FROM + 1][y0:y1, x0:x1]).resize(((x1 - x0) * 4, (y1 - y0) * 4), Image.LANCZOS).save(DIR / 'src_124_card.png')
    with ThreadPoolExecutor(2) as pool:  # the card and shot 1 together, then shot 2 with shot 1's Musk as its reference
        print(list(pool.map(codex, [STILL1, TRUCK])))
    print(codex(STILL2))


def translate(img, dx, dy):
    return ndimage.shift(img, (dy, dx) + (0,) * (img.ndim - 2), order=1, mode='nearest')


def cover(path, w, h):
    im = Image.open(path).convert('RGB')
    s = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * s)), max(h, round(im.height * s))), Image.LANCZOS)
    x0, y0 = (im.width - w) // 2, (im.height - h) // 2
    return np.asarray(im.crop((x0, y0, x0 + w, y0 + h)), np.float32)


def render():
    OUT.mkdir(parents=True, exist_ok=True)
    full = OUT / 'source_exact_with_audio.mp4'
    if not full.exists():
        shutil.copy2(SOURCE, full)
    src = frames(full)
    stills = {k: cover(DIR / n, 1024, 576) for k, n in ((K1, STILL1[0]), (K2, STILL2[0]))}
    if V2:
        stills[K2] = still2_v2()
    x0, y0, x1, y1 = CARD
    card = cover(DIR / TRUCK[0], x1 - x0, y1 - y0)
    slot = np.zeros((576, 1024), bool)
    slot[y0:y1, x0:x1] = True
    # v1 took whatever the source changed beyond the drift: that also pasted Gakuganji's own late mouth and line changes over Musk and
    # the landscape card's flickering flames over the truck. Each later card is found once: the largest block its entrance frame
    # changes (opened, so the flame flicker beside it stays out), closed and filled.
    cards = {}
    for f in PIECES:
        d = ndimage.binary_opening(np.abs(src[f].astype(np.float32) - src[f - 1]).max(-1) > 45, iterations=2)
        lab, n = ndimage.label(d)
        big = lab == 1 + int(np.argmax(ndimage.sum(d, lab, range(1, n + 1))))
        m = ndimage.binary_dilation(ndimage.binary_fill_holes(ndimage.binary_closing(big, iterations=5)), iterations=2)
        cards[f] = m
        ys, xs = np.where(m)
        print('card at', f, (xs.min(), ys.min(), xs.max(), ys.max()), int(m.sum()), 'px', flush=True)
    layers = []  # v2: (first frame, mask, canvas) pasted in this order - truck, Dogecoin, Starlink strip, Mars card on top
    if V2:
        def canvas_for(name, box):
            bx0, by0, bx1, by1 = box
            c = np.zeros((576, 1024, 3), np.float32)
            c[by0:by1, bx0:bx1] = cover(DIR / name, bx1 - bx0, by1 - by0)
            m = np.zeros((576, 1024), bool)
            m[by0:by1, bx0:bx1] = True
            return c, m
        truck_c, _ = canvas_for(TRUCK[0], CARD)
        layers.append((CARD_FROM, slot, truck_c))
        # the gold card is a rectangle: its measured mask has holes where its dark print matched the dark robe behind it
        ys, xs = np.nonzero(cards[GOLD_FROM])
        doge_c, doge_m = canvas_for(ART2['doge'][0], (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
        layers.append((GOLD_FROM, doge_m, doge_c))
        for key in ('starlink', 'mars'):
            c, m = canvas_for(ART2[key][0], ART2[key][1])
            if key == 'starlink':
                # the satellites are 1-2 px dots in the 1024 x 1536 art and vanish at the strip's ~107 px: found there, redrawn as 3 px
                # bright dots with a soft glow at the same places
                art = np.asarray(Image.open(DIR / ART2[key][0]).convert('L'), np.float32)
                lab, n = ndimage.label(art > 200)
                pts = np.array(ndimage.center_of_mass(art > 200, lab, range(1, n + 1)) if n else np.zeros((0, 2)))
                # only the train: the straight line through the most bright points (RANSAC); the grain's specks are off it
                rng = np.random.default_rng(124)
                best = np.zeros(len(pts), bool)
                for _ in range(2000):
                    a_, b_ = pts[rng.choice(len(pts), 2, replace=False)]
                    d = b_ - a_
                    if np.hypot(*d) < 50:
                        continue
                    nrm = np.array([-d[1], d[0]]) / np.hypot(*d)
                    inl = np.abs((pts - a_) @ nrm) < 6
                    if inl.sum() > best.sum():
                        best = inl
                pts = pts[best]
                bx0, by0, bx1, by1 = ART2[key][1]
                s = max((bx1 - bx0) / art.shape[1], (by1 - by0) / art.shape[0])  # as cover() scales and centres it
                ox, oy = (art.shape[1] * s - (bx1 - bx0)) / 2, (art.shape[0] * s - (by1 - by0)) / 2
                dots = np.zeros((576, 1024), np.float32)
                for py, px in pts:
                    X, Y = int(round(px * s - ox)) + bx0, int(round(py * s - oy)) + by0
                    if bx0 <= X < bx1 and by0 <= Y < by1:
                        dots[Y, X] = 1
                print('Starlink dots', int(dots.sum()), flush=True)
                core = np.clip(ndimage.gaussian_filter(ndimage.binary_dilation(dots > 0, iterations=1).astype(np.float32), 0.6) * 1.6, 0, 1)
                glow = np.clip(ndimage.gaussian_filter(dots, 2.0) * 12, 0, 0.5)
                a = np.maximum(core, glow)[..., None] * m[..., None]
                c = c * (1 - a) + np.array([235, 242, 255], np.float32) * a
            if key == 'mars':  # the black card's thin pale paper edge, as on the source's card
                edge = m & ~ndimage.binary_erosion(m, iterations=2)
                c[edge] = (200, 204, 210)
            layers.append((17, m, c))
    result, drifts = [], []
    for i in range(len(src)):
        k0 = K1 if i < CUT else K2
        dy, dx, _ = shift(src[k0], src[i])
        dx, dy = -float(dx), -float(dy)  # where frame k0's content sits in frame i
        drifts.append((round(dx, 1), round(dy, 1)))
        si = src[i].astype(np.float32)
        s0_i = translate(src[k0].astype(np.float32), dx, dy)
        diff = si - s0_i
        # the source's grain and flicker carried onto the still (small differences only)
        grain = np.where(np.abs(diff).max(-1, keepdims=True) < 20, diff, 0)
        out = translate(stills[k0], dx, dy) + grain
        if V2:
            for f, m, c in layers:
                if i >= f:
                    t = ndimage.gaussian_filter(m.astype(np.float32), 0.8)[..., None]
                    out = out * (1 - t) + c * t
            result.append(np.clip(out, 0, 255).astype(np.uint8))
            continue
        # the later cards from the source; the landscape slot (minus whatever later card lies on it) takes the truck card
        pasted = np.zeros((576, 1024), bool)
        for f, m in cards.items():
            if i >= f:
                pasted |= m
        truck = slot & ~pasted if i >= CARD_FROM else np.zeros((576, 1024), bool)
        w = ndimage.gaussian_filter(pasted.astype(np.float32), 1.0)[..., None]
        out = out * (1 - w) + si * w
        t = ndimage.gaussian_filter(truck.astype(np.float32), 0.8)[..., None]
        canvas = np.zeros_like(out)
        canvas[y0:y1, x0:x1] = card
        out = out * (1 - t) + canvas * t
        result.append(np.clip(out, 0, 255).astype(np.uint8))
    silent = OUT / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(result)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(result).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = OUT / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    for k in (3, 8, 14, 21):
        Image.fromarray(result[k]).save(OUT / f'preview_f{k:03d}.png')
    print('drift per frame', drifts, flush=True)
    if '--no-register' in sys.argv:
        print('PREVIEW', clip, flush=True)
        return
    runner.configure(OUT)
    check = runner.batch.validate_output(clip, len(result), True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    me = pathlib.Path(__file__).resolve()
    record = OUT / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), stills=[STILL1[0], STILL2[0], TRUCK[0]],
                              drift=drifts, recipe_text=(
        '两个镜头各用一张 Codex 静帧（第 3 帧：乐岩寺→卡通马斯克；第 8 帧：同一个马斯克，以第一张为参考，乌鸦→星舰剪影），按原片逐帧测得的'
        '镜头漂移平移并叠上原片的颗粒；第 12 帧起右边风景卡片的位置换成 Codex 重画的 Cybertruck 卡片，其余后贴的卡片（金色纹理、'
        '红三角暗卡、噪点条）直接用原片当帧。原片原音。未经 H3。\nCodex 提示词（镜头一）：' + STILL1[2] + '\n（镜头二）：' + STILL2[2]
        + '\n（卡片）：' + TRUCK[2] + ((
        '\nv2：镜头二静帧再由 Codex 改两处（树枝与星舰→发射塔架旁的星舰，右上黑块→Optimus 剪影），只取这两块；后贴卡片全部换成新画'
        '（第 12 帧 Cybertruck、第 14 帧狗狗币、第 17 帧星链卫星列车与火星），按原片测得的位置贴上，原片卡片不再出现。\n（镜头二 v2）：'
        + STILL2B[2] + ''.join(f'\n（{k}）：{v[2]}' for k, v in ART2.items())) if V2 else ''))))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, flush=True)


if __name__ == '__main__':
    {'draw': draw_v2 if V2 else draw, 'render': render}[sys.argv[1]]()
