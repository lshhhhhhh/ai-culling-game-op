"""JJK first night batch: the units whose characters are cast (CPU prepare / queue, GPU when the user sleeps).

Casting (user, 2026-10-01): 虎杖 → DeepSeek (assets/人设/鲸鱼娘.png, “这个才是我们该用的”), 伏黑惠 → Claude (claude娘.png),
天元 → 黄仁勋 (cartoon by Codex, deliverables/jujutsu/人设/tengen_jensen_v1.png). Units checked on the strips: 059 Tengen,
030-031 and 032-034 Megumi, 069 and 020-026a Itadori. 001 v3 has its own script. Prompts follow the official six-section
format with positions and “never mirror”, and describe only what should be there (lesson of Lycoris 021).
Usage: render_batch_0001.py --queue UNIT@REV ...   (adds the plans to review/queue.json as 待推理)
       render_batch_0001.py UNIT@REV ...           (generates in order, checks each, logs to batch_0001/)
"""
import json
import msvcrt
import subprocess
import sys
import time

import numpy as np
from PIL import Image

import render_shot as runner
from common import PROD, ROOT, p
from gpu import wait_cool

sys.path.insert(0, str(ROOT / 'pipelines/anime_op'))
import review_queue  # noqa: E402

LOG = PROD / 'batch_0001'
GAMES = ['ntegame.exe', 'dota2.exe']
DEEPSEEK = ROOT / 'assets/人设/鲸鱼娘.png'
CLAUDE = ROOT / 'assets/人设/claude娘.png'
JENSEN = ROOT / 'deliverables/jujutsu/人设/tengen_jensen_v1.png'
DS = ('DeepSeek from <Picture 1>: a slender young woman with grown-up proportions, very long wavy dark-blue hair, an ahoge, '
      'a white frilled maid headband, blue whale-fin ears on both sides of her head, an off-shoulder navy maid dress with a white '
      'apron, white stockings and a large blue whale tail')
CL = ('Claude from <Picture 1>: a young woman with very long flowing orange hair, amber eyes and an orange flower ornament with '
      'a black ribbon, wearing a white blouse with a black bow and a layered white, black and orange dress')
TAIL = ['', 'overall_soundscape:', 'N/A. Generated audio is disabled; the original clip audio is restored after retiming.', '',
        'non_diegetic_music:', 'N/A']


def build(subject, source, preserve, shot, contrast, g):
    return '\n'.join([
        'subject_definitions:',
        f'<Subject 1> is {subject}.',
        f'<Subject 2> is {source} in <Video 1>.',
        '<Video 1> is the source video for the target video edit.', '',
        'summary:',
        '[video editing + reference generation] The target video is an edited version of <Video 1>. Replace <Subject 2> with '
        '<Subject 1>, preserving the original performance, camera and timing.', '',
        'retention_analysis:',
        '<Subject 1> (appears in [Shot 1]): fully_preserved - identity, face, hairstyle and clothing come from <Picture 1>.',
        '<Subject 2> (appears in [Shot 1]): attribute_transfer - all original motion, poses, expressions, screen position and '
        'scale are transferred to <Subject 1>, with their original timing.',
        f'<Video 1> (source video editing): partially_preserved - replace the character; preserve {preserve}; the frame is never '
        'mirrored.', '',
        'detailed_description:',
        f'The target video keeps the 2D TV-anime style, the colour grading and the lighting of <Video 1> over this '
        f'{g / 24:.3f}-second model sequence.',
        '[Shot 1] 2D-animated, ' + shot,
        contrast,
        'Keep <Subject 1> on the side of the frame where <Video 1> shows the original character; never mirror the shot.',
        'The reference picture supplies appearance; the source video supplies the complete performance. The reference picture '
        'supplies no pose, expression, camera distance or composition.', *TAIL]) + '\n'


