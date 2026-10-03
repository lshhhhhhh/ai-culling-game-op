"""002-004 v3: the thinking-level scale printed on the panel by Codex, composited under the moving hand.

User (2026-10-01): on the CPU text overlay (v2) “可以用codex生图吗？现在这个好难看”. The camera is still and only the hand moves, so one
Codex-edited still of frame 0 (deliverables/jujutsu/关键帧/kf_002-004_f00_thinking_v1.png, codex_keyframes_0002.py) replaces the
panel around the right knob in every frame: aligned to the source by phase correlation, colour-matched to the source panel, feathered
at the edge, and kept behind the hand (pixels clearly brighter than the per-pixel median plate, as in v2).
"""
import pathlib
import subprocess

import numpy as np
from PIL import Image
from scipy import ndimage

import render_shot as runner
import render_batch_0001 as b1
from common import PROD, ROOT, p
import thinking_002_004 as v2

import sys

UID = '002-004'
FULL_HAND = '--full-hand' in sys.argv  # v5: hand mask from the difference to the bare panel (v3/v4 used brightness only)
REV = ('thinking_codex_v6' if '--ink' in sys.argv else 'thinking_codex_v5' if FULL_HAND else 'thinking_codex_v4' if '--boost' in sys.argv
       else 'thinking_codex_v3')
OUT = PROD / 'shots' / UID / REV
STILL = ROOT / 'deliverables/jujutsu/关键帧/kf_002-004_f00_thinking_v1.png'
LABEL = ('煤气灶旋钮→Thinking level 刻度（Codex 画在面板上，合成到原片，手在字前面）' + ('；提高字的对比度' if '--boost' in sys.argv else '')
         + ('；修正手的遮挡（手指完整）' if FULL_HAND else '') + ('；THINKING 用 Codex 原字形改成深色（不加强对比、不换字体）' if '--ink' in sys.argv else ''))
REGION = (700, 0, 1024, 470)  # the panel around the right knob that takes the Codex still
LUMA = np.array([0.299, 0.587, 0.114], np.float32)


