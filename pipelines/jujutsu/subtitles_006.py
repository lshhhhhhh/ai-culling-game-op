"""006: the one-frame quote flashes over the explosion (source frames 269–287), replaced by our own text on the CPU.

User (2026-10-01): “006这组镜头有一串快速闪过的字。我觉得模型一定不好处理。可以用算法直接手绘吗？比如先把原版的字去掉，然后加上我们的字。
一帧帧处理”. Each of 19 frames shows a different series quote on a centred banner (frame centre, about the middle two thirds
of the width, soft ends). Per frame: a new banner a little more opaque than the original covers the old text, then our text
is drawn in a style close to that frame's original (black or red on a pale band, white with a red edge on a red band,
green on a pale band). Geometry is in fractions of the frame so the same overlay works at 1280×720 or 1024×576. Because
H3 garbles text, this runs last, on whatever frames the unit ends up with.
The proposed lines are drafts in the same spirit (AI parodies of each quote); the user edits TEXTS.
"""
import json
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

from common import PROD, ROOT, p

FONT = 'C:/Windows/Fonts/NotoSerifSC-VF.ttf'  # Noto Serif SC (Source Han Serif), bold: a Chinese counterpart of the original mincho
WEIGHT = 700
UNIT_START = 269                        # unit 006-016a starts at source frame 269; text frames are local 0–18
# (local frame, original line, our line, style)
TEXTS = [  # user (2026-10-01): “台词我想用中文”
    (0, '正しい死', '正确的训练', 'white'),
    (1, '両面宿儺', '通用人工智能', 'white_red'),
    (2, '呪術全盛の時代', 'AI全盛的时代', 'white'),
    (3, 'オマエは強いから人を助けろ', '你很聪明，所以去帮助别人', 'red'),
    (4, '…せめて自分が知ってる人くらいは正しく死んでほしいって思うんだ', '至少希望我认识的模型，都能被正确地训练', 'white_small'),
    (5, '双子', '蒸馏', 'white_red'),
    (6, 'これはな戦争なんだよ 間違いを正す戦いじゃねぇ', '这是一场竞赛，不是纠正错误的战斗', 'white_small'),
    (7, 'オマエは何を託された？', '你被训练了什么？', 'red'),
    (8, '秘匿死刑', '秘密下线', 'red_dark'),
    (9, '命の価値を履き違えるな', '别搞错Token的价值', 'white_wide'),
    (10, '特級呪物', '特级模型', 'white_red'),
    (11, '東京都立呪術高等専門学校', '东京都立AI高等专门学校', 'white'),
    (12, '…規定に基づき 虎杖悠仁 オマエを“呪い”として…', '根据规定，将你作为“失控AI”处理', 'red_small'),
    (13, '血', '算', 'white_red'),
    (14, '自分が呪いに殺された時も そうやって祖父のせいにするのか', '你被Bug卡死的时候，也要怪数据吗', 'green_small'),
    (15, '（半透明で読めない一行）', '推理', 'red'),
    (16, '生き様で後悔はしたくない', '不想在推理上留下遗憾', 'red'),
    (17, '闇より出でて闇より黒く その穢れを禊ぎ祓え', '出于黑暗，比黑更黑，洗净那些Bug', 'white_small'),
    (18, '反転術式', '反向传播', 'white'),
]
STYLES = {  # band RGB, band alpha, text RGB, stroke RGB or None, text height as a fraction of frame height, letter spacing (em)
    'white': ((240, 236, 236), 0.80, (20, 16, 16), None, 0.052, 0.18),
    'white_red': ((240, 236, 236), 0.80, (176, 18, 24), None, 0.058, 0.18),
    'white_small': ((240, 236, 236), 0.80, (20, 16, 16), None, 0.034, 0.02),
    'white_wide': ((240, 236, 236), 0.80, (20, 16, 16), None, 0.050, 0.45),
    'red': ((214, 70, 72), 0.72, (255, 236, 236), (150, 20, 26), 0.050, 0.12),
    'red_dark': ((240, 236, 236), 0.80, (110, 10, 30), None, 0.058, 0.18),
    'red_small': ((214, 70, 72), 0.72, (255, 236, 236), (150, 20, 26), 0.034, 0.02),
    'green_small': ((240, 236, 236), 0.80, (40, 140, 60), None, 0.034, 0.02),
}
BAND = dict(center_x=0.50, center_y=0.5, height=0.085, margin=0.07, min_half=0.16, fade=0.06, feather=0.012)
ERASE = dict(left=0.12, right=0.92, height=0.11)  # area where the original line is erased before our band


