"""Splice a range of JJK units into one preview with the source soundtrack, to judge continuity.

User (2026-10-01): “先把001到034拼接一下。我看看连续效果”. Per unit: the latest version the user approved on the review page; if none,
the newest generated version (listed as unapproved); if none, the exact source. Video concatenated and encoded once, audio cut from
the source over the whole span and encoded once (as Lycoris assemble_final_v1). CPU only.
Usage: preview_splice.py FIRST_UNIT LAST_UNIT
"""
import sys

from common import FPS, PROD, REVIEW, ROOT, p
import render_shot as runner

B = runner.batch
OUT = ROOT / 'deliverables/jujutsu/preview'


def source_clip(uid, a, b, work):
    out = work / f'{uid}_source_exact.mp4'
    if not out.exists():
        inv = B.read(PROD / 'source_inventory/inventory.json')
        p.run([p.FFMPEG, '-v', 'error', '-y', '-i', inv['source'], '-map', '0:v:0', '-an',
               '-vf', f'trim=start_frame={a}:end_frame={b},setpts=N*1001/(24000*TB),scale=1024:576:flags=lanczos,setsar=1,format=yuv420p',
               '-r', '24000/1001', '-c:v', 'libx264', '-crf', '12', out])
    return out


def choose(unit, decisions):
    uid = unit['id']
    versions = {v['id']: v for v in unit['versions']}
    approved = sorted((d.get('updated', ''), key.split('/', 1)[1]) for key, d in decisions.items()
                      if key.split('/', 1)[0] == uid and isinstance(d, dict) and d.get('status') == 'approved' and key.split('/', 1)[1] in versions)
    if approved:
        return versions[approved[-1][1]], '已通过'
    made = [v for v in unit['versions'] if not v['id'].startswith('plan')]
    if made:
        return made[-1], '未通过（最新候选）'
    return None, '原片（还没有候选）'


def main(first, last):
    manifest = B.read(REVIEW / 'manifest.json')
    decisions = B.read(REVIEW / 'review_state.json')['decisions']
    plan = {u['id']: u for u in B.read(PROD / 'unit_plan.json')['units']}
    ids = [u['id'] for u in manifest['shots']]
    units = manifest['shots'][ids.index(first):ids.index(last) + 1]
    work = PROD / 'preview' / f'{first}-{last}'
    work.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    runner.configure(work)
    items, expected = [], int(plan[first]['start_frame'])
    for unit in units:
        uid = unit['id']
        a, b = int(plan[uid]['start_frame']), int(plan[uid]['end_frame'])
        assert a == expected, (uid, a, expected)
        expected = b
        version, status = choose(unit, decisions)
        video = version['video'] if version else str(source_clip(uid, a, b, work))
        B.validate_output(video, b - a, version is not None)
        items.append(dict(unit=uid, frames=b - a, status=status, label=version['label'] if version else '原片', video=video))
    start, end = int(plan[first]['start_frame']), expected
    concat = work / 'concat.txt'
    concat.write_text('\n'.join("file '" + str(x['video']).replace('\\', '/').replace("'", "'\\''") + "'" for x in items), encoding='utf-8')
    silent = work / 'silent.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', concat, '-map', '0:v:0', '-an',
           '-vf', 'setpts=N*1001/(24000*TB)', '-c:v', 'libx264', '-threads', '4', '-crf', '16', '-r', '24000/1001',
           '-frames:v', end - start, '-pix_fmt', 'yuv420p', silent])
    audio = work / 'source_audio.m4a'
    inv = B.read(PROD / 'source_inventory/inventory.json')
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', inv['source'], '-map', '0:a:0', '-vn',
           '-af', f'atrim=start={start / FPS:.9f}:end={end / FPS:.9f},asetpts=PTS-STARTPTS', '-c:a', 'aac', '-b:a', '192k', audio])
    final = OUT / f'JJK_preview_{first}-{last}.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', audio, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', final])
    check = B.validate_output(final, end - start, True)
    at = 0
    for x in items:
        x['start_seconds'] = round(at / FPS, 2)
        at += x['frames']
    p.write_json(OUT / f'JJK_preview_{first}-{last}.json', dict(video=str(final), frames=end - start, source_interval=[start, end],
                                                                 parts=items, validation=check))
    print('DONE', final, end - start, 'frames')
    for x in items:
        print(f"{x['start_seconds']:6.2f}s  {x['unit']:9s} {x['status']:12s} {x['label'][:50]}")


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
