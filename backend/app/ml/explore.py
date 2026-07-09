import sys
import os
from pathlib import Path

# Add backend directory to PYTHONPATH
backend_dir = str(Path(__file__).resolve().parent.parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

from app.ml.pipeline import preprocess

DATA_DIR = Path(__file__).parent / "data" / "raw"
REPORT_DIR = Path(__file__).parent / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

def explore_data():
    dataset_file = DATA_DIR / "SMSSpamCollection"
    if not dataset_file.exists():
        print(f"Dataset not found at {dataset_file}")
        return
        
    print("Loading dataset...")
    df = pd.read_csv(dataset_file, sep='\t', header=None, names=['label', 'text'])
    
    total = len(df)
    counts = df['label'].value_counts()
    ham_count = counts.get('ham', 0)
    spam_count = counts.get('spam', 0)
    
    df['length'] = df['text'].apply(len)
    avg_len = df['length'].mean()
    avg_len_ham = df[df['label'] == 'ham']['length'].mean()
    avg_len_spam = df[df['label'] == 'spam']['length'].mean()

    print("Preprocessing messages for vocabulary analysis...")
    processed = []
    for i, text in enumerate(df['text']):
        if i % 1000 == 0:
            print(f"Processed {i}/{total} messages")
        res = preprocess(text)
        processed.append(res['tokens'])
    
    df['tokens'] = processed
    
    all_ham_tokens = [tok for toks in df[df['label'] == 'ham']['tokens'] for tok in toks]
    all_spam_tokens = [tok for toks in df[df['label'] == 'spam']['tokens'] for tok in toks]
    
    vocab_size = len(set(all_ham_tokens + all_spam_tokens))
    
    ham_counter = Counter(all_ham_tokens)
    spam_counter = Counter(all_spam_tokens)
    
    print("Generating visualizations...")
    sns.set_theme(style="whitegrid")
    
    # Class distribution plot
    plt.figure(figsize=(6, 4))
    sns.countplot(data=df, x='label', hue='label', palette='viridis', legend=False)
    plt.title('Class Distribution (Ham vs Spam)')
    plt.savefig(REPORT_DIR / 'class_distribution.png')
    plt.close()
    
    # Length distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='length', hue='label', bins=50, kde=True, palette='viridis')
    plt.title('Message Length Distribution')
    plt.xlim(0, 300)
    plt.savefig(REPORT_DIR / 'length_distribution.png')
    plt.close()

    # Top words
    def plot_top_words(counter, title, filename):
        top_words = counter.most_common(20)
        words, counts = zip(*top_words)
        plt.figure(figsize=(10, 6))
        sns.barplot(x=list(counts), y=list(words), hue=list(words), palette='viridis', legend=False)
        plt.title(title)
        plt.savefig(REPORT_DIR / filename)
        plt.close()
        
    plot_top_words(ham_counter, 'Top 20 Words in Ham Messages', 'top_ham_words.png')
    plot_top_words(spam_counter, 'Top 20 Words in Spam Messages', 'top_spam_words.png')
    
    report = f"""# SENTINEL Dataset Exploration Report

## Dataset Source
UCI SMS Spam Collection

## Summary Statistics
- **Total Messages**: {total}
- **Ham Messages**: {ham_count} ({ham_count/total*100:.1f}%)
- **Spam Messages**: {spam_count} ({spam_count/total*100:.1f}%)
- **Spam vs Ham Ratio**: 1 : {ham_count/spam_count:.2f}
- **Average Message Length**: {avg_len:.1f} characters
  - **Average Ham Length**: {avg_len_ham:.1f} characters
  - **Average Spam Length**: {avg_len_spam:.1f} characters
- **Total Vocabulary Size**: {vocab_size} unique tokens

## Visualizations
![Class Distribution](./class_distribution.png)
![Message Length Distribution](./length_distribution.png)
![Top Ham Words](./top_ham_words.png)
![Top Spam Words](./top_spam_words.png)
"""
    with open(REPORT_DIR / "data_exploration_report.md", "w") as f:
        f.write(report)
        
    print("Exploration complete. Reports saved to app/ml/reports.")

if __name__ == "__main__":
    explore_data()
