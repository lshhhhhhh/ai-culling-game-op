"""CPU-only shot inventory of the Jujutsu Kaisen S3 (Culling Game part 1) NCOP: cuts, per-shot brightness, contact sheets.

Cut detection as in the Makeine plan (ffmpeg scene score >= 0.20) but cuts may be 2 frames apart. Brightness is the
mean luma of each shot, because dark shots are where H3 editing is weakest. Output: source_inventory/inventory.json
and shot_sheet_NN.jpg (one mid-shot thumbnail per shot) for planning; nothing is generated.
"""
import json
import re
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from common import FPS, INVENTORY, SOURCE, p

THRESHOLD, MIN_GAP = 0.20, 2  # this OP has 1-2 frame flash cuts; false cuts in fights are merged later
COLS, ROWS, TW, TH = 5, 6, 384, 216


def main():
    inventory = INVENTORY
    inventory.mkdir(parents=True, exist_ok=True)
    probe = json.loads(p.run([p.FFPROBE, '-v', 'error', '-select_streams', 'v:0', '-count_frames', '-show_entries',
                              'stream=nb_read_frames', '-of', 'json', SOURCE]).stdout)['streams'][0]
    total = int(probe['nb_read_frames'])
    scores_path = inventory / 'scene_scores.txt'
    if not scores_path.exists():
        proc = p.run([p.FFMPEG, '-hide_banner', '-i', SOURCE, '-vf',
                      'scale=480:270,select=gte(scene\\,0),metadata=print', '-an', '-f', 'null', '-'])
        scores_path.write_text(proc.stderr, encoding='utf-8')
    pairs = re.findall(r'pts_time:([0-9.]+).*?lavfi.scene_score=([0-9.]+)', scores_path.read_text(encoding='utf-8'), re.S)
    scores = {round(float(t) * FPS): float(s) for t, s in pairs}
    selected = []
    for frame in sorted((f for f, s in scores.items() if 0 < f < total - 4 and s >= THRESHOLD), key=lambda f: -scores[f]):
        if all(abs(frame - other) >= MIN_GAP for other in selected):
            selected.append(frame)
    cuts = sorted(set([0] + selected + [total]))
    # mean luma per frame from a small grey decode
    raw = subprocess.run([str(p.FFMPEG), '-v', 'error', '-i', str(SOURCE), '-an', '-vf', 'scale=96:54', '-f', 'rawvideo',
                          '-pix_fmt', 'gray', '-'], capture_output=True, check=True).stdout
    luma = np.frombuffer(raw, np.uint8).reshape(-1, 54, 96).mean(axis=(1, 2))
    shots = []
    for i, (a, b) in enumerate(zip(cuts, cuts[1:]), 1):
        shots.append(dict(id=f'{i:03d}', start=a, end=b, frames=b - a, start_seconds=round(a / FPS, 3),
                          end_seconds=round(b / FPS, 3), representative_frame=(a + b - 1) // 2,
                          cut_score=round(scores.get(a, 0.0), 3), mean_luma=round(float(luma[a:b].mean()), 1)))
    p.write_json(inventory / 'inventory.json', dict(source=str(SOURCE), total_frames=total, fps='24000/1001',
                                                     threshold=THRESHOLD, min_gap=MIN_GAP, shots=shots))
    select = '+'.join(f'eq(n\\,{s["representative_frame"]})' for s in shots)
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', SOURCE, '-vf', f'select={select},scale={TW}:{TH}', '-fps_mode', 'vfr',
           '-q:v', '3', inventory / 'thumb_%03d.jpg'])
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 17)
    per = COLS * ROWS
    for page in range((len(shots) + per - 1) // per):
        sheet = Image.new('RGB', (COLS * TW, ROWS * (TH + 24)), '#202020')
        draw = ImageDraw.Draw(sheet)
        for k, shot in enumerate(shots[page * per:(page + 1) * per]):
            x, y = (k % COLS) * TW, (k // COLS) * (TH + 24)
            sheet.paste(Image.open(inventory / f'thumb_{page * per + k + 1:03d}.jpg'), (x, y))
            draw.text((x + 4, y + TH + 2), f"{shot['id']}  {shot['start']}+{shot['frames']}f  L{shot['mean_luma']:.0f}",
                      font=font, fill='#ffd84a' if shot['mean_luma'] < 45 else 'white')
        sheet.save(inventory / f'shot_sheet_{page + 1:02d}.jpg', quality=88)
    dark = sum(1 for s in shots if s['mean_luma'] < 45)
    print(len(shots), 'shots,', total, 'frames;', dark, 'dark (mean luma < 45);',
          'shortest', min(s['frames'] for s in shots), 'frames', flush=True)


if __name__ == '__main__':
    main()
