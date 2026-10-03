"""Keyframes for the user's review notes of 2026-10-02 02:08-02:14 (Codex image editing; stdin closed, 10-minute timeout).

- 087 “deepseek太壮了。需要重新跑，也许需要关键帧。” - frames of our own minimax_ds_h3_v1 with DeepSeek slimmed.
- 089 “最左边的claude应该是一脸不情愿的样子……而且另外几个人物也太壮了。也许需要关键帧。” - frames of gym_trio_h3_v1: Claude reluctant,
  MiniMax and DeepSeek slimmed.
- 091 “熊猫换成QQ企鹅吧。网上搜一下QQ企鹅。” - the doll beside Ma Huateng (ma_tint_h3_v1) becomes a QQ penguin plush (described from
  a web search: chibi black-and-white penguin, white belly, yellow beak and feet, red scarf, three tufts on its head, one eye winking).
- 103 “……也许可以做一个象征着convolution neural network的镜头？这一个个长方形有点像。” - the glass panes become CNN feature maps.
- 105 “改成巨大的回形针砸在地上。” - the falling stone cube becomes a giant paperclip.
- 140 “换成显卡。需要关键帧。可以用RTX3090作为模板。” - the falling bomb becomes an RTX 3090-style card (no text, no logos).
Edits on our own H3 frames keep the cast exactly as H3 drew them. Only the area Codex changed is taken (solid difference regions);
the rest of each frame is the base.
"""
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

from codex_keyframes_0001 import DIR, source_frame
from codex_keyframes_0003 import CODEX
from common import PROD, ROOT
from title_057 import frames

A = ROOT / 'assets/人设'
KEEP = ('Keep EVERYTHING else exactly as in Image 1 - the background, the light, the colours, the camera framing and the 2D anime '
        'rendering. The output is a 16:9 image with the framing of Image 1. No text, no logos. Do not create or modify any other files.')
SLIM = 'slender and feminine like her design: slim arms, narrow shoulders and a slight build, no bulging muscles anywhere'
GYM87 = ('Image 1 is a frame from an anime: a bright yellow gym, a girl in a blue-and-yellow costume on the left and, on the right, '
         'DeepSeek, the girl of Image 2. Redraw ONLY the girl on the right so that she is ' + SLIM + ', keeping exactly her pose, raised '
         'arm, facial expression, hair, clothes, place and size. Keep the girl on the left exactly as she is. ')
GYM89 = ('Image 1 is a frame from an anime: three girls in a bright yellow gym raise their fists - on the left Claude (Image 2), in the '
         'middle MiniMax (Image 3), on the right DeepSeek (Image 4). Change two things only: (1) the girl on the left looks thoroughly '
         'unwilling - a flat, embarrassed scowl, cheeks slightly puffed, eyes looking away to the side, shoulders slumped, her fist raised '
         'only halfway; (2) the girls in the middle and on the right are ' + SLIM + ', keeping their poses and raised fists. Every girl '
         'keeps her own hair, ears, clothes, place and size from Image 1; do not give one girl another girl\'s features. ')
QQ = ('Image 1 is a frame from an anime opening: on a black background a man lit entirely in green light, and a small floppy doll '
      'floating to his right. Replace ONLY the doll with a small plush of the QQ penguin, Tencent\'s mascot: a round chibi black-and-white '
      'penguin with a white belly, a yellow beak and yellow feet, a red scarf around its neck with one end hanging down, three little black '
      'tufts on top of its head and one eye winking, at the same size and place as the doll, lit by the same single green light against '
      'the black background. Keep the man exactly as he is. ')
CNN = ('Image 1 is a frame from an anime opening: a row of translucent cyan glass panes in perspective over a dark red background. Turn '
       'the panes into the feature maps of a convolutional neural network: each pane becomes a glowing cyan grid of small square cells '
       'with brighter and darker activations forming soft blurry shapes, the panes growing smaller toward the back like successive layers; '
       'on the front pane a small bright square window (the convolution kernel) is highlighted, with a few thin glowing lines running from '
       'it to one cell of the next pane. Same panes at the same positions, sizes and angles, same cyan glow. ')
