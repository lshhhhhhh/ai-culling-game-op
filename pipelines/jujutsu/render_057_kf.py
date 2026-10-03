"""057: a text-free clip with the falling bomb turned into a graphics card, by H3 with five Codex keyframes; the title is composited after.

User (2026-10-02) on title_cpu_v2: “4秒左右，画面变淡的时候原版的字又出现了。其实我觉得这个镜头可能还是要用模型，这个炸弹的画面我想改掉。
这样如何？我们把炸弹改成显卡，然后让模型处理文字。如果模型处理文字失败，再用你的算法把字去掉，手动添加”.
Source (frames 827-942): the gold title 呪術廻戦 over a black-and-white city, slowly shrinking; the subtitle 死滅回游 前編 appears; frames
66-90 the city dissolves into a dark red sky with a black eclipsed sun; frames 90-100 the title fades out; from about frame 100 a bomb
falls in the upper right and dives toward the camera, huge by frame 114.
kf_title_gpu_h3_v1 (title keyframes from codex_keyframes_0003.py) was stopped before it ran - the user: “这个视频一定会失败，因为标题的“回”就
不一样。要不这样。让模型去掉字，直接你来写？”. Now keyframes 0, 40 and 88 are the source frames with all text removed
(codex_keyframes_0004.py), 106 and 114 have the graphics card; H3 makes the clip without any text and title_057.py v3 lays one fixed
logo drawing and the subtitle over it. No characters, so a hand-written prompt in the official format (as render_056_kf.py).
"""
import sys

from PIL import Image

import render_batch_0002 as b2
import render_shot as runner
import title_057_v3
from common import PROD, ROOT, p
from gpu import wait_cool

UID, REV = '057', 'clean_gpu_h3_v1'
KF = ROOT / 'deliverables/jujutsu/关键帧'
SEED = 2610019057
LABEL = '标题→「模型回战」＋炸弹→显卡（H3 出无字底片：关键帧第 0/40/88 帧去字、第 106/114 帧显卡；标题与副标题由 CPU 叠加）'
KEYFRAMES = [('kf_057_f000_clean_v2.png', 0), ('kf_057_f040_clean_v2.png', 40), ('kf_057_f088_clean_v2.png', 88),
             ('kf_057_f106_gpu_v1.png', 106), ('kf_057_f114_gpu_v1.png', 114)]


def prompt(g):
    t = [b2.t(local, UID) for _, local in KEYFRAMES]
    return '\n'.join([
        'subject_definitions:',
        f'<Picture 1> is the keyframe of [Shot 1] at {t[0]}: the exact first frame of <Video 1> with all the text removed - the '
        'black-and-white city of tall buildings, with no title.',
        f'<Picture 2> is the keyframe of [Shot 1] at {t[1]}: the exact frame of <Video 1> at that moment with all the text removed - the '
        'black-and-white city, with no title and no subtitle.',
        f'<Picture 3> is the keyframe of [Shot 1] at {t[2]}: the exact frame of <Video 1> at that moment with all the text removed - the '
        'dark red sky with the black eclipsed sun, with no title and no subtitle.',
        f'<Picture 4> is the keyframe of [Shot 1] at {t[3]}: the exact frame of <Video 1> at that moment with the bomb replaced - a small black '
        'graphics card with round fans falling in the upper right of the dark red sky.',
        f'<Picture 5> is the keyframe of [Shot 1] at {t[4]}: the exact frame of <Video 1> at that moment with the bomb replaced - the same '
        'graphics card, huge and close to the camera, diving toward the lower left.',
        '<Video 1> is the source video for the target video edit: a gold title with small kana and a white subtitle over a black-and-white '
        'city that dissolves into a dark red sky with a black eclipsed sun; the title fades out and a bomb falls toward the camera.',
        '',
        'summary:',
        '[video editing + keyframe completion] The target video is an edited version of <Video 1> with all the text removed - no title, no '
        'kana, no subtitle at any moment - and with the falling bomb turned into a falling graphics card; everything else preserves '
        '<Video 1>, its motion and its timing.',
        '',
        'retention_analysis:',
        *[f'<Picture {i + 1}> ([Shot 1] at {ts}): fully_preserved - at that moment the frame matches <Picture {i + 1}>{what}.'
          for i, (ts, what) in enumerate(zip(t, [': the city with no text', ': the city with no text', ': the red sky and the eclipsed sun with no text',
                                                 ': the graphics card\'s shape, size, angle and position, and the red sky',
                                                 ': the huge graphics card, its fans, its angle and position']))],
        '<Video 1> (source video editing): partially_preserved - remove the text and replace the bomb; preserve the city and its falling '
        'debris, the dissolve from the black-and-white city into the red sky, the black eclipsed sun, the black cloud streaks, and the fall '
        'of the object toward the camera with its timing; the frame is never mirrored.',
        '',
        'detailed_description:',
        f'The target video keeps the 2D TV-anime style, the colour grading and the lighting of <Video 1> over this {g / 24:.3f}-second model sequence.',
        '[Shot 1] 2D-animated, a black-and-white city of tall buildings with falling debris, with no text over it. The city darkens and '
        'dissolves into a dark red sky streaked with black clouds, with a black eclipsed sun ringed in glowing red at the left. Then a small '
        'black graphics card appears falling in the upper right and dives toward the camera, growing huge as it tumbles toward the lower '
        'left, its round fans and metal bracket visible in the dark red light.',
        'There is no text, no letters and no logo anywhere in the frame at any moment: where <Video 1> shows the title and the subtitle, the '
        'target video shows only the background behind them. The falling object is a graphics card from its first appearance and is never a bomb.',
        'The keyframes supply the text-free background and the graphics card; the source video supplies all motion, the dissolve and the timing.',
        *b2.b1.TAIL]) + '\n'


def main():
    import msvcrt
    job = PROD / 'shots' / UID / REV
    start, end = b2.b1.interval(UID)
    g = p.snap_frames(end - start)
    text = prompt(g)
    if '--prompt-only' in sys.argv:
        print(text)
        return
    job.mkdir(parents=True, exist_ok=True)
    if (job / 'prompt.txt').exists():
        assert (job / 'prompt.txt').read_text(encoding='utf-8') == text
    else:
        (job / 'prompt.txt').write_text(text, encoding='utf-8')
    refs = []
    for name, _ in KEYFRAMES:
        out = b2.REFS / name
        if not out.exists():
            Image.open(KF / name).convert('RGB').resize((1024, 576), Image.LANCZOS).save(out)
        refs.append(out)
    runner.REFERENCES[UID] = refs
    runner.SEEDS[UID], runner.LABELS[UID] = SEED, LABEL
    runner.SHOT_OVERRIDES[UID] = dict(id=UID, start=start, end=end, frames=end - start)
    runner.POSTPROCESSORS[UID] = title_057_v3.postprocess  # the registered version carries the composited title
    with (PROD / 'batch.lock').open('a+b') as lock:
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        runner.prepare(UID, REV)
        p.write_json(job / 'authorization.json', dict(request='用户（2026-10-02）：057 炸弹改显卡；“让模型去掉字，直接你来写？”',
                                                      references=[str(r) for r in refs], visual_review='pending_user'))
        if not (job / 'validation.json').exists():
            wait_cool()
        sys.argv = [__file__, '--shot', UID, '--revision', REV]
        runner.main()
    print('DONE', job, flush=True)


if __name__ == '__main__':
    main()
