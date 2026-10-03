"""JJK character table: original characters (frames from the OP) next to our parody cast, served at http://127.0.0.1:8769/casting.

User (2026-10-01, after reviewing every unit): “很多角色没有被识别出来，很多没有人物的镜头需要独立设计。这样，我们做一个人物表，需要原版
人物（包含照片）和我们的二创人物对照”. Three sections: identified roles, people still to identify or cast, and shots without people
that need their own design. Images are embedded (one self-contained file: PROD/casting_review.html); unit status comes from
review/review_state.json, the user's notes are quoted as written.
"""
import base64
import html
import io
import json
import subprocess

from PIL import Image

from common import PROD, ROOT, p

A, D = ROOT / 'assets/人设', ROOT / 'deliverables/jujutsu/人设'
UNITS = PROD / 'review/source_units'
DESIGN = {
    'DeepSeek': A / '鲸鱼娘.png', 'DeepSeek（宿傩纹）': A / '鲸鱼娘.png', 'Claude': A / 'claude娘.png', 'GPT（二设）': D / 'gpt_yuta_v6.png',
    'Gemini·真希（新二设）': D / 'gemini_maki_v4.png', 'Gemini·真依（新二设）': D / 'gemini_mai_v3.png', 'Gemini（社区原设）': A / 'GEMINI娘.jpg', 'HY 混元': A / 'HY娘.png',
    'Mistral': A / 'mistral娘.jpg', 'GLM': A / 'GLM娘.png', '黄仁勋（卡通）': D / 'tengen_jensen_v1.png', '马化腾（卡通）': D / 'ma_huateng_v3.png',
    '马斯克（卡通）': D / 'musk_gakuganji_v1.png', '梁文锋（卡通）': D / 'liang_kusakabe_v1.png', 'MiniMax': A / 'minimax娘.jpg',
    'Grok': A / 'grok.jpg', 'Kimi': A / 'KIMI娘.png', 'Spark 讯飞星火': A / 'spark娘.png', 'Qwen': A / 'qwen娘.jpg',
    '回形针最大化器（反派 AI 少女）': D / 'paperclip_maximizer_v2.png', '豆包·扇': D / 'doubao_zenin_ogi_v1.png', '豆包·甚壹': D / 'doubao_zenin_jinichi_v1.png',
    '豆包·兰太': D / 'doubao_zenin_ranta_v1.png', 'Q版 DeepSeek': A / '鲸鱼娘-小.jpg',
    '豆包（直哉／长寿郎／信朗／直毘人）': [D / f'doubao_zenin_{n}_v1.png' for n in ('naoya', 'chojuro', 'nobuaki', 'naobito')],
    'GLM 的两个妹妹（坏相／血涂）': [D / 'glm_eso_v1.png', D / 'glm_kechizu_v1.png'], 'Bard（Gemini 的前身）': D / 'bard_twins_mother_v1.png',
    'GPT（妹妹）＋Q版 DeepSeek（武）': [ROOT / 'deliverables/lycoris/人设需求/生成_GPT娘_去龙_v1.png', A / '鲸鱼娘-小.jpg'], 'DeepSeek（母亲）＋Q版 DeepSeek（婴儿）': [A / '鲸鱼娘.png', A / '鲸鱼娘-小.jpg'],
    'Copilot（丽美）': ROOT / 'assets/fate_zero/op1_v1/character_designs/outputs/copilot_aoi_v1.png',
    'Grok＋Mistral': [A / 'grok.jpg', A / 'mistral娘.jpg'],
}
L = (90, 490)  # 058 line-up: vertical extent of the seven figures
# (original name, [(unit, local frame, crop box or None)], units, cast, note)
ROLES = [
    ('虎杖悠仁', [('058', 15, (305, L[0], 440, L[1])), ('082', 5, None)], '001 020-026a 041(后半) 049 050(左) 058 073(婴儿) 082 088 094(第三段)', 'DeepSeek', '073 婴儿按你的备注用 Q 版 DeepSeek；088 你指出是虎杖'),
    ('宿傩（夺舍虎杖）', [('054', 2, None)], '054', 'DeepSeek（宿傩纹）', '按你的备注“被宿傩夺舍的虎杖”'),
    ('伏黑惠', [('058', 15, (712, L[0], 852, L[1])), ('030-031', 2, None)], '030-031 032-034 036 058 085 098(第二段) 143', 'Claude', '036、143 按你的备注；085 Y 字路口与丽美相遇'),
    ('乙骨忧太', [('058', 15, (172, L[0], 305, L[1])), ('042', 9, None)], '006-016a 016b-019 040 042 048 058 090 092(第一段) 126', 'GPT（二设）', '126 按你的备注'),
    ('禅院真希', [('058', 15, (38, L[0], 172, L[1])), ('099', 2, None)], '035 058 064 065-067 072(左) 074(婴儿) 083(左) 099 134 135', 'Gemini·真希（新二设）', '姐妹都用 Gemini、重新设计并做出小差异（你的意见）：高马尾＋眼镜＋东京校制服＋长刀'),
    ('禅院真依', [('041', 5, None), ('046', 5, None)], '041(前半) 046 072(右) 074(婴儿) 083(右)', 'Gemini·真依（新二设）', '不对称齐肩短发、无眼镜、京都校制服长裙、左轮手枪'),
    ('熊猫', [('037-038', 20, None), ('098', 14, None)], '037-038 044 071 075 098(第三段)', 'HY 混元', '071 替换失败（你说熊猫的动作和人走路不同）'),
    ('九十九由基', [('058', 15, (598, L[0], 715, L[1])), ('043', 5, None)], '043 055 058 101(第三段) 116', 'Mistral', '116 按你的备注'),
    ('胀相', [('058', 15, (850, L[0], 1002, L[1])), ('045', 5, None)], '026b-029 045 047 058 094(第一段)', 'GLM', ''),
    ('天元', [('058', 15, (440, L[0], 598, L[1])), ('059', 10, None)], '058 059', '黄仁勋（卡通）', ''),
    ('夜蛾正道', [('091', 4, None), ('052', 1, None)], '039 052 075 091', '马化腾（卡通）', '052 你说像管理层人物：是倒躺的夜蛾'),
    ('乐岩寺嘉伸', [('093', 3, None)], '093 124-125', '马斯克（卡通）', '124-125 按你的识别（原先误做成羂索）'),
    ('日下部笃也', [('095-097', 3, None)], '095-097 133', '梁文锋（卡通）', '133 推轮椅的是他（你的识别）'),
    ('日车宽见', [('094', 10, None), ('086', 5, None)], '086 094(第二段)', 'Claude', '094 你说 Claude 那段保持立绘姿势没动'),
    ('高羽史彦', [('081', 10, None), ('130', 7, None)], '081 087 089 130 141 142', 'MiniMax', '141 按你的识别；142 是同一段的惊叫'),
    ('雷吉·斯塔', [('106', 4, None), ('098', 2, None)], '098(第一段) 106', 'Grok', '106 身后的小弟你说也要换'),
    ('秤金次', [('101', 1, None), ('111b-114', 5, None)], '101(第一段) 111b-114 136-138', 'Kimi', ''),
    ('星绮罗罗', [('109-111a', 10, None), ('101', 5, None)], '101(第二段) 109-111a 136-138', 'Spark 讯飞星火', ''),
    ('石流龙', [('121-122', 8, None)], '121-122', 'Qwen', ''),
    ('乌鹭亨子', [('123', 10, None)], '123', 'Gemini（社区原设）', '和真依重复用 Gemini，待你定'),
    ('羂索', [('060', 5, None), ('062', 7, None), ('145', 15, None)], '060 061（手） 062 063（眼） 145', '回形针最大化器（反派 AI 少女）',
     '原来的“初代失控AI”长得就是羂索本人（062 只改了 0.4% 的像素），改由回形针最大化器演：她把一块城市隔绝出来，要做成回形针。124-125 原先当成羂索，你说左边像高专管理层老头'),
    ('禅院扇', [('101', 18, None)], '101(最后一段) 115(前排?)', '豆包·扇', ''),
    ('禅院甚壹', [('100', 2, None)], '100 115(前排?)', '豆包·甚壹', ''),
    ('禅院兰太', [('092', 12, None)], '092(第二段)', '豆包·兰太', ''),
    ('坏相、血涂（胀相的弟弟）', [('050', 1, None), ('132', 12, None)], '050(右、中) 132', 'GLM 的两个妹妹（坏相／血涂）', '050 你说右边可换 Claude；132 你说是“出场过两集的杂鱼”——就是这两兄弟'),
    ('伏黑津美纪（伏黑的姐姐）', [('051', 1, None)], '051', 'Qwen', '你说随便找一个；查到是津美纪'),
    ('虎杖香织（虎杖的母亲）', [('073', 3, None)], '073', 'DeepSeek（母亲）＋Q版 DeepSeek（婴儿）', '席勒《死去的母亲》'),
    ('日下部的妹妹与儿子武', [('076', 8, None)], '076 133', 'GPT（妹妹）＋Q版 DeepSeek（武）', '按“角色不够用就让热门角色替换”；133 轮椅上的白发女人'),
    ('真希真依的母亲', [('077-080', 10, None)], '077-080', 'Bard（Gemini 的前身）', '蒙克《呐喊》式，眼睛被黑条遮住'),
    ('丽美、甘井凛', [('085', 4, None)], '084-085', 'Copilot（丽美）', '085 画面里只看得到很小的伏黑，丽美不在画面中'),
    ('死灭回游玩家二人（未查到名字）', [('129', 8, None)], '129', 'Grok＋Mistral', '你说随便安排'),
    ('禅院直哉／长寿郎／信朗／直毘人', [('102', 1, None), ('115', 5, None), ('127', 10, None)], '102 115(前排) 127', '豆包（直哉／长寿郎／信朗／直毘人）', '102 是直哉（你的识别）；115 前排和 127 都是禅院家'),
    ('黑沐死（咒灵）', [('090', 12, None)], '090', '保留原样', '和里香一样是咒灵'),
    ('禅院家的蒙面忍者（无名）', [('128', 7, None), ('131', 10, None)], '115(后排) 128 131', 'Q版 DeepSeek', '无名路人按你的规则'),
]
# (unit, frame, what is there / my guess, the user's note)
UNKNOWN = [
    ('074', 3, '鲁本斯风的两个婴儿（真希与真依）', '还是要替换。'),
    ('086', 5, '杜米埃《三个法官》：左边倒下的人', '左边倒下的角色没有替换'),
    ('101', 12, '第四段：薰衣草色光里的小人影（只有 2 帧）', ''),
    ('106', 4, '雷吉身后的小弟', '后面的小弟也要替换'),
    ('130', 7, '高羽身后的肌肉舞者', '最前面的搞笑艺人（替换minimax），后面应该都是路人角色'),
]
# (unit, frame, the user's note)
NO_PERSON = [
    ('002-004', 7, '需要重新设计不一样的镜头。'), ('053', 2, '没有人物。想想怎么重新设计。'), ('056', 6, '需要重新设计。'),
    ('057', 110, '炸弹的镜头要不要重新设计？'), ('061', 8, '需要重新设计。'), ('063', 17, '需要重新设计。'), ('068', 22, '镜头需要重新设计。'),
    ('070', 14, '需要重新设计。'), ('084', 3, '需要重新设计'), ('103', 8, '需要重新设计。也许可以做一个象征着convolution neural network的镜头？这一个个长方形有点像。'),
    ('104', 3, '需要设计'), ('105', 6, '需要设计。'), ('107', 2, '需要设计'), ('108', 5, '需要设计'), ('117', 6, '需要设计'),
    ('118-120', 10, '需要设计'), ('139', 3, '需要设计'), ('140', 8, '需要设计'), ('144', 6, '没有人物。需要设计'),
]


