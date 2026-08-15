
DATA_DIR = "/content/drive/MyDrive/AtlasData"
VIDEO_DIR = f"{DATA_DIR}/storage/videos"
THUMBNAIL_DIR = f"{DATA_DIR}/storage/thumbnails"

DRIVE_DB_PATH = f"{DATA_DIR}/atlas.db"
LOCAL_DB_PATH = "/content/atlas_local.db"
DB_PATH = DRIVE_DB_PATH

IA_RESULTS_PER_QUERY = 20
IA_MAX_FILESIZE_MB = 80
IA_MAX_DURATION_SECONDS = 600

SCENE_THRESHOLD = 27.0
MIN_SCENE_LEN_SECONDS = 1.0
CHECKPOINT_EVERY = 10

CAPTION_MIN_DURATION = 0.5
CAPTION_MAX_DURATION = 60.0
CAPTION_BATCH_SIZE = 16
CAPTION_CHECKPOINT_EVERY_BATCHES = 5

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
FAISS_INDEX_PATH = f"{DATA_DIR}/atlas.faiss"
FAISS_IDS_PATH = f"{DATA_DIR}/atlas_faiss_ids.npy"
EMBED_BATCH_SIZE = 64

RELEVANCE_WEIGHT = 1.0
USAGE_PENALTY_WEIGHT = 0.15
RECENCY_PENALTY_WEIGHT = 0.10

PRODUCTION_DIR = f"{DATA_DIR}/production"
SCRIPT_PATH = f"{PRODUCTION_DIR}/script.txt"
WHISPER_MODEL_SIZE = "medium"
PARAGRAPH_TIMINGS_PATH = f"{PRODUCTION_DIR}/paragraph_timings.json"
WHISPER_WORDS_PATH = f"{PRODUCTION_DIR}/whisper_words.json"
TIMELINE_OUTPUT_PATH = f"{PRODUCTION_DIR}/timeline.json"
MIN_CLIP_DURATION_SECONDS = 1.5
MAX_CLIPS_PER_PARAGRAPH = 6
SEARCH_CANDIDATES_PER_PARAGRAPH = 15

EDITED_TIMELINE_PATH = f"{PRODUCTION_DIR}/timeline_edited.json"
KEN_BURNS_MIN_ZOOM = 1.0
KEN_BURNS_MAX_ZOOM = 1.12
KEN_BURNS_MAX_PAN_FRACTION = 0.08
CROSSFADE_DURATION_SECONDS = 0.4
MIN_DURATION_FOR_PAN = 3.0

RENDER_WORK_DIR = "/content/render_work"
RENDER_WIDTH = 1920
RENDER_HEIGHT = 1080
RENDER_FPS = 30
FINAL_VIDEO_PATH = f"{PRODUCTION_DIR}/video.mp4"

GRADE_CONTRAST = 1.08
GRADE_SATURATION = 0.92
GRADE_BRIGHTNESS = -0.02
GRADE_VIGNETTE_STRENGTH = 0.25

GEMINI_MODEL_NAME = "gemini-2.5-flash"
GRAPHICS_PLAN_PATH = f"{PRODUCTION_DIR}/graphics_plan.json"
GRAPHICS_PLAN_TIMED_PATH = f"{PRODUCTION_DIR}/graphics_plan_timed.json"

GRAPHICS_WORK_DIR = "/content/graphics_work"
GRAPHICS_DISPLAY_DURATION = 4.5

TITLE_FONT_PATH = "/content/Atlas/assets/fonts/Anton-Regular.ttf"
BODY_FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
BODY_FONT_REGULAR_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SERIF_FONT_PATH = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"

NAVY_DEEP = (6, 14, 36, 255)
NAVY_PANEL = (8, 18, 44, 222)
GFX_WHITE = (255, 255, 255, 255)
GFX_OFFWHITE = (225, 231, 242, 255)
GFX_ORANGE = (255, 138, 24, 255)
GFX_SHADOW = (0, 0, 0, 150)

VOICES_DIR = f"{DATA_DIR}/voices"
TTS_MODEL_NAME = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
TTS_CHUNK_MAX_CHARS = 240
TTS_WORK_DIR = "/content/tts_work"
NARRATION_OUTPUT_PATH = f"{PRODUCTION_DIR}/narration.mp3"

CONFIG_DIR = f"{DATA_DIR}/config"
GEMINI_API_KEY_PATH = f"{CONFIG_DIR}/gemini_api_key.txt"

TARGET_VIDEO_MINUTES = 10
WORDS_PER_MINUTE = 150

PEXELS_API_KEY_PATH = f"{CONFIG_DIR}/pexels_api_key.txt"
PIXABAY_API_KEY_PATH = f"{CONFIG_DIR}/pixabay_api_key.txt"
FOOTAGE_RESULTS_PER_QUERY = 15

CLIP_CACHE_DIR = f"{DATA_DIR}/cache/videos"
CLIP_CACHE_MAX_BYTES = 3 * 1024 * 1024 * 1024  # 3GB rolling cache, LRU-evicted

SCENE_SPLIT_TEMP_DIR = "/content/scene_split_temp"

USE_NVENC = True
RENDER_PARALLELISM = 2  # T4 typically supports ~2 concurrent NVENC sessions

TTS_BATCH_SIZE = 4

IMAGES_DIR = f"{DATA_DIR}/storage/images"
IMAGE_DISPLAY_DURATION = 5.0
FOOTAGE_KEYWORDS_PATH = f"{PRODUCTION_DIR}/footage_keywords.json"
FOOTAGE_KEYWORDS_PER_VIDEO = 20
VIDEO_RESULTS_PER_KEYWORD = 8
IMAGE_RESULTS_PER_KEYWORD = 5

# Narrower default discovery - most keywords don't need 15+ results each
VIDEO_RESULTS_PER_KEYWORD_DEFAULT = 3
IMAGE_RESULTS_PER_KEYWORD_DEFAULT = 3

# Bounded per-run processing so a growing backlog can never block a run indefinitely
MAX_ASSETS_PER_SPLIT_RUN = 120

# Below this average relevance, a paragraph gets a targeted second discovery pass
LOW_RELEVANCE_THRESHOLD = 0.38
BOOST_VIDEO_RESULTS_PER_KEYWORD = 6
BOOST_IMAGE_RESULTS_PER_KEYWORD = 4
LOW_RELEVANCE_PARAGRAPHS_PATH = f"{PRODUCTION_DIR}/low_relevance_paragraphs.json"

SPLIT_PARALLELISM = 6

GENERIC_CONCEPT_QUERIES = [
    "business meeting handshake",
    "team collaboration office",
    "world map global connections",
    "city skyline aerial view",
    "hands typing on laptop",
    "clock time lapse",
    "money growth chart finance",
    "government building flags",
    "people walking city street",
    "sunrise hope future",
    "scientist research laboratory",
    "family home lifestyle",
]
PARAGRAPH_QUERY_OVERRIDES_PATH = f"{PRODUCTION_DIR}/paragraph_query_overrides.json"
MAX_BOOST_PARAGRAPHS = 5
