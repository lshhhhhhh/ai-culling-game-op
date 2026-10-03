"""Render one authorised JJK H3 unit and register its actual inputs.

Copied from pipelines/lycoris/render_shot.py (itself from fate_zero) without the Fate-only parts (001 title overlay, old reference
tables). Drivers set REFERENCES/SEEDS/LABELS/SHOT_OVERRIDES for their unit before calling main(). Generation files
and safety state stay in the JJK project; the shared guard, ledger and review registration are unchanged.
"""
import argparse
import math
import os
from pathlib import Path

from common import FPS, PROD, REVIEW, ROOT, p
import build_teaser_001_020 as safety
import render_school_full_op as batch
import review_school_op as review

RUNTIME = PROD / 'runtime'
PREFIX = 'video/jujutsu/op1_v1/'
REFERENCES = {}
SEEDS = {}
LABELS = {}
SHOT_OVERRIDES = {}
POSTPROCESSORS = {}


def configure(job):
    batch.RUN, batch.STOP, batch.OUT = RUNTIME, RUNTIME / 'STOP_GPU_GUARD.json', job
    batch.PREFIX, batch.NATIVE_ONLY, batch.COOLDOWN_TO_C = PREFIX, True, 57
    review.PROD, review.REVIEW = PROD, REVIEW


