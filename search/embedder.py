
from sentence_transformers import SentenceTransformer

_model = None


def load_embedder():
    global _model
    if _model is None:
        from config import EMBED_MODEL_NAME
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading embedding model {EMBED_MODEL_NAME} on {device}...")
        _model = SentenceTransformer(EMBED_MODEL_NAME, device=device)
    return _model


def embed_texts(texts, batch_size=64):
    """
    Returns a normalized numpy array of embeddings, shape (len(texts), dim).
    Normalized so that inner product search == cosine similarity.
    """
    model = load_embedder()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return embeddings
