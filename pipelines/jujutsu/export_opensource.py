"""Build the open-source release folder of the JJK S3 OP parody (CPU only, rebuildable).

User (2026-10-02): “我觉得这个项目也可以在github开源。我们总结一下我们遇到的难点和解决方案”, then: a separate repository; the
designs we drew (AI girls and the cartoons of real people) published with their prompts; community designs, as before, not.
Copies the pipeline code (pipelines/jujutsu and the shared modules it imports from pipelines/anime_op), our character designs with
their Codex prompts, every final unit's prompt (H3) or recipe (Codex + code), one ComfyUI workflow and the plan data. Excludes all
video, original frames and anything drawn on them (keyframes, stills, paintings), community designs, downloaded photos, the user's
photos, logs and secrets. Absolute workspace paths are rewritten repo-relative, and the build fails if any local path, username, key or
signed URL is left in a text file. README.md, docs/ and LICENSE are hand-written and not touched.
Usage: export_opensource.py
"""
import csv
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROD = ROOT / 'assets/jujutsu/op1_v1'
OUT = ROOT / 'opensource/ai-culling-game-op'
JJK = ROOT / 'pipelines/jujutsu'
SHARED = ROOT / 'pipelines/anime_op'
DESIGN_DIR = ROOT / 'deliverables/jujutsu/人设'
FINAL = ROOT / 'deliverables/jujutsu/final_v1/final_validation.json'
WORKFLOW = PROD / 'shots/130/ds_dance_kf_h3_v3/workflow.json'
LEAKS = [r'\b[A-Z]:[\\/]+(?!Program Files|Windows[\\/]+Fonts)', r'\blsh\b', r'sk-or-v1-[A-Za-z0-9]', r'@gmail\.com',
         r'X-Amz-(?:Credential|Signature)=', r'Bearer [A-Za-z0-9]{12}']

# our designs in the final cut: file stem -> (role in the OP, cast, note for the cast table)
DESIGNS = {
    'gpt_yuta_v6': ('乙骨忧太', 'GPT', '米白西装外套、黑色水手领与百褶裙、深绿色小领带，发饰是结形花饰；基于本系列原创的 GPT 娘'),
    'gpt_yuta_v6_tights': ('乙骨忧太（042）', 'GPT', '同上，只在一个仰拍镜头里加了黑色连裤袜'),
    'gemini_maki_v4': ('禅院真希', 'Gemini', '黑色水手服、Google 四色渐变领结、高马尾、眼镜、长刀；基于社区 Gemini 娘'),
    'gemini_mai_v3': ('禅院真依（也演乌鹭亨子）', 'Gemini', '黑色水手服长袖长裙、不对称短发、左轮；基于社区 Gemini 娘'),
    'paperclip_maximizer_v2': ('羂索', '回形针最大化器', '原创反派 AI 少女，取自“回形针最大化器”思想实验'),
    'bard_twins_mother_v1': ('真希真依的母亲', 'Bard', 'Gemini 的前身'),
    'glm_eso_v1': ('坏相', 'GLM 的妹妹', '基于社区 GLM 娘'),
    'glm_kechizu_v1': ('血涂', 'GLM 的小妹', '基于社区 GLM 娘'),
    'doubao_zenin_ogi_v1': ('禅院扇', '豆包', '黑纹付袴、火焰刀；3D 画风，基于豆包官方头像'),
    'doubao_zenin_jinichi_v1': ('禅院甚壹', '豆包', '深色和服、巨石拳；同上'),
    'doubao_zenin_ranta_v1': ('禅院兰太', '豆包', '白道服红腰带、眼纹头带；同上'),
    'doubao_zenin_naoya_v1': ('禅院直哉', '豆包', '同上'),
    'doubao_zenin_chojuro_v1': ('禅院长寿郎', '豆包', '同上'),
    'doubao_zenin_nobuaki_v1': ('禅院信朗', '豆包', '同上'),
    'doubao_zenin_naobito_v1': ('禅院直毘人', '豆包', '同上'),
    'tengen_jensen_v1': ('天元', '黄仁勋（卡通）', '二创卡通形象'),
    'ma_huateng_v3': ('夜蛾正道', '马化腾（卡通）', '二创卡通形象；参考照片：Wikimedia Commons「马化腾 Pony Ma 2019.jpg」，'
                      '中国新闻网，CC BY 3.0（照片本身不在仓库里）'),
    'musk_gakuganji_v1': ('乐岩寺嘉伸', '马斯克（卡通）', '二创卡通形象'),
    'liang_kusakabe_v1': ('日下部笃也', '梁文锋（卡通）', '二创卡通形象'),
    'ma_yun_v1': ('推轮椅的人（133）', '马云（卡通）', '二创卡通形象；参考照片：Wikimedia Commons「Ma Yun (2017-10-19).jpg」，'
                  '俄罗斯总统新闻处（kremlin.ru），CC BY 4.0（照片本身不在仓库里）'),
}
# community designs: credited by name only, no images (as in the previous repository)
COMMUNITY = [('虎杖悠仁、虎杖香织', 'DeepSeek（也有 Q 版 DeepSeek 演路人群像）'), ('伏黑惠、日车宽见', 'Claude'), ('熊猫', '混元 HY'),
             ('九十九由基', 'Mistral'), ('星绮罗罗', 'Spark 讯飞星火'), ('秤金次', 'Kimi'), ('胀相', 'GLM'), ('高羽史彦', 'MiniMax'),
             ('雷吉·斯塔', 'Grok'), ('石流龙、伏黑津美纪、日下部的妹妹', 'Qwen')]
