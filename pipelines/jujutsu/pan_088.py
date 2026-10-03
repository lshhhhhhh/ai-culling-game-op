"""088 as an original shot: DeepSeek with her pressed hands raised overhead, the camera tilting up a tall Codex painting (CPU; no H3).

User (2026-10-02 12:30): H3 kept the young man twice (ds_kf_h3_v2: inside the keyframes' area the output stayed 4.5-12.5 from the
source, 50-57 from the keyframes); per-frame Codex was rejected (“逐帧生成也太疯狂了，这等于完全推翻视频模型的价值了”) and instead:
“我们做一个原创的镜头：大肥鱼双手合十举过头顶，镜头从下往上。类似之前乙骨+绘画的那次”.
Frames 0-28: a 1024x1536 portrait by Codex, panned from the bottom (her chest) to the top (her pressed hands) with an ease-in-out,
travelling in the source's tilt span; frames 29-32 (the dark sphere on red) stay the source.
Usage: pan_088.py codex | render [--no-register]
"""
import pathlib
import shutil
import subprocess
import sys
import time

import numpy as np
from PIL import Image

import render_shot as runner
from codex_keyframes_0003 import CODEX
from common import PROD, ROOT, p
from title_057 import frames

UID, REV = '088', 'pan_codex_v4'
SRC = PROD / 'shots/088/ds_kf_h3_v2/source_exact_with_audio.mp4'
DIR = ROOT / 'deliverables/jujutsu/静帧'
TALL = DIR / 'pan_088_deepseek_v1.png'
DS = ROOT / 'assets/人设/鲸鱼娘.png'
PAN_END = 29  # frames 0-28 are the tilt; 29-32 the sphere
LABEL = '虎杖→DeepSeek·原创镜头：双手合十举过头顶，镜头从下往上摇（v4：v3 的简洁画风＋人物随背景从品红到紫色染色；结尾黑球保留原片；未经 H3）'
PROMPT = ('Image 1 is DeepSeek, a girl: very long wavy dark-blue hair, a white frilled maid headband, blue whale-fin ears, a navy maid '
          'dress with a white apron and white frilled cuffs. Draw ONE tall portrait image (2:3, vertical) for an anime opening: she stands '
          'facing the camera, seen from her waist up, both arms raised straight above her head with her palms pressed together in prayer '
          'high above her, her eyes closed, a calm, focused face between her raised arms, her long hair falling around her. The camera '
          'will tilt up this image from her waist to her pressed hands, so the hands are near the top edge and her waist at the bottom '
          'edge, with nothing cut off. Style: clean 2D TV-anime line art and cel shading in the style of the anime Jujutsu Kaisen; she is '
          'outlined by a thin pale green rim light; flat background that is magenta-pink at the bottom and turns deep violet toward the '
          'top. No text, no logos. Do not create or modify any other files.')


# v3, the user on v2 (screenshot of source frame 10 beside ours): “好像还是不太对。你看原版这里，颜色已经接近黑白了，然后整个画作的线条
# 也比较简单” - redrawn with two source frames as the style reference; no CPU re-lighting
TALL = DIR / 'pan_088_deepseek_v3.png'
STYLE = [DIR / 'src_088_f010.png', DIR / 'src_088_f020.png']
PROMPT += (' Images 2 and 3 are frames of the anime shot this replaces: draw in EXACTLY their style - very simple, clean line art with '
           'few lines, flat shading with almost no detail, and their nearly monochrome palette: everything, including her hair, skin and '
           'clothes, is a dull, desaturated mauve-purple close to black and white (no blue hair, no saturated colours), darker toward '
           'the top where the background turns violet; only the edges of her hands and arms carry the thin pale green rim light. Simplify '
           'her maid outfit to plain shapes (no lace patterns, no buttons, no embroidery).')