JOBS = {
    ('059', 'jensen_h3_v1'): dict(ref=JENSEN, seed=2610010059, label='天元→黄仁勋（卡通设定图）', prompt=lambda g: build(
        'the cartoon of Jensen Huang from <Picture 1>: a smiling man with short swept-back black-and-grey hair and glasses, '
        'wearing a black leather jacket under a long white hooded robe with a thin green trim',
        'the tall pale figure with an elongated, four-eyed face in a white hooded robe (Tengen)',
        'the pale lavender-white light, the soft background, the frontal framing and the slow movement',
        'a frontal close-up in pale lavender-white light: <Subject 1> faces the camera in the centre of the frame, the white '
        'robe around his shoulders, and opens his mouth slightly as if to speak.',
        'His human face with short black-grey hair and glasses, and his black leather jacket, take the place of the elongated '
        'four-eyed face of <Video 1>; the robe stays white.', g)),
    ('030-031', 'claude_h3_v1'): dict(ref=CLAUDE, seed=2610010030, label='伏黑惠→Claude·面部特写', prompt=lambda g: build(
        CL, 'the young man with spiky black hair in a dark high-collared school uniform (Megumi)',
        'the cold pale lighting, the dark background and the slight push-in',
        'a close-up of <Subject 1> facing the camera in the centre of the frame, her face lit pale and cold, looking up with a '
        'sharp, determined stare as the camera pushes in slightly.',
        'Her long orange hair and flower ornament frame her face in place of the spiky black hair of <Video 1>.', g)),
    ('069', 'deepseek_h3_v1'): dict(ref=DEEPSEEK, seed=2610010069, label='虎杖→DeepSeek·青蓝惊愕近景', prompt=lambda g: build(
        DS, 'the boy with short spiky hair and a red hood around his neck (Itadori)',
        'the cyan-and-blue tint, the turbulent white clouds and deep blue sky behind and the trembling camera',
        'a cyan-tinted medium close-up: <Subject 1> faces the camera in the centre of the frame, shocked and trembling, against '
        'turbulent white clouds and a deep blue sky, the whole image washed in cyan.',
        'Her long wavy dark-blue hair, frilled headband and whale-fin ears take the place of the short spiky hair of '
        '<Video 1>, tinted cyan like the rest of the frame.', g)),
    ('020-026a', 'deepseek_h3_v1'): dict(ref=DEEPSEEK, seed=2610010020, label='虎杖→DeepSeek·高空坠落与连续出拳', prompt=lambda g: build(
        DS, 'the boy with short spiky pink hair in a dark school uniform (Itadori)',
        'the orange and blue-grey palette, the ink-black crack effects, the camera tilt from the building wall to the city, '
        'the dive, the punch impact frames and the final purple-white flash',
        'the camera tilts from a building wall with rows of red windows to a high aerial view of the city; <Subject 1> falls '
        'from the sky with her arms spread wide in the centre of the frame; the camera dives with her to an orange-lit close-up '
        'of her face, her long hair streaming upward; she throws a flurry of fast punches toward the camera among ink-black '
        'cracks, and the last punch hits the lens and the frame flashes purple-white.',
        'Her long wavy dark-blue hair, frilled headband and whale-fin ears take the place of the short spiky pink hair of '
        '<Video 1>, in every frame of the fall and of the punches.', g)),
    ('032-034', 'claude_h3_v1'): dict(ref=CLAUDE, seed=2610010032, label='伏黑惠→Claude·楼顶坠下与蓝色光线', prompt=lambda g: build(
        CL, 'the young man with spiky black hair in a dark school uniform (Megumi)',
        'the night city, the tall buildings, the camera tilting down to the street, the blue lines of light spreading across the '
        'street and the high aerial view',
        'at night <Subject 1> crouches on the edge of a rooftop in the centre of the frame and steps off; the camera tilts down '
        'the tall building to the street far below, where blue lines of light spread across the asphalt as she falls toward '
        'them, small in the centre; then a high aerial view of the dark city.',
        'Her long orange hair streams above her as she falls, in place of the spiky black hair of <Video 1>.', g)),
}


def interval(uid):
    plan = json.loads((PROD / 'unit_plan.json').read_text(encoding='utf-8'))
    u = next(x for x in plan['units'] if x['id'] == uid)
    return u['start_frame'], u['end_frame']


