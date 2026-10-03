"""Register a unit's source clip as its version (kind original_copy), when the user decides to keep the original.

First used by hand for 056 (2026-10-02: “算了，还是不好。还是用原版吧。”); 063 the same day: “063的回形针眼睛有点奇怪。还是用原版吧”.
Usage: keep_original.py UNIT "the user's words"
"""
import shutil
import sys

import render_batch_0001 as b1
import render_shot as runner
from common import PROD, p


def main():
    uid, words = sys.argv[1], sys.argv[2]
    out = PROD / 'shots' / uid / 'original_v1'
    out.mkdir(parents=True, exist_ok=True)
    clip = out / 'review_with_audio.mp4'
    if not clip.exists():
        # any job folder's exact source clip of this unit (all are cut the same way from the OP)
        src = next((PROD / 'shots' / uid).glob('*/source_exact_with_audio.mp4'))
        shutil.copy2(src, clip)
    start, end = b1.interval(uid)
    runner.configure(out)
    check = runner.batch.validate_output(clip, end - start, True)
    record = out / 'original_copy.json'
    p.write_json(record, dict(kind='original_copy', note=f'用户：“{words}” 用原片。'))
    p.write_json(out / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, decision='用户在对话中选择用原片'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == uid)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(uid, str(clip), record, '原片（用户决定保留原版）')
    print('READY', clip, check, flush=True)


if __name__ == '__main__':
    main()
