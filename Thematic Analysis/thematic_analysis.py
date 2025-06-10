import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter

# === Configuration ===
INPUT_FILE = "./data/bank_reviews_with_sentiment.csv"
OUTPUT_FILE = "./data/bank_reviews_with_sentiment_and_themes.csv"


def load_data(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        print(f"📄 Loaded {len(df)} reviews from {path}")
        return df
    except Exception as e:
        raise RuntimeError(f"❌ Error loading file: {e}")


def extract_keywords_tfidf(df: pd.DataFrame, max_features=1000, top_n=3) -> pd.DataFrame:
    #Add a 'keywords' column using top TF-IDF terms per review.
    print("🔍 Extracting keywords using TF-IDF...")

    tfidf = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2),        # unigrams and bigrams
        max_features=max_features
    )

    tfidf_matrix = tfidf.fit_transform(df['review'])
    feature_names = tfidf.get_feature_names_out()

    top_keywords = []
    for row in tfidf_matrix:
        row_array = row.toarray().flatten()
        top_indices = row_array.argsort()[-top_n:][::-1]
        keywords = [feature_names[i] for i in top_indices if row_array[i] > 0]
        top_keywords.append(", ".join(keywords))

    df['keywords'] = top_keywords
    return df


def map_to_theme(keywords: str) -> str:
    #Map keyword phrases to broader review themes using improved matching logic.
    if not isinstance(keywords, str):
        return "Other"
    
    keywords = keywords.lower()

    themes = {
        "Account Access Issues": ["login", "password", "otp", "fail", "reset", "account", "credential", "sign in", "issue", "error"],
        "Transaction Performance": ["transfer", "transaction", "delay", "slow", "time", "send", "load", "balance", "process", "service"],
        "User Interface & Design": ["design", "layout", "interface", "menu", "simple", "navigation", "ui", "user friendly", "easy", "nice app"],
        "App Speed & Stability": ["crash", "hang", "bug", "freeze", "working", "load", "respond", "open", "update", "performance"],
        "Customer Satisfaction": ["good", "best", "nice", "love", "amazing", "great", "helpful", "thanks", "recommend", "really"],
        "Feature Requests": ["add", "feature", "option", "setting", "request", "upgrade", "improve"]
    }

    for theme, keywords_list in themes.items():
        if any(kw in keywords for kw in keywords_list):
            return theme

    return "Other"



def apply_theme_mapping(df: pd.DataFrame) -> pd.DataFrame:
    print("🧠 Mapping keywords to themes...")
    df['theme'] = df['keywords'].apply(map_to_theme)
    return df


def save_output(df: pd.DataFrame, path: str):
    try:
        df.to_csv(path, index=False)
        print(f"✅ Saved themed data to: {path}")
    except Exception as e:
        raise RuntimeError(f"❌ Error saving output: {e}")

def get_keyword_frequencies(df: pd.DataFrame, column: str = 'keywords', top_n: int = 50) -> pd.DataFrame:
    
    all_keywords = []

    for row in df[column].dropna():
        # Split the comma-separated keywords and strip whitespace
        all_keywords.extend([kw.strip().lower() for kw in row.split(",") if kw.strip()])

    keyword_counts = Counter(all_keywords)
    most_common = keyword_counts.most_common(top_n)

    return pd.DataFrame(most_common, columns=["keyword", "count"])

def main():
    df = load_data(INPUT_FILE)
    df = extract_keywords_tfidf(df)
    
    #for making the thematic grouping more better and acurate
    top_keywords_df = get_keyword_frequencies(df, top_n=30)
    print(top_keywords_df)

    df = apply_theme_mapping(df)
    save_output(df, OUTPUT_FILE)


if __name__ == "__main__":
    print("🚀 Starting Thematic Analysis...")
    main()