CLIP = ('Image 1 is a frame from an anime opening drawn like an old sepia photograph: a giant stone cube crashing down onto the ground, '
        'raising huge clouds of dust and debris, mountains behind. Replace ONLY the stone cube with a giant silver paperclip of about the '
        'same overall size, slamming down into the ground at an angle, its lower end buried in the rising dust, in the same sepia '
        'old-photo rendering and light. The dust clouds, the debris and the mountains stay exactly as in Image 1. ')
GPU = ('Image 1 is a frame from an anime opening: an aerial view of a city seen from straight above, with a dark bomb falling down toward '
       'it. Replace ONLY the bomb with a falling graphics card modelled on the NVIDIA GeForce RTX 3090 Founders Edition - a long, thick '
       'card with a dark gunmetal shroud, a silver X-shaped metal frame and a large fan, no text and no logos - at the same place, size '
       'and angle as the bomb, falling away from the camera toward the city. ')
KNOT = ('Image 1 is a frame from an anime opening: a girl with long wavy white hair is knocked flying backward against a dark grey sky. '
        'Image 2 is her character design. Redraw ONLY her small hair ornament so that it is exactly the white knot-shaped ornament of '
        'Image 2 - the same shape, size and colour, crisp and undistorted - at the same place on her head, seen from the angle of her head '
        'in Image 1. Change nothing else about her or the frame. ')
KNOT006 = ('Image 1 is a frame from an anime opening: a girl with long wavy white hair falls through an orange explosion with a katana. '
           'Image 2 is her character design. Redraw ONLY her small hair ornament so that it is exactly the white knot-shaped ornament of '
           'Image 2 - the same shape, size and colour, crisp and undistorted - at the same place on her head, seen from the angle of her '
           'head in Image 1. Change nothing else about her or the frame. ')
REDBLACK = ('Image 1 is a frame from an anime opening drawn entirely in a red-and-black two-tone: glowing red clan crest symbols on '
            'black, and a girl. Recolour ONLY the girl so that she is drawn in exactly the same red-and-black two-tone as the rest of the '
            'frame - only black and shades of red, from dark red to bright red with pale pink highlights, no other colour anywhere on her '
            '(no brown, orange, beige, white, blue or skin tones) - keeping her shape, pose, face, hair, outfit lines, place and size exactly. ')
MA3 = ROOT / 'deliverables/jujutsu/人设/ma_huateng_v3.png'
SLIM_MA = ('Redraw ONLY the man as the man of Image 2 (Pony Ma): his face, glasses and hairstyle from Image 2 and his SLIM build - narrow '
           'shoulders, slim arms and torso, no bulk, no muscles - in exactly the same pose, place and gesture, with the same light on him; '
           'he is noticeably smaller and slimmer than the big man of Image 1. No sunglasses, no stubble. ')
MA075 = ('Image 1 is a frame from an anime opening painted like a Monet impressionist oil painting: a man sits at a small white garden '
         'table on the left and a girl sits on the right in a sunny flower garden. ' + SLIM_MA + 'He keeps the soft visible oil-paint brush '
         'strokes of the painting. Keep the girl and everything else exactly as in Image 1. ')
MA091 = ('Image 1 is a frame from an anime opening: on a black background a man lit entirely in green light, and a QQ penguin plush '
         'floating to his right. ' + SLIM_MA + 'He stays lit entirely by the same single green light against black. Keep the penguin '
         'plush exactly as it is. ')
TIGHTS = ('Image 1 is a frame from an anime opening: a girl with long wavy white hair is knocked flying backward against a dark grey '
          'sky. Image 2 is her character design. Make two changes only: (1) extend her black socks upward into opaque black tights that '
          'cover both legs completely, all the way up under her skirt, so no bare leg shows; (2) redraw her small hair ornament so that it '
          'is exactly the white knot-shaped ornament of Image 2, crisp and undistorted, at the same place on her head. Keep her pose, '
          'face, hair, blazer, skirt and everything else in the frame exactly as in Image 1. ')
KNOT092 = ('Image 1 is a frame from an anime opening: on a black background a girl with long wavy white hair stands lit entirely in a '
           'single pale blue light, her arms folded. Image 2 is her character design. Redraw ONLY her small hair ornament so that it is '
           'exactly the white knot-shaped ornament of Image 2 - the same shape and size, crisp, undistorted and clearly readable - at the '
           'same place on her head, lit by the same pale blue light. Change nothing else about her or the frame. ')