# the Jensen sheet was made with a one-off command; its prompt is taken from the run log
JENSEN_PROMPT = ('Jensen Huang cast as Tengen, the ancient guardian who keeps the great barrier running: his recognisable short swept-back '
                 'black-and-grey hair, warm confident smile and adult proportions, wearing his signature black leather jacket and dark '
                 'trousers, with a long pale-white Tengen-style hooded robe draped over his shoulders and falling to the floor (hood down, so '
                 'the face and hair are clearly visible). A subtle thin green trim along the robe\'s edges. Clean anime line art and flat cel '
                 'shading in the same style as Image 1, not photorealistic, not a caricature with exaggerated features.')


# the painting series, the user (2026-10-02): “可以把我们生成的名画系列也上传吗”. Codex's own pictures only (no original pixels): the
# whole paintings of the pan shots cut back from Codex's 2:3 canvas exactly as the renders did, 088 re-lit as in the film. Shots made
# by H3 (075 Monet, 077-080 Munch) are left out: H3's licence limits where its outputs may be published.
STILLS = ROOT / 'deliverables/jujutsu/静帧'
GALLERY = [  # (output, Codex picture, original painting it was cut to (for the 2:3 crop) or None, title, text)
    ('040_kuniyoshi_1.png', 'pan_040_painting1_gpt_v1.png', 'pan_040_painting1_src.png', '040 · 歌川国芳风武者绘（一）',
     '乙骨 → GPT。原片是镜头沿着画竖直往上摇的长卷，整幅由 Codex 重画后按原轨迹重新“拍”。'),
    ('040_kuniyoshi_2.png', 'pan_040_painting2_gpt_v1.png', 'pan_040_painting2_src.png', '040 · 歌川国芳风武者绘（二）',
     '同一个镜头的后半段，镜头往下摇。'),
    ('076_kollwitz.png', 'pan_076_sketch_qwen_dsq_v1.png', 'pan_076_sketch_src.png', '076 · 珂勒惠支风铅笔素描',
     '日下部的妹妹与儿子 → 千问与 Q 版 DeepSeek，只用铅笔灰。'),
    ('085_yokoo.png', 'still_085_seg1_v1.png', None, '085 · 横尾忠则风夜晚 Y 字路口',
     '伏黑惠 → Claude 的背影。'),
    ('088_original.png', 'pan_088_deepseek_v3.png', None, '088 · 原创：双手合十举过头顶',
     '原片这个镜头太难换，改成原创：DeepSeek 双手合十举过头顶，镜头从下往上摇；按成片的方式逐行重新打光（品红渐变到紫）。'),
    ('090_klimt.png', 'pan_090_painting_gpt_v2.png', 'pan_090_painting_src.png', '090 · 克林姆特《吻》风',
     '乙骨 → GPT，全身换成她的制服。'),
]


