
DATA_DIR = "/content/drive/MyDrive/AtlasData"
VIDEO_DIR = f"{DATA_DIR}/storage/videos"
THUMBNAIL_DIR = f"{DATA_DIR}/storage/thumbnails"

DRIVE_DB_PATH = f"{DATA_DIR}/atlas.db"
LOCAL_DB_PATH = "/content/atlas_local.db"
DB_PATH = DRIVE_DB_PATH  # kept for main.py (Module 1), unaffected by this fix

IA_RESULTS_PER_QUERY = 20
IA_MAX_FILESIZE_MB = 80
IA_MAX_DURATION_SECONDS = 600

SCENE_THRESHOLD = 27.0
MIN_SCENE_LEN_SECONDS = 1.0
CHECKPOINT_EVERY = 10  # sync local DB back to Drive every N processed assets
