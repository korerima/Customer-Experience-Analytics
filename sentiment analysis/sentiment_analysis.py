import pandas as pd
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax

# --- Configuration ---
INPUT_FILE = "./data/bank_reviews_cleaned.csv"
OUTPUT_FILE = "./data/bank_reviews_with_sentiment.csv"
MODEL_NAME = "distilbert/distilbert-base-uncased-finetuned-sst-2-english" 
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
THRESHOLD = 0.4  # Neutral if confidence < this value from both ends


def load_data(file_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path)
        print(f"📄 Loaded {len(df)} reviews")
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to read file: {e}")


def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.to(DEVICE)
    return tokenizer, model


def predict_sentiment_batch(texts, tokenizer, model, batch_size=32):
    sentiments = []
    scores = []

    model.eval()
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            inputs = tokenizer(batch_texts, return_tensors="pt", padding=True, truncation=True, max_length=512).to(DEVICE)
            outputs = model(**inputs)
            logits = outputs.logits.detach().cpu().numpy()
            probs = softmax(logits, axis=1)

            for prob in probs:
                score = prob[1]  # Positive class confidence
                if score >= (1 - THRESHOLD):
                    label = "positive"
                elif score <= THRESHOLD:
                    label = "negative"
                else:
                    label = "neutral"

                sentiments.append(label)
                scores.append(round(float(score), 4))

    return sentiments, scores


def add_sentiment(df: pd.DataFrame, tokenizer, model):
    print("🔍 Predicting sentiment using DistilBERT...")
    texts = df['review'].astype(str).tolist()
    sentiments, scores = predict_sentiment_batch(texts, tokenizer, model)
    df['sentiment_label'] = sentiments
    df['sentiment_score'] = scores
    return df


def save_output(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False)
    print(f"✅ Output saved to: {path}")


def main():
    df = load_data(INPUT_FILE)

    # Add review_id before analysis
    df.reset_index(drop=True, inplace=True)
    df['review_id'] = df.index.map(lambda i: f"rev_{i+1:05d}")

    tokenizer, model = load_model()
    df = add_sentiment(df, tokenizer, model)
    save_output(df, OUTPUT_FILE)



if __name__ == "__main__":
    print("🚀 Starting Task 2 Sentiment Analysis with DistilBERT...")
    main()