# v2, the user on mistral_kf_h3_v2: “116完全不对啊 没有变成mistral，原型人物特征太多了” - the face, the straight centre-parted hair, the
# bare raised arm and the black sleeveless top stayed Yuki's; in the silhouette only the hat and ears changed
MIS116B = ('Image 1 is a frame from an anime opening: a woman with one arm raised high and her head bowed, eyes closed, seen against a '
           'deep red backlight. Image 2 is Mistral, a girl. Redraw the woman COMPLETELY as the girl of Image 2, keeping only her pose '
           '(the raised arm, the bowed head, closed eyes), her place and size, and the deep red backlight behind her: Mistral\'s face; '
           'her long, voluminous WAVY orange-gold hair fading to red at the ends (not straight, not centre-parted); her cat ears; her red '
           'musketeer hat with a white feather; her raised arm in a puffy white sleeve with a red cuff and a white glove (no bare arm); '
           'the red-and-white corseted top of her dress (no black sleeveless top). Nothing of the original woman remains. Besides the red '
           'backlight and the bright rim light along her edges, a soft warm light falls on her front, so her orange hair, white sleeve '
           'and red-and-white dress read clearly in the darkness. ')
# v3, the user on mistral_full_kf_h3_v3: “116有点奇怪，衣服和细节有微妙的变化。大概是因为关键帧用多了。然后每个关键帧之间有微妙的区别
# （比如衣服帽子的褶皱）” - frame 7's keyframe is the master; frames 0 and 14 are redrawn to match it exactly (Image 3)
MIS116C = (MIS116B + 'Image 3 is the same girl at another moment of this shot, already drawn: copy her EXACTLY from Image 3 - the same hat '
           'with the same folds and feather, the same hair strands, the same sleeve, glove, cuff and dress details, the same colours and '
           'light - changing only what the pose of Image 1 requires (the slight sway of her arm, head and hair). ')
SMILE121 = ('Image 1 is a frame from an anime opening: a girl with long purple hair and a flower hair ornament, her face turned up, '
            'grinning fiercely with bared teeth, surrounded by collage pieces. Redraw ONLY her facial expression into a confident, '
            'pleasant smile - lips closed or only slightly parted, no bared teeth, no sneer, calm bright eyes - keeping her face shape, '
            'the angle of her head, her hair and ornament, the light, and every collage piece exactly as in Image 1. ')
MIS116 = ('Image 1 is a frame from an anime opening: a blonde woman in a black sleeveless top, one arm raised high, her head slightly '
          'bowed, seen almost in silhouette against a deep red backlight with bright rim light on her hair and arm. Image 2 is Mistral, '
          'a girl. Replace the woman with the girl of Image 2 exactly as she is designed - her face, hair style and colour, and outfit '
          'from Image 2 - in exactly the woman\'s pose, raised arm, bowed head, place and size, lit the same way: mostly in shadow '
          'against the deep red backlight, with the same bright rim light along her hair, face and raised arm. ')
DS088 = ('Image 1 is a frame from an anime opening: a close view of a young man pressing his hands together, outlined in pale green '
         'light against a magenta-to-violet background. Image 2 is DeepSeek, a girl: very long wavy dark-blue hair, a white frilled maid '
         'headband, blue whale-fin ears, a navy maid dress with a white apron and white frilled cuffs. Replace whatever part of the young '
         'man is in the frame with the same part of her, in exactly his pose and place: his dark hoodie becomes the top of her navy maid '
         'dress with the white apron bib; his hands become her slender girl\'s hands pressed together exactly the same way, with her white '
         'frilled cuffs at the wrists; if his face is visible it becomes her face with the same expression (eyes closed), her hair, '
         'headband and fin ears. Keep the pale green outline light on her edges, the background colours and the framing exactly as in '
         'Image 1. ')
