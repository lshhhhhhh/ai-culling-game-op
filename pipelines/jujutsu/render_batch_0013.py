"""JJK batch 13 - PLANS ONLY: every Yuta unit again with the GPT redesign v3 (registered as 待推理).

User (2026-10-01): “GPT/乙骨的形象有点不好看。我想重新设计一下” -> deliverables/jujutsu/人设/gpt_yuta_v6.png (after v2-v5: logo only in the hair, an unbroken
sword case, a symmetric collar, black instead of purple), then “对，所有乙骨的镜头都变回待推理”.
Each job is the unit's latest plan from its batch with the cast key GPT -> GPT6 (a new key: tinted references are cached per key,
so reusing “GPT” would keep the old design) and the old outfit words updated. Kusakabe's sister (076, 133) is not Yuta: she keeps
the plain GPT girl design (new key GPT_GIRL) instead of Yuta's uniform.
Usage: render_batch_0013.py --queue | render_batch_0013.py UNIT@REV ... (only after the user says to run)
"""
import copy
import sys

import render_batch_0002 as b2
from common import PROD, ROOT

JOBS2 = dict(b2.JOBS)
import render_batch_0003  # noqa: E402
JOBS3 = dict(b2.JOBS)
import render_batch_0007  # noqa: E402
JOBS7 = dict(b2.JOBS)
import render_batch_0010  # noqa: E402
JOBS10 = dict(b2.JOBS)
import render_batch_0011  # noqa: E402
JOBS11 = dict(b2.JOBS)

# v6 = v5 (“这个好看！”, drawn fresh in a square front pose after v3/v4 kept a crooked collar; black-and-white like GPT) with the tie
# recoloured on the CPU to a dark ChatGPT green (the user: “其实领带换成深绿色是不是更符合设定？” -> “非常好，就这个”)
b2.CAST['GPT6'] = (b2.D / 'gpt_yuta_v6.png', 'a young woman with very long wavy white hair, a small ahoge, lavender eyes and a small white knot-shaped hair ornament, in an off-white blazer-style jujutsu school uniform with a black sailor collar with white stripes, a small dark green necktie, black cuffs and a short black pleated skirt with white stripes, with a katana in a black scabbard')
b2.CAST['GPT_GIRL'] = (ROOT / 'deliverables/lycoris/人设需求/生成_GPT娘_去龙_v1.png', 'a young woman with very long wavy white hair, a small ahoge, lavender eyes and a small white knot-shaped hair ornament, in the dress shown in her reference picture')
b2.NAMES.update({'GPT6': 'GPT', 'GPT_GIRL': 'GPT'})
b2.LOG = PROD / 'batch_0013'
b2.AUTH_REQUEST = '用户（2026-10-01 晚）：GPT/乙骨重新设计（gpt_yuta_v3）；“对，所有乙骨的镜头都变回待推理”'

OUTFIT = [('in her white shirt and black trousers', 'in her off-white uniform jacket and black pleated skirt'),
          ('in a white shirt and black trousers', 'in an off-white uniform jacket and a black pleated skirt')]
# unit -> (source jobs, its latest revision there, new revision)
YUTA = {
    '006-016a': (JOBS2, 'gpt_h3_v1', 'gpt6_h3_v1'), '016b-019': (JOBS2, 'gpt_h3_v1', 'gpt6_h3_v1'),
    '048': (JOBS2, 'gpt_red_h3_v1', 'gpt6_red_h3_v1'), '040': (JOBS3, 'gpt_ukiyoe_h3_v1', 'gpt6_ukiyoe_h3_v1'),
    '042': (JOBS3, 'gpt_h3_v1', 'gpt6_h3_v1'), '092': (JOBS7, 'gpt_doubao_tint_h3_v2', 'gpt6_doubao_tint_h3_v3'),
    '126': (JOBS10, 'gpt_grey_h3_v1', 'gpt6_grey_h3_v1'), '058': (JOBS11, 'lineup7_h3_v2', 'lineup7_gpt6_h3_v3'),
    '090': (JOBS11, 'gpt_klimt_bomb_h3_v2', 'gpt6_klimt_bomb_h3_v3'),
}
SISTER = {'076': (JOBS10, 'gpt_takeru_h3_v1', 'gptgirl_takeru_h3_v1'), '133': (JOBS10, 'liang_gpt_h3_v1', 'liang_gptgirl_h3_v1')}


def recast(spec, new_key, seed_offset):
    spec = copy.deepcopy(spec)
    spec['subjects'] = [(new_key if key == 'GPT' else key, *rest) for key, *rest in spec['subjects']]
    def words(text):
        for a, b in OUTFIT:
            text = text.replace(a, b)
        return text
    spec['shots'] = [(s, words(text)) for s, text in spec['shots']]
    spec['extras'] = [words(e) for e in spec.get('extras', [])]
    spec['seed'] += seed_offset
    label = spec['label']
    if new_key != 'GPT6':
        label += '（妹妹用 GPT 娘原设）'
    elif 'GPT（二设）' in label:
        label = label.replace('GPT（二设）', 'GPT（新设计v6）')
    elif '→GPT' in label:
        label = label.replace('→GPT', '→GPT（新设计v6）', 1)
    else:
        label += '（乙骨换 GPT 新设计v6）'
    spec['label'] = label
    return spec


b2.JOBS = {}
for uid, (jobs, old, new) in YUTA.items():
    b2.JOBS[(uid, new)] = recast(jobs[(uid, old)], 'GPT6', 100000)
for uid, (jobs, old, new) in SISTER.items():
    b2.JOBS[(uid, new)] = recast(jobs[(uid, old)], 'GPT_GIRL', 100000)

if __name__ == '__main__':
    if '--queue' in sys.argv:
        import review_queue
        for (uid, rev), spec in b2.JOBS.items():
            start, end = b2.b1.interval(uid)
            prompt, refs = b2.build(spec['subjects'], spec['preserve'], spec['shots'], spec.get('extras', []), b2.p.snap_frames(end - start),
                                    spec.get('keyframes', ()))
            review_queue.add(PROD, uid, rev, spec['label'], note='乙骨换新设计 gpt_yuta_v6（你：所有乙骨的镜头都变回待推理；深绿领带“非常好，就这个”）' if 'GPT6' in str(spec['subjects'])
                             else '日下部的妹妹改用 GPT 娘原设（不穿乙骨的制服）', when='第十三批（未排期）',
                             script='pipelines/jujutsu/render_batch_0013.py', prompt=prompt, references=refs)
            print('QUEUED', uid, rev, [r.name for r in refs], flush=True)
    else:
        b2.main()