def codex():
    if TALL.exists():
        return
    args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
            '-o', str(DIR / f'codex_last_message_{TALL.stem}.txt'), '-i', str(DS), *[a for s in STYLE for a in ('-i', str(s))], '--',
            f'Use your image generation tool to create ONE image and save it in the current directory as {TALL.name}. {PROMPT}']
    t = time.time()
    subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
    print('done' if TALL.exists() else 'FAILED', TALL.name, f'{time.time() - t:.0f} s', flush=True)


def grade(tall, strength=0.8):
    """v2, the user: “大肥鱼的身体没有从下往上渐变，只有背景渐变了” - in the source the figure is lit by the same coloured light as the
    background. Each row's light colour is the painting's own background at that row (the median of its outer 80 px); every pixel is
    re-lit as that colour scaled by its own brightness, except the pale green rim light, which stays."""
    edge = np.concatenate([tall[:, :80], tall[:, -80:]], axis=1)
    light = np.median(edge, axis=1)                                   # (rows, 3)
    light = np.stack([np.convolve(np.pad(light[:, c], 40, mode='edge'), np.ones(81) / 81, mode='valid') for c in range(3)], -1)
    lum = tall @ np.array([0.299, 0.587, 0.114], np.float32)
    llum = light @ np.array([0.299, 0.587, 0.114], np.float32)
    relit = light[:, None, :] * (lum / np.maximum(llum, 1)[:, None])[..., None]
    rim = (tall[..., 1] > tall[..., 0] + 15) & (tall[..., 1] > tall[..., 2] + 5) & (tall[..., 1] > 120)
    w = np.where(rim, 0.0, strength)[..., None]
    return np.clip(tall * (1 - w) + relit * w, 0, 255)


def render():
    src = frames(SRC)
    tall = np.asarray(Image.open(TALL).convert('RGB').resize((1024, 1536), Image.LANCZOS)).astype(np.float32)
    # v4, the user on v3: “其实还是可以代码染色。现在人物的色彩其实是统一的，没有渐变效果” - v3's drawing, re-lit row by row
    tall = grade(tall, strength=0.7)
    travel = tall.shape[0] - 576
    result = []
    for f in range(len(src)):
        if f >= PAN_END:
            result.append(src[f])
            continue
        u = f / (PAN_END - 1)
        e = u * u * (3 - 2 * u)  # ease in and out, like the source's tilt (slow, fast, settling)
        top = travel * (1 - e)
        y0 = int(np.floor(top))
        w = top - y0
        y1 = min(y0 + 1, travel)
        crop = tall[y0:y0 + 576] * (1 - w) + tall[y1:y1 + 576] * w
        result.append(np.clip(crop, 0, 255).astype(np.uint8))
    out = PROD / 'shots' / UID / REV
    out.mkdir(parents=True, exist_ok=True)
    full = out / 'source_exact_with_audio.mp4'
    if not full.exists():
        shutil.copy2(SRC, full)
    silent = out / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                           '-i', '-', '-frames:v', str(len(result)), '-c:v', 'libx264', '-crf', '12', '-pix_fmt', 'yuv420p', str(silent)],
                          input=np.stack(result).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = out / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', clip])
    runner.configure(out)
    check = runner.batch.validate_output(clip, len(result), True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    me = pathlib.Path(__file__).resolve()
    record = out / 'title_compositing.json'
    p.write_json(record, dict(kind='cpu_text', builder=str(me), builder_sha256=p.sha(me), painting=str(TALL), recipe_text=(
        '原创镜头：Codex 画竖幅图（DeepSeek 双手合十举过头顶，品红到紫色背景、淡绿轮廓光），第 0–28 帧从腰部缓入缓出地向上摇到合十的'
        '双手；第 29–32 帧（红底黑球）保留原片。原片原音。未经 H3。\nCodex 提示词：' + PROMPT)))
    p.write_json(out / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, visual_review='pending_user'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if '--no-register' not in sys.argv and not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    print('READY', clip, flush=True)


if __name__ == '__main__':
    {'codex': codex, 'render': render}[sys.argv[1]]()
