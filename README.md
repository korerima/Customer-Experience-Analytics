# Customer Experience Analytics for Ethiopian Banks

This project collects, cleans, and analyzes customer reviews for major Ethiopian banks' mobile apps from the Google Play Store. The goal is to extract insights about customer sentiment and recurring themes to improve digital banking experiences.

## 🚀 Features

- ✅ Scrapes Google Play reviews for:
  - Commercial Bank of Ethiopia
  - Bank of Abyssinia
  - Dashen Bank
- ✅ Saves to a unified CSV file with deduplication
- ✅ Preprocessing pipeline includes:
  - Date normalization (YYYY-MM-DD)
  - Removal of blank and non-English reviews
  - Emoji stripping and repeated punctuation cleaning

## 📂 Project Structure
```bash
    
```
```bash
.
├── data/
│   ├── bank_reviews.csv              # Raw scraped reviews
│   └── bank_reviews_cleaned.csv      # Cleaned version for analysis
├── scraper.py                        # Scrapes reviews from Google Play
├── preprocess.py                     # Cleans and filters review data
├── README.md                         # You’re here

```
🛠️ Requirements
Python 3.10+

Install dependencies:

```bash
    pip install -r requirements.txt
```
Or manually:
```bash
    pip install google-play-scraper pandas langdetect
```

🧪 Run the Pipeline
Scrape latest reviews:
```bash
    python scraper.py
```
Preprocess and clean:
```bash
    python preprocess.py
```

