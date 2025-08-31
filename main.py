import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import nltk
import re

# Download NLTK data
try:
    nltk.download("punkt")
    nltk.download("cmudict")
except:
    print("NLTK downloads failed, continuing anyway...")

# Get dictionary for counting syllables
try:
    from nltk.corpus import cmudict
    pronunciation_dict = cmudict.dict()
except:
    pronunciation_dict = {}

def get_articles_from_excel(file_path):
    """Read URLs from Excel file"""
    print("Reading Excel file...")
    data = pd.read_excel(file_path)
    return data

def download_article(url):
    """Download and clean article from URL"""
    try:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Get the webpage
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                break  # Success, exit retry loop
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == max_retries - 1:  # Last attempt
                    print(f"All {max_retries} attempts failed for {url}")
                    return None, None
        
        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove unwanted parts
        for tag in soup(['script', 'style', 'header', 'footer', 'nav']):
            tag.decompose()
        
        # Get title
        title = ""
        if soup.find("h1"):
            title = soup.find("h1").get_text().strip()
        elif soup.title:
            title = soup.title.get_text().strip()
        
        # Get all paragraphs
        paragraphs = soup.find_all("p")
        article_text = ""
        
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 20:  # Only keep paragraphs with some content
                article_text += text + "\n"
        
        return title, article_text
        
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None, None

def save_article(article_id, title, text, folder):
    """Save article to text file"""
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    filename = f"{article_id}.txt"
    file_path = os.path.join(folder, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"{title}\n\n{text}")
    
    return file_path, filename

def read_stopwords(folder_path):
    """Read all stopwords from text files in folder"""
    all_stopwords = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    words = f.read().split()
                    all_stopwords.extend(words)
            except:
                # Try different encoding if UTF-8 fails
                with open(file_path, "r", encoding="latin-1") as f:
                    words = f.read().split()
                    all_stopwords.extend(words)
    
    return list(set(all_stopwords))  # Remove duplicates

def remove_stopwords_from_text(text, stopwords):
    """Remove stopwords from text"""
    words = text.split()
    clean_words = []
    
    for word in words:
        if word.lower() not in stopwords:
            clean_words.append(word)
    
    return " ".join(clean_words)

def count_syllables(word):
    """Count syllables in a word"""
    word = word.lower()
    
    # Try using pronunciation dictionary first
    if word in pronunciation_dict:
        return len([sound for sound in pronunciation_dict[word][0] if sound[-1].isdigit()])
    
    # Simple fallback method
    vowels = "aeiouy"
    count = 0
    prev_was_vowel = False
    
    for char in word:
        if char in vowels:
            if not prev_was_vowel:
                count += 1
            prev_was_vowel = True
        else:
            prev_was_vowel = False
    
    # Every word has at least 1 syllable
    return max(1, count)

def read_word_list(file_path):
    """Read positive or negative words from file"""
    words = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip().lower()
                if word and not word.startswith(";"):
                    words.add(word)
    except:
        print(f"Could not read {file_path}")
    
    return words

def analyze_article_text(text, positive_words, negative_words):
    """Analyze text and calculate various scores"""
    
    # Split into sentences and words
    sentences = nltk.sent_tokenize(text)
    words = nltk.word_tokenize(text)
    
    # Filter out punctuation and keep only words
    clean_words = [word for word in words if word.isalpha()]
    
    # Basic counts
    word_count = len(clean_words)
    sentence_count = len(sentences)
    
    if word_count == 0 or sentence_count == 0:
        return {}
    
    # Count positive and negative words
    positive_count = 0
    negative_count = 0
    
    for word in clean_words:
        word_lower = word.lower()
        if word_lower in positive_words:
            positive_count += 1
        if word_lower in negative_words:
            negative_count += 1
    
    # Calculate sentiment scores
    total_sentiment_words = positive_count + negative_count
    if total_sentiment_words > 0:
        polarity = (positive_count - negative_count) / total_sentiment_words
        subjectivity = total_sentiment_words / word_count
    else:
        polarity = 0.0
        subjectivity = 0.0
    
    # Calculate readability metrics
    avg_sentence_length = word_count / sentence_count
    
    # Count complex words (more than 2 syllables)
    complex_word_count = 0
    total_syllables = 0
    
    for word in clean_words:
        syllables = count_syllables(word)
        total_syllables += syllables
        if syllables > 2:
            complex_word_count += 1
    
    percentage_complex = (complex_word_count / word_count) * 100
    fog_index = 0.4 * (avg_sentence_length + percentage_complex)
    avg_syllables_per_word = total_syllables / word_count
    
    # Count personal pronouns (case-insensitive search in original text)
    personal_pronouns = len(re.findall(r'\b(I|we|my|ours|us)\b', text, re.IGNORECASE))
    
    # Average word length (character count)
    total_chars = sum(len(word) for word in clean_words)
    avg_word_length = total_chars / word_count
    
    # Return all metrics rounded to 3 decimal places
    return {
        "POSITIVE SCORE": positive_count,
        "NEGATIVE SCORE": negative_count,
        "POLARITY SCORE": round(polarity, 3),
        "SUBJECTIVITY SCORE": round(subjectivity, 3),
        "AVG SENTENCE LENGTH": round(avg_sentence_length, 3),
        "PERCENTAGE OF COMPLEX WORDS": round(percentage_complex, 3),
        "FOG INDEX": round(fog_index, 3),
        "AVG NUMBER OF WORDS PER SENTENCE": round(avg_sentence_length, 3),
        "COMPLEX WORD COUNT": complex_word_count,
        "WORD COUNT": word_count,
        "SYLLABLE PER WORD": round(avg_syllables_per_word, 3),
        "PERSONAL PRONOUNS": personal_pronouns,
        "AVG WORD LENGTH": round(avg_word_length, 3),
    }

