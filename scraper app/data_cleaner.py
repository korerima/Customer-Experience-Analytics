import os
import pandas as pd
import re
from datetime import datetime
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Make detection consistent
DetectorFactory.seed = 42

def load_reviews(file_path: str) -> pd.DataFrame:
    #Loading the scraped CSV file into a DataFrame
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ File not found: {file_path}")
    try:
        df = pd.read_csv(file_path)
        print(f"📄 Loaded {len(df)} rows from: {file_path}")
        return df
    except Exception as e:
        raise RuntimeError(f"❌ Failed to load CSV: {e}")


def normalize_dates(df: pd.DataFrame) -> pd.DataFrame:
    #Ensuring all dates are in YYYY-MM-DD format
    try:
        df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
    except Exception as e:
        raise ValueError(f"❌ Date normalization failed: {e}")
    return df


def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    #Removing missing reviews, emojis, and excessive punctuation/whitespace
    # Drop missing or blank reviews
    df = df.dropna(subset=['review'])
    df['review'] = df['review'].astype(str).str.strip()
    df = df[df['review'].str.len() > 0]

    # Remove emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002700-\U000027BF"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    df['review'] = df['review'].apply(lambda x: emoji_pattern.sub('', x))

    # Normalize whitespace
    df['review'] = df['review'].str.replace(r'\s+', ' ', regex=True).str.strip()

    return df


def save_cleaned_data(df: pd.DataFrame, output_path: str):
    #Saving the cleaned DataFrame to CSV
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"✅ Cleaned data saved to: {output_path} ({len(df)} rows)")
    except Exception as e:
        raise RuntimeError(f"❌ Failed to save cleaned data: {e}")

def remove_non_english_reviews(df: pd.DataFrame) -> pd.DataFrame:
    #Removing  reviews not detected as English (lang='en')
    def is_english(text):
        try:
            return detect(text.strip()) == 'en'
        except LangDetectException:
            return False  # empty or malformed

    print("🌍 Filtering non-English reviews...")
    df['is_english'] = df['review'].apply(is_english)
    df = df[df['is_english']].drop(columns=['is_english'])
    print(f"✅ Remaining after language filter: {len(df)} rows")
    return df

def preprocess_reviews(input_path: str, output_path: str):
    #Full preprocessing pipeline
    try:
        df = load_reviews(input_path)
        df = normalize_dates(df)
        df = clean_reviews(df)
        df = remove_non_english_reviews(df)
        save_cleaned_data(df, output_path)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    input_file = "./data/bank_reviews.csv"
    output_file = "./data/bank_reviews_cleaned.csv"
    print("🔧 Starting preprocessing...")
    preprocess_reviews(input_file, output_file)