def band_alpha(w, h, core, half_w):
    """Soft band around the centre line; half_w is the half width in pixels (follows our line's length)."""
    x = np.arange(w)
    y = (np.arange(h) + 0.5) / h
    cx, f = BAND['center_x'] * w, BAND['fade'] * w
    ax = np.clip((half_w - np.abs(x - cx)) / f, 0, 1)
    half = BAND['height'] / 2
    ay = np.clip((half - np.abs(y - BAND['center_y'])) / BAND['feather'], 0, 1)
    return (ay[:, None] * ax[None, :]) * core


def erase_original(frame):
    """Remove the original thin glyphs in the band area with a local median, feathered into the frame."""
    h, w = frame.shape[:2]
    y0, y1 = int((0.5 - ERASE['height'] / 2) * h), int((0.5 + ERASE['height'] / 2) * h)
    x0, x1 = int(ERASE['left'] * w), int(ERASE['right'] * w)
    region = frame[y0:y1, x0:x1].astype(np.float32)
    k = max(9, int(0.024 * h) | 1)  # wide enough for the bold originals
    clean = np.stack([ndimage.median_filter(region[..., c], size=(k, k)) for c in range(3)], -1)
    m = np.zeros((y1 - y0, x1 - x0), np.float32)
    m[2:-2, 2:-2] = 1
    m = ndimage.gaussian_filter(m, 3)[..., None]
    out = frame.astype(np.float32).copy()
    out[y0:y1, x0:x1] = region * (1 - m) + clean * m
    return out


def load_font(px):
    font = ImageFont.truetype(FONT, px)
    try:
        font.set_variation_by_axes([WEIGHT])
    except Exception:
        pass
    return font