def gallery():
    import sys
    import numpy as np
    from PIL import Image
    sys.path.insert(0, str(JJK))
    import pan_088
    rows = []
    for out, name, orig, title, text in GALLERY:
        im = Image.open(STILLS / name).convert('RGB')
        if orig:  # the renders resized Codex's 2:3 picture to (w, h + pad) and took the middle h rows
            w, h = Image.open(STILLS / orig).size
            pad = max(0, round(w * 1.5) - h)
            im = im.resize((w, h + pad), Image.LANCZOS).crop((0, pad // 2, w, pad // 2 + h))
        if out.startswith('088'):
            tall = np.asarray(im.resize((1024, 1536), Image.LANCZOS)).astype(np.float32)
            im = Image.fromarray(pan_088.grade(tall, strength=0.7).astype(np.uint8))
        (OUT / 'gallery').mkdir(parents=True, exist_ok=True)
        im.save(OUT / 'gallery' / out, optimize=True)
        rows.append(f'## {title}\n\n{text}\n\n<img src="{out}" width="{480 if im.height > im.width else 720}">\n')
    write(OUT / 'gallery/README.md', '\n'.join([
        '# 名画系列', '',
        '原版 OP 里有一组致敬名画的镜头（浮世绘武者绘、克林姆特、珂勒惠支、横尾忠则……）。我们把画里的人物换成 AI 娘，整幅画交给 Codex（GPT 生图）重画，'
        '再用代码按原片的镜头运动重新“拍”出来，做法见[思路总结](../docs/思路总结.md)第二节。这里是 Codex 画的整幅画（摇镜头的长画已裁回实际画幅）。', '',
        '这些画是照着原版 OP 的画面重画的二创图，构图属于原作，不在本仓库的 CC BY-NC 许可之内；如有权利方要求会删除。'
        '同组里的莫奈花园（075）和蒙克《呐喊》（077-080）两个镜头由视频模型 H3 生成，受其许可限制没有放在这里。', '',
        *rows]))
    print('gallery:', len(rows), 'pictures', flush=True)


def rel(text):
    """Workspace-absolute paths -> repo-relative, forward slashes."""
    for root in (str(ROOT), str(ROOT).replace('\\', '/'), str(ROOT).replace('\\', '\\\\')):
        text = text.replace(root + ('\\\\' if '\\\\' in root else '\\' if '\\' in root else '/'), '').replace(root, '.')
    return text


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def shared_modules():
    """The pipelines/anime_op modules the JJK code imports, followed through their own imports."""
    local, shared = {p.stem for p in JJK.glob('*.py')}, {p.stem for p in SHARED.glob('*.py')}
    need, todo, seen = set(), list(JJK.glob('*.py')), set()
    while todo:
        f = todo.pop()
        if f in seen:
            continue
        seen.add(f)
        for m in re.findall(r'^\s*(?:import|from)\s+([A-Za-z_][A-Za-z0-9_]*)', f.read_text(encoding='utf-8-sig'), re.M):
            if m in local:
                todo.append(JJK / f'{m}.py')
            elif m in shared:
                need.add(m)
                todo.append(SHARED / f'{m}.py')
    return sorted(need)


def design_prompts():
    """stem -> full Codex prompt, as each design script sends it."""
    import importlib
    import sys
    sys.path.insert(0, str(JJK))
    out = {}
    for n in ('0002', '0004', '0005', '0006', '0007'):
        m = importlib.import_module(f'codex_designs_{n}')
        items = [(a, b, c) for a, b, c in m.DESIGNS] + [(a, b, c) for a, b, c in getattr(m, 'EDITS', [])]
        for name, x, y in items:
            prompt = x if isinstance(x, str) else y
            if n in ('0002', '0004'):
                prompt = f'{prompt} {m.SHEET}'
            elif n == '0005':
                prompt = prompt + ('Do not create or modify any other files.' if name.endswith(('_v3.png', '_v4.png')) else m.SHEET)
            elif n == '0006' and (name, x, y) in [(a, b, c) for a, b, c in m.DESIGNS]:
                prompt = f'{prompt}{m.SHEET}'
            out[name[:-4]] = prompt
    out['tengen_jensen_v1'] = JENSEN_PROMPT
    # v6 is v5 with the necktie recoloured dark green in code (no new generation)
    out['gpt_yuta_v6'] = out['gpt_yuta_v5'] + '\n\n（v6：在 v5 的图上用代码把领带改成深绿色，其余与 v5 相同。）'
    return out


def method(part, versions):
    """(method, script, prompt text, prompt folder) of one unit of the final cut."""
    if part['version'] == 'source':
        return '原片', '', '', ''
    v = versions[(part['unit'], part['version'])]
    prompt = v.get('prompt') or {}
    src = prompt.get('source') or '' if isinstance(prompt, dict) else ''
    if part['version'].startswith('plan') or not src:
        return '原片', '', '', ''
    if src.endswith('workflow.json'):
        text = (Path(src).parent / 'prompt.txt').read_text(encoding='utf-8')
        return ('H3 视频编辑＋关键帧' if 'keyframe' in text else 'H3 视频编辑'), '', text, 'h3'
    rec = read(src)
    if rec.get('kind') == 'h3_multistage':
        texts = []
        for part_ in rec['parts']:
            pt = Path(part_['workflow']).parent / 'prompt.txt'
            if pt.exists():
                texts.append(f"### {part_['label']}\n\n{pt.read_text(encoding='utf-8').strip()}\n")
        texts.append(f"### 合成\n\n{rec.get('note', '')}\n")
        return 'H3 分段生成＋代码合成', '', '\n'.join(texts), 'h3'
    if rec.get('kind') == 'original_copy':
        return '原片', '', '', ''
    builder = Path(rec.get('builder', '')).name
    return 'Codex 生图＋代码合成', builder, rec.get('recipe_text', ''), 'cpu'


def main():
    for item in ('pipelines', 'data', 'prompts', 'workflows', 'cast', 'gallery'):
        shutil.rmtree(OUT / item, ignore_errors=True)
    gallery()
    # code
    for f in sorted(list(JJK.glob('*.py')) + list(JJK.glob('*.ps1'))):
        write(OUT / 'pipelines/jujutsu' / f.name, rel(f.read_text(encoding='utf-8-sig')))
    mods = shared_modules()
    for m in mods:
        write(OUT / 'pipelines/anime_op' / f'{m}.py', rel((SHARED / f'{m}.py').read_text(encoding='utf-8-sig')))
    write(OUT / 'pipelines/anime_op/review_school_op.html', rel((SHARED / 'review_school_op.html').read_text(encoding='utf-8-sig')))
    print('code:', len(list(JJK.glob('*.py'))), 'JJK scripts,', len(mods), 'shared modules', flush=True)
    # designs
    prompts = design_prompts()
    rows = []
    for stem, (role, cast, note) in DESIGNS.items():
        shutil.copy2(DESIGN_DIR / f'{stem}.png', (OUT / 'cast/designs').mkdir(parents=True, exist_ok=True) or OUT / 'cast/designs' / f'{stem}.png')
        write(OUT / 'cast/designs' / f'{stem}.prompt.txt', rel(prompts[stem]).strip() + '\n')
        rows.append(f'| <img src="designs/{stem}.png" width="220"> | {role} | **{cast}** | {note}；[提示词](designs/{stem}.prompt.txt) |')
    community = '\n'.join(f'| {role} | **{cast}** |' for role, cast in COMMUNITY)
    write(OUT / 'cast/README.md', '\n'.join([
        '# 演员表', '',
        '原作角色换成各家大模型的拟人 AI 娘；年长的管理层换成 AI 圈企业家的卡通形象，大反派换成虚构的 AI 少女。人设图只决定外观，站位、动作和镜头都跟原片走。', '',
        '## 本作绘制的设定图', '',
        '以下设定图由 Codex（GPT 生图）绘制，图片和完整生图提示词都在 [designs/](designs/)。生图时用到的社区原设图、原片截帧和参考照片不在仓库里。', '',
        '| 设定图 | 原作角色 | 演员 | 说明 |', '|---|---|---|---|', *rows, '',
        '## 使用社区原设的角色', '',
        '这些角色直接用社区流行的 AI 娘设计（例如 DeepSeek 娘由社区共同完成设计），原图不在仓库里。', '',
        '| 原作角色 | 演员 |', '|---|---|', community, '',
        '企业家卡通形象均为二创玩梗，与本人及其公司无关。', '']))
    # per-unit prompts / recipes
    final = read(FINAL)
    manifest = read(PROD / 'review/manifest.json')
    versions = {(s['id'], v['id']): v for s in manifest['shots'] for v in s['versions']}
    index = []
    for part in final['parts']:
        how, script, text, folder = method(part, versions)
        name = ''
        if text:
            name = f"{folder}/{part['unit']}.txt"
            write(OUT / 'prompts' / name, rel(text).rstrip() + '\n')
        index.append(dict(unit=part['unit'], start_frame=part['start_frame'], frames=part['frames'], method=how,
                          script=script, prompt=name, label=part['label'] if how != '原片' else '原片'))
    with (OUT / 'prompts/index.csv').open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(index[0]))
        w.writeheader()
        w.writerows(index)
    counts = {}
    for row in index:
        counts[row['method']] = counts.get(row['method'], 0) + 1
    print('units by method:', counts, flush=True)
    # workflow and data
    write(OUT / 'workflows/h3_ref2va_keyframes.json', rel(WORKFLOW.read_text(encoding='utf-8-sig')))
    plan = read(PROD / 'unit_plan.json')
    for key in list(plan):
        if 'source' in key and isinstance(plan[key], str):
            plan[key] = '<your NCOP file of Jujutsu Kaisen S3 (2160 frames, 24000/1001)>'
    write(OUT / 'data/unit_plan.json', rel(json.dumps(plan, ensure_ascii=False, indent=1)))
    write(OUT / 'data/casting.json', rel((PROD / 'casting.json').read_text(encoding='utf-8-sig')))
    # leak check over every text file
    bad = []
    for f in OUT.rglob('*'):
        if f.is_file() and f.suffix in ('.py', '.ps1', '.html', '.json', '.txt', '.csv', '.md'):
            text = f.read_text(encoding='utf-8-sig')
            for pat in LEAKS:
                for m in re.finditer(pat, text):
                    bad.append(f'{f.relative_to(OUT)}: {text[max(0, m.start() - 40):m.end() + 40]!r}')
    if bad:
        raise SystemExit('LEAKS:\n' + '\n'.join(bad[:40]) + f'\n... {len(bad)} in all')
    size = sum(f.stat().st_size for f in OUT.rglob('*') if f.is_file() and '.git' not in f.parts)
    print('DONE', OUT, f'{size / 1e6:.1f} MB', flush=True)


if __name__ == '__main__':
    main()
