"""001: the red-and-black street long take; Itadori → the DeepSeek community girl (test of the JJK pipeline).

User (2026-10-01): “我们先试试001.用deepseek社区形象替换虎杖”. 001 is 238 frames; one H3 pass would need 243 model frames, above
anything that has worked here (192 peaked at 31.1 GB; 345 failed). Frames 0–62 show only the street and the black sun, and
the boy enters around frame 70, so only [63, 238) is generated (175 frames → 175 model frames, the length Fate ran fine).
The full unit is the source for 0–62, a 6-frame crossfade from the source to the generation over 63–68, then the
generation, with the unit's original audio. Reference: the community three-view used for the Lycoris DeepSeek design.
"""
import json
import shutil
import subprocess
import sys

import numpy as np

import render_shot as runner
from common import PROD, ROOT, p
from gpu import wait_cool

UID, REV = '001', 'deepseek_h3_v1'
START, CUT, END, FADE = 0, 63, 238, 6
REF_SRC = ROOT / 'deliverables/lycoris/人设需求/身份参考/DeepSeek娘_社区_三视图.png'
REF = PROD / 'character_designs/refs/deepseek_community_3view.png'
SEED = 2610010001
LABEL = 'DeepSeek社区形象替换虎杖·红黑长镜头（后175帧生成＋前段原片）'
PROMPT = '''subject_definitions:
<Subject 1> is DeepSeek from <Picture 1>: a small girl with very long wavy dark-blue hair, an ahoge, a white frilled maid headband with blue bows, white-and-blue whale-fin ears on both sides of her head, a navy maid dress with a white apron, and a blue whale tail.
<Subject 2> is the boy with short spiky hair in a dark hooded school jacket who walks into <Video 1>.
<Video 1> is the source video for the target video edit.

summary:
[video editing + reference generation] The target video is an edited version of <Video 1>. Replace <Subject 2> with <Subject 1>, preserving the original performance, the rotating camera, the timing and the red-and-black two-tone look.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - identity, face, long wavy hair, frilled headband, whale-fin ears and clothing come from <Picture 1>, drawn in the red-and-black two-tone of <Video 1>.
<Subject 2> (appears in [Shot 1]): attribute_transfer - all original motion, walking, head turns, screen position and scale are transferred to <Subject 1>, with their original timing.
<Video 1> (source video editing): partially_preserved - replace the character; preserve the red-and-black two-tone rendering, the city street, the black sun with its red ring, the camera that turns around her head, and at the end the black sun forming a red halo behind her head; the frame is never mirrored.

detailed_description:
The target video keeps the 2D TV-anime style and the red-and-black two-tone rendering of <Video 1> over this 7.292-second model sequence.
[Shot 1] 2D-animated, a red-and-black two-tone city street seen from low, a black sun with a glowing red ring in the sky; <Subject 1> walks in from the left very close to the camera, her long wavy hair, frilled headband and fin ears outlined in red and black; the camera turns around her head as she walks; at the end, seen from behind and below, she looks up and the black sun behind her head forms a red halo.
Even in red and black she is clearly <Subject 1>: her long wavy hair flows down her back and the whale-fin ears stand out on both sides of her head, in place of the short spiky hair and the hood of <Video 1>.
Keep <Subject 1> on the side of the frame where <Video 1> shows the boy; never mirror the shot.
The reference picture supplies appearance; the source video supplies the complete performance. The reference picture supplies no pose, expression, camera distance or composition.

overall_soundscape:
N/A. Generated audio is disabled; the original clip audio is restored after retiming.

non_diegetic_music:
N/A
'''