def main():
    """Main function to run the entire analysis"""
    
    # Step 1: Read URLs from Excel
    print("Step 1: Reading URLs from Excel file...")
    excel_file = "data/Input.xlsx"
    url_data = get_articles_from_excel(excel_file)
    
    # Step 2: Download articles
    print("Step 2: Downloading articles...")
    articles_folder = "data/articles"
    
    # Keep track of downloaded articles with their URLs
    article_info = {}  # Will store {url_id: {"url": url, "filename": filename}}
    
    for index, row in url_data.iterrows():
        url_id = str(row['URL_ID'])
        url = row['URL']
        
        print(f"Downloading article {url_id}...")
        title, article_text = download_article(url)
        
        if title and article_text:
            file_path, filename = save_article(url_id, title, article_text, articles_folder)
            article_info[url_id] = {"url": url, "filename": filename}
            print(f"Saved: {file_path}")
        else:
            print(f"Failed to download article {url_id}")
    
    # Step 3: Load stopwords
    print("Step 3: Loading stopwords...")
    stopwords_folder = "data/StopWords"
    stopwords = read_stopwords(stopwords_folder)
    print(f"Loaded {len(stopwords)} stopwords")
    
    # Step 4: Clean articles (remove stopwords)
    print("Step 4: Removing stopwords from articles...")
    clean_articles_folder = "data/articles_clean"
    
    for url_id, info in article_info.items():
        # Read original file
        original_file_path = os.path.join(articles_folder, info["filename"])
        with open(original_file_path, "r", encoding="utf-8") as f:
            original_text = f.read()
        
        # Remove stopwords
        clean_text = remove_stopwords_from_text(original_text, stopwords)
        
        # Save clean version
        clean_file_path = os.path.join(clean_articles_folder, info["filename"])
        
        if not os.path.exists(clean_articles_folder):
            os.makedirs(clean_articles_folder)
        
        with open(clean_file_path, "w", encoding="utf-8") as f:
            f.write(clean_text)
    
    # Step 5: Load sentiment word lists
    print("Step 5: Loading positive and negative word lists...")
    positive_words = read_word_list("data/MasterDictionary/positive-words.txt")
    negative_words = read_word_list("data/MasterDictionary/negative-words.txt")
    
    print(f"Loaded {len(positive_words)} positive words")
    print(f"Loaded {len(negative_words)} negative words")
    
    # Step 6: Analyze all articles
    print("Step 6: Analyzing articles...")
    all_results = []
    
    for url_id, info in article_info.items():
        filename = info["filename"]
        url = info["url"]
        file_path = os.path.join(clean_articles_folder, filename)
        
        # Read clean article
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        # Analyze the text
        results = analyze_article_text(text, positive_words, negative_words)
        
        # Add URL_ID, URL, and filename (without .txt extension)
        results["URL_ID"] = url_id
        results["URL"] = url
        # results["filename"] = filename.replace(".txt", "")  # Remove .txt extension
        
        all_results.append(results)
        print(f"Analyzed: {filename}")
    
    # Step 7: Save results to CSV
    print("Step 7: Saving results...")
    results_df = pd.DataFrame(all_results)
    
    # Reorder columns - put URL_ID, URL, and filename first
    columns = [
        "URL_ID",
        "URL", 
        
        "POSITIVE SCORE", 
        "NEGATIVE SCORE", 
        "POLARITY SCORE", 
        "SUBJECTIVITY SCORE",
        "AVG SENTENCE LENGTH", 
        "PERCENTAGE OF COMPLEX WORDS", 
        "FOG INDEX",
        "AVG NUMBER OF WORDS PER SENTENCE", 
        "COMPLEX WORD COUNT", 
        "WORD COUNT", 
        "SYLLABLE PER WORD", 
        "PERSONAL PRONOUNS", 
        "AVG WORD LENGTH"
    ]
    
    results_df = results_df[columns]
    results_df.to_csv("Sentiment_analysis_output.csv", index=False)
    print("✅ Analysis complete! Results saved to Sentiment_analysis_output.csv")
    
    # Show summary
    print(f"\nSummary:")
    print(f"- Processed {len(all_results)} articles")
    print(f"- Results saved to CSV file")

if __name__ == "__main__":
    main()