# my first proposal per shot without people, for discussion with the user (“我们可以一起讨论”)
PROPOSAL = {
    '002-004': '那只手伸过去托住的小圆球，换成一颗发着电路纹光的小芯片（算力的“种子”）；用 Codex 改一帧做关键帧，H3 保留手的动作',
    '053': '回廊不动，院子里那块石头换成一台长满青苔的老式显示器（旧时代的机器）；只有 4 帧，Codex 改静帧即可',
    '056': '黑太阳是全片的核心意象（宿傩之眼）。提议换成一块黑色芯片晶圆，在红底上裂成碎片；关键帧＋H3',
    '057': '片尾落下的炸弹换成一块下坠的显卡（外形同样细长）；标题部分已通过',
    '061': '按你的意见：画面不动，只把巨手换成回形针最大化器的少女之手（她要把这块城市隔绝出来做成回形针）',
    '063': '已定（待推理）：漂在黑暗里的那块城市保留；睁开的眼睛换成回形针最大化器的眼睛（灰色、虹膜是回形针般的细线圈）',
    '068': '云层上悬浮的黑色方碑换成一座巨大的黑色服务器塔，表面一排排状态灯在闪；与 105 呼应',
    '070': '灰白的建筑碎片改成像素／体素碎块在空中解体（数据损坏感）；后半的夜森林保留',
    '084': '横尾忠则 Y 字路口的画风保留，路口那栋高楼改成亮着机柜灯的机房小楼',
    '103': '按你的想法：一层层青色玻璃片做成卷积神经网络的特征图，一个发光的卷积核在上面滑动，一层传到下一层',
    '104': '霓虹城市里的蓝色光束改成数据中心之间的光纤数据流',
    '105': '旧照片色的方碑与尘烟：方碑改成和 068 同款的服务器塔，在沙尘里矗立',
    '107': '燃烧的书和纸改成燃烧的打印论文（只有公式和网络结构图，没有可读文字）',
    '108': '雨中的海面：可以保留；或者让海面下透出成排服务器的灯光',
    '117': '接 116 的 Mistral：红光里那只手换成她的手（袖口与手套跟着改）',
    '118-120': '拼贴里的图块换成 AI 意象：对话气泡、加载转圈、光标、token 网格；不用任何商标',
    '139': '城市上空的蓝色光柱（结界）改成从数据中心射向天空的上行数据光柱',
    '140': '同 139，俯瞰城市时能看到一座座发光的机房',
    '144': '俯瞰城市：街区渐渐显出电路板纹路，作为片尾过渡',
}


