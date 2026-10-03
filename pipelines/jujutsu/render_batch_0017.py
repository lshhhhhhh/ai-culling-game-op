"""JJK batch 17 - PLANS ONLY: Kenjaku recast as the paperclip maximizer (060, 061's hand, 062, 145); 060's monitors show Jensen Huang.

The first rogue AI (ROGUE, rogue_ai_kenjaku_v1.png) looked like Kenjaku himself: 062's H3 version changed 0.4 % of the pixels. The
user took my paperclip-maximizer proposal (codex_designs_0007.py): “如果是回形针放大器，那061其实是不用动的：反派把一块城市隔绝出来，
要做成回形针。唯一要变化的是手。要变成少女的手”. 060 also carries the user's review note “电视机上的人应该换成黄仁勋”.
063 (the floating block of city, then an eye opening in the dark) is still under discussion.
Design v2 (CLIP2; the key changed because references are cached per key): the user on v1 “额头上的回形针不好看。别的可以”.
061 v2: the user on clip_hand_grey_h3_v1 “061的画面不行。手没有变化。需要关键帧。先记下来之后再推理” - Codex keyframes at frames 1 and 14
(codex_keyframes_0006.py): her slender hand with silver-grey nails and the black sleeve hem with a paperclip chain at the wrist.
Usage: render_batch_0017.py --queue [UNIT@REV ...] | render_batch_0017.py UNIT@REV ... (only after the user says to run)
--queue with UNIT@REV registers only those plans: re-adding an entry renews its time and would reopen a unit the user has approved.
"""
import sys

import render_batch_0004  # noqa: F401  (JENSEN)
import render_batch_0002 as b2
from PIL import Image

from common import PROD, ROOT

KF = ROOT / 'deliverables/jujutsu/关键帧'


def kf(name):
    out = b2.REFS / name
    if not out.exists() and (KF / name).exists():
        Image.open(KF / name).convert('RGB').resize((1024, 576), Image.LANCZOS).save(out)
    return out


SLEEVE = "<A>'s slender hand with long silver-grey nails reaching in from the upper right, the hem of her black sleeve with a paperclip chain at the wrist"

b2.CAST['CLIP2'] = (b2.D / 'paperclip_maximizer_v2.png',
                   'a slender young woman with very long straight silver-grey hair, its upper part in a small half-up bun held by two large '
                   'bent-wire paperclip hairpins, a bare forehead, half-lidded grey eyes and '
                   'a faint sinister closed-mouth smile, in a long black monk\'s robe with wide sleeves and a dark grey kesa over her left '
                   'shoulder lined with chains of tiny silver paperclips')
b2.NAMES['CLIP2'] = 'the paperclip maximizer'
b2.LOG = PROD / 'batch_0017'
b2.AUTH_REQUEST = '用户（2026-10-02）：羂索改由回形针最大化器演；061 只把巨手换成少女的手；060 屏幕上的人换成黄仁勋'
GREY = 'She is drawn in black, white and grey like the rest of the frame; her silver hair and the paperclip hairpins stay clearly visible.'

