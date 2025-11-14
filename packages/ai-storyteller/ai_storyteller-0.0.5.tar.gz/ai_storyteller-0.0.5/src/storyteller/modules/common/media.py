import logging
from pathlib import Path
from urllib.parse import quote

from storyteller.settings import OUTPUT_ROOT, OUTPUT_MEDIA_URL_BASE

logger = logging.getLogger(__name__)

# OUTPUT_ROOT = os.getenv("STORYTELLER_OUTPUT_PATH", "./drawthings_output")
#
# # Resolve media config
# MEDIA_ROOT = Path(OUTPUT_ROOT or os.getenv("STORYTELLER_MEDIA_ROOT", "media")).resolve()
# MEDIA_URL_BASE = os.getenv(
#     "STORYTELLER_MEDIA_URL", "/media/"
# )  # can be "/media/" or "https://host/media/"
# OUTPUT_MEDIA_URL_BASE = os.getenv(
#     "STORYTELLER_OUTPUT_MEDIA_URL", "/media/output/"
# )  # can be "/media/" or "https://host/media/"
# if not MEDIA_URL_BASE.endswith("/"):
#     MEDIA_URL_BASE += "/"


# Same idea: we return file:// URLs or whatever mapping you later replace
# with signed GCS URLs / static hosting.
def as_url(
    p: Path,
    media_root: str = OUTPUT_ROOT,
    media_url_base: str = OUTPUT_MEDIA_URL_BASE,
) -> str:
    logger.info(f"p: {p}")
    logger.info(f"media_root: {media_root}")
    logger.info(f"media_url_base: {media_url_base}")
    # return f"{MEDIA_URL_BASE}{p}"
    rel_path = p.relative_to(media_root)
    return f"{media_url_base}{quote(rel_path.as_posix())}"
