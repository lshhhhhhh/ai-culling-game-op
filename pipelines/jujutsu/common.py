"""Paths of the Jujutsu Kaisen (S3 Culling Game part 1) OP project. Generic tools (ffmpeg helpers, H3 runner, review page)
stay in pipelines/anime_op."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'pipelines/anime_op'))

import op_pipeline as p  # noqa: E402

PROD = ROOT / 'assets/jujutsu/op1_v1'
SOURCE = ROOT / 'assets/clip/咒术回战 第三季「死灭回游」前篇 NCOP&ED映像.mp4'
INVENTORY = PROD / 'source_inventory'
REVIEW = PROD / 'review'
DELIVERY = ROOT / 'deliverables/jujutsu'
FPS = 24000 / 1001
REVIEW_PORT = 8769