HYS = ('Image 1 is a frame from an anime opening: a dark night forest around a small moonlit green clearing, with about ten tiny '
       'pandas scattered over the clearing. Image 2 is HY, a girl. Replace EVERY tiny panda with a tiny chibi version of the girl of '
       'Image 2 - her long black-blue hair and red scarf readable even at this size - each at exactly that panda\'s place, size and '
       'direction, as if running or wandering across the clearing; no panda remains. Keep the forest, the trees, the light on the '
       'clearing and the painted texture exactly as in Image 1. ')
ARMY128 = ('Image 1 is a frame from an anime opening: a formation of masked ninja soldiers charging toward the camera in a wooden dojo, '
           'katanas in their hands. Image 2 is the chibi DeepSeek girl: a big head, very long wavy dark-blue hair, a white frilled maid '
           'headband, blue whale-fin ears, a navy maid dress with a white apron. Replace EVERY ninja with a chibi DeepSeek girl at the '
           'same place and size, in exactly his stance, each gripping her katana with both small hands closed around the hilt exactly '
           'where his hands are and the blade pointing exactly the same way - correct hands with five fingers, no extra, missing or '
           'melted hands. Draw them in exactly the drawing style of Image 1, NOT the soft glossy style of Image 2: the same flat 2D '
           'TV-anime cel shading, the same bold outlines and the same colour wash and lighting as Image 1 (the whole frame keeps its '
           'colour cast). ')
# 127, the user (2026-10-02): “最右边的角色没有替换（前几帧没有替换）” - in doubao_zenin_group_h3_v1 the three Doubao on the left are
# right, but the woman in the purple dress who enters on the right at frame 6 stayed the source's; she becomes Doubao in the Naoya
# costume (DB_NAOYA) on our frames 7/12/19
NAOYA127 = ('Image 1 is a frame from an anime opening: against a blue-and-white sunburst sky, girls rendered in soft 3D stand in a row on '
            'the left, and on the right a 2D anime woman with a black bob in a purple dress strikes a pose with one arm raised behind her '
            'head, a string of big black beads hanging beside her. Image 2 is the character design of Doubao in a clan costume. Redraw '
            'ONLY the woman in the purple dress as the girl of Image 2 - her face, her dark bob with blond-dyed ends, small earrings, a '
            'smug half-smile, the loose dark grey kimono with a black haori - in exactly the woman\'s pose (one arm raised behind her '
            'head), place, size and cropping, in the same soft 3D-rendered look as the other girls (smooth CG shading, big glossy eyes). '
            'Nothing of the woman in purple remains. Keep the string of big black beads, the other girls and the sky exactly as they are. ')
# 130, the user (2026-10-02): “最前面的搞笑艺人没有替换” - in ds_dsq_dance_h3_v1 the dancers became chibi DeepSeek maids but the comedian
# in the middle stayed Takaba; on our frames 0/5/10 (facing us, turning, back turned) only he is redrawn as DeepSeek wagging her tail
def DS130(pose):
    return ('Image 1 is a frame from an anime opening: on a neon disco stage full of coloured lights, a crowd of small chibi girls in navy '
            'maid dresses dances around a comedian in a half-blue, half-bare costume with red gloves in the middle. Image 2 is DeepSeek, '
            'a girl with long wavy dark-blue hair, small fin-shaped ears, a navy maid dress with a white apron and a big dark-blue whale '
            'tail. Redraw ONLY the comedian in the middle as the girl of Image 2 - her face, long blue hair, maid dress and her big whale '
            f'tail - at exactly his place and size, {pose}. Nothing of the comedian remains: no half-bare costume, no red gloves, no '
            'yellow stripes. Keep every chibi girl, the speech bubble, the stage and the lights exactly as they are. ')
POSE130 = {0: 'dancing in his pose: facing the camera, one fist raised, the other arm bent, her tail curling out beside her',
           5: 'turning her back to the camera exactly as he turns, her whale tail swinging out from under her apron bow',
           10: 'her back to the camera exactly where his is, looking back over her shoulder with a cheeky grin, wagging her big whale '
               'tail high to one side where he shakes his hips',
           # the last frame too (ds_dance_kf_h3_v2 matched only frame 0 and copied the source from frame 2 on)
           14: 'her back to the camera exactly where his is, looking back over her shoulder with a cheeky grin, her big whale tail swung '
               'high to the other side where he shakes his hips'}
