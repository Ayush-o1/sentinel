# Machine Learning Pipeline

## Overview
SENTINEL identifies spam using a highly optimized, scikit-learn based Machine Learning pipeline. The entire process—from text cleaning to inference to explainability—is managed natively within the Python ecosystem.

## Dataset
- **Source**: UCI SMS Spam Collection Dataset.
- **Characteristics**: 5,574 labeled messages. Imbalanced distribution (~86% Ham, ~14% Spam), which accurately reflects the real-world occurrence of spam.
- **Why this dataset?**: It is the gold standard benchmark for text-based message classification.

## Preprocessing (NLP)
Before inference, raw text passes through an 11-stage NLP pipeline (`app/ml/pipeline.py`):
1. **Unicode Normalization**: Strips zero-width characters and normalizes encoding.
2. **Entity Replacement**: URLs (`[URL]`), Emails (`[EMAIL]`), and Phone numbers (`[PHONE]`) are substituted with neutral tokens to prevent the model from overfitting to specific links.
3. **Punctuation Stripping**: Retains alphanumeric data.
4. **Emoji Translation**: Uses `emoji.demojize()` to convert emojis into textual features (e.g., 🚨 becomes `:police_car_light:`).
5. **Tokenization**: Splits text into arrays using `nltk.word_tokenize`.
6. **Smart Stopword Removal**: Removes common English words but explicitly retains high-signal terms (e.g., "free", "win", "now").
7. **Lemmatization**: Reduces words to their dictionary root (`WordNetLemmatizer`).

## Feature Engineering
The preprocessed text is transformed into numerical vectors using **TF-IDF (Term Frequency-Inverse Document Frequency)**.
- `ngram_range=(1,2)`: Captures both individual words and bigrams ("claim prize").
- `max_features=5000`: Caps the vocabulary size to keep the serialized model exceptionally lightweight (~20MB) and fast.

## Model Training & Comparison
Four models were evaluated using the offline training scripts (`ml/scripts/train.py`). F1-Score on the Spam class was the primary evaluation metric, as it optimally balances catching malicious messages while strictly minimizing false positives.

| Model | Accuracy | Precision (Spam) | Recall (Spam) | F1-Score (Spam) |
|---|---|---|---|---|
| Multinomial NB | 97.94% | 100.00% | 84.56% | 91.64% |
| Logistic Regression | 98.12% | 91.56% | 94.63% | 93.07% |
| **LinearSVC (Calibrated)** | **98.74%** | **97.20%** | **93.29%** | **95.21%** |
| Random Forest | 98.48% | 99.25% | 89.26% | 93.99% |

## The Final Model
The **Linear Support Vector Machine (LinearSVC)** was selected. Because a standard SVM does not natively output confidence probabilities, it was wrapped in a `CalibratedClassifierCV`. The final artifact is serialized as `sentinel_v1.0.0.joblib`.

## Explainability (LIME)
SENTINEL provides "glass-box" transparency. When a prediction is made, the text is also passed to `SentinelExplainer` which uses **LIME**. 
LIME randomly perturbs (masks) words in the message and observes how the model's prediction changes. This allows the system to assign exact numeric "suspicion weights" to individual words, which the frontend highlights in red or green.

## Inference Pipeline Architecture
The `MLModel` class loads the `.joblib` file into FastAPI's memory exactly once at startup. When `predict()` is called, all heavy CPU operations (NLP, sklearn inference, LIME) are wrapped in `asyncio.to_thread()` to prevent blocking the asynchronous ASGI event loop. Average inference latency is `< 10ms`.
