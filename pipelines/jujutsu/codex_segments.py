"""Units that are a sequence of still shots: one Codex-edited source frame per shot, each held for its shot's length (no H3).

036, the user (2026-10-02 10:49, on claude_redblack_kf_h3_v2): “claude没有红黑，动作也没有变化”. Measured: the source is seven still
images (frame differences 0.0 inside each shot, cuts after frames 3, 7, 10, 13, 17, 21) of the young man crouching or standing in
different red crest symbols; H3 had put Claude in her design-sheet pose. Each shot's frame is edited by Codex (the young man ->
Claude in the same red-and-black two-tone; Image 2 is her reference already turned red and black), pasted onto the source where it
differs, and any pixel left outside the red-and-black palette inside that area is put back on the palette with the same gradient map.
Usage: codex_segments.py UNIT [--no-register]
"""
import json
import pathlib
import shutil
import subprocess
import sys
import time

import numpy as np
from PIL import Image
from scipy import ndimage

import render_batch_0002 as b2
import render_shot as runner
from codex_keyframes_0003 import CODEX
from common import PROD, ROOT, p
from title_057 import frames
from tones import RED_STOPS

DIR = ROOT / 'deliverables/jujutsu/静帧'
RB_CLAUDE = b2.REFS / 'cl_redblack.png'
SEGMENTS = {
    '036': dict(rev='codex_segments_v1', label='伏黑惠→Claude·红色家纹七连（每段一张 Codex 静帧，红黑配色，姿势照原片）',
                source=PROD / 'shots/036/claude_red_h3_v1/source_exact_with_audio.mp4', cuts=[0, 4, 8, 11, 14, 18, 22, 29],
                refs=[RB_CLAUDE], palette='redblack',
                prompt='Image 1 is a frame from an anime opening drawn entirely in a red-and-black two-tone: glowing red clan-crest symbols '
                       'on black, and a young man. Image 2 is Claude, a girl, already drawn in red and black. Replace the young man with the '
                       'girl of Image 2 in exactly his pose, place and size - crouching, kneeling or standing exactly as he does, however '
                       'small he is - drawn in exactly the same red-and-black two-tone as the rest of the frame: only black and shades of red '
                       'with pale pink highlights, no other colour anywhere on her (no orange, beige, brown, white, blue or skin tones). Keep '
                       'the crest symbols, the room and everything else exactly as in Image 1. The output is a 16:9 image with the framing '
                       'of Image 1. No text. Do not create or modify any other files.'),
}
# Units found to be ONE still shot (frame differences 0.0 throughout, 2026-10-02 morning survey) with the user's notes:
# 058 “动作非常不自然，都是设定图动作，没有对应原图的动作”; 085 “应该是背影，而且不要用毫无变化的人设图，要对应动作”;
# 115 “前排有一个没有替换成豆包”; 142 (3 frames) “太夸张了，不好看。需要关键帧”.
A, D = ROOT / 'assets/人设', ROOT / 'deliverables/jujutsu/人设'
KEEP = (' Keep EVERYTHING else exactly as in Image 1 - the background, the light, the colours, the framing and the drawing style. '
        'The output is a 16:9 image with the framing of Image 1. No text. Do not create or modify any other files.')
