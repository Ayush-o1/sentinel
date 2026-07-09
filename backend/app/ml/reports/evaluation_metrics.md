# Best Model Evaluation Report

## Selected Architecture
- **Model**: Linear SVM (Calibrated)
- **Vectorization**: TF-IDF (ngram_range=(1,2), max_features=5000, min_df=2)

## Classification Report
```text
              precision    recall  f1-score   support

         ham       0.99      1.00      0.99       966
        spam       0.97      0.93      0.95       149

    accuracy                           0.99      1115
   macro avg       0.98      0.96      0.97      1115
weighted avg       0.99      0.99      0.99      1115

```

## Confusion Matrix
| | Predicted Ham | Predicted Spam |
|---|---|---|
| **Actual Ham** | 962 | 4 |
| **Actual Spam** | 10 | 139 |
