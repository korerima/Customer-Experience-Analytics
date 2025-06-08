

from google_play_scraper import reviews,Sort
import pandas as pd
import os
from datetime import datetime

# --- Bank configurations ---
BANKS = [
    {
        'app_id': 'com.combanketh.mobilebanking',
        'name': 'Commercial Bank of Ethiopia',
    },
    {
        'app_id': 'com.boa.boaMobileBanking',
        'name': 'Bank of Abyssinia',
    },
    {
        'app_id': 'com.dashen.dashensuperapp',
        'name': 'Dashen Bank',
    }
]

CSV_FILENAME = './data/bank_reviews.csv'
SOURCE = 'Google Play'
REVIEWS_PER_BANK = 4000  # Or more if needed


def load_existing_reviews(filepath):
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    return pd.DataFrame(columns=['date', 'bank name', 'review', 'rating', 'source'])


def fetch_reviews(app_id, bank_name):
    result, _ = reviews(
        app_id,
        lang='en',
        country='us',
        count=REVIEWS_PER_BANK,
        sort=Sort.MOST_RELEVANT  # newest first
    )

    return [
        {
            'date': r['at'].strftime('%Y-%m-%d'),
            'bank name': bank_name,
            'review': r['content'],
            'rating': r['score'],
            'source': SOURCE
        }
        for r in result
    ]


def update_combined_csv(new_data, existing_df, csv_file):
    new_df = pd.DataFrame(new_data)
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    combined_df.drop_duplicates(subset=['date', 'bank name', 'review'], inplace=True)
    
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)

    combined_df.to_csv(csv_file, index=False)
    return len(new_df), len(combined_df)


def scrape_all_banks():
    print(f"\n📥 Loading existing reviews from: {CSV_FILENAME}")
    existing_df = load_existing_reviews(CSV_FILENAME)

    all_new_reviews = []

    for bank in BANKS:
        print(f"🔍 Scraping reviews for: {bank['name']}")
        reviews_data = fetch_reviews(bank['app_id'], bank['name'])
        all_new_reviews.extend(reviews_data)
        print(f"✅ Collected {len(reviews_data)} reviews for {bank['name']}")

    


    print(f"\n📦 Updating CSV and removing duplicates...")
    new_count, total_count = update_combined_csv(all_new_reviews, existing_df, CSV_FILENAME)
    print(f"📝 Saved {new_count} new reviews (Total in file: {total_count}) → {CSV_FILENAME}")


if __name__ == '__main__':
    scrape_all_banks()


###########################################
