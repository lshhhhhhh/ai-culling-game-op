"""001 v4: v3 with the switch to the generated part moved from frame 63 to frame 46.

User on v3: “刚登场的时候有几帧虎杖。可能是模型能力问题。讨论一下怎么处理。” Not the model: the source figure's red hood starts entering
at the left edge around frames 58-60, and v3 showed source frames up to 62 and crossfaded source into the generation over 63-68.
Switching at 46 (crossfade 46-51) keeps every frame with the figure generated. The generated part is then 192 frames, the
tested maximum (31.1 GB peak), so it runs only in away mode (0.6 GB reserve) while the user is not using the computer.
"""
import render_001_v3  # noqa: F401  (v3 reference, prompt and label)
import render_001 as base

base.CUT = 46
base.REV = 'deepseek_official_redblack_h3_v4'
old = '7.292-second'  # v3's generated part: 175 frames
assert old in base.PROMPT
base.PROMPT = base.PROMPT.replace(old, f'{base.p.snap_frames(base.END - base.CUT) / 24:.3f}-second')
base.LABEL = 'DeepSeek新形象v4·从第46帧开始生成（避开虎杖入场）'

if __name__ == '__main__':
    base.main()
