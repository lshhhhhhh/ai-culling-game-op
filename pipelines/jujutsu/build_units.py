"""JJK S3 OP review units: merge the 146 detector shots into real shots (CPU only, no generation).

User (2026-10-01): “你可以先镜头合并吗？比如002-004明显是一个镜头”. The detector (2-frame minimum gap) splits continuous actions at
impact/smear frames. A boundary is merged when the frames on both sides are the same shot (high correlation/histogram
similarity across the cut, confirmed on the strip sheets); real hard cuts stay, even very short ones (e.g. the seven
characters of 043–049). Three real cuts sit inside detector shots and were read from frame differences: 331 (inside 016:
Yuta's drift → the slash close-up), 393 (inside 026: the punch flash → the dojo), 1680 (inside 111: Kirara → Hakari).
Units are exact source intervals; members are the detector shots they overlap. review_state.json is not touched.
"""
import datetime as dt
import hashlib
import json
import shutil

from common import FPS, PROD, REVIEW, p
import review_school_op as review
from build_review import analysis

# merged units: (unit id, start, end, reason). Every other detector shot stays a unit of its own.
MERGED = [
    ('002-004', 238, 252, '同一只手托住小球的连续动作，检测在冲击帧处切开。'),
    ('006-016a', 269, 331, '俯视城市爆炸，镜头推进到爆炸里，乙骨在火光中下坠、翻身、举刀，一个连续镜头（大量2帧残影切）；第 331 帧切到背后近景。'),
    ('016b-019', 331, 349, '斩击：背后近景、刀光与速度线、冲出，快速连续，合并。'),
    ('020-026a', 349, 393, '镜头从楼墙摇到俯瞰城市，虎杖坠落、推到面部、连续出拳，一个镜头（2帧冲击切）；第 393 帧切进道场。'),
    ('026b-029', 393, 433, '道场格斗，从第 393 帧开始，一个镜头。'),
    ('030-031', 433, 438, '伏黑惠面部特写，轻微推近，一个镜头。'),
    ('032-034', 438, 472, '伏黑惠从楼顶迈出坠下街道，蓝色光线铺满，镜头连续。'),
    ('037-038', 528, 557, '熊猫趴在花草地上→抬头，一个镜头。'),
    ('065-067', 1094, 1116, '真希站姿，镜头连续上摇（064 只拍腿，是前一个镜头）。'),
    ('077-080', 1297, 1316, '油画尖叫，同一画面的推近与抖动（2帧切）。'),
    ('095-097', 1541, 1548, '青绿光中披风人物转身（2帧切），一个镜头。'),
    ('109-111a', 1658, 1680, '星空中的绮罗罗，近景到全身拉远，一个镜头；第 1680 帧切到秤。'),
    ('111b-114', 1680, 1690, '秤与蓝色火焰，开头一帧放射状闪光，一个镜头。'),
    ('118-120', 1727, 1748, '同一张拼贴画逐步贴上新元素、最后变色，一个镜头。'),
    ('121-122', 1748, 1765, '飞机头男人的拼贴，贴纸遮眼，一个镜头。'),
    ('124-125', 1785, 1807, '黑袍人物正面，随后背景出现拼贴色块，一个镜头。'),
    ('136-138', 2014, 2034, '两人勾肩大笑，推近，一个镜头（2帧切）。'),
]


def units(inv):
    shots = inv['shots']
    out, at = [], 0
    merged = {m[1]: m for m in MERGED}
    while at < inv['total_frames']:
        if at in merged:
            uid, a, b, reason = merged[at]
        else:
            s = next(x for x in shots if x['start'] == at)
            uid, a, b, reason = s['id'], s['start'], s['end'], '单独一个镜头。'
        members = [s['id'] for s in shots if s['start'] < b and s['end'] > a]
        out.append((uid, a, b, members, reason))
        at = b
    return out


def original_shots():
    """The 146 per-shot entries (with their plan versions) from the last manifest before units existed."""
    for path in sorted((REVIEW / 'backups').glob('before_units_*/manifest.json')):
        shots = json.loads(path.read_text(encoding='utf-8'))['shots']
        if len(shots) == 146 and shots[0]['id'] == '001' and shots[-1]['id'] == '146':
            return {e['id']: e for e in shots}
    raise RuntimeError('no 146-shot manifest backup found')