# 133, the user (2026-10-02): “轮椅上的换成千问吧。” - on our liang_gptgirl_h3_v1 frames 0/11/22 only the girl in the wheelchair changes
QWEN133 = ('Image 1 is a frame from an anime opening: in a sunlit forest clearing, a man in a dark suit pushes a wheelchair in which a pale '
           'girl with long white hair sits quietly, her hands folded in her lap. Image 2 is Qwen, a girl with long wavy blue-violet hair, '
           'purple eyes, a small navy beret with a white flower, and a long white-and-blue Chinese-style robe under a navy coat. Redraw '
           'ONLY the girl in the wheelchair as the girl of Image 2 - her face, blue-violet hair, beret, white-and-blue robe and navy coat - '
           'sitting quietly in the wheelchair in exactly the same pose (hands folded in her lap, a calm, slightly frail look), place and '
           'size, lit by the same soft forest light. Nothing of the white-haired girl remains. Keep the man pushing the wheelchair, the '
           'wheelchair and the forest exactly as they are. ')
# 098, the user (2026-10-02) on the hold fix: “098现在完全就是静止帧了，不好看。要不还是用视频模型生成动态的。” - in our
# kf_grok_claude_hy_h3_v3 only frame 0 of the violet shot is all Grok (1-2 her head on Reggie's receipt coat, 3-5 Reggie): frames 3 and 5
# are redrawn as the Grok of frame 0 for an H3 run that takes that version itself as <Video 1>
GROK098 = ('Image 1 is a frame from an anime opening: on a black background, a figure lit entirely in a single violet light, wrapped in a '
           'big coat of fluttering paper strips. Image 2 is the same shot a moment earlier, showing the girl who must replace that '
           'figure, exactly as she looks in this light. Image 3 is her character design. Redraw the figure completely as the girl of '
           'Image 2 - her face, long twin tails, small crown and horns, and her gothic dress with its full skirt, all lit in the same '
           'single violet light against black as in Image 2 - in exactly the pose, place and size of the figure in Image 1 (the same arm '
           'positions and the same turn of the head). Nothing of the original figure remains: no coat of paper strips, no long straight '
           'hair, no beard. ')
