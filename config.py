
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

# Scoring weights for clip selection (Module 4+ search)
RELEVANCE_WEIGHT = 1.0
USAGE_PENALTY_WEIGHT = 0.15   # subtracted per prior use
RECENCY_PENALTY_WEIGHT = 0.10 # extra subtraction if used very recently
