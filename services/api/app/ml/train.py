# app/ml/train.py
"""
Simple training orchestration script exposing a function and CLI.
It will:
- load dataset CSV/TSV (label/text)
- optionally augment spam samples
- build pipeline using pipeline.build_pipeline
- run CV optionally
- save artifact & metadata via persist.save_model_artifact
"""
import argparse
import pandas as pd
import numpy as np
import json
import random
import joblib
import os
from .pipeline import build_pipeline, numeric_feature_transformer
from .augment import add_noise
from .persist import save_model_artifact
from datetime import datetime
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import classification_report, average_precision_score, roc_auc_score
import logging

logger = logging.getLogger("app.train")

def load_dataset(path: str) -> pd.DataFrame:
    p = path
    if p.endswith(".csv"):
        df = pd.read_csv(p)
    else:
        # try tsv as fallback
        df = pd.read_csv(p, sep='\t', header=None, names=['label', 'text'], quoting=3)
    if 'label' not in df.columns or 'text' not in df.columns:
        raise ValueError("Dataset must have 'label' and 'text' columns")
    return df[['label','text']].dropna().reset_index(drop=True)

def normalize_label_series(series):
    def _map(v):
        if isinstance(v, str):
            v0 = v.strip().lower()
            if v0 in ('spam','1','true','yes','s'):
                return 1
            else:
                return 0
        try:
            return 1 if int(v) == 1 else 0
        except Exception:
            return 0
    return series.map(_map).astype(int)

def augment_dataset(X, y, aug_frac=0.4):
    newX, newy = [], []
    for xi, yi in zip(X, y):
        if yi == 1 and random.random() < aug_frac:
            newX.append(add_noise(xi))
            newy.append(yi)
    return np.array(list(X) + newX), np.array(list(y) + newy)

def train_and_save(dataset_path: str, version: str = None, classifier='logreg', use_embeddings=False, embedding_transformer=None, augment=True, out_dir=None):
    df = load_dataset(dataset_path)
    df['label_bin'] = normalize_label_series(df['label'])
    X = df['text'].values
    y = df['label_bin'].values

    if augment:
        X, y = augment_dataset(X, y, aug_frac=0.4)

    config = {
        'use_hashing': False,
        'include_word_tfidf': True,
        'include_char_tfidf': True,
        'include_numeric_feats': True,
        'use_svd': False,
        'classifier': classifier,
        'use_embeddings': use_embeddings,
        'embedding_transformer': embedding_transformer
    }

    pipeline = build_pipeline(config)
    logger.info("Fitting pipeline on %d samples", len(X))
    pipeline.fit(X, y)

    # evaluate on hold-out
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    preds = pipeline.predict(X_test)
    probs = pipeline.predict_proba(X_test)[:,1] if hasattr(pipeline, "predict_proba") else None
    logger.info("Classification report:\n%s", classification_report(y_test, preds, target_names=['ham','spam']))

    metrics = {}
    if probs is not None:
        try:
            metrics['auprc'] = float(average_precision_score(y_test, probs))
            metrics['roc_auc'] = float(roc_auc_score(y_test, probs))
        except Exception:
            pass

    # save artifact
    version = version or datetime.utcnow().strftime("v%Y%m%d%H%M%S")
    out_dir = out_dir or os.getenv("MODEL_DIR", "/app/models")
    version_dir = os.path.join(out_dir, version)
    os.makedirs(version_dir, exist_ok=True)
    artifact_path = os.path.join(version_dir, "artifact.joblib")
    joblib.dump(pipeline, artifact_path)
    metadata = {"version": version, "path": artifact_path, "created_at": datetime.utcnow().isoformat(), "metrics": metrics, "threshold": 0.5}
    save_model_artifact(version, artifact_path, metadata=metadata)
    return version, metadata

# CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser("train")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--version", default=None)
    parser.add_argument("--no-augment", action="store_true")
    args = parser.parse_args()
    v, m = train_and_save(args.dataset, version=args.version, augment=not args.no_augment)
    print("Saved model", v)
