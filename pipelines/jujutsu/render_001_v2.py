"""001 v2: same unit, cut, seed and compose as render_001.py, but DeepSeek drawn in the shot's red-and-black two-tone.

User (2026-10-01) on v1: the motion is right, the only problem is the colour (she came out blue-grey); the CPU recolour was
noisy — “还是用模型重跑吧”. v1 copied the blue of its colour reference, so v2's reference is the same community three-view
turned into red-and-black two-tone on the CPU (black background, flat red above a brightness split, black lines and
shadows below), and the prompt says she is drawn only in flat red and black like the street.
"""
import render_001 as base
from common import PROD

base.REV = 'deepseek_redblack_h3_v2'
base.REF = PROD / 'character_designs/refs/deepseek_community_3view_redblack.png'
base.LABEL = 'DeepSeek社区形象v2·红黑参考图＋红黑提示（同种子）'
base.PROMPT = '''subject_definitions:
<Subject 1> is DeepSeek from <Picture 1>: a small girl with very long wavy hair, an ahoge, a frilled maid headband with bows, whale-fin ears on both sides of her head, a maid dress with an apron, and a whale tail. <Picture 1> already shows her in the red-and-black two-tone of this shot: flat red shapes with black lines and shadows.
<Subject 2> is the boy with short spiky hair in a dark hooded school jacket who walks into <Video 1>.
<Video 1> is the source video for the target video edit.

summary:
[video editing + reference generation] The target video is an edited version of <Video 1>. Replace <Subject 2> with <Subject 1>, preserving the original performance, the rotating camera, the timing and the red-and-black two-tone look.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - identity, face, long wavy hair, frilled headband, whale-fin ears and clothing come from <Picture 1>, in the same flat red and black as <Picture 1> and <Video 1>.
<Subject 2> (appears in [Shot 1]): attribute_transfer - all original motion, walking, head turns, screen position and scale are transferred to <Subject 1>, with their original timing.
<Video 1> (source video editing): partially_preserved - replace the character; preserve the red-and-black two-tone rendering, the city street, the black sun with its red ring, the camera that turns around her head, and at the end the black sun forming a red halo behind her head; the frame is never mirrored.

detailed_description:
The target video keeps the 2D TV-anime style and the red-and-black two-tone rendering of <Video 1> over this 7.292-second model sequence.
[Shot 1] 2D-animated, a red-and-black two-tone city street seen from low, a black sun with a glowing red ring in the sky; <Subject 1> walks in from the left very close to the camera; the camera turns around her head as she walks; at the end, seen from behind and below, the black sun behind her head forms a red halo.
She is drawn entirely in flat red and black exactly like the street and the boy of <Video 1>: her long wavy hair, frilled headband, whale-fin ears and dress are flat red shapes with black lines and shadows, the same red as the rest of the frame.
Her long wavy hair flows down her back and the whale-fin ears stand out on both sides of her head, in place of the short spiky hair and the hood of <Video 1>.
Keep <Subject 1> on the side of the frame where <Video 1> shows the boy; never mirror the shot.
The reference picture supplies appearance; the source video supplies the complete performance. The reference picture supplies no pose, expression, camera distance or composition.

overall_soundscape:
N/A. Generated audio is disabled; the original clip audio is restored after retiming.

non_diegetic_music:
N/A
'''

if __name__ == '__main__':
    base.main()
