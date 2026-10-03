"""A character replaced by one Codex still that follows the source's slow camera drift, with everything else taken from the source
frame by frame (the collage pieces that land over her, the moving light) - CPU, no H3.

123, the user (2026-10-02 11:00): “没有替换。用了关键帧吗？” then “接下来处理123”. gemini_mai3_uro_h3_v3 was the source again (Uro
kept). The source: a close view of Uro looking up, hair swept back, drifting ~0.5 px per frame; from frame 6 a hand, then a prism,
a splash painting and a sparkler are pasted over the picture. Here: frame 0 edited by Codex (Uro -> Gemini in the Mai design), the
still moved with the drift measured by phase correlation, and inside her area every pixel that the source changes beyond the drift
(the pasted pieces) comes from the source.
Usage: still_drift.py UNIT [--no-register]
"""
import pathlib
import shutil
import subprocess
import sys
import time

import numpy as np
from PIL import Image
from scipy import ndimage

import render_shot as runner
from codex_keyframes_0003 import CODEX
from common import PROD, ROOT, p
from pan_040 import shift
from title_057 import frames

DIR = ROOT / 'deliverables/jujutsu/静帧'
D = ROOT / 'deliverables/jujutsu/人设'
KEEP = (' Keep EVERYTHING else exactly as in Image 1 - the background, the light, the colours, the framing and the 2D anime '
        'rendering. The output is a 16:9 image with the framing of Image 1. No text. Do not create or modify any other files.')
UNITS = {
    '123': dict(rev='codex_drift_v1', source=PROD / 'shots/123/gemini_mai3_uro_h3_v3/source_exact_with_audio.mp4', frame=0,
                refs=[D / 'gemini_mai_v3.png'],
                label='乌鹭→Gemini（真依造型）·仰视与拼贴（Codex 静帧随原片镜头漂移；手、棱镜、泼溅画、火花用原片逐帧叠上）',
                prompt='Image 1 is a frame from an anime opening: a close view of a woman with swept-back purple hair, big round gold '
                       'earrings and a black choker, looking up and to the left with a confident smirk, the wind sweeping her hair back, '
                       'against a dark background with a streak of white light. Image 2 is Gemini, a girl: a shoulder-length asymmetric '
                       'purple-to-pink bob, cat ears, amber eyes, a black sailor uniform with a bow in Google\'s blue, red, yellow and green. '
                       'Replace the woman with the girl of Image 2 - her face, cat ears, hair colour, amber eyes and her black sailor collar '
                       'with the gradient bow - in exactly the woman\'s pose, head angle, place, size and confident smirk, her hair blown '
                       'back by the same wind, lit the same way. No gold earrings, no choker.' + KEEP),
    # 126, the user (2026-10-02): “依旧需要关键帧。发饰还是不对。” - GPT in gpt6_grey_h3_v1 is right except the round ornament; the source
    # barely moves (drift under 2 px, the jumps are collage panels popping in). Codex redraws the knot on OUR H3 frame 0 ('base'), only
    # the box around the ornament is taken from its picture ('patch'), and that still follows the source's drift under the source's panels.
    '126': dict(rev='codex_drift_v1', source=PROD / 'shots/126/gpt6_grey_h3_v1/source_exact_with_audio.mp4', frame=0,
                base=PROD / 'shots/126/gpt6_grey_h3_v1/native_fullframe.mp4', patch=(535, 160, 630, 260),
                refs=[ROOT / 'deliverables/jujutsu/人设/gpt_yuta_v6.png'],
                label='乙骨→GPT·黑白持刀与拼贴（H3 第 0 帧由 Codex 重画结形发饰，静帧随原片镜头漂移；拼贴小图用原片逐帧叠上）',
                prompt='Image 1 is a frame from an anime opening drawn in black, white and grey: a girl with long wavy white hair holds a '
                       'long sword across the frame. Image 2 is her character design. Redraw ONLY her small hair ornament so that it is '
                       'exactly the knot-shaped ornament of Image 2 - the same shape and size, crisp, undistorted and clearly readable - '
                       'at the same place on her head, drawn in the same black, white and grey as the frame. Change nothing else about '
                       'her or the frame.' + KEEP),
}


def codex(name, src, refs, prompt):
    if (DIR / name).exists():
        return
    args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
            '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt'), '-i', str(src), *[a for r in refs for a in ('-i', str(r))], '--',
            f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {prompt}']
    t = time.time()
    subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
    print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', flush=True)
    if not (DIR / name).exists():
        raise SystemExit(f'Codex failed; see codex_last_message_{name[:-4]}.txt')