def main():
    inv = json.loads((PROD / 'source_inventory/inventory.json').read_text(encoding='utf-8'))
    shots = {s['id']: s for s in inv['shots']}
    drafts = json.loads((PROD / 'source_inventory/shot_analysis_draft.json').read_text(encoding='utf-8'))['shots']
    state = json.loads((REVIEW / 'review_state.json').read_text(encoding='utf-8'))
    notes = {k.split('/')[0]: v.get('note', '') for k, v in state['decisions'].items() if v.get('note')}
    plan = units(inv)
    assert plan[0][1] == 0 and plan[-1][2] == inv['total_frames'] and all(a[2] == b[1] for a, b in zip(plan, plan[1:]))
    backup = REVIEW / 'backups' / ('before_units_' + dt.datetime.now().strftime('%Y%m%d_%H%M%S'))
    backup.mkdir(parents=True)
    for name in ('manifest.json', 'review_state.json'):
        shutil.copy2(REVIEW / name, backup / name)
    old = {e['id']: e for e in json.loads((REVIEW / 'manifest.json').read_text(encoding='utf-8'))['shots']}
    originals = original_shots()
    out_dir = REVIEW / 'source_units'
    out_dir.mkdir(exist_ok=True)
    entries = []
    for uid, start, end, members, reason in plan:
        clip = out_dir / f'{uid}.mp4'
        if not clip.exists():
            p.run([p.FFMPEG, '-v', 'error', '-y', '-threads', '2', '-i', inv['source'], '-map', '0:v:0', '-map', '0:a:0',
                   '-vf', f'trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS,scale=1024:576:flags=lanczos,setsar=1,format=yuv420p',
                   '-af', f'atrim=start={start / FPS:.9f}:end={end / FPS:.9f},asetpts=PTS-STARTPTS',
                   '-r', '24000/1001', '-c:v', 'libx264', '-threads', '2', '-preset', 'veryfast', '-crf', '18',
                   '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', clip])
        assert p.video_info(clip)['frames'] == end - start, uid
        parts, seen = [], set()
        for m in members:
            s = shots[m]
            text = analysis(s, drafts[m])
            text = '\n'.join(l for l in text.splitlines() if not l.startswith('【建议合并】'))
            key = drafts[m]['what']
            a, b = max(s['start'], start), min(s['end'], end)
            portion = '' if (a, b) == (s['start'], s['end']) else f'（本单元只含第 {a}–{b - 1} 帧）'
            if key in seen and not portion:
                parts.append(f'——{m}——（同上）')
            else:
                parts.append(f'——{m}{portion}——\n' + text)
            seen.add(key)
            if notes.get(m):
                parts[-1] += '\n【用户意见】' + notes[m]
        header = f'【生成单元】{uid}（原片第 {start}–{end - 1} 帧，共 {end - start} 帧）\n【合并理由】{reason}'
        text = header + '\n\n' + '\n\n'.join(parts)
        cast = list(dict.fromkeys(c for m in members for c in drafts[m]['chars']))
        version = dict(id='plan-unit-v1', label='合并原片·镜头分析' if len(members) > 1 else '镜头分析·计划',
                       video=str(clip), video_sha256=p.sha(clip), prompt_sha256=hashlib.sha256(text.encode()).hexdigest(),
                       created=review.stamp(),
                       prompt=dict(text=text, source=None, kind='plan', refs=[], seed=None,
                                   note='还没有生成。合并对就点“通过”，不对（该拆开、该并上、切点不准）就写下修改意见。'))
        entry = dict(id=uid, start=start / FPS, end=end / FPS, frames=end - start, cast=cast, credits=[],
                     description=' / '.join(dict.fromkeys(drafts[m]['what'] for m in members)),
                     source_video=str(clip), source_exact_video=str(clip), planned_prompt=text,
                     versions=[version] + [v for v in old.get(uid, {}).get('versions', []) if not v['id'].startswith('plan')],
                     raw_start_frame=start, raw_end_frame=end)
        if len(members) > 1 or (start, end) != (shots[members[0]]['start'], shots[members[0]]['end']):
            entry.update(merged_from=members, members=[originals[m] for m in members], preserve_internal_cuts=False)
        entries.append(entry)
    assert sum(e['frames'] for e in entries) == inv['total_frames']
    manifest = json.loads((REVIEW / 'manifest.json').read_text(encoding='utf-8'))
    manifest.update(shots=entries, updated=review.stamp(),
                    subtitle=f'镜头合并第一版：146 个检测镜头 → {len(entries)} 个单元（只合并被冲击帧/残影误切开的连续动作，真正的硬切保留）。请检查合并是否正确；选角未定。')
    review.write(REVIEW / 'manifest.json', manifest)
    p.write_json(PROD / 'unit_plan.json', dict(schema=1, created=review.stamp(), total_frames=inv['total_frames'],
        units=[dict(id=u, start_frame=a, end_frame=b, members=m, reason=r) for u, a, b, m, r in plan],
        backup=str(backup), note='用户在对话中要求“你可以先镜头合并吗？比如002-004明显是一个镜头”，2026-10-01。'))
    print(len(entries), 'units;', sum(len(e.get('merged_from', [])) > 1 for e in entries), 'merged; backup', backup)


if __name__ == '__main__':
    main()