def jpeg(im, height):
    im = im.convert('RGB')
    im = im.resize((max(1, round(im.size[0] * height / im.size[1])), height), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=82)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def frame(unit, n, crop=None, height=150):
    raw = subprocess.run([str(p.FFMPEG), '-v', 'error', '-i', str(UNITS / f'{unit}.mp4'), '-vf', f'select=eq(n\\,{n}),scale=1024:576',
                          '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    im = Image.frombytes('RGB', (1024, 576), raw)
    return jpeg(im.crop(crop) if crop else im, height)


def approved_units():
    state = json.loads((PROD / 'review/review_state.json').read_text(encoding='utf-8'))
    # decisions are keyed 'unit/version'
    return {k.split('/')[0] for k, d in state['decisions'].items() if isinstance(d, dict) and d.get('status') == 'approved'}


def units_html(text, ok):
    out = []
    for token in text.split():
        uid = token.split('(')[0].rstrip('?')
        out.append(f'<span class="u{" ok" if uid in ok else ""}">{html.escape(token)}</span>')
    return ' '.join(out)


def main():
    ok = approved_units()
    e = html.escape
    rows = []
    for name, shots, units, cast, note in ROLES:
        imgs = ''.join(f'<img src="{frame(u, n, c)}" title="{u} 第{n}帧">' for u, n, c in shots)
        design = DESIGN.get(cast)
        paths = design if isinstance(design, list) else [design] if design else []
        dimg = ''.join(f'<img src="{jpeg(Image.open(d), 150)}">' for d in paths if d.exists()) or ('—' if cast == '保留原样' else '<span class="todo">待设计</span>')
        rows.append(f'<tr><td class="name">{e(name)}</td><td class="imgs">{imgs}</td><td>{units_html(units, ok)}</td>'
                    f'<td class="name">{e(cast)}</td><td class="imgs">{dimg}</td><td class="note">{e(note)}</td></tr>')
    unknown = ''.join(f'<div class="card"><img src="{frame(u, n, None, 170)}"><b>{e(u)}</b><p>{e(what)}</p>'
                      f'<p class="quote">{e(q) if q else "（无备注）"}</p></div>' for u, n, what, q in UNKNOWN)
    nop = ''.join(f'<div class="card"><img src="{frame(u, n, None, 170)}"><b>{e(u)}</b><p class="quote">{e(q)}</p>'
                  f'<p class="prop">{e(PROPOSAL.get(u, ""))}</p></div>' for u, n, q in NO_PERSON)
    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>人物对照表</title><style>
:root{{--bg:#f6f5f2;--fg:#1d1d1f;--mute:#6b6b70;--line:#dddbd6;--card:#fff;--ok:#1f7a3a;--todo:#b4441c}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151517;--fg:#ececee;--mute:#a0a0a8;--line:#333338;--card:#1f1f22;--ok:#5cc583;--todo:#f0875a}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,"Microsoft YaHei",sans-serif}}
main{{max-width:1500px;margin:0 auto;padding:16px}} h1{{font-size:22px;margin:8px 0}} h2{{font-size:18px;margin:28px 0 8px}}
p.lead{{color:var(--mute);margin:0 0 12px}} .wrap{{overflow-x:auto}}
table{{border-collapse:collapse;width:100%;background:var(--card)}} th,td{{border-bottom:1px solid var(--line);padding:8px;vertical-align:top;text-align:left}}
th{{position:sticky;top:0;background:var(--card);font-weight:600}} td.name{{font-weight:600;white-space:nowrap}}
td.imgs img{{height:150px;margin-right:6px;border-radius:4px}} td.note{{color:var(--mute);min-width:180px}}
.u{{display:inline-block;padding:0 6px;margin:1px;border:1px solid var(--line);border-radius:10px;font-size:12px}} .u.ok{{border-color:var(--ok);color:var(--ok)}}
.todo{{color:var(--todo);font-weight:600}} .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:12px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px}} .card img{{width:100%;height:auto;border-radius:4px}}
.card p{{margin:4px 0}} .quote{{color:var(--mute)}} .quote::before{{content:"你的备注："}} .prop::before{{content:"我的提议：";font-weight:600}}
</style></head><body><main>
<h1>咒术回战 OP · 人物对照表</h1>
<p class="lead">左边是原片画面（多数截自 OP 本身，058 群像截了七个人的全身），右边是我们的二创角色。单元编号带绿框的是你已经通过的。</p>
<h2>一、已识别的角色（{len(ROLES)}）</h2>
<div class="wrap"><table><tr><th>原版角色</th><th>原片画面</th><th>出场单元</th><th>二创角色</th><th>二创设定图</th><th>备注</th></tr>{"".join(rows)}</table></div>
<h2>二、还没认出的人物（{len(UNKNOWN)}）</h2><div class="grid">{unknown}</div>
<h2>三、没有人物、需要独立设计的镜头（{len(NO_PERSON)}）</h2><div class="grid">{nop}</div>
</main></body></html>'''
    out = PROD / 'casting_review.html'
    out.write_text(page, encoding='utf-8')
    print(out, round(out.stat().st_size / 1e6, 2), 'MB')


if __name__ == '__main__':
    main()
