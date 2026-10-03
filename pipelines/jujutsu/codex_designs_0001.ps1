# JJK designs by Codex image generation (user, 2026-10-01 before sleeping: “codex生图也可以用，只要符合常识……如果实在不协调（比如原作在用武器打斗），
# 那就用codex生图设计二社”). Four sheets, run one after another; each is a 16:9 turnaround on white. Outputs in deliverables/jujutsu/人设.
$ErrorActionPreference = 'Continue'
$codex = "$env:LOCALAPPDATA\OpenAI\Codex\bin\faa963e871dd422c\codex.exe"
$dir = 'deliverables\jujutsu\人设'
$common = 'Draw a 16:9 character turnaround sheet: front view, side view and back view of the same character, full body, standing naturally, side by side on a plain white background, the same scale in all three views. Clean 2D Japanese TV-anime line art and flat cel shading in the style of the anime Jujutsu Kaisen, adult proportions. No text, no labels, no logos. Do not create or modify any other files.'

function Run-Design($name, $images, $prompt) {
    if (Test-Path "$dir\$name") { "skip $name (exists)"; return }
    $cargs = @('exec', '-C', $dir, '-s', 'workspace-write', '--skip-git-repo-check', '--ephemeral', '-o', "$dir\codex_last_message_$($name -replace '\.png$','').txt")
    foreach ($i in $images) { $cargs += @('-i', $i) }
    $cargs += "Use your image generation tool to create ONE image and save it in the current directory as $name. $prompt $common"
    $t = Get-Date
    & $codex @cargs 2>&1 | Select-Object -Last 2
    "done $name in $([int]((Get-Date) - $t).TotalSeconds) s"
}

Run-Design 'gpt_yuta_v1.png' @('deliverables\lycoris\人设需求\生成_GPT娘_去龙_v1.png', "$dir\ref_yuta_315.png") (
  'Image 1 is the identity reference: the GPT girl with very long wavy white hair, a small ahoge, lavender eyes, a soft face and a small round white knot-shaped hair ornament. Keep her face, hair and hair ornament. Image 2 is a frame of Yuta Okkotsu from Jujutsu Kaisen, used only for the outfit and the weapon: dress her in a crisp white long-sleeved shirt, slim black trousers and black shoes, with a katana in a black scabbard - held at her side in the front view and slung across her back in the back view. No dragon horns, wings, tail or dress.')

Run-Design 'gemini_maki_v1.png' @('assets\人设\GEMINI娘.jpg', "$dir\ref_maki_1105.png") (
  'Image 1 is the identity reference: the Gemini girl with very long wavy purple-to-pink gradient hair, cat ears and amber eyes. Keep her face, hair colours and cat ears, and tie her hair back in a high ponytail for fighting. Image 2 is a frame of Maki Zenin from Jujutsu Kaisen, used only for the outfit: a dark green-black sleeveless high-neck combat top, a belt, dark cargo trousers and boots, with a long sword in a dark scabbard on her back. Strong, athletic build.')

Run-Design 'rogue_ai_kenjaku_v1.png' @("$dir\ref_kenjaku_robe_2120.png") (
  'Design an original fictional villain, "the first rogue AI", for a parody of Jujutsu Kaisen. Image 1 (a frame of the villain Kenjaku) is used only for the robe and the mood. The character is an elegant, unsettling man with long black hair tied in a half-up bun, pale skin and a calm, sinister smile, with a thin seam of glowing red circuitry running across his forehead in place of stitches. He wears a black and dark-grey Buddhist monk kesa robe over a dark kimono, with subtle red circuit patterns along the hems. He must not resemble any real person.')

Run-Design 'ma_huateng_yaga_v1.png' @() (
  'A friendly cartoon parody of Tencent founder Pony Ma (Ma Huateng) cast as Principal Masamichi Yaga of Jujutsu High: his recognisable short black hair, rectangular glasses, round friendly face and gentle smile, a sturdy adult build, wearing a black high-collared long coat over a dark shirt and dark trousers like Yaga, holding a small handmade plush doll in one hand. Not a caricature with exaggerated features.')
