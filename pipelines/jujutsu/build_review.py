"""JJK S3 (Culling Game part 1) OP planning page (CPU only): per-shot analysis on the shared review tool, nothing is generated.

Each inventory shot gets a 1024x576 preview with the original audio and one "镜头分析·计划" version whose
text is the shot analysis (characters, action, difficulty, suggested unit, casting). The analysis comes from
source_inventory/shot_analysis_draft.json (written from the strip sheets); the user approves or annotates each shot:
    pipelines/jujutsu/start_review.ps1   (review_school_op.py --serve --project assets/jujutsu/op1_v1 --port 8769)
"""
import hashlib
import json

from common import FPS, PROD, REVIEW, p
import review_school_op as review

# Casting not decided yet (2026-10-01); the page only carries the shot analysis and suggested units.
CAST = {}


def analysis(s, a):
    lines = ['【原版人物】' + ('、'.join(a['chars']) if a['chars'] else '无人物'), '【画面】' + a['what']]
    if a['hard']:
        lines.append('【难点】' + a['hard'])
    lines.append(f"【亮度】平均亮度 {s['mean_luma']:.0f}" + ('（暗场）' if s['mean_luma'] < 45 else ''))
    lines.append('【建议合并】' + a['unit'])
    names = [c for c in CAST if any(c in x for x in a['chars'])]
    if names:
        lines.append('【替换计划】' + '；'.join(f'{c} → {CAST[c]}' for c in names))
    if a['note']:
        lines.append('【备注】' + a['note'])
    return '\n'.join(lines)


def main():
    inv = json.loads((PROD / 'source_inventory/inventory.json').read_text(encoding='utf-8'))
    shots_analysis = json.loads((PROD / 'source_inventory/shot_analysis_draft.json').read_text(encoding='utf-8'))['shots']
    assert [s['id'] for s in inv['shots']] == sorted(shots_analysis), 'analysis must cover every inventory shot'
    src = inv['source']
    (REVIEW / 'source').mkdir(parents=True, exist_ok=True)
    previous = json.loads((REVIEW / 'manifest.json').read_text(encoding='utf-8-sig')) if (REVIEW / 'manifest.json').exists() else {'shots': []}
    previous_units = {e['id']: e for e in previous['shots']}
    shots = []
    for s in inv['shots']:
        a = shots_analysis[s['id']]
        clip = REVIEW / 'source' / f"{s['id']}.mp4"
        if not clip.exists():
            # exact frame interval of the inventory, original audio for the same interval
            p.run([p.FFMPEG, '-v', 'error', '-y', '-threads', '2', '-i', src, '-map', '0:v:0', '-map', '0:a:0',
                   '-vf', f"trim=start_frame={s['start']}:end_frame={s['end']},setpts=PTS-STARTPTS,scale=1024:576:flags=lanczos,setsar=1,format=yuv420p",
                   '-af', f"atrim=start={s['start'] / FPS:.9f}:end={s['end'] / FPS:.9f},asetpts=PTS-STARTPTS",
                   '-r', '24000/1001', '-c:v', 'libx264', '-threads', '2', '-preset', 'veryfast', '-crf', '18',
                   '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', clip])
        info = p.video_info(clip)
        assert info['frames'] == s['frames'], (s['id'], info)
        text = analysis(s, a)
        entry = dict(id=s['id'], start=s['start_seconds'], end=s['end_seconds'], frames=s['frames'], cast=a['chars'],
                     credits=[], description=a['what'], source_video=str(clip), source_exact_video=str(clip),
                     planned_prompt=text,
                     versions=[dict(id='plan-v1', label='镜头分析·计划', video=str(clip), video_sha256=p.sha(clip),
                                    prompt_sha256=hashlib.sha256(text.encode()).hexdigest(), created=review.stamp(),
                                    prompt=dict(text=text, source=None, kind='plan', refs=[], seed=None,
                                                note='还没有生成。这里是镜头分析和替换计划：内容对就点“通过”，不对就写下修改意见。'))])
        entry['versions'] += [v for v in previous_units.get(s['id'], {}).get('versions', []) if v['id'] != 'plan-v1']
        shots.append(entry)
    assert sum(s['frames'] for s in shots) == inv['total_frames']
    manifest = dict(title='咒术回战 S3 死灭回游 OP · AI版（技术探索）', subtitle='镜头分析第一版：人物识别（“疑似”为不确定）、画面、难点、建议合并。请确认或写下修改意见；选角未定。',
                    source=src, fps='24000/1001', total_frames=inv['total_frames'], shots=shots, updated=review.stamp())
    review.write(REVIEW / 'manifest.json', manifest)
    if not (REVIEW / 'review_state.json').exists():
        review.write(REVIEW / 'review_state.json', dict(schema=1, revision=0, decisions={}, history=[]))
    print(len(shots), 'review units on the planning page', flush=True)


if __name__ == '__main__':
    main()