# (unit, local frame, base: 'src', an H3 revision of ours or an image path, output name, reference images, prompt)
EDITS = [('087', 0, 'minimax_ds_h3_v1', 'kf_087_f000_ds_slim_v1.png', [A / '鲸鱼娘.png'], GYM87),
         ('087', 25, 'minimax_ds_h3_v1', 'kf_087_f025_ds_slim_v1.png', [A / '鲸鱼娘.png'], GYM87),
         ('089', 0, 'gym_trio_h3_v1', 'kf_089_f000_trio_v1.png', [A / 'claude娘.png', A / 'minimax娘.jpg', A / '鲸鱼娘.png'], GYM89),
         ('089', 26, 'gym_trio_h3_v1', 'kf_089_f026_trio_v1.png', [A / 'claude娘.png', A / 'minimax娘.jpg', A / '鲸鱼娘.png'], GYM89),
         ('091', 0, 'ma_tint_h3_v1', 'kf_091_f000_qq_v1.png', [], QQ),
         ('091', 7, 'ma_tint_h3_v1', 'kf_091_f007_qq_v1.png', [], QQ),
         ('103', 8, 'src', 'kf_103_f008_cnn_v1.png', [], CNN),
         ('103', 16, 'src', 'kf_103_f016_cnn_v1.png', [], CNN),
         ('105', 0, 'src', 'kf_105_f000_clip_v1.png', [], CLIP),
         ('105', 12, 'src', 'kf_105_f012_clip_v1.png', [], CLIP),
         ('140', 0, 'src', 'kf_140_f000_gpu_v1.png', [], GPU),
         ('140', 8, 'src', 'kf_140_f008_gpu_v1.png', [], GPU),
         # 036, the user (02:37): “颜色不对。claude需要也变成红黑配色。” - one frame per shot with her in it, from our claude_red_h3_v1
         ('036', 2, 'claude_red_h3_v1', 'kf_036_f002_redblack_v1.png', [], REDBLACK),
         ('036', 9, 'claude_red_h3_v1', 'kf_036_f009_redblack_v1.png', [], REDBLACK),
         ('036', 15, 'claude_red_h3_v1', 'kf_036_f015_redblack_v1.png', [], REDBLACK),
         # 042, the user (03:08): “可能还是要关键帧。头上的GPT发饰经常会扭曲。” - frames of our gpt6_h3_v1, only the ornament redrawn
         *[('042', i, 'gpt6_h3_v1', f'kf_042_f{i:03d}_knot_v1.png', [ROOT / 'deliverables/jujutsu/人设/gpt_yuta_v6.png'], KNOT)
           for i in (0, 7, 13)],
         # 006, the user (03:15): “006的gpt发饰也有问题。如果042解决了那就用同样方法解决006”
         *[('006-016a', i, 'gpt6_h3_v1', f'kf_006_f{i:03d}_knot_v1.png', [ROOT / 'deliverables/jujutsu/人设/gpt_yuta_v6.png'], KNOT006)
           for i in (48, 54, 61)],
         # Ma Huateng, the user (03:20): “马化腾形象完全无法辨认！问题关键是马化腾其实是比较瘦的，但是替换的人物太大了。” - slim Ma (design v3)
         # on our frames: 075 from ma_hy_h3_v1, 091 on top of the QQ-penguin keyframes (so both changes are in one picture)
         *[('075', i, 'ma_hy_h3_v1', f'kf_075_f{i:03d}_ma3_v1.png', [MA3], MA075) for i in (0, 8)],
         *[('091', i, DIR / f'kf_091_f{i:03d}_qq_v2.png', f'kf_091_f{i:03d}_ma3qq_v1.png', [MA3], MA091) for i in (0, 7)],
         # 128, the user (03:30, on deepseek_army_h3_v1): “128的动作有问题，手做坏了。也许需要关键帧” “而且画风也不一样” - edits of the
         # SOURCE frames, so the flat cel style and the yellow wash stay; every ninja becomes a chibi DeepSeek gripping the katana like him
         *[('128', i, 'src', f'kf_128_f{i:03d}_dsq_v1.png', [A / '鲸鱼娘-小.jpg'], ARMY128) for i in (0, 7, 14)],
         *[('116', i, 'src', f'kf_116_f{i:03d}_mis3_v1.png', [A / 'mistral娘.jpg'], MIS116B) for i in (0, 4, 7, 10, 14)],
         *[('116', i, 'src', f'kf_116_f{i:03d}_mis4_v1.png', [A / 'mistral娘.jpg', DIR / 'kf_116_f007_mis3_v1.png'], MIS116C)
           for i in (0, 14)],
         # 121-122, the user (10:59): “表情有点狰狞，不好看，没必要用原版的表情。” - our kf_qwen_h3_v2 frames, expression only
         *[('121-122', i, 'kf_qwen_h3_v2', f'kf_121_f{i:03d}_smile_v1.png', [], SMILE121) for i in (4, 8, 12)],
         # 116, the user (10:59): “完全没有替换” - the blonde woman (Yuki) in red backlight -> Mistral; source frames 0/7/14
         *[('116', i, 'src', f'kf_116_f{i:03d}_mis_v1.png', [A / 'mistral娘.jpg'], MIS116) for i in (0, 7, 14)],
         # 092, the user (10:56): “这个有用关键帧吗？怎么头饰还是看不清楚” - the 006 method on our gpt6_doubao_tint_h3_v3, shot 1 only
         *[('092', i, 'gpt6_doubao_tint_h3_v3', f'kf_092_f{i:03d}_knot_v1.png', [ROOT / 'deliverables/jujutsu/人设/gpt_yuta_v6.png'], KNOT092)
           for i in (2, 6)],
         # 088, the user (10:55): “虎杖没有替换”, then “可以，就这么干” - the tilt up from the hands to the face to the raised hands
         *[('088', i, 'src', f'kf_088_f{i:03d}_ds_v1.png', [A / '鲸鱼娘.png'], DS088) for i in (4, 10, 18)],
         # 071, the user (10:53): “应该是很多个HY跑过去，和原镜头对应” then “试试1” (keyframes on source frames + H3)
         *[('071', i, 'src', f'kf_071_f{i:03d}_hys_v1.png', [A / 'HY娘.png'], HYS) for i in (0, 10, 19)],
         # 042 v3, the user (03:55): “只给这个镜头加黑色连裤袜。其实就是把下面的袜子加长” - tights and the ornament in one edit
         *[('042', i, 'gpt6_h3_v1', f'kf_042_f{i:03d}_tights_v1.png', [ROOT / 'deliverables/jujutsu/人设/gpt_yuta_v6.png'], TIGHTS)
           for i in (0, 7, 13)],
         *[('127', i, 'doubao_zenin_group_h3_v1', f'kf_127_f{i:03d}_naoya_v1.png',
            [ROOT / 'deliverables/jujutsu/人设/doubao_zenin_naoya_v1.png'], NAOYA127) for i in (7, 12, 19)],
         *[('130', i, 'ds_dsq_dance_h3_v1', f'kf_130_f{i:03d}_ds_v1.png', [A / '鲸鱼娘.png'], DS130(POSE130[i])) for i in (0, 5, 10, 14)],
         *[('133', i, 'liang_gptgirl_h3_v1', f'kf_133_f{i:03d}_qwen_v1.png', [A / 'qwen娘.jpg'], QWEN133) for i in (0, 11, 22)],
         *[('098', i, 'kf_grok_claude_hy_h3_v3', f'kf_098_f{i:03d}_grokfull_v1.png',
            [DIR / 'h3_098_kf_grok_claude_hy_h3_v3_f000.png', A / 'grok.jpg'], GROK098) for i in (3, 5)]]


