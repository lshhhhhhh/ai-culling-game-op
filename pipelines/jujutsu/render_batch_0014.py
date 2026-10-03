"""JJK batch 14 - PLANS ONLY: every Maki / Mai unit with the redrawn Gemini twins (registered as 待推理).

User (2026-10-01): “gemini姐妹的人设我也想重画。现在这个身体太壮了不好看” -> gemini_maki_v3 / gemini_mai_v2 (slender, square front pose),
then “换成这样的黑色制服如何？然后领结是GOOGLE的渐变色……真依的话，可以是长袖+长裙” -> gemini_maki_v4 / gemini_mai_v3 (black sailor
uniform, Google-gradient bow; Mai with long sleeves and a long skirt), approved: “可以，非常好”.
Each job is the unit's latest plan (batch 11; 058 from batch 13, which already has GPT v6) with the twins' keys replaced by new keys
GEM_MAKI4 / GEM_MAI3 (tinted references are cached per key) and outfit words updated. 123 (Uro) also takes the new Mai design, as the
user had said “123可以用gemini新形象”.
Usage: render_batch_0014.py --queue | render_batch_0014.py UNIT@REV ... (only after the user says to run)
"""
import copy
import sys

import render_batch_0013 as b13  # noqa: F401  (imports batches 2, 3, 7, 10, 11; keeps their job tables)
import render_batch_0002 as b2
from common import PROD

JOBS13 = dict(b2.JOBS)
JOBS11 = b13.JOBS11

BOW = 'a large bow in Google\'s blue, red, yellow and green gradient'
b2.CAST['GEM_MAKI4'] = (b2.D / 'gemini_maki_v4.png', 'a slender young woman with long purple-to-pink gradient hair in a high ponytail, cat ears, amber eyes and thin rectangular glasses, in a black sailor uniform - a black collar edged with three white stripes, ' + BOW + ', short sleeves and a black pleated skirt - holding a katana')
b2.CAST['GEM_MAI3'] = (b2.D / 'gemini_mai_v3.png', 'a slender young woman with a shoulder-length asymmetric purple-to-pink bob, cat ears and amber eyes, no glasses, in a black sailor uniform - a black collar edged with three white stripes, ' + BOW + ', long sleeves and a long black pleated skirt - holding a revolver')
b2.NAMES.update({'GEM_MAKI4': 'Gemini', 'GEM_MAI3': 'Gemini'})
b2.LOG = PROD / 'batch_0014'
b2.AUTH_REQUEST = '用户（2026-10-01 晚）：Gemini 姐妹重画（黑色水手服、Google 渐变领结；真依长袖长裙）“可以，非常好”；有方案的镜头都是待推理'

KEYS = {'GEM_MAKI2': 'GEM_MAKI4', 'GEM_MAI': 'GEM_MAI3'}
WORDS = [('in her dark combat uniform', 'in her black sailor uniform'),
         ('in dark uniform trousers and boots', 'in black socks and shoes below a black pleated skirt'),
         ('in her dark sleeveless combat top', 'in her black sailor uniform')]
# unit -> (source jobs, revision there, new revision)
TWINS = {
    '035': (JOBS11, 'gemini_maki2_h3_v1', 'gemini_maki4_h3_v1'), '041': (JOBS11, 'gemini_mai_ds_h3_v2', 'gemini_mai3_ds_h3_v3'),
    '046': (JOBS11, 'gemini_mai_red_h3_v2', 'gemini_mai3_red_h3_v3'), '064': (JOBS11, 'gemini_maki2_h3_v1', 'gemini_maki4_h3_v1'),
    '065-067': (JOBS11, 'gemini_maki2_h3_v1', 'gemini_maki4_h3_v1'), '072': (JOBS11, 'gemini_twins2_h3_v1', 'gemini_twins4_h3_v1'),
    '083': (JOBS11, 'gemini_twins2_h3_v1', 'gemini_twins4_h3_v1'), '099': (JOBS11, 'gemini_maki2_tint_h3_v1', 'gemini_maki4_tint_h3_v1'),
    '134': (JOBS11, 'gemini_maki2_red_h3_v1', 'gemini_maki4_red_h3_v1'), '135': (JOBS11, 'gemini_mai_h3_v1', 'gemini_mai3_h3_v1'),
    '074': (JOBS11, 'gemini_twin_babies_h3_v1', 'gemini_twin_babies4_h3_v1'), '123': (JOBS11, 'gemini_uro_h3_v2', 'gemini_mai3_uro_h3_v3'),
    '058': (JOBS13, 'lineup7_gpt6_h3_v3', 'lineup7_gpt6_maki4_h3_v4'),
}


def recast(spec):
    spec = copy.deepcopy(spec)
    spec['subjects'] = [(KEYS.get(key, key), *rest) for key, *rest in spec['subjects']]
    def words(text):
        for a, b in WORDS:
            text = text.replace(a, b)
        return text
    spec['shots'] = [(s, words(text)) for s, text in spec['shots']]
    spec['extras'] = [words(e) for e in spec.get('extras', [])]
    spec['seed'] += 200000
    spec['label'] = spec['label'].replace('Gemini新二设', 'Gemini黑水手服').replace('Gemini姐妹新二设', 'Gemini姐妹黑水手服').replace('Gemini新形象', 'Gemini黑水手服（真依造型）')
    if '黑水手服' not in spec['label']:
        spec['label'] += '（Gemini姐妹换黑水手服设计）'
    return spec


b2.JOBS = {(uid, new): recast(jobs[(uid, old)]) for uid, (jobs, old, new) in TWINS.items()}

if __name__ == '__main__':
    if '--queue' in sys.argv:
        import json
        import review_queue
        q = json.loads((PROD / 'review/queue.json').read_text(encoding='utf-8'))
        for uid, (jobs, old, new) in TWINS.items():
            for e in q['entries']:
                if e['unit'] == uid and e['revision'] == old and not e.get('cancelled'):
                    review_queue.cancel(PROD, uid, old, reason='Gemini 姐妹换新设计（黑水手服）')
        for (uid, rev), spec in b2.JOBS.items():
            start, end = b2.b1.interval(uid)
            prompt, refs = b2.build(spec['subjects'], spec['preserve'], spec['shots'], spec.get('extras', []), b2.p.snap_frames(end - start),
                                    spec.get('keyframes', ()))
            review_queue.add(PROD, uid, rev, spec['label'], note='Gemini 姐妹换新设计（黑色水手服、Google 渐变领结；真依长袖长裙）', when='第十四批（未排期）',
                             script='pipelines/jujutsu/render_batch_0014.py', prompt=prompt, references=refs)
            print('QUEUED', uid, rev, [r.name for r in refs], flush=True)
    else:
        b2.main()