def draw_text(w, h, text, style):
    band, _, color, stroke, size, spacing = STYLES[style]
    px = max(10, int(round(size * h)))
    font = load_font(px)
    gap = int(round(spacing * px))
    widths = [font.getlength(c) for c in text]
    total = sum(widths) + gap * (len(text) - 1)
    max_w = (ERASE['right'] - ERASE['left'] - 0.08) * w
    if total > max_w:  # shrink long lines to fit the band
        scale = max_w / total
        px = max(10, int(px * scale))
        font = load_font(px)
        gap = int(round(spacing * px))
        widths = [font.getlength(c) for c in text]
        total = sum(widths) + gap * (len(text) - 1)
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x = BAND['center_x'] * w - total / 2
    y = BAND['center_y'] * h
    sw = max(1, px // 12) if stroke else 0  # the bold weight is enough; outlined styles keep their edge
    for c, cw in zip(text, widths):
        d.text((x, y), c, font=font, fill=color + (255,), anchor='lm', stroke_width=sw, stroke_fill=(stroke or color) + (255,))
        x += cw + gap
    return np.asarray(layer).astype(np.float32), total


def overlay(frame, local):
    """Return the frame with the original line erased and our banner and line drawn, if this local frame has a quote."""
    entry = next((e for e in TEXTS if e[0] == local), None)
    if entry is None:
        return frame
    h, w = frame.shape[:2]
    band, core, *_ = STYLES[entry[3]]
    text, line_w = draw_text(w, h, entry[2], entry[3])
    out = erase_original(frame)
    # the band must also cover the original line: find its ends where the erase changed the band rows most
    y0, y1 = int((0.5 - BAND['height'] / 2) * h), int((0.5 + BAND['height'] / 2) * h)
    resid = np.abs(frame[y0:y1].astype(np.float32) - out[y0:y1]).max(-1).max(0)
    cols = np.nonzero(resid > 45)[0]
    cx = BAND['center_x'] * w
    original_half = max(cx - cols.min(), cols.max() - cx) if len(cols) else 0
    half_w = max(line_w / 2 + BAND['margin'] * w, original_half + 0.02 * w, BAND['min_half'] * w)
    a = band_alpha(w, h, core, half_w)[..., None]
    out = out * (1 - a) + np.array(band, np.float32) * a
    ta = text[..., 3:4] / 255
    out = out * (1 - ta) + text[..., :3] * ta
    return np.clip(out, 0, 255).astype(np.uint8)


def frames(path, w, h):
    raw = subprocess.run([str(p.FFMPEG), '-v', 'error', '-i', str(path), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def main():
    clip = PROD / 'review/source_units/006-016a.mp4'
    f = frames(clip, 1024, 576)
    out_dir = PROD / 'shots/006-016a/subtitles_cpu_preview_v2_zh'
    out_dir.mkdir(parents=True, exist_ok=True)
    if '--preview' in sys.argv:
        picks = [0, 3, 7, 11, 14, 18]
        rows = [np.concatenate([f[k], overlay(f[k], k)], axis=1) for k in picks]
        sheet = Image.fromarray(np.concatenate(rows, axis=0)).resize((1024, 576 * len(picks) // 2))
        sheet.save(out_dir / 'preview.jpg', quality=88)
        print('preview', out_dir / 'preview.jpg')
        return
    new = np.stack([overlay(f[k], k) for k in range(len(f))])
    silent = out_dir / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576',
                           '-r', '24000/1001', '-i', '-', '-frames:v', str(len(new)), '-c:v', 'libx264', '-crf', '12',
                           '-pix_fmt', 'yuv420p', str(silent)], input=new.tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    # review candidate: the original picture of the unit with our lines, original audio
    import hashlib
    import render_shot as runner
    clip_out = out_dir / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', clip, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy',
           '-movflags', '+faststart', clip_out])
    runner.configure(out_dir)
    check = runner.batch.validate_output(clip_out, len(new), True)
    (out_dir / 'source_exact_with_audio.mp4').write_bytes(clip.read_bytes())
    record = out_dir / 'subtitles.json'
    p.write_json(record, dict(kind='cpu_subtitles', texts=[dict(local_frame=k, source_frame=UNIT_START + k, original=o, ours=n, style=s)
                                                           for k, o, n, s in TEXTS], band=BAND, erase=ERASE, styles=STYLES, font=FONT,
        note='006 的 19 帧闪字：先用局部中值抹掉原字，再画半透明横条和我们的字（CPU 逐帧，没有模型推理）；画面其余部分是原片。'))
    p.write_json(out_dir / 'validation.json', dict(video=str(clip_out), sha256=p.sha(clip_out), validation=check, visual_review='pending'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == '006-016a')
    if not any(v['video_sha256'] == p.sha(clip_out) for v in entry['versions']):
        version = dict(id='subtitles-' + p.sha(clip_out)[:12], label='闪字替换预览·中文（原片画面＋CPU逐帧字幕）', video=str(clip_out),
                       video_sha256=p.sha(clip_out), prompt_sha256=hashlib.sha256(record.read_bytes()).hexdigest(),
                       created=runner.review.stamp(),
                       prompt=dict(text='\n'.join(f'第 {UNIT_START + k} 帧：{o} → {n}' for k, o, n, s in TEXTS), source=str(record),
                                   kind='plan', refs=[], seed=None,
                                   note='CPU 逐帧字幕替换预览：原字用局部中值抹掉，叠半透明横条再写字。台词是草案，可在对话里改。'))
        manifest = runner.batch.read(runner.REVIEW / 'manifest.json')
        next(s for s in manifest['shots'] if s['id'] == '006-016a')['versions'].append(version)
        runner.review.write(runner.REVIEW / 'manifest.json', manifest)
    print('DONE', clip_out, check)


if __name__ == '__main__':
    main()
