"""
SENTINEL — Model Training Script

Trains the TF-IDF + Logistic Regression spam classifier on the
UCI SMS Spam Collection dataset.

Usage:
    python ml/scripts/train.py --data ml/data/raw/spam.csv --output backend/app/ml/models/

Dataset:
    UCI SMS Spam Collection:
    https://archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection

    Download the dataset and place it at: ml/data/raw/spam.csv
    The file uses tab-separated values with columns: label, message

Output:
    - backend/app/ml/models/sentinel_v{VERSION}.joblib (trained pipeline)
    - ml/reports/model_evaluation.md (metrics report)
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

# Add the backend directory to Python path for importing app modules
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))


def main():
    parser = argparse.ArgumentParser(description="Train SENTINEL spam classifier")
    parser.add_argument("--data", required=True, help="Path to the raw dataset CSV (TSV)")
    parser.add_argument("--output", required=True, help="Directory to save the model file")
    parser.add_argument("--version", default="1.0.0", help="Model version string")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test set fraction")
    args = parser.parse_args()

    # Lazy imports — only required when training, not at inference time
    import joblib
    import numpy as np
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import (
        classification_report,
        confusion_matrix,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )
    from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
    from sklearn.pipeline import Pipeline
    from sklearn.feature_extraction.text import TfidfVectorizer

    from app.ml.pipeline import preprocess

    # -----------------------------------------------------------------------
    # 1. Load Dataset
    # -----------------------------------------------------------------------
    print(f"[1/6] Loading dataset from: {args.data}")
    df = pd.read_csv(args.data, sep="\t", header=None, names=["label", "message"])
    print(f"      Loaded {len(df)} records ({df['label'].value_counts().to_dict()})")

    # -----------------------------------------------------------------------
    # 2. Preprocess Text
    # -----------------------------------------------------------------------
    print("[2/6] Preprocessing text through NLP pipeline...")
    df["processed"] = df["message"].apply(lambda t: preprocess(t)["processed_text"])
    df["label_binary"] = (df["label"] == "spam").astype(int)

    X = df["processed"].values
    y = df["label_binary"].values
    print(f"      Preprocessing complete. Vocabulary will be built from {len(X)} documents.")

    # -----------------------------------------------------------------------
    # 3. Train/Test Split (stratified to preserve class ratio)
    # -----------------------------------------------------------------------
    print(f"[3/6] Splitting dataset (test_size={args.test_size}, stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=42, stratify=y
    )
    print(f"      Train: {len(X_train)} | Test: {len(X_test)}")

    # -----------------------------------------------------------------------
    # 4. Build & Train Pipeline
    # -----------------------------------------------------------------------
    print("[4/6] Training Logistic Regression + TF-IDF pipeline...")
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),      # Unigrams + bigrams
            min_df=2,                # Ignore terms in fewer than 2 documents
            max_df=0.95,             # Ignore terms in > 95% of documents
            sublinear_tf=True,       # Log scaling for TF
            analyzer="word",
        )),
        ("clf", LogisticRegression(
            C=1.0,
            class_weight="balanced", # Handle class imbalance
            max_iter=1000,
            solver="lbfgs",
            random_state=42,
        )),
    ])

    pipeline.fit(X_train, y_train)
    print("      Training complete.")

    # -----------------------------------------------------------------------
    # 5. Evaluate
    # -----------------------------------------------------------------------
    print("[5/6] Evaluating model...")
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    accuracy = pipeline.score(X_test, y_test)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_proba)

    print(f"\n{'='*50}")
    print(f"  SENTINEL Model v{args.version} — Evaluation Results")
    print(f"{'='*50}")
    print(f"  Accuracy:       {accuracy:.4f}")
    print(f"  Precision(SPAM):{precision:.4f}")
    print(f"  Recall(SPAM):   {recall:.4f}")
    print(f"  F1(SPAM):       {f1:.4f}")
    print(f"  ROC-AUC:        {roc_auc:.4f}")
    print(f"{'='*50}\n")
    print(classification_report(y_test, y_pred, target_names=["HAM", "SPAM"]))

    # -----------------------------------------------------------------------
    # 6. Save Model
    # -----------------------------------------------------------------------
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_file = output_dir / f"sentinel_v{args.version}.joblib"

    print(f"[6/6] Saving model to: {model_file}")
    joblib.dump(pipeline, model_file)
    print(f"      Model saved. File size: {model_file.stat().st_size / 1024:.1f} KB")

    # Write evaluation report
    report_dir = Path(__file__).parent.parent / "reports"
    report_dir.mkdir(exist_ok=True)
    report_path = report_dir / "model_evaluation.md"
    with open(report_path, "w") as f:
        f.write(f"# SENTINEL Model Evaluation Report\n\n")
        f.write(f"**Version:** {args.version}  \n")
        f.write(f"**Date:** {date.today()}  \n")
        f.write(f"**Training Samples:** {len(X_train)}  \n")
        f.write(f"**Test Samples:** {len(X_test)}  \n\n")
        f.write(f"## Metrics\n\n")
        f.write(f"| Metric | Score |\n|---|---|\n")
        f.write(f"| Accuracy | {accuracy:.4f} |\n")
        f.write(f"| Precision (SPAM) | {precision:.4f} |\n")
        f.write(f"| Recall (SPAM) | {recall:.4f} |\n")
        f.write(f"| F1 Score (SPAM) | {f1:.4f} |\n")
        f.write(f"| ROC-AUC | {roc_auc:.4f} |\n\n")
        f.write(f"## Classification Report\n\n```\n")
        f.write(classification_report(y_test, y_pred, target_names=["HAM", "SPAM"]))
        f.write(f"```\n")

    print(f"\nEvaluation report saved to: {report_path}")
    print("\n✅ Training complete! Next steps:")
    print(f"   1. Copy {model_file} to backend/app/ml/models/")
    print(f"   2. Update MODEL_FILE_NAME in .env to: sentinel_v{args.version}.joblib")
    print(f"   3. Restart the backend service")


if __name__ == "__main__":
    main()