def prepare(sid, revision):
    inventory = batch.read(PROD / 'source_inventory/inventory.json')
    shot = SHOT_OVERRIDES[sid] if sid in SHOT_OVERRIDES else next(s for s in inventory['shots'] if s['id'] == sid)
    job = PROD / 'shots' / sid / revision
    job.mkdir(parents=True, exist_ok=True)
    configure(job)
    prompt = (job / 'prompt.txt').read_text(encoding='utf-8-sig').strip()
    references = [key if isinstance(key, Path) else PROD / 'character_designs/outputs' / (key + '.png') for key in REFERENCES[sid]]
    frames, model_frames = shot['frames'], p.snap_frames(shot['frames'])
    source = job / 'source_exact_with_audio.mp4'
    if not source.exists():
        p.run([p.FFMPEG, '-v', 'error', '-y', '-threads', '2', '-i', inventory['source'],
               '-map', '0:v:0', '-map', '0:a:0',
               '-vf', f'trim=start_frame={shot["start"]}:end_frame={shot["end"]},setpts=N*1001/(24000*TB),scale=1024:576:flags=lanczos,setsar=1,format=yuv420p',
               '-af', f'atrim=start={shot["start"] / FPS:.9f}:end={shot["end"] / FPS:.9f},asetpts=PTS-STARTPTS',
               '-r', '24000/1001', '-c:v', 'libx264', '-threads', '2', '-preset', 'veryfast',
               '-crf', '12', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', source])
    batch.validate_output(source, frames, True)
    reference_video = job / 'reference_fullframe.mp4'
    if not reference_video.exists():
        p.run([p.FFMPEG, '-v', 'error', '-y', '-i', source, '-vf',
               f'setpts=N*{model_frames - 1}/({frames - 1}*24*TB),fps=24,tpad=stop_mode=clone:stop_duration=0.2',
               '-frames:v', model_frames, '-r', '24', '-an', '-c:v', 'libx264', '-crf', '12',
               '-pix_fmt', 'yuv420p', reference_video])
    ref_info = p.video_info(reference_video)
    assert (ref_info['frames'], ref_info['fps']) == (model_frames, '24/1'), ref_info
    prefix = PREFIX + sid + '/' + revision + '/h3'
    workflow = batch.graph.core.build_workflow(prompt, 1024, 576, model_frames, SEEDS[sid], 20,
        'res_multistep', 'simple', prefix, video=p.stage(reference_video),
        ref_images=[p.stage(path) for path in references], ref_audio=False)
    workflow['6']['inputs']['unet_name'] = batch.graph.HYBRID
    workflow.pop('23')
    workflow['91']['inputs'].pop('audio')
    wf_path = job / 'workflow.json'
    if wf_path.exists():
        assert batch.read(wf_path) == workflow, 'Prepared workflow changed; use a new revision'
    else:
        p.write_json(wf_path, workflow)
    selection = [math.floor(i * (model_frames - 1) / (frames - 1) + .5) for i in range(frames)]
    assert len(set(selection)) == frames and selection[0] == 0 and selection[-1] == model_frames - 1
    p.write_json(job / 'preparation.json', dict(shot=sid, revision=revision, original_interval=[shot['start'], shot['end']],
        frames=frames, model_frames=model_frames, original_source=inventory['source'],
        source_clip=str(source), source_sha256=p.sha(source), reference_video=str(reference_video),
        reference_video_sha256=p.sha(reference_video), workflow_sha256=batch.signature(workflow),
        references=[dict(index=i+1, path=str(path), sha256=p.sha(path)) for i, path in enumerate(references)],
        seed=SEEDS[sid], steps=20, frame_selection=selection, super_resolution=False))
    return shot, job, workflow, prefix, selection, source


def register(job, sid):
    validation = batch.read(job / 'validation.json')
    manifest = batch.read(REVIEW / 'manifest.json')
    entry = next(s for s in manifest['shots'] if s['id'] == sid)
    if not any(v['video_sha256'] == validation['sha256'] for v in entry['versions']):
        review.register(sid, validation['video'], job / 'workflow.json', LABELS[sid])
    # Compare against the exact same interval supplied to H3, not the legacy
    # planning preview's 0.010-second pre-roll. Keep legacy media/versions intact.
    manifest = batch.read(REVIEW / 'manifest.json')
    entry = next(s for s in manifest['shots'] if s['id'] == sid)
    if sid in POSTPROCESSORS and (job / 'title_compositing.json').exists():
        version = next(v for v in entry['versions'] if v['video_sha256'] == validation['sha256'])
        version['postprocessing'] = batch.read(job / 'title_compositing.json')
        note = ' 后期CPU处理参数见同目录title_compositing.json，未由H3生成。'
        if note not in version['prompt']['note']:
            version['prompt']['note'] += note
    entry['source_video'] = str(job / 'source_exact_with_audio.mp4')
    entry['source_exact_video'] = entry['source_video']
    manifest['updated'] = review.stamp()
    review.write(REVIEW / 'manifest.json', manifest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shot', choices=REFERENCES, required=True)
    parser.add_argument('--revision', default='h3_v1')
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    if not args.revision.replace('_', '').isalnum():
        parser.error('Invalid revision name')
    shot, job, workflow, prefix, selection, source = prepare(args.shot, args.revision)
    if args.prepare_only:
        print('Prepared', args.shot, shot['frames'], 'source frames;', workflow['104']['inputs']['length'], 'H3 frames', flush=True)
        return
    if (job / 'validation.json').exists():
        register(job, args.shot)
        print('Existing verified candidate registered; no generation repeated', flush=True)
        return
    # Honor both project and shared safety latches; archive or clear neither here.
    shared_runtime = ROOT / 'assets/anime_op/school_full_op_v1/runtime'
    for stop in [RUNTIME / 'STOP_GPU_GUARD.json', shared_runtime / 'STOP_GPU_GUARD.json']:
        if stop.exists():
            raise batch.SafetyStop('Retained safety STOP: ' + str(stop))
    fresh_runtime = not RUNTIME.exists()
    RUNTIME.mkdir(parents=True, exist_ok=True)
    if fresh_runtime:
        p.write_json(RUNTIME / 'STOP_GUARD_MONITOR', dict(reason='New JJK runtime; no previous monitor session'))
        p.write_json(RUNTIME / 'gpu_guard_status.json', dict(status='not_started', tripped=False))
    p.write_json(job / 'worker_pid.json', dict(pid=os.getpid(), shot=args.shot, script=__file__, started=batch.stamp()))
    try:
        with safety.guarded(job, guard_args=['--runtime', str(RUNTIME), '--scope', PREFIX], shot=args.shot, native_only=True):
            observation = batch.guard()
            assert observation['temperature_c'] <= 57, 'Wait for the established 57C submission threshold'
            p.write_json(job / 'monitor_observation.json', observation)
            raw = batch.gpu_job(workflow, job, 'h3', prefix)
        info = p.video_info(raw)
        assert (info['frames'], info['width'], info['height']) == (workflow['104']['inputs']['length'], 1024, 576), info
        native = job / 'native_fullframe.mp4'
        choose = '+'.join(f'eq(n\\,{i})' for i in selection)
        p.run([p.FFMPEG, '-v', 'error', '-y', '-i', raw, '-vf',
               f'select={choose},setpts=N*1001/(24000*TB),setsar=1',
               '-frames:v', shot['frames'], '-r', '24000/1001', '-an', '-c:v', 'libx264',
               '-crf', '12', '-pix_fmt', 'yuv420p', native])
        visual = native
        if args.shot in POSTPROCESSORS:
            visual = POSTPROCESSORS[args.shot](job, visual, shot['frames'])
        preview = job / 'review_with_audio.mp4'
        p.run([p.FFMPEG, '-v', 'error', '-y', '-i', visual, '-i', source,
               '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', preview])
        validation = batch.validate_output(preview, shot['frames'], True)
        audio_hash = batch.audio_hash(preview)
        assert audio_hash == batch.audio_hash(source), 'Original shot audio packets changed'
        p.write_json(job / 'timing.json', dict(original_interval=[shot['start'], shot['end']],
            source_frames=shot['frames'], generated_frames=info['frames'], selection=selection,
            method='Uniform whole-frame stretching to legal H3 length and timing restoration'))
        p.write_json(job / 'validation.json', dict(video=str(preview), sha256=p.sha(preview), validation=validation,
            full_decode_passed=True, original_audio_packets_match=True, audio_packet_hash=audio_hash,
            workflow_sha256=batch.signature(workflow), super_resolution=False,
            user_visual_review='pending', completed=batch.stamp()))
        register(job, args.shot)
        batch.state(status='ready_for_user', stage='complete', video=str(preview))
        print('READY', preview, flush=True)
    except Exception as exc:
        p.write_json(job / 'failure.json', dict(time=batch.stamp(), error=repr(exc)))
        raise


if __name__ == '__main__':
    main()