def translate(img, dx, dy):
    return ndimage.shift(img, (dy, dx) + (0,) * (img.ndim - 2), order=1, mode='nearest')


def main():
    uid = sys.argv[1]
    spec = UNITS[uid]
    out = PROD / 'shots' / uid / spec['rev']
    out.mkdir(parents=True, exist_ok=True)
    src = frames(spec['source'])
    k0 = spec['frame']
    # the picture Codex edits: the source frame, or our H3 frame when only a detail of our character is fixed ('base')
    base = frames(spec['base'])[k0] if 'base' in spec else src[k0]
    sf = DIR / (f'h3_{uid}_{spec["base"].parent.name}_f{k0:03d}.png' if 'base' in spec else f'src_{uid}_f{k0:03d}.png')
    if not sf.exists():
        Image.fromarray(base).save(sf)
    name = f'still_{uid}_{spec["rev"]}.png'
    codex(name, sf, spec['refs'], spec['prompt'])
    still = np.asarray(Image.open(DIR / name).convert('RGB').resize((1024, 576), Image.LANCZOS)).astype(np.float32)
    if 'patch' in spec:  # only this box from Codex's picture, feathered into the base frame
        x0, y0, x1, y1 = spec['patch']
        box = np.zeros((576, 1024), np.float32)
        box[y0:y1, x0:x1] = 1
        box = ndimage.gaussian_filter(box, 6)[..., None]
        still = still * box + base.astype(np.float32) * (1 - box)
        Image.fromarray(still.round().clip(0, 255).astype(np.uint8)).save(DIR / name.replace('.png', '_patched.png'))
    s0 = src[k0].astype(np.float32)
    # her area: where the still differs from the source frame (Uro's figure and hers), filled and grown
    d = np.abs(still - s0).max(-1) > 30
    lab, n = ndimage.label(ndimage.binary_closing(d, iterations=3))
    sizes = ndimage.sum(np.ones_like(d), lab, range(1, n + 1))
    char = np.isin(lab, [i + 1 for i, z in enumerate(sizes) if z >= 300])
    char = ndimage.binary_dilation(ndimage.binary_fill_holes(char), iterations=4).astype(np.float32)
    result, drifts = [], []
    for i in range(len(src)):
        dy, dx, _ = shift(src[k0], src[i])
        dx, dy = -float(dx), -float(dy)  # where frame k0's content sits in frame i
        drifts.append((round(dx, 1), round(dy, 1)))
        si = src[i].astype(np.float32)
        still_i, char_i, s0_i = translate(still, dx, dy), translate(char, dx, dy), translate(s0, dx, dy)
        # pasted pieces: what the source changes beyond the drift
        pasted = ndimage.binary_opening(np.abs(si - s0_i).max(-1) > 45, iterations=2)
        lab, n = ndimage.label(pasted)
        if n:
            sz = ndimage.sum(pasted, lab, range(1, n + 1))
            pasted = np.isin(lab, [j + 1 for j, z in enumerate(sz) if z >= 400])
        pasted = ndimage.binary_dilation(pasted, iterations=2)
        w = ndimage.gaussian_filter(char_i * (~pasted), 1.5)[..., None]
        result.append(np.clip(si * (1 - w) + still_i * w, 0, 255).astype(np.uint8))
    full = out / 'source_exact_with_audio.mp4'
    if not full.exists():
        shutil.copy2(spec['source'], full)
    silent = out / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(result)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(result).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = out / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    for k in (0, 7, 12, len(result) - 1):
        Image.fromarray(result[k]).save(out / f'preview_f{k:03d}.png')
    print('drift per frame', drifts, flush=True)
    if '--no-register' in sys.argv:
        print('PREVIEW', clip, flush=True)
        return
    runner.configure(out)
    check = runner.batch.validate_output(clip, len(result), True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    me = pathlib.Path(__file__).resolve()
    record = out / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), still=name, drift=drifts, recipe_text=(
        f'Codex 改原片第 {k0} 帧换人（{spec["label"]}），静帧按原片逐帧测得的镜头漂移平移；人物区域外、以及原片后来贴上的拼贴（超出漂移的变化）'
        '都直接用原片当帧。原片原音。未经 H3。\nCodex 提示词：' + spec['prompt'])))
    p.write_json(out / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == uid)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(uid, str(clip), record, spec['label'])
    print('READY', clip, flush=True)


if __name__ == '__main__':
    main()