SEGMENTS.update({
    '058': dict(rev='codex_still_v1', label='高专群像七人（Codex 静帧：每人姿势照原片）', palette=None,
                source=PROD / 'shots/058/lineup7_gpt6_maki4_h3_v4/source_exact_with_audio.mp4', cuts=[0, 30],
                refs=[D / 'gemini_maki_v4.png', D / 'gpt_yuta_v6.png', A / '鲸鱼娘.png', D / 'tengen_jensen_v1.png', A / 'mistral娘.jpg',
                      A / 'claude娘.png', A / 'GLM娘.png'],
                prompt='Image 1 is a frame from an anime opening: seven figures stand side by side in one row facing the camera, full body, on a '
                       'pale grey-white background with long shadows. Replace each of them, keeping exactly that person\'s stance, gesture, '
                       'place and height in the frame, from left to right: (1) the young woman on the far left -> the girl of Image 2 (Gemini, '
                       'one hand on her hip); (2) the young man second from the left with a long bag over his shoulder -> the girl of Image 3 '
                       '(GPT, with the long bag over her shoulder); (3) the young man third from the left -> the girl of Image 4 (DeepSeek); '
                       '(4) the tall figure in the middle in a white robe with arms folded -> the man of Image 5 (cartoon Jensen Huang, arms '
                       'folded); (5) the tall blonde woman third from the right -> the girl of Image 6 (Mistral); (6) the young man second from '
                       'the right -> the girl of Image 7 (Claude); (7) the young man on the far right with arms crossed -> the girl of Image 8 '
                       '(GLM, arms crossed). Each one looks exactly like her own reference image - her own hair, ears, eyes and outfit - and '
                       'never takes another\'s features. All seven are drawn in the clean, softly shaded TV-anime style and muted cool tones '
                       'of Image 1, standing naturally like the people they replace, not in design-sheet poses.' + KEEP),
    '085': dict(rev='codex_still_v1', label='伏黑惠→Claude·夜晚Y字路口（横尾忠则）（Codex 静帧：背影）', palette=None,
                source=PROD / 'shots/085/claude_h3_v1/source_exact_with_audio.mp4', cuts=[0, 8], refs=[A / 'claude娘.png'],
                prompt='Image 1 is a frame from an anime opening: an oil-painted night street splitting in a Y around a tall narrow building, '
                       'with a small figure standing in the street under a street light, seen from behind. Replace that figure with the girl '
                       'of Image 2 (Claude) seen from BEHIND, at exactly the same small size, place and stance, her back to the camera, painted '
                       'in the same oil-painting style and night light as Image 1.' + KEEP),
    '115': dict(rev='codex_still_v1', label='禅院家合影：前排全部→豆包（各造型），后排→Q版DeepSeek（Codex 静帧）', palette=None,
                source=PROD / 'shots/115/doubao_deepseek_photo_h3_v2/source_exact_with_audio.mp4', cuts=[0, 10],
                refs=[ROOT / 'assets/fate_zero/op1_v1/character_designs/references/doubao_official_avatar.jpg', D / 'doubao_zenin_naobito_v1.png', D / 'doubao_zenin_jinichi_v1.png',
                      D / 'doubao_zenin_naoya_v1.png', A / '鲸鱼娘-小.jpg'],
                prompt='Image 1 is an old sepia group photograph in front of a traditional Japanese hall: a front row of clan elders seated and '
                       'standing, and rows upon rows of people on the steps behind them. Image 2 is Doubao (a young woman with a chocolate-brown '
                       'bob and big glossy eyes); Images 3-5 show her in three clan costumes. Image 6 is a chibi DeepSeek girl. Replace EVERY '
                       'person in the front row - all of them, none left as the original - with Doubao in a different traditional clan kimono '
                       'for each, the seated one in the middle as in Image 3, the big one as in Image 4, the young one standing at the left as '
                       'in Image 5, each keeping that person\'s place, pose and size. Replace every person in the rows behind with a small '
                       'chibi DeepSeek girl of Image 6, evenly spaced like the people of Image 1. Everyone is tinted in the same faded sepia as '
                       'the photograph.' + KEEP),
    # 063, the user (11:40): “这个镜头完全没变化” - clip_eye_h3_v1 changed 0.00-0.01 % of the pixels. The source is two still shots: the
    # floating block of city (frames 0-12, kept as it is, as agreed) and the eye in a faint warm circle (13-33, static), which becomes hers
    '063': dict(rev='codex_segments_v1', label='漂浮的城市块保留；暗处的眼睛→回形针最大化器的眼睛（Codex 静帧）', palette=None,
                source=PROD / 'shots/063/clip_eye_h3_v1/source_exact_with_audio.mp4', cuts=[0, 13, 34], keep=[1],
                refs=[D / 'paperclip_maximizer_v2.png'],
                prompt='Image 1 is a frame from an anime opening: in a black void, a single eye seen inside a faint, warm circle of light. '
                       'Image 2 is the character design of the paperclip maximizer, a villain girl. Replace ONLY the eye with HER eye: a '
                       'half-lidded grey eye with long silver-grey lashes, its iris drawn as thin looped silver wire like the curves of a '
                       'paperclip, looking out calmly and a little sinister - at exactly the same place, size and angle, in the same dim warm '
                       'light and painted texture, still surrounded by the same faint circle of light and black.' + KEEP),
    # 071, the user (10:53) “应该是很多个HY跑过去，和原镜头对应”; H3 with keyframes ignored the tiny figures (hys_kf_h3_v3: the output
    # matched the source, not the keyframes). The source is animated on twos - ten distinct drawings, each held 2 frames - so each
    # drawing is redrawn by Codex (“试试方案1.5”), the first one anchoring the look of the others
    '071': dict(rev='codex_twos_v1', label='熊猫群→一群小 HY·夜森林空地（原片一拍二：10 张画面各由 Codex 重画，每张 2 帧）', palette=None,
                source=PROD / 'shots/071/hys_kf_h3_v3/source_exact_with_audio.mp4', cuts=list(range(0, 21, 2)), anchor_first=True,
                refs=[A / 'HY娘.png'],
                prompt='Image 1 is a frame from an anime opening: a dark night forest around a small moonlit green clearing, with about ten '
                       'tiny pandas scattered over the clearing. Image 2 is HY, a girl. Replace EVERY tiny panda with a tiny chibi version of '
                       'the girl of Image 2 - her long black-blue hair and red scarf readable even at this size - each at exactly that '
                       'panda\'s place, size, pose and direction, as if running or wandering across the clearing; no panda remains.' + KEEP),
    # 095-097, the user (10:56): “这个没有替换” - 7 frames in 4 shots of 1-2 frames (cuts after 0, 2, 4): one Codex still per shot
    '095-097': dict(rev='codex_segments_v1', label='日下部→梁文锋·青光中披风转身（每段一张 Codex 静帧）', palette=None,
                    source=PROD / 'shots/095-097/liang_tint_h3_v1/source_exact_with_audio.mp4', cuts=[0, 1, 3, 5, 7],
                    refs=[b2.REFS / 'liang_tint_55BBB4.png', D / 'liang_kusakabe_v1.png'],
                    prompt='Image 1 is a frame from an anime opening: on a black background a dark-haired man in a long pale coat turns '
                           'sharply, the coat swirling around him, lit entirely by a single cyan light. Images 2 and 3 are the cartoon of Liang '
                           'Wenfeng (Image 2 already in that cyan light). Replace the man with him: his face, glasses and hair from Images 2-3, '
                           'in exactly the man\'s pose, turn, place and size, still wearing the long swirling coat with the same folds and '
                           'motion smear, lit entirely by the same single cyan light against black, drawn in the same 2D anime style as Image 1.'
                           + KEEP),
    '142': dict(rev='codex_still_v1', label='高羽→MiniMax·扁平卡通吃惊掉手机（Codex 静帧，表情改可爱）', palette=None,
                source=PROD / 'shots/142/minimax_flat_h3_v1/source_exact_with_audio.mp4', cuts=[0, 3], refs=[A / 'minimax娘.jpg'],
                prompt='Image 1 is a frame from an anime opening: a flat cartoon of a man\'s face drawn with thick red outlines, screaming in '
                       'shock as his phone drops at the lower left, over wavy pink and cream colour bands. Replace the man with the girl of '
                       'Image 2 (MiniMax) drawn in the same flat cartoon style with thick red outlines, at the same place and size, with a CUTE '
                       'surprised face - round wide eyes and a small open "oh!" mouth, both hands up - not a grotesque scream; her phone drops '
                       'at the lower left like in Image 1.' + KEEP),
})


