import sys
import os
from pathlib import Path

# Add backend directory to PYTHONPATH
backend_dir = str(Path(__file__).resolve().parent.parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import pandas as pd
import json
import joblib
from time import time
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, f1_score, confusion_matrix, precision_score, recall_score, accuracy_score

from app.ml.pipeline import preprocess
from app.core.config import settings

DATA_DIR = Path(__file__).parent / "data" / "raw"
MODELS_DIR = Path(__file__).parent / "models"
REPORTS_DIR = Path(__file__).parent / "reports"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def train_and_evaluate():
    print("Loading dataset...")
    df = pd.read_csv(DATA_DIR / "SMSSpamCollection", sep='\t', header=None, names=['label', 'text'])
    
    print("Preprocessing texts...")
    processed_texts = []
    total = len(df)
    for i, text in enumerate(df['text']):
        if i % 1000 == 0:
            print(f"Processed {i}/{total} messages")
        processed_texts.append(preprocess(text)['processed_text'])
    
    df['processed_text'] = processed_texts
    
    X = df['processed_text']
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("Training models...")
    models = {
        "Multinomial Naive Bayes": MultinomialNB(),
        "Logistic Regression": LogisticRegression(class_weight='balanced', random_state=42),
        "Linear SVM (Calibrated)": CalibratedClassifierCV(LinearSVC(class_weight='balanced', random_state=42)),
        "Random Forest": RandomForestClassifier(class_weight='balanced', random_state=42, n_jobs=-1)
    }
    
    results = []
    best_f1 = 0
    best_pipeline = None
    best_model_name = ""
    best_y_pred = None
    
    for name, clf in models.items():
        print(f"Training {name}...")
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=5000)),
            ('clf', clf)
        ])
        
        t0 = time()
        pipeline.fit(X_train, y_train)
        train_time = time() - t0
        
        t0 = time()
        y_pred = pipeline.predict(X_test)
        infer_time = time() - t0
        
        f1 = f1_score(y_test, y_pred, pos_label='spam')
        precision = precision_score(y_test, y_pred, pos_label='spam')
        recall = recall_score(y_test, y_pred, pos_label='spam')
        accuracy = accuracy_score(y_test, y_pred)
        
        results.append({
            "Model": name,
            "Accuracy": accuracy,
            "Precision (Spam)": precision,
            "Recall (Spam)": recall,
            "F1-Score (Spam)": f1,
            "Train Time (s)": train_time,
            "Inference Time (s)": infer_time
        })
        
        if f1 > best_f1:
            best_f1 = f1
            best_pipeline = pipeline
            best_model_name = name
            best_y_pred = y_pred

    # Print results table
    results_df = pd.DataFrame(results).round(4)
    print("\nModel Comparison:")
    print(results_df.to_string(index=False))
    
    # Save comparison to report
    with open(REPORTS_DIR / "model_comparison.md", "w") as f:
        f.write("# Model Comparison\n\n")
        f.write(results_df.to_markdown(index=False))
        f.write(f"\n\n**Selected Model:** {best_model_name} (F1: {best_f1:.4f})\n")
    
    # Final Evaluation for best model
    cm = confusion_matrix(y_test, best_y_pred, labels=['ham', 'spam'])
    cr = classification_report(y_test, best_y_pred)
    
    eval_report = f"""# Best Model Evaluation Report

## Selected Architecture
- **Model**: {best_model_name}
- **Vectorization**: TF-IDF (ngram_range=(1,2), max_features=5000, min_df=2)

## Classification Report
```text
{cr}
```

## Confusion Matrix
| | Predicted Ham | Predicted Spam |
|---|---|---|
| **Actual Ham** | {cm[0][0]} | {cm[0][1]} |
| **Actual Spam** | {cm[1][0]} | {cm[1][1]} |
"""
    with open(REPORTS_DIR / "evaluation_metrics.md", "w") as f:
        f.write(eval_report)
        
    print(f"\nSaving best model ({best_model_name}) to disk...")
    model_path = MODELS_DIR / settings.MODEL_FILE_NAME
    joblib.dump(best_pipeline, model_path)
    print(f"Model saved successfully to {model_path}")
    
    # Save metadata
    metadata = {
        "version": settings.ACTIVE_MODEL_VERSION,
        "algorithm": best_model_name,
        "training_samples": len(X_train),
        "accuracy": float(accuracy_score(y_test, best_y_pred)),
        "precision": float(precision_score(y_test, best_y_pred, pos_label='spam')),
        "recall": float(recall_score(y_test, best_y_pred, pos_label='spam')),
        "f1": float(best_f1)
    }
    with open(MODELS_DIR / "model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

if __name__ == "__main__":
    train_and_evaluate()
