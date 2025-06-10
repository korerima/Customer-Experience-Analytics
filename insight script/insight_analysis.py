import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
import oracledb

# --- Database Connection ---
# IMPORTANT: Replace with your actual database credentials and connection string.
# Example DSN format: "your_hostname:your_port/your_service_name"
db_user = "SYS"
db_password = "aeiou"
db_dsn = oracledb.makedsn("localhost", 1521, service_name="XEPDB1")

connection = None # Initialize connection to None
try:
    # Establish the connection to the Oracle database
    connection = oracledb.connect(user=db_user, password=db_password, dsn=db_dsn, mode=oracledb.SYSDBA)
    print("Successfully connected to Oracle Database!")

    # --- Load Banks Data (can use pandas directly) ---
    banks_query = "SELECT ID, NAME FROM BANKS"
    banks_df = pd.read_sql_query(banks_query, connection)

    # --- Load Reviews Data with Explicit LOB Handling ---
    reviews_data_list = [] # To store lists of row data
    cursor = connection.cursor() # Create a cursor to fetch reviews
    reviews_query_sql = "SELECT ID, BANK_ID, REVIEW_TEXT, RATING, SENTIMENT_LABEL FROM REVIEWS"
    cursor.execute(reviews_query_sql)

    # Define column names for clarity for the DataFrame
    reviews_columns = ['ID', 'BANK_ID', 'REVIEW_TEXT', 'RATING', 'SENTIMENT_LABEL']

    for row in cursor:
        row_list = list(row) # Convert tuple to list to modify
        
        # Check if the REVIEW_TEXT (at index 2) is an oracledb.LOB object
        if isinstance(row_list[2], oracledb.LOB):
            try:
                # Read the CLOB content into a Python string
                row_list[2] = row_list[2].read()
            except oracledb.Error as e:
                error_obj, = e.args
                print(f"Warning: Could not read LOB for review ID {row_list[0]}. Error: {error_obj.message}")
                row_list[2] = None # Set to None if reading fails
        # Handle cases where it might already be None or a string (though unlikely for CLOB from raw fetch)
        elif row_list[2] is None:
            row_list[2] = None # Explicitly keep as None
        # If it's already a string, it remains as is

        reviews_data_list.append(row_list)

    reviews_df = pd.DataFrame(reviews_data_list, columns=reviews_columns)
    cursor.close() # Close cursor after fetching all data

except Exception as e:
    print("Error connecting to the database or fetching data:", e)
    # Exit the script if the database connection fails
    exit()

finally:
    # Always close the connection when you're done
    if connection and connection.is_healthy(): # Check if connection object exists and is healthy before closing
        connection.close()
        print("Database connection closed.")


# --- Rest of your code (Data Preparation, Text Preprocessing, Visualizations) ---

# Data Preparation and Merging
df = pd.merge(reviews_df, banks_df, left_on='BANK_ID', right_on='ID')
df.rename(columns={'NAME': 'BANK_NAME'}, inplace=True)


