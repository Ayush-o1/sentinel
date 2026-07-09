# Model Comparison

| Model                   |   Accuracy |   Precision (Spam) |   Recall (Spam) |   F1-Score (Spam) |   Train Time (s) |   Inference Time (s) |
|:------------------------|-----------:|-------------------:|----------------:|------------------:|-----------------:|---------------------:|
| Multinomial Naive Bayes |     0.9794 |             1      |          0.8456 |            0.9164 |           0.0507 |               0.0079 |
| Logistic Regression     |     0.9812 |             0.9156 |          0.9463 |            0.9307 |           0.0523 |               0.0075 |
| Linear SVM (Calibrated) |     0.9874 |             0.972  |          0.9329 |            0.9521 |           0.0905 |               0.0086 |
| Random Forest           |     0.9848 |             0.9925 |          0.8926 |            0.9399 |           0.1565 |               0.0215 |

**Selected Model:** Linear SVM (Calibrated) (F1: 0.9521)
