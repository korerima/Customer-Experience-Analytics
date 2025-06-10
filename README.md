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

---

🛠️ **Requirements**

* Python 3.11+ (Note: `google-play-scraper` has shown compatibility issues with Python 3.13+, so 3.11 or 3.12 is recommended).
* An Oracle Database instance (e.g., Oracle XE) with connection details (username, password, DSN) accessible from your environment.
* **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    Or manually:
    ```bash
    pip install google-play-scraper pandas matplotlib seaborn transformers torch scipy oracledb langdetect scikit-learn
    ```
    *Note: For Oracle Database connectivity, ensure `oracledb` is properly configured, which might require Oracle Client libraries depending on your setup.*

---

🧪 **Run the Complete Pipeline**

To execute the full data pipeline from scraping to analysis and database integration:

1.  **Scrape latest reviews:**
    ```bash
    python scraper.py
    ```
    This script collects raw reviews and saves them to `data/bank_reviews.csv`.

2.  **Preprocess and clean data:**
    ```bash
    python preprocess.py
    ```
    This step cleans the raw data and saves it to `data/bank_reviews_cleaned.csv`.

3.  **Perform Sentiment Analysis:**
    ```bash
    python sentiment_analysis.py
    ```
    This script applies a DistilBERT model to add `sentiment_label` and `sentiment_score` columns, saving the output to `data/bank_reviews_with_sentiment.csv`.

4.  **Extract Keywords and Map to Themes:**
    ```bash
    python thematic_analysis.py
    ```
    This script uses TF-IDF to extract keywords and assigns broader themes to each review, saving the enhanced dataset to `data/bank_reviews_with_sentiment_and_themes.csv`.

5.  **Load data into Oracle Database:**
    ```bash
    python database_script.py
    ```
    **Before running:**
    * Ensure your Oracle Database is running and accessible.
    * Update the `USERNAME`, `PASSWORD`, and `ORACLE_DSN` variables in `database_script.py` with your actual database credentials.
    This script connects to your Oracle DB, creates the `banks` and `reviews` tables (if they don't exist), and inserts the processed data from `bank_reviews_with_sentiment_and_themes.csv`.

6.  **Analyze and Generate Visualizations:**
    ```bash
    python insight_analysis.py
    ```
    **Before running:**
    * Update `db_user`, `db_password`, and `db_dsn` variables in `insight_analysis.py` to match your Oracle Database credentials.
    This final script connects to the Oracle Database, retrieves the data, performs statistical analysis, and generates visualization plots (e.g., `rating_distribution_from_db.png`, `sentiment_distribution_from_db.png`, `positive_words_barchart_from_db.png`, `negative_words_barchart_from_db.png`) in your project directory.

---

📊 **Insights & Recommendations**

This project provides actionable insights by identifying key drivers of positive customer experience (e.g., app simplicity, strong performance, reliable core functionalities like transfers) and major pain points (e.g., transaction failures, system errors, verification issues). Through comparative analysis of CBE, BOA, and Dashen Bank, it highlights unique challenges and strengths, offering targeted recommendations for app improvements focused on consistency, stability, and user-friendliness.

---

🚀 **Future Enhancements**

* **Deeper Thematic Analysis**: Implement more advanced NLP techniques (e.g., Topic Modeling like LDA) for richer, underlying theme discovery.
* **Time-Series Sentiment Analysis**: Track sentiment trends over time to effectively evaluate the impact of app updates and new features.
* **User Segmentation**: Identify distinct user groups based on review characteristics to offer more tailored recommendations.
* **Live Dashboard Integration**: Develop an interactive dashboard (e.g., using Dash or Streamlit) for real-time monitoring and visualization of customer feedback.
* **Benchmarking & Competitive Analysis**: Expand the scope to include more competitors or international banking apps for broader market insights.
* **A/B Testing Integration**: Collaborate with banks to design and implement A/B tests for recommended features, using sentiment shifts as key success metrics.