def base_frame(unit, local, base):
    if isinstance(base, Path):
        return base
    if base == 'src':
        return source_frame(unit, local, DIR / f'src_{unit}_f{local:03d}.png')
    out = DIR / f'h3_{unit}_{base}_f{local:03d}.png'
    if not out.exists():
        job = PROD / 'shots' / unit / base
        # the H3 picture before any CPU overlay (006's flash subtitles are composited after native_fullframe)
        Image.fromarray(frames(job / 'native_fullframe.mp4' if (job / 'native_fullframe.mp4').exists() else job / 'review_with_audio.mp4')[local]).save(out)
    return out


def composite(base, name):
    out = DIR / name.replace('_v1', '_v2')
    a = np.asarray(Image.open(DIR / name).convert('RGB').resize((1024, 576), Image.LANCZOS)).astype(np.float32)
    b = np.asarray(Image.open(base).convert('RGB').resize((1024, 576), Image.LANCZOS)).astype(np.float32)
    d = np.abs(a - b).max(-1) > 35
    lab, n = ndimage.label(ndimage.binary_closing(d, iterations=3))
    sizes = ndimage.sum(np.ones_like(d), lab, range(1, n + 1))
    m = np.isin(lab, [k + 1 for k, z in enumerate(sizes) if z >= 300])
    m = ndimage.binary_dilation(ndimage.binary_fill_holes(m), iterations=4)
    w = ndimage.gaussian_filter(m.astype(np.float32), 2)[..., None]
    Image.fromarray((a * w + b * (1 - w)).round().clip(0, 255).astype(np.uint8)).save(out)
    print('composited', out.name, f'{100 * d.mean():.1f} % changed by Codex, {100 * m.mean():.1f} % taken', flush=True)


def main():
    only = set(sys.argv[1:])
    for unit, local, base, name, refs, prompt in EDITS:
        if only and unit not in only and name not in only:
            continue
        src = base_frame(unit, local, base)
        if not (DIR / name).exists():
            args = [str(CODEX), 'exec', '-C', str(DIR), '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral',
                    '-o', str(DIR / f'codex_last_message_{name[:-4]}.txt'), '-i', str(src), *[a for r in refs for a in ('-i', str(r))], '--',
                    f'Use your image generation tool to create ONE image and save it in the current directory as {name}. {prompt}{KEEP}']
            t = time.time()
            try:
                subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
            except subprocess.TimeoutExpired:
                print('TIMEOUT', name, flush=True)
                continue
            print('done' if (DIR / name).exists() else 'FAILED', name, f'{time.time() - t:.0f} s', flush=True)
        if (DIR / name).exists() and not (DIR / name.replace('_v1', '_v2')).exists():
            composite(src, name)


if __name__ == '__main__':
    main()
