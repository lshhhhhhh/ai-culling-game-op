"""Planned reruns waiting for inference, shown as “待推理” on the review page (CPU only, never submits anything).

User (2026-10-01): “我觉得状态这里应该多一个‘待推理’，就是我们已经有了新的方案，但是在队列里面等着跑”. Entries live in
<project>/review/queue.json. A unit shows “待推理” until its planned revision folder has a validation.json (the run
finished) or the entry is cancelled. Python use: add(prod, unit, revision, label, ...); cancel(prod, unit, revision).
"""
import datetime as dt
import json
from pathlib import Path


def _path(prod):
    return Path(prod) / 'review/queue.json'


def _read(prod):
    path = _path(prod)
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else dict(schema=1, entries=[])


def _write(prod, data):
    path = _path(prod)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
    tmp.replace(path)


def add(prod, unit, revision, label, note='', when='', script='', prompt='', references=()):
    data = _read(prod)
    data['entries'] = [e for e in data['entries'] if not (e['unit'] == unit and e['revision'] == revision)]
    data['entries'].append(dict(unit=unit, revision=revision, label=label, note=note, when=when, script=script,
                                prompt=prompt, references=[str(r) for r in references],
                                added=dt.datetime.now().astimezone().isoformat()))
    _write(prod, data)


def cancel(prod, unit, revision, reason=''):
    data = _read(prod)
    for e in data['entries']:
        if e['unit'] == unit and e['revision'] == revision:
            e.update(cancelled=True, cancel_reason=reason, cancelled_at=dt.datetime.now().astimezone().isoformat())
    _write(prod, data)
