"""JJK S3 OP parody final cut v1: each unit's latest user-approved version, the source's own soundtrack over the whole timeline.

User (2026-10-02): “不太完美，但是就这样吧。把全片都剪起来吧，都通过了” (after 134's last fix).
Per unit: the latest approved decision in review_state.json (as pipelines/lycoris/assemble_final_v1.py). 142 is approved on an older
version on purpose (the newer H3 run turned back into Takaba). 146 (21 frames of pure black, the source's ending) never had a version:
it is cut from the source, so the timeline is the source's full [0, 2160) and the audio is the source's AAC stream copied unchanged.
Units approved as their plan (keep the source) are cut from the source too. Video concatenated and encoded once. No super-resolution.
Usage: assemble_final_v1.py
"""
import subprocess

from common import DELIVERY, FPS, PROD, REVIEW, SOURCE, p
from title_057 import frames
import render_shot as runner

OUT = DELIVERY / 'final_v1'
WORK = PROD / 'final_v1'
START, END = 0, 2160
SOURCE_UNITS = {'146': '原片结尾纯黑（无可替换内容，未生成过版本），按原片保留，使音轨与原片完全对齐'}
B = runner.batch


def source_clip(uid, start, end):
    """Exact source frames at the review resolution, the same way render_shot cuts <Video 1>."""
    out = WORK / f'{uid}_source_exact_with_audio.mp4'
    if not out.exists():
        p.run([p.FFMPEG, '-v', 'error', '-y', '-i', SOURCE, '-map', '0:v:0', '-map', '0:a:0',
               '-vf', f'trim=start_frame={start}:end_frame={end},setpts=N*1001/(24000*TB),scale=1024:576:flags=lanczos,setsar=1,format=yuv420p',
               '-af', f'atrim=start={start / FPS:.9f}:end={end / FPS:.9f},asetpts=PTS-STARTPTS',
               '-r', '24000/1001', '-c:v', 'libx264', '-crf', '12', '-c:a', 'aac', '-b:a', '192k', out])
    return out


def parts():
    manifest = B.read(REVIEW / 'manifest.json')
    decisions = B.read(REVIEW / 'review_state.json')['decisions']
    plan = {u['id']: u for u in B.read(PROD / 'unit_plan.json')['units']}
    out, expected = [], START
    for unit in manifest['shots']:
        uid = unit['id']
        a, b = plan[uid]['start_frame'], plan[uid]['end_frame']
        assert a == expected, (uid, a, expected)
        expected = b
        versions = {v['id']: v for v in unit['versions']}
        if uid in SOURCE_UNITS:
            video = str(source_clip(uid, a, b))
            out.append(dict(unit=uid, source_interval=[a, b], frames=b - a, version='source', label='原片', video=video,
                            sha256=p.sha(video), decision_origin=SOURCE_UNITS[uid], decision_note=''))
            continue
        approved = sorted((d.get('updated', ''), key.split('/', 1)[1]) for key, d in decisions.items()
                          if key.split('/', 1)[0] == uid and d.get('status') == 'approved' and key.split('/', 1)[1] in versions)
        assert approved, f'{uid} has no approved version'
        version = versions[approved[-1][1]]
        decision = decisions[f'{uid}/{version["id"]}']
        assert decision['video_sha256'] == version['video_sha256'], uid
        if version['id'].startswith('plan'):
            video = str(source_clip(uid, a, b))
        else:
            video = version['video']
            assert p.sha(video) == version['video_sha256'], uid
        out.append(dict(unit=uid, source_interval=[a, b], frames=b - a, version=version['id'], label=version.get('label', ''),
                        video=video, sha256=p.sha(video), decision_origin=decision.get('origin'), decision_note=decision.get('note', ''),
                        latest=version['id'] == unit['versions'][-1]['id']))
    assert expected == END, expected
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    runner.configure(WORK)
    items = parts()
    total = END - START
    assert sum(x['frames'] for x in items) == total
    for x in items:
        B.validate_output(x['video'], x['frames'], True)
    # every part decoded to raw frames and piped into one encoder, in order (the concat demuxer + -r, as in the Lycoris cut, dropped
    # 812 of 2160 frames here: the parts' timestamps do not join evenly)
    silent = WORK / 'final_silent.mp4'
    enc = subprocess.Popen([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576', '-r', '24000/1001',
                            '-i', '-', '-frames:v', str(total), '-c:v', 'libx264', '-threads', '4', '-crf', '16', '-pix_fmt', 'yuv420p',
                            str(silent)], stdin=subprocess.PIPE)
    for x in items:
        f = frames(x['video'])
        assert len(f) == x['frames'], (x['unit'], len(f))
        enc.stdin.write(f.tobytes())
    enc.stdin.close()
    assert enc.wait() == 0
    final = OUT / 'JJK_S3_OP_parody_final_v1_1024x576.mp4'
    # the timeline is the whole source, so its AAC stream is copied as it is (no re-encode)
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', SOURCE, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy',
           '-movflags', '+faststart', final])
    check = B.validate_output(final, total, True)
    offsets, at = [], 0
    for x in items:
        offsets.append(at)
        at += x['frames']
    p.write_json(OUT / 'final_validation.json', dict(video=str(final), sha256=p.sha(final), validation=check, frames=total,
        source_interval=[START, END], units=len(items), source_units=SOURCE_UNITS,
        audio_note='原片 AAC 音轨（整条 [0, 2160)）原样拷贝，未重新编码。', super_resolution=False,
        parts=[dict(**x, start_frame=o) for x, o in zip(items, offsets)],
        requested_by='用户在对话中表示“不太完美，但是就这样吧。把全片都剪起来吧，都通过了”（2026-10-02）'))
    print('DONE', final, check)


if __name__ == '__main__':
    main()
