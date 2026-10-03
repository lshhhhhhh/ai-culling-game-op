"""GPU cooldown gate before a fresh H3 submission (copied from fate_zero/render_character_refresh_002_003.wait_cool)."""
import subprocess
import time

from common import PROD, ROOT, p

STOP_ROOTS = (PROD, ROOT / 'assets/lycoris/op1_v1', ROOT / 'assets/fate_zero/op1_v1', ROOT / 'assets/anime_op/school_full_op_v1')


def wait_cool():
    deadline = time.monotonic() + 1800
    while time.monotonic() < deadline:
        for root in STOP_ROOTS:
            if (root / 'runtime/STOP_GPU_GUARD.json').exists():
                raise RuntimeError('Retained GPU safety STOP; no automatic restart')
        if not p.queue_empty():
            raise RuntimeError('Queue occupied; refusing overlapping generation')
        result = subprocess.run(['nvidia-smi', '--query-gpu=temperature.gpu,power.limit',
                                 '--format=csv,noheader,nounits'], capture_output=True,
                                text=True, check=True, timeout=10)
        temperature, limit = map(float, result.stdout.strip().split(','))
        if limit > 400.5:
            raise RuntimeError('Power limit exceeds 400W')
        # 2 C below render_shot's 57 C submission assert: 069 (2026-10-01) left this gate at 57 and failed that assert seconds later.
        if temperature <= 55:
            return
        print('Cooling before fresh guard session:', temperature, flush=True)
        time.sleep(5)
    raise RuntimeError('GPU did not cool within 30 minutes')