# Text Preprocessing for Word Frequency Analysis (Your function as provided previously)
# ... (your get_most_common_words function goes here, as it was corrected)
def get_most_common_words(review_series, num_words=15):
    """
    Analyzes a pandas Series of reviews, handles Oracle LOBs, and returns the most common words.

    Args:
        review_series: A pandas Series containing review text (can include strings or LOBs).
        num_words: The number of top words to return.

    Returns:
        A list of tuples with the most common words and their counts.
    """
    clean_texts = []
    # Loop through each item in the Series to handle LOBs safely
    for review in review_series:
        try:
            # If the item is an oracledb.LOB object (typically for CLOBs)
            # This check might still be useful if data comes from other sources,
            # but after the explicit reading above, it should ideally be a string.
            if isinstance(review, oracledb.LOB):
                text_content = review.read()
                if text_content: # Ensure it's not None or empty
                    clean_texts.append(text_content)
            # If it's already a string
            elif isinstance(review, str):
                if review: # Ensure it's not empty
                    clean_texts.append(review)
            # If it's bytes (e.g., a BLOB that needs decoding)
            elif isinstance(review, bytes):
                try:
                    # Attempt to decode bytes to a string (e.g., UTF-8)
                    decoded_text = review.decode('utf-8')
                    if decoded_text:
                        clean_texts.append(decoded_text)
                except UnicodeDecodeError:
                    print(f"Warning: Could not decode bytes for a review. Skipping.")
            # Handle pandas NaN or None values
            elif review is None or (isinstance(review, float) and pd.isna(review)):
                continue # Skip None/NaN values
            else:
                # Catch any other unexpected types
                print(f"Warning: Unexpected data type for review: {type(review)}. Skipping.")

        except Exception as e:
            # This will skip any problematic entries and print a warning
            print(f"Warning: Could not process a review. Error: {e}")
            continue

    # Join all the cleaned review strings into one large text block
    all_text = ' '.join(filter(None, clean_texts)).lower()

    # The rest of the logic is the same as before
    all_text = re.sub(r'[^a-zA-Z0-9\s]', '', all_text)
    words = all_text.split()

    # Define words to ignore in the analysis
    stop_words = set([
        'the', 'a', 'an', 'and', 'is', 'in', 'it', 'of', 'for', 'on', 'with',
        'to', 'app', 'bank', 'cbe', 'boa', 'awash', 'dashen', 'i', 'this',
        'not', 'but', 'its', 'be', 'are', 'you', 'my', 'that', 'have', # Added from current lists
        'what', 'when', 'where', 'how', 'why', 'which', 'who', 'whom', 'whose', # Wh-words
        'can', 'will', 'just', 'get', 'dont', 'doesnt', 'cant', 'would', 'could', # Modals/contractions
        'like', 'very', 'much', 'so', 'really', 'good', 'great', 'best', 'nice', # Common evaluative words
        'more', 'less', 'than', 'them', 'then', 'there', 'these', 'those',
        'from', 'about', 'out', 'up', 'down', 'through', 'after', 'before', 'over', 'under',
        'we', 'they', 'she', 'he', 'me', 'us', 'him', 'her', 'itself', 'myself',
        'our', 'your', 'their', 'only', 'also', 'even', 'one', 'two', 'three', 'etc',
        'use', 'using', 'used', 'service', 'customer', 'online', 'mobile', 'internet', # Common domain-specific but generic
        'time', 'now', 'always', 'still', 'yet', 'never', 'ever', 'too', 'just', 'some', 'any',
        'all', 'every', 'each', 'no', 'none', 'nothing', 'something', 'anything',
        'where', 'here', 'there', 'then', 'hence', 'thus', 'else', 'etc',
        'working', 'work', 'please', 'update', # From your current negative list
        'easy', 'fast', 'application', 'banking', 'transaction', # From your current lists, if too generic
        'couldn', 'didn', 'doesn', 'hadn', 'hasn', 'haven', 'isn', 'mightn', 'mustn', # More contractions
        'need', 'should', 'wasn', 'weren', 'won', 'wouldn', # More contractions
        'etc', 'etc', # Just in case
        'thank','thanks','amazing','ethiopia','love','user','am','better','apps','make','life','has',
        'keep','money','account','if','or','was','as','other','make','has','do','at',
        'wow','add','well','makes','by','experience','excellent',
        'been','code','try','sometimes','option','developer','phone','problem','worst','fix',
        'go','times','says','recent','bad','see','show','new',
        'job','most','version','services','digital','useful'
    ])

    words = [word for word in words if word not in stop_words and word.strip() != '']
    word_counts = Counter(words)

    return word_counts.most_common(num_words)


# Get most common words for positive and negative reviews
positive_reviews_texts = df[df['SENTIMENT_LABEL'] == 'positive']['REVIEW_TEXT']
negative_reviews_texts = df[df['SENTIMENT_LABEL'] == 'negative']['REVIEW_TEXT']

# These calls should now receive pandas Series of strings, not LOB objects
most_common_positive = get_most_common_words(positive_reviews_texts)
most_common_negative = get_most_common_words(negative_reviews_texts)

# Convert to DataFrames for plotting
positive_words_df = pd.DataFrame(most_common_positive, columns=['word', 'count'])
negative_words_df = pd.DataFrame(most_common_negative, columns=['word', 'count'])


# --- Visualizations (The rest of the script remains the same) ---

# 1. Rating Distribution per Bank
plt.figure(figsize=(10, 6))
sns.countplot(data=df, x='RATING', hue='BANK_NAME', palette='viridis')
plt.title('Distribution of Ratings per Bank')
plt.xlabel('Rating')
plt.ylabel('Number of Reviews')
plt.legend(title='Bank')
plt.tight_layout()
plt.savefig('rating_distribution_from_db.png')
plt.show()

# 2. Sentiment Distribution per Bank
plt.figure(figsize=(10, 6))
sns.countplot(data=df, x='SENTIMENT_LABEL', hue='BANK_NAME', order=['positive', 'negative', 'neutral'], palette='magma')
plt.title('Distribution of Sentiments per Bank')
plt.xlabel('Sentiment')
plt.ylabel('Number of Reviews')
plt.legend(title='Bank')
plt.tight_layout()
plt.savefig('sentiment_distribution_from_db.png')
plt.show()

# 3. Most Common Words in Positive Reviews (Drivers)
plt.figure(figsize=(12, 7))
sns.barplot(data=positive_words_df, x='count', y='word', palette='Greens_r')
plt.title('Most Common Words in Positive Reviews (Drivers)')
plt.xlabel('Frequency')
plt.ylabel('Words')
plt.tight_layout()
plt.savefig('positive_words_barchart_from_db.png')
plt.show()

# 4. Most Common Words in Negative Reviews (Pain Points)
plt.figure(figsize=(12, 7))
sns.barplot(data=negative_words_df, x='count', y='word', palette='Reds_r')
plt.title('Most Common Words in Negative Reviews (Pain Points)')
plt.xlabel('Frequency')
plt.ylabel('Words')
plt.tight_layout()
plt.savefig('negative_words_barchart_from_db.png')
plt.show()

print("\nAnalysis complete. All visualizations have been saved with the '_from_db' suffix.")