def shift(a, b):
    """Integer translation that moves b onto a (phase correlation on luma)."""
    F = np.fft.fft2(a) * np.conj(np.fft.fft2(b))
    r = np.fft.ifft2(F / (np.abs(F) + 1e-6)).real
    dy, dx = np.unravel_index(r.argmax(), r.shape)
    return (dy if dy < a.shape[0] // 2 else dy - a.shape[0]), (dx if dx < a.shape[1] // 2 else dx - a.shape[1])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    full = OUT / 'source_exact_with_audio.mp4'
    if not full.exists():
        import shutil
        shutil.copy2(v2.OUT.parent / 'thinking_cpu_v2' / 'source_exact_with_audio.mp4', full)
    src = v2.frames(full)
    start, end = b1.interval(UID)
    assert len(src) == end - start
    still = np.asarray(Image.open(STILL).convert('RGB').resize((1024, 576), Image.LANCZOS)).astype(np.float32)
    lums = src.astype(np.float32) @ LUMA
    plate_l = np.median(lums, axis=0)
    plate = np.median(src.astype(np.float32), axis=0)
    dy, dx = shift(lums[0], still @ LUMA)
    still = np.roll(still, (dy, dx), axis=(0, 1))
    x0, y0, x1, y1 = REGION
    region = np.zeros((576, 1024), np.float32)
    region[y0:y1, x0:x1] = 1
    region = ndimage.gaussian_filter(region, 12)
    # colour match the still to the source panel inside the region (mean and spread per channel)
    sel = region > 0.5
    for c in range(3):
        a, b = plate[..., c][sel], still[..., c][sel]
        still[..., c] = (still[..., c] - b.mean()) / (b.std() + 1e-6) * a.std() + a.mean()
    if '--boost' in sys.argv:
        # the user on v3: “我是感觉颜色有点看不清” - the pale grey print almost matches the grey panel. Find the strokes Codex added
        # (brighter than their surroundings and absent from the source panel), push them to near white (EXTRA to saturated red)
        # and darken a thin ring around them.
        sl = still @ LUMA
        new = (sl - ndimage.median_filter(sl, size=11) > 7) & (np.abs(sl - plate_l) > 10) & (region > 0.5)
        new = ndimage.binary_opening(new, iterations=1) | (new & ndimage.binary_dilation(new, iterations=1))
        # red print is not brighter than the panel, so it is found by hue instead: reddish in the still, not reddish in the source
        # the panel is purple (R above G, B about R), so red print is told apart by R well above B as well as G
        red = ((still[..., 0] - still[..., 2] > 25) & (still[..., 0] - still[..., 1] > 30) & (plate[..., 0] - plate[..., 2] < 10)
               & (region > 0.5))
        red = ndimage.binary_opening(red, iterations=1) | (red & ndimage.binary_dilation(ndimage.binary_opening(red, iterations=1), iterations=1))
        # THINKING sits on the bright upper panel, where “brighter than the surroundings” only caught bits of each letter and the
        # dark ring mangled them: there the strokes are found by their difference from the source panel and printed dark instead.
        think = np.zeros(sl.shape, bool)
        think[15:85, 815:965] = True
        dark = think & (sl - plate_l > 12)
        dark = ndimage.binary_opening(dark, iterations=1) | (dark & ndimage.binary_dilation(ndimage.binary_opening(dark, iterations=1), iterations=1))
        new = new & ~think
        white = new & ~red
        new = new | red
        ring = ndimage.binary_dilation(new, iterations=2) & ~new & (region > 0.5)
        soft = lambda m: ndimage.gaussian_filter(m.astype(np.float32), 0.7)[..., None]
        still = still * (1 - 0.35 * soft(ring))
        still = still * (1 - soft(white)) + np.array([246, 242, 250], np.float32) * soft(white)
        still = still * (1 - soft(red)) + np.array([242, 58, 48], np.float32) * soft(red)
        # The Codex THINKING was too faint to recover cleanly (the stroke mask caught only fragments of the letters): put the source
        # panel back there (its own small labels erased) and print the word in dark ink, no outline, softened like the panel print.
        clean = v2.erase(plate.astype(np.uint8))
        tb = ndimage.gaussian_filter(think.astype(np.float32), 3)[..., None]
        still = still * (1 - tb) + clean * tb
        from PIL import ImageDraw, ImageFilter, ImageFont
        ink = Image.new('L', (1024, 576), 0)
        d = ImageDraw.Draw(ink)
        font = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 27)
        w = d.textlength('THINKING', font=font)
        d.text((890 - w / 2, 34), 'THINKING', font=font, fill=235)
        ink = ink.rotate(-3, resample=Image.BICUBIC, center=(890, 48)).filter(ImageFilter.GaussianBlur(0.6))
        a = (np.asarray(ink).astype(np.float32) / 255)[..., None]
        still = still * (1 - a) + np.array([48, 38, 62], np.float32) * a
        print('boosted strokes', int(white.sum()), 'white px', int(red.sum()), 'red px', flush=True)
    if '--ink' in sys.argv:
        # v6, the user (2026-10-02): “revision-ffcfdf这个版本是最好的，唯一的问题是thinking看不太清楚，换个颜色就行。最新版本的字加的不好看，
        # 很假” - v3's look (no boost, no typeset word) with Codex's own THINKING letters re-inked dark: the letters are a little brighter
        # than the panel around them, so that local excess becomes the ink's opacity (letter shapes and antialiasing kept)
        sl = still @ LUMA
        # the word only, as a band along its slope (it rises to the right: T near y 74 at x 830, G near y 45 at x 927); a wide box
        # also inked the panel's top-edge highlight and scratches, a level box cut off ING
        yy, xx = np.mgrid[0:576, 0:1024]
        think = ((np.abs(yy - (74 - 0.3 * (xx - 830))) < 13) & (xx > 812) & (xx < 948)).astype(np.float32)
        think = ndimage.gaussian_filter(think, 1.5)
        excess = sl - ndimage.gaussian_filter(sl, 5)
        alpha = np.clip((excess - 2.5) / 9, 0, 1) * think
        lab, n = ndimage.label(alpha > 0.25)
        if n:  # letters are strokes of some size; scratches and grain are specks
            sizes = ndimage.sum(np.ones_like(alpha), lab, range(1, n + 1))
            keep = ndimage.binary_dilation(np.isin(lab, [k + 1 for k, z in enumerate(sizes) if z >= 14]), iterations=1)
            alpha = alpha * keep
        alpha = alpha[..., None]
        still = still * (1 - alpha) + np.array([44, 30, 62], np.float32) * alpha
        print('THINKING re-inked: %d px above half opacity' % int((alpha[..., 0] > 0.5).sum()), flush=True)
    result = []
    for fr, lum in zip(src, lums):
        if FULL_HAND:
            # The user on v4: “手指少了一块，然后右边有一片白色的” - the brightness test missed the shadowed part of the finger (covered
            # by the still) and left the lit fingertip floating. The camera is still, so the hand is whatever differs from the bare panel:
            # colour difference to the median plate, closed, holes filled, specks dropped, grown a little.
            diff = np.abs(fr.astype(np.float32) - plate).max(axis=-1)
            hand = ndimage.binary_closing(diff > 22, iterations=3)
            hand = ndimage.binary_fill_holes(hand)
            lab, n = ndimage.label(hand)
            if n:
                sizes = ndimage.sum(hand, lab, range(1, n + 1))
                hand = np.isin(lab, [k + 1 for k, s in enumerate(sizes) if s >= 400])
            hand = ndimage.binary_dilation(hand, iterations=3).astype(np.float32)
        else:
            hand = ndimage.binary_dilation((lum > 170) & (lum > plate_l + 35), iterations=3).astype(np.float32)
        m = (region * (1 - ndimage.gaussian_filter(hand, 1.5)))[..., None]
        out = fr.astype(np.float32) * (1 - m) + still * m
        result.append(np.clip(out, 0, 255).astype(np.uint8))
    silent = OUT / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(end - start), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(result).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    Image.fromarray(result[0]).save(OUT / 'preview_f00.png')
    Image.fromarray(result[10]).save(OUT / 'preview_f10.png')
    clip = OUT / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    runner.configure(OUT)
    check = runner.batch.validate_output(clip, end - start, True)
    record = OUT / 'title_compositing.json'
    builder = pathlib.Path(__file__).resolve()
    p.write_json(record, dict(kind='cpu_text', builder=str(builder), builder_sha256=p.sha(builder),
                              recipe_text=f'Codex 在第 0 帧的面板上印出 THINKING 与 LOW / MEDIUM / HIGH / EXTRA 刻度（{STILL.name}）；'
                                          f'对齐（位移 {dy},{dx}）、调色后合成到每一帧右侧旋钮一带，手经过时保留原片的手。未经 H3。'))
    p.write_json(OUT / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if '--no-register' not in sys.argv and not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, 'shift', (dy, dx), flush=True)


if __name__ == '__main__':
    main()
