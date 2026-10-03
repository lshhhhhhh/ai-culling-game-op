"""Overnight driver for the JJK 待推理 queue (2026-10-02 night): run each planned unit in turn through its own script.

User (2026-10-02 02:15): “我准备睡觉了，开始推理队列吧。记得看我给的意见。” ComfyUI runs in away mode (0.6 GB reserve).
The job list (assets/jujutsu/op1_v1/batch_1002/jobs.json) is re-read after every unit, so plans made during the night can be
appended. A unit is done when its job folder has validation.json (or `done` names another folder); a failed unit is recorded
and skipped; a safety STOP or a failed cool-down ends the night.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

from common import PROD

HERE = Path(__file__).resolve().parent
PY = Path(sys.executable)
DIR = PROD / 'batch_1002'
JOBS, STATE, LOG = DIR / 'jobs.json', DIR / 'state.json', DIR / 'driver.log'
STOPS = [PROD / 'runtime/STOP_GPU_GUARD.json', PROD.parent.parent / 'anime_op/school_full_op_v1/runtime/STOP_GPU_GUARD.json']


def say(text):
    line = f'{time.strftime("%H:%M:%S")} {text}'
    print(line, flush=True)
    with LOG.open('a', encoding='utf-8') as f:
        f.write(line + '\n')


def done(job):
    return (PROD / 'shots' / job['unit'] / job.get('done', job['revision']) / 'validation.json').exists()


def idle_seconds():
    """Seconds since the user's last keyboard or mouse input (GetLastInputInfo)."""
    import ctypes

    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]
    info = LASTINPUTINFO(ctypes.sizeof(LASTINPUTINFO), 0)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info))
    return (ctypes.windll.kernel32.GetTickCount() - info.dwTime) / 1000


def comfy_mode():
    out = subprocess.run(['powershell', '-NoProfile', '-Command',
                          "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -match 'ComfyUI.main\\.py' } "
                          "| ForEach-Object { $_.CommandLine }"], capture_output=True, text=True).stdout
    return 'away' if 'reserve-vram 0.6' in out else 'present' if 'reserve-vram 4' in out else 'unknown'


def match_mode():
    """2026-10-02 02:50: the user was still at the PC (a live stream playing) after saying good night. The rig hard-locked once when
    H3 ran with the small reserve while the user watched video, so: input within 20 minutes -> present mode (4 GB), else away."""
    want = 'away' if idle_seconds() >= 1200 else 'present'
    have = comfy_mode()
    if have != want:
        # output to a file, not a pipe: the restarted ComfyUI inherits the handles, and a pipe would never close (hung at 02:51)
        with (DIR / 'comfy_restart.log').open('a', encoding='utf-8') as out:
            rc = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                                 str(HERE.parent / 'restart_comfyui_hidden.ps1'), '-Mode', want], stdout=out, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL, timeout=300).returncode
        time.sleep(20)
        say(f'ComfyUI {have} -> {want} (idle {idle_seconds():.0f} s): rc={rc}, now {comfy_mode()}')


def main():
    DIR.mkdir(exist_ok=True)
    state = json.loads(STATE.read_text(encoding='utf-8')) if STATE.exists() else dict(failed={}, finished=[])
    while True:
        if any(s.exists() for s in STOPS):
            say('STOP file present; ending')
            return
        jobs = json.loads(JOBS.read_text(encoding='utf-8'))
        todo = [j for j in jobs if not done(j) and f"{j['unit']}@{j['revision']}" not in state['failed']]
        if not todo:
            say('queue empty; ending')
            return
        job = todo[0]
        key = f"{job['unit']}@{job['revision']}"
        match_mode()
        cmd = [str(PY), '-X', 'utf8', '-u', str(HERE / job['script']), *job.get('args', [key])]
        say(f'START {key} ({job["script"]}) - {len(todo)} left')
        started = time.time()
        with (DIR / f"{job['unit']}_{job['revision']}.log").open('w', encoding='utf-8') as out:
            rc = subprocess.run(cmd, cwd=str(HERE), stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                env={**__import__('os').environ, 'PYTHONIOENCODING': 'utf-8'}).returncode
        text = (DIR / f"{job['unit']}_{job['revision']}.log").read_text(encoding='utf-8', errors='replace')
        if rc == 0 and done(job) and 'UNIT FAILED' not in text:
            state['finished'].append(dict(key=key, seconds=round(time.time() - started), at=time.strftime('%H:%M')))
            say(f'DONE {key} in {time.time() - started:.0f} s')
        elif 'did not cool' in text and state.setdefault('cool_retries', {}).get(key, 0) < 6:
            # the idle GPU sat at 56-57 C with a stream playing; wait and retry instead of ending the night
            state['cool_retries'][key] = state['cool_retries'].get(key, 0) + 1
            say(f'{key}: GPU did not cool to 55 C in 30 min (retry {state["cool_retries"][key]}/6 after 5 min)')
            STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding='utf-8')
            time.sleep(300)
            continue
        else:
            tail = ' | '.join(text.strip().splitlines()[-3:])[-400:]
            state['failed'][key] = dict(rc=rc, tail=tail, at=time.strftime('%H:%M'))
            say(f'FAILED {key} rc={rc}: {tail}')
            if any(k in text for k in ('STOP_GPU', 'SafetyStop', 'Retained', 'Power limit')):
                STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding='utf-8')
                say('safety-related failure; ending')
                return
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