b2.JOBS = {
    ('060', 'clip_jensen_h3_v1'): dict(seed=2610017060, label='羂索→回形针最大化器·监视器墙（屏幕上的人→黄仁勋）',
        subjects=[('CLIP2', None, 'the long-haired figure seen from behind in front of the monitors (Kenjaku)'),
                  ('JENSEN', None, 'the man whose face appears on the monitor screens')],
        preserve='the dark room, the curved wall of glowing blue monitors and the silhouette lighting',
        shots=[(None, 'a dark room with a curved wall of glowing blue monitors, every screen showing <B>\'s face: <A> stands with her back '
                      'to the camera in the centre of the frame, a dark silhouette with long silver hair in a half-up bun held by paperclip '
                      'hairpins, and turns slightly to the side.')],
        extras=['<B> appears only on the monitor screens, small, in the blue glow of the screens, in place of the face shown on them in <Video 1>.']),
    ('061', 'clip_hand_grey_h3_v1'): dict(seed=2610017061, label='羂索的巨手→回形针最大化器的少女之手（画面其余不动）',
        subjects=[('CLIP2', 'grey', 'the giant hand reaching in from the upper right (Kenjaku\'s hand; only the hand and wrist are in the frame)')],
        preserve='the black-and-white manga rendering, the city skyline, the mountains, the tall black pillar, the gesture of the hand and the still camera',
        shots=[(None, 'black-and-white manga style: a city skyline with mountains behind it and a tall black pillar rising from the middle; the '
                      'giant hand of <A> reaches in from the upper right toward the pillar, its long fingers spread as if to pinch out the block '
                      'of city around it.')],
        extras=['Only her hand and wrist are in the frame: a slender young woman\'s hand with long fingers and silver-grey nails, drawn in '
                'black, white and grey, in place of the large man\'s hand of <Video 1>; nothing else in the frame changes.']),
    ('062', 'clip_grey_h3_v1'): dict(seed=2610017062, label='羂索→回形针最大化器·黑白俯身抠出一块城市',
        subjects=[('CLIP2', 'grey', 'the long-haired man in robes bending over the city (Kenjaku)')],
        preserve='the black-and-white manga rendering, the city far below and the block of city lifted out of it',
        shots=[(None, 'black-and-white manga style: <A> bends over a city far below, her long silver hair falling forward and her hands '
                      'working a block of the city loose, a smile on her face.')],
        extras=[GREY]),
    ('145', 'clip_grey_h3_v1'): dict(seed=2610017145, label='羂索→回形针最大化器·白色光圈',
        subjects=[('CLIP2', 'grey', 'the long-haired man in a black robe laughing upward (Kenjaku)')],
        preserve='the black-and-white rendering, the white circle of light with shattered edges and the black background',
        shots=[(None, 'black and white: <A> stands inside a circle of white light with shattered edges, laughing upward, her long hair falling behind her.')],
        extras=[GREY]),
    # the user on my 063 proposal (the block of city stays, the eye becomes hers): “可以。先这样做”
    ('063', 'clip_eye_h3_v1'): dict(seed=2610017063, label='黑暗中漂浮的城市块保留；睁开的眼睛→回形针最大化器的眼睛（线圈虹膜）',
        subjects=[('CLIP2', None, 'the eye that opens in the dark (Kenjaku\'s eye; only the eye and the skin around it are visible)')],
        preserve='the black void, the floating block of city, the faint warm circle of light around the eye, the slow opening of the eye and the timing',
        shots=[(None, 'a black void: the block of city lifted out of the ground floats and slowly turns in the dark; then, inside a faint warm '
                      'circle of light, the eye of <A> slowly opens and looks out.')],
        extras=['Only her eye and the skin right around it are visible: a half-lidded grey eye with silver-grey lashes, its iris drawn as thin '
                'looped wire like the curves of a paperclip; nothing else of her is in the frame. The block of city stays exactly as in <Video 1>.']),
    ('061', 'clip_hand_kf_grey_h3_v2'): dict(seed=2610017161, label='羂索的巨手→回形针最大化器的少女之手（关键帧第 1/14 帧：纤细的手、银灰指甲、黑袖口回形针链）',
        subjects=[('CLIP2', 'grey', "the giant hand reaching in from the upper right (Kenjaku's hand; only the hand and wrist are in the frame)")],
        preserve='the black-and-white manga rendering, the city skyline, the mountains, the tall black pillar, the gesture of the hand and the still camera',
        shots=[(None, 'black-and-white manga style: a city skyline with mountains behind it and a tall black pillar rising from the middle; the '
                      'giant hand of <A> reaches in from the upper right toward the pillar, its long fingers spread as if to pinch out the block '
                      'of city around it.')],
        extras=["Only her hand, her wrist and the hem of her sleeve are in the frame: a slender young woman's hand with long fingers and long "
                'silver-grey nails, and at the wrist the black hem of her wide sleeve with a chain of small paperclips, drawn in black, white and '
                "grey, in place of the large bare man's hand of <Video 1>; nothing else in the frame changes."],
        keyframes=[(kf('kf_061_f001_clip_hand_v2.png'), b2.t(1, '061'), 1, SLEEVE), (kf('kf_061_f014_clip_hand_v2.png'), b2.t(14, '061'), 1, SLEEVE)]),
}
OLD = {'060': 'rogue_h3_v1', '062': 'rogue_grey_h3_v1', '145': 'rogue_grey_h3_v1', '061': 'clip_hand_grey_h3_v1'}

if __name__ == '__main__':
    if '--queue' in sys.argv:
        import json
        import review_queue
        q = json.loads((PROD / 'review/queue.json').read_text(encoding='utf-8'))
        picked = [tuple(a.split('@')) for a in sys.argv[1:] if '@' in a] or list(b2.JOBS)
        for uid, old in OLD.items():
            if uid not in {u for u, _ in picked}:
                continue
            for e in q['entries']:
                if e['unit'] == uid and e['revision'] == old and not e.get('cancelled'):
                    review_queue.cancel(PROD, uid, old, reason='061 的手没有变化，改用关键帧（clip_hand_kf_grey_h3_v2）' if uid == '061' else '羂索改由回形针最大化器演')
        for uid, rev in picked:
            spec = b2.JOBS[(uid, rev)]
            start, end = b2.b1.interval(uid)
            prompt, refs = b2.build(spec['subjects'], spec['preserve'], spec['shots'], spec.get('extras', []), b2.p.snap_frames(end - start),
                                    spec.get('keyframes', ()))
            review_queue.add(PROD, uid, rev, spec['label'], note='羂索改由回形针最大化器（反派 AI 少女）演', when='第十七批（未排期）',
                             script='pipelines/jujutsu/render_batch_0017.py', prompt=prompt, references=refs)
            print('QUEUED', uid, rev, [r.name for r in refs], flush=True)
    else:
        b2.main()
