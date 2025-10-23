# app/ml/embeddings.py
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np

class SentenceTransformerVectorizer(BaseEstimator, TransformerMixin):
    """
    Wrapper to expose sentence-transformers encoder as a sklearn transformer.
    Lazy-loads the model to avoid heavy import at module import time.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu", batch_size: int = 64):
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        self._model = None

    def _load(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except Exception as e:
                raise RuntimeError("sentence-transformers is required for embeddings. Install it.") from e
            self._model = SentenceTransformer(self.model_name, device=self.device)

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        self._load()
        texts = list(X)
        emb = self._model.encode(texts, batch_size=self.batch_size, show_progress_bar=False)
        return np.array(emb, dtype=float)
