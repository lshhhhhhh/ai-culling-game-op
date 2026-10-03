"""Per-shot frame strips of the Jujutsu Kaisen S3 OP for the shot analysis (CPU only).

Each shot gets 3 frames (<= 12 frames), 4 frames, or 6 frames (> 80 frames), evenly spread from its first to its
last frame; 8 shots per sheet, labelled with id, start frame, length and mean luma.
"""
import json
import subprocess

from PIL import Image, ImageDraw, ImageFont

from common import INVENTORY as INV, p
TW, TH, PER = 240, 135, 8


def picks(s):
    a, n = s['start'], s['frames']
    k = 3 if n <= 12 else 6 if n > 80 else 4
    return [a + round(i * (n - 1) / (k - 1)) for i in range(k)]


def main():
    inv = json.loads((INV / 'inventory.json').read_text(encoding='utf-8'))
    shots = inv['shots']
    frames = sorted({f for s in shots for f in picks(s)})
    out = INV / 'strips'
    out.mkdir(exist_ok=True)
    select = '+'.join(f'eq(n\\,{f})' for f in frames)
    subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-i', inv['source'], '-vf', f'select={select},scale={TW}:{TH}',
                    '-fps_mode', 'vfr', '-q:v', '4', str(out / 'f_%04d.jpg')], check=True)
    index = {f: i + 1 for i, f in enumerate(frames)}
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 15)
    for page in range((len(shots) + PER - 1) // PER):
        group = shots[page * PER:(page + 1) * PER]
        sheet = Image.new('RGB', (TW * 6 + 150, len(group) * (TH + 4)), '#181818')
        draw = ImageDraw.Draw(sheet)
        for r, s in enumerate(group):
            y = r * (TH + 4)
            draw.text((6, y + 8), s['id'], font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 26), fill='white')
            draw.text((6, y + 44), f"{s['start']}+{s['frames']}f", font=font, fill='#cccccc')
            draw.text((6, y + 66), f"L{s['mean_luma']:.0f}", font=font, fill='#ffd84a' if s['mean_luma'] < 45 else '#cccccc')
            for c, f in enumerate(picks(s)):
                sheet.paste(Image.open(out / f'f_{index[f]:04d}.jpg'), (150 + c * TW, y))
                draw.text((150 + c * TW + 4, y + 2), str(f - s['start']), font=font, fill='yellow')
        sheet.save(INV / f'strip_sheet_{page + 1:02d}.jpg', quality=85)
    print(len(shots), 'shots,', (len(shots) + PER - 1) // PER, 'strip sheets', flush=True)


if __name__ == '__main__':
    main()