def frames(path):
    raw = subprocess.run([str(p.FFMPEG), '-v', 'error', '-i', str(path), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 576, 1024, 3)


def compose(job, inv):
    out = PROD / 'shots' / UID / f'{REV}_joined'
    out.mkdir(parents=True, exist_ok=True)
    full = out / 'source_exact_with_audio.mp4'
    if not full.exists():
        p.run([p.FFMPEG, '-v', 'error', '-y', '-i', inv['source'], '-map', '0:v:0', '-map', '0:a:0',
               '-vf', f'trim=start_frame={START}:end_frame={END},setpts=N*1001/(24000*TB),scale=1024:576:flags=lanczos,setsar=1,format=yuv420p',
               '-af', f'atrim=start=0:end={END / (24000 / 1001):.9f},asetpts=PTS-STARTPTS',
               '-r', '24000/1001', '-c:v', 'libx264', '-crf', '12', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', full])
    src, gen = frames(full), frames(job / 'native_fullframe.mp4')
    assert len(src) == END - START and len(gen) == END - CUT
    result = [src[i] for i in range(CUT)]
    for k in range(END - CUT):
        if k < FADE:
            w = (k + 1) / (FADE + 1)
            result.append(np.clip(src[CUT + k] * (1 - w) + gen[k] * w, 0, 255).astype(np.uint8))
        else:
            result.append(gen[k])
    silent = out / 'native_fullframe.mp4'
    proc = subprocess.run([str(p.FFMPEG), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1024x576',
                           '-r', '24000/1001', '-i', '-', '-frames:v', str(END - START), '-c:v', 'libx264', '-crf', '12',
                           '-pix_fmt', 'yuv420p', str(silent)], input=np.stack(result).tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr
    clip = out / 'review_with_audio.mp4'
    p.run([p.FFMPEG, '-v', 'error', '-y', '-i', silent, '-i', full, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy',
           '-movflags', '+faststart', clip])
    runner.configure(out)
    check = runner.batch.validate_output(clip, END - START, True)
    assert runner.batch.audio_hash(clip) == runner.batch.audio_hash(full)
    parts = [dict(label=f'原片第 {START}–{CUT - 1} 帧（街道与黑太阳，人物尚未进画）', workflow=None),
             dict(label=f'H3 生成第 {CUT}–{END - 1} 帧（DeepSeek 社区形象）', workflow=str(job / 'workflow.json'),
                  workflow_sha256=p.sha(job / 'workflow.json'))]
    record = out / 'multistage.json'
    p.write_json(record, dict(kind='h3_multistage', parts=[x for x in parts if x['workflow']], note=(
        f'001 全长 238 帧，一次生成需要 243 个模型帧，超过本机稳定上限，所以只生成人物出场的第 {CUT}–{END - 1} 帧（175 帧）；'
        f'第 0–{CUT - 1} 帧用原片，第 {CUT}–{CUT + FADE - 1} 帧从原片淡入生成画面。原片原音。')))
    p.write_json(out / 'validation.json', dict(video=str(clip), sha256=p.sha(clip), validation=check, cut=CUT, fade=FADE,
                                                visual_review='pending'))
    entry = next(s for s in runner.batch.read(runner.REVIEW / 'manifest.json')['shots'] if s['id'] == UID)
    if not any(v['video_sha256'] == p.sha(clip) for v in entry['versions']):
        runner.review.register(UID, str(clip), record, LABEL)
    return clip


def main():
    import msvcrt
    REF.parent.mkdir(parents=True, exist_ok=True)
    if not REF.exists():
        shutil.copy2(REF_SRC, REF)
    inv = json.loads((PROD / 'source_inventory/inventory.json').read_text(encoding='utf-8'))
    job = PROD / 'shots' / UID / REV
    job.mkdir(parents=True, exist_ok=True)
    if (job / 'prompt.txt').exists():
        assert (job / 'prompt.txt').read_text(encoding='utf-8') == PROMPT
    else:
        (job / 'prompt.txt').write_text(PROMPT, encoding='utf-8')
    runner.REFERENCES[UID] = [REF]
    runner.SEEDS[UID], runner.LABELS[UID] = SEED, LABEL
    runner.SHOT_OVERRIDES[UID] = dict(id=UID, start=CUT, end=END, frames=END - CUT)
    runner.register = lambda job, sid: None  # the 175-frame part is registered only as the joined 238-frame unit
    with (PROD / 'batch.lock').open('a+b') as lock:
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        _, _, workflow, _, _, _ = runner.prepare(UID, REV)
        assert workflow['104']['inputs']['length'] == 175, workflow['104']['inputs']['length']
        p.write_json(job / 'authorization.json', dict(request='用户：我们先试试001.用deepseek社区形象替换虎杖（2026-10-01）',
            reference=str(REF), reference_sha256=p.sha(REF), generated_interval=[CUT, END], visual_review='pending_user'))
        print('PREPARED', job, flush=True)
        if '--prepare-only' in sys.argv:
            return
        if not (job / 'validation.json').exists():
            wait_cool()
        sys.argv = [__file__, '--shot', UID, '--revision', REV]
        runner.main()
        clip = compose(job, inv)
        print('DONE', clip, flush=True)


if __name__ == '__main__':
    main()