def prepare(uid, rev):
    spec = JOBS[(uid, rev)]
    start, end = interval(uid)
    n = end - start
    g = p.snap_frames(n)
    prompt = spec['prompt'](g)
    job = PROD / 'shots' / uid / rev
    job.mkdir(parents=True, exist_ok=True)
    if (job / 'prompt.txt').exists():
        assert (job / 'prompt.txt').read_text(encoding='utf-8') == prompt, f'{uid}: prompt changed; use a new revision'
    else:
        (job / 'prompt.txt').write_text(prompt, encoding='utf-8')
    runner.REFERENCES[uid] = [spec['ref']]
    runner.SEEDS[uid], runner.LABELS[uid] = spec['seed'], spec['label']
    runner.SHOT_OVERRIDES[uid] = dict(id=uid, start=start, end=end, frames=n)
    runner.prepare(uid, rev)
    p.write_json(job / 'authorization.json', dict(request='用户：先把人物安排好，这样我睡觉的时候可以跑（2026-10-01）', reference=str(spec['ref']),
                                                  reference_sha256=p.sha(spec['ref']), interval=[start, end], visual_review='pending_user'))
    return job, prompt


def check(uid, rev):
    job = PROD / 'shots' / uid / rev
    def gray(path):
        raw = subprocess.run([str(p.FFMPEG), '-v', 'error', '-i', str(path), '-vf', 'scale=128:72,format=gray', '-f', 'rawvideo', '-'],
                             capture_output=True, check=True).stdout
        return np.frombuffer(raw, np.uint8).reshape(-1, 72, 128).astype(np.float32)
    def corr(a, b):
        a, b = a - a.mean(), b - b.mean()
        return float((a * b).sum() / (np.sqrt((a * a).sum() * (b * b).sum()) + 1e-6))
    s, o = gray(job / 'source_exact_with_audio.mp4'), gray(job / 'native_fullframe.mp4')
    same = float(np.mean([corr(x, y) for x, y in zip(o, s)]))
    flipped = float(np.mean([corr(x, y[:, ::-1]) for x, y in zip(o, s)]))
    result = dict(unit=uid, revision=rev, corr_with_source=round(same, 3), corr_with_mirrored_source=round(flipped, 3), mirrored=flipped > same)
    p.write_json(job / 'mirror_check.json', result)
    return result


def log(entry):
    LOG.mkdir(parents=True, exist_ok=True)
    with (LOG / 'queue_log.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(dict(time=runner.batch.stamp(), **entry), ensure_ascii=False) + '\n')


def wait_games():
    while True:
        out = subprocess.run(['tasklist', '/FO', 'CSV', '/NH'], capture_output=True, text=True).stdout.lower()
        if not any(g in out for g in GAMES):
            return
        time.sleep(60)


def main():
    units = [tuple(u.split('@')) for u in sys.argv[1:] if not u.startswith('--')]
    if '--queue' in sys.argv:
        for uid, rev in units:
            spec = JOBS[(uid, rev)]
            start, end = interval(uid)
            review_queue.add(PROD, uid, rev, spec['label'], note='首批选角后的第一版（虎杖→DeepSeek、伏黑惠→Claude、天元→黄仁勋）',
                             when='用户睡觉时（ComfyUI 切 away 模式）', script='pipelines/jujutsu/render_batch_0001.py',
                             prompt=spec['prompt'](p.snap_frames(end - start)), references=[spec['ref']])
            print('QUEUED', uid, rev, flush=True)
        return
    with (PROD / 'batch.lock').open('a+b') as lock:
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        for uid, rev in units:
            try:
                job, _ = prepare(uid, rev)
                if not (job / 'validation.json').exists():
                    wait_games()
                    wait_cool()
                started = time.time()
                sys.argv = [__file__, '--shot', uid, '--revision', rev]
                runner.main()
                result = check(uid, rev)
                result['seconds'] = round(time.time() - started)
                log(dict(event='done', **result))
                print('UNIT DONE', json.dumps(result, ensure_ascii=False), flush=True)
            except Exception as exc:
                text = repr(exc)
                log(dict(event='failed', unit=uid, revision=rev, error=text))
                print('UNIT FAILED', uid, rev, text, flush=True)
                if any(k in text for k in ('STOP', 'Safety', 'safety', 'Power limit', 'did not cool')):
                    raise
        print('DONE', len(units), flush=True)


if __name__ == '__main__':
    main()
