"""001 v3: v2 (red-and-black reference and prompt, same seed and compose), with the user's new DeepSeek design.

User (2026-10-01) on v2: “很完美，但是身材比例好像有点怪？你确定你用的形象不是Q版的？” — v1/v2 used the Lycoris community sheet
(= assets/人设/鲸鱼娘-中.png, about four and a half heads tall). The user then added the design to use from now on:
assets/人设/鲸鱼娘.png (“我更新了deepseek的形象，这个才是我们该用的”): adult proportions, long wavy blue hair, maid headband,
whale-fin ears, off-shoulder sleeves, an ankle-length maid dress with apron, white stockings and a large whale tail.
v3 uses it turned into the same red-and-black two-tone, and the prompt describes that figure.
"""
import render_001_v2  # noqa: F401  (sets the v2 prompt on render_001)
import render_001 as base
from common import PROD

base.REV = 'deepseek_official_redblack_h3_v3'
base.REF = PROD / 'character_designs/refs/deepseek_official_3view_redblack.png'
base.LABEL = 'DeepSeek新形象v3·官方三视图（红黑，同种子）'
old = ('a small girl with very long wavy hair, an ahoge, a frilled maid headband with bows, whale-fin ears on both sides of '
       'her head, a maid dress with an apron, and a whale tail.')
assert old in base.PROMPT
base.PROMPT = base.PROMPT.replace(old, (
    'a slender young woman with grown-up proportions and very long wavy hair, an ahoge, a frilled maid headband, whale-fin ears '
    'on both sides of her head, an off-shoulder maid dress that reaches her ankles with an apron, white stockings, and a large '
    'whale tail.'))
old = 'Her long wavy hair flows down her back'
assert old in base.PROMPT
base.PROMPT = base.PROMPT.replace(old, 'She has the slim grown-up proportions of <Picture 1>, as tall as the boy of <Video 1>. '
                                       'Her long wavy hair flows down her back')

if __name__ == '__main__':
    base.main()