def codex(name, src, refs, prompt):
    if (DIR / name).exists():
        return True
    args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
            '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt'), '-i', str(src), *[a for r in refs for a in ('-i', str(r))], '--',
            f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {prompt}']
    t = time.time()
    try:
        subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
    except subprocess.TimeoutExpired:
        print('TIMEOUT', name, flush=True)
        return False
    ok = (DIR / name).exists()
    print('done' if ok else 'FAILED', name, f'{time.time() - t:.0f} s', flush=True)
    return ok


def off_redblack(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (np.maximum(g, b) > 60) & ((np.abs(g - b) > 35) | (g > 0.75 * r) | (b > 0.75 * r))


def paste(src_frame, edit, palette):
    a = np.asarray(Image.open(edit).convert('RGB').resize((1024, 576), Image.LANCZOS)).astype(np.float32)
    s = src_frame.astype(np.float32)
    d = np.abs(a - s).max(-1) > 30
    lab, n = ndimage.label(ndimage.binary_closing(d, iterations=2))
    sizes = ndimage.sum(np.ones_like(d), lab, range(1, n + 1))
    m = np.isin(lab, [k + 1 for k, z in enumerate(sizes) if z >= 40])  # low: the figure is tiny in the last shots
    m = ndimage.binary_dilation(ndimage.binary_fill_holes(m), iterations=3)
    w = ndimage.gaussian_filter(m.astype(np.float32), 1.5)[..., None]
    out = a * w + s * (1 - w)
    fixed = 0
    if palette == 'redblack':
        bad = off_redblack(out) & (w[..., 0] > 0.05)
        fixed = int(bad.sum())
        if fixed:
            y = out @ np.array([0.299, 0.587, 0.114], np.float32)
            v = np.clip(y / 255, 0, 1)
            ramp = np.stack([np.interp(v, RED_STOPS[:, 0], RED_STOPS[:, c]) for c in (1, 2, 3)], -1)
            region = ndimage.binary_dilation(bad, iterations=2) & (w[..., 0] > 0.05)
            out[region] = ramp[region]
    return np.clip(out, 0, 255).astype(np.uint8), float(m.mean()), fixed


def main():
    uid = sys.argv[1]
    spec = SEGMENTS[uid]
    out_dir = PROD / 'shots' / uid / spec['rev']
    out_dir.mkdir(parents=True, exist_ok=True)
    src = frames(spec['source'])
    cuts = spec['cuts']
    assert cuts[-1] == len(src), (cuts, len(src))
    result, notes = [], []
    jobs = []
    keep = set(spec.get('keep', ()))  # 1-based shots kept exactly as the source
    for k in range(len(cuts) - 1):
        if k + 1 in keep:
            continue
        mid = (cuts[k] + cuts[k + 1] - 1) // 2
        sf = DIR / f'src_{uid}_seg{k + 1}_f{mid:03d}.png'
        if not sf.exists():
            Image.fromarray(src[mid]).save(sf)
        jobs.append((f'still_{uid}_seg{k + 1}_v1.png', sf))
    # all shots at once (the user, 2026-10-02: Codex may run in parallel and the quota is plentiful)
    from concurrent.futures import ThreadPoolExecutor
    if spec.get('anchor_first'):
        # drawings of one animation: the first frame first, then every other frame drawn to match it (Image 3)
        first = codex(jobs[0][0], jobs[0][1], spec['refs'], spec['prompt'])
        extra = (' Image 3 is the same scene a moment earlier, already redrawn: draw every tiny girl exactly as she looks in Image 3 - '
                 'the same drawing, colours and size - only at her new place and pose from Image 1.')
        with ThreadPoolExecutor(max(1, len(jobs) - 1)) as pool:
            rest = list(pool.map(lambda j: codex(j[0], j[1], spec['refs'] + [DIR / jobs[0][0]], spec['prompt'] + extra), jobs[1:]))
        ok = [first] + rest
    else:
        with ThreadPoolExecutor(len(jobs)) as pool:
            ok = list(pool.map(lambda j: codex(j[0], j[1], spec['refs'], spec['prompt']), jobs))
    if not all(ok):
        raise SystemExit('Codex failed for ' + ', '.join(j[0] for j, o in zip(jobs, ok) if not o))
    names = iter(j[0] for j in jobs)
    for k in range(len(cuts) - 1):
        a, b = cuts[k], cuts[k + 1]
        mid = (a + b - 1) // 2
        if k + 1 in keep:
            result += [src[i] for i in range(a, b)]
            notes.append(dict(shot=k + 1, frames=[a, b - 1], kept_source=True))
            print(f'shot {k + 1}: frames {a}-{b - 1} kept as the source', flush=True)
            continue
        name = next(names)
        frame, taken, fixed = paste(src[mid], DIR / name, spec['palette'])
        Image.fromarray(frame).save(DIR / f'still_{uid}_seg{k + 1}_v2.png')
        notes.append(dict(shot=k + 1, frames=[a, b - 1], source_frame=mid, codex=name, taken_percent=round(100 * taken, 1),
                          recoloured_px=fixed))
        print(f'shot {k + 1}: frames {a}-{b - 1}, {100 * taken:.1f} % from Codex, {fixed} px put back on the palette', flush=True)
        result += [frame] * (b - a)
    full = out_dir / 'source_exact_with_audio.mp4'
    if not full.exists():
        shutil.copy2(spec['source'], full)
    silent = out_dir / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(result)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(result).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = out_dir / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    runner.configure(out_dir)
    check = runner.batch.validate_output(clip, len(result), True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    me = pathlib.Path(__file__).resolve()
    record = out_dir / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), shots=notes, recipe_text=(
        '原片是一串静止镜头：每段取中间一帧由 Codex 换人（姿势、位置、大小照原片），按差异区域贴回原片，'
        '区域内仍有非红黑像素则用同一渐变映射拉回红黑；每段定格原长度，原片原音。未经 H3。\nCodex 提示词：' + spec['prompt'])))
    p.write_json(out_dir / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == uid)
    if '--no-register' not in sys.argv and not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(uid, str(clip), record, spec['label'])
    print('READY', clip, flush=True)


if __name__ == '__main__':
    main()
