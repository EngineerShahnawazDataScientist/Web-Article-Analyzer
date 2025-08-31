# Web-Article-Analyzer
Python tool for web article extraction, preprocessing, sentiment analysis, and readability metrics

# 📘 Text Analysis Pipeline

This project performs *end-to-end text analysis* on articles extracted from a list of URLs.
It covers *data extraction, scraping, cleaning, ingestion, and scoring* using sentiment and readability metrics.

---

## 🛠 Features

1. *Data Extraction*

   * Reads a list of URLs from an Excel file.
   * Fetches and parses article content using BeautifulSoup.
   * Cleans text (removes headers, footers, scripts, ads).
   * Saves each article as a .txt file.

2. *Ingestion*

   * Reads the cleaned .txt articles.
   * Loads *positive* and *negative word lexicons*.

3. *Text Analysis / Scoring*

   * Sentiment Analysis:

     * Positive Score
     * Negative Score
     * Polarity Score
     * Subjectivity Score
   * Readability Metrics:

     * Average Sentence Length
     * Percentage of Complex Words
     * Fog Index
     * Average Number of Words per Sentence
     * Complex Word Count
     * Word Count
     * Syllable per Word
     * Personal Pronouns Count
     * Average Word Length

4. *Results Export*

   * Saves all calculated scores into a *CSV file*.
   * Columns:

     
     FILENAME | POSITIVE SCORE | NEGATIVE SCORE | POLARITY SCORE | SUBJECTIVITY SCORE 
     | AVG SENTENCE LENGTH | PERCENTAGE OF COMPLEX WORDS | FOG INDEX 
     | AVG NUMBER OF WORDS PER SENTENCE | COMPLEX WORD COUNT 
     | WORD COUNT | SYLLABLE PER WORD | PERSONAL PRONOUNS | AVG WORD LENGTH
     

---

## 📂 Project Structure


project/
│
├── data/                          # Stores dictionary/lexicons
│   ├── MasterDictionary/
│   │   ├── positive-words.txt
│   │   ├── negative-words.txt
│
├── articles_clean/                 # Extracted & cleaned text files (output of scraping)
│
├── Input.xlsx                      # Excel file with URL_ID and URL
│
├── extract_articles.py             # Script for scraping and saving articles
├── analyze_articles.py             # Script for scoring text files
├── requirements.txt                # Dependencies
└── README.md                       # Documentation


---

## ⚙ Dependencies

All dependencies are listed in requirements.txt.


pandas
requests
beautifulsoup4
lxml
nltk
openpyxl


> Install with:

bash
pip install -r requirements.txt


---

## 🚀 Instructions Documentation

### (a) Data Extraction (extract_articles.py)

1. Reads Input.xlsx (must contain columns: URL_ID, URL).
2. Fetches content from each URL.
3. Cleans article text.
4. Saves into articles_clean/URL_ID.txt.
5. Returns a summary DataFrame of processed URLs.

*Run:*

bash
python extract_articles.py


---

### (b) Text Analysis (analyze_articles.py)

1. Loads positive & negative lexicons.
2. Reads each .txt file in articles_clean/.
3. Computes sentiment & readability metrics.
4. Saves final results in Output.csv.

*Run:*

bash
python analyze_articles.py


---

### (c) Workflow (End-to-End)

1. Place your input file: Input.xlsx.

2. Run:

   bash
   python extract_articles.py
   

   → generates cleaned text files in articles_clean/.

3. Run:

   bash
   python analyze_articles.py
   

   → generates Output.csv with all metrics.

---

## 🧠 Approach

1. *Data Extraction*
   Used requests + BeautifulSoup to scrape web pages. Cleaned unwanted tags (header, footer, script, etc.) and extracted only meaningful article text.

2. *Ingestion*
   Standardized input by saving each article as .txt. Ensures reproducibility & offline availability.

3. *Lexicon-Based Sentiment Analysis*
   Compared article words against predefined positive & negative dictionaries.

4. *Readability Metrics*

   * Sentence segmentation with *NLTK Punkt tokenizer*.
   * Word complexity computed by syllable count.
   * Readability indices (Fog Index, Avg Sentence Length, etc.) calculated.

5. *Output*
   Compiled all scores into a single *CSV file* for analysis & visualization.

---

## ✅ Example Output (CSV)

| FILENAME | POSITIVE SCORE | NEGATIVE SCORE | POLARITY SCORE | SUBJECTIVITY SCORE | FOG INDEX | WORD COUNT |
| -------- | -------------- | -------------- | -------------- | ------------------ | --------- | ---------- |
| 101.txt  | 120            | 45             | 0.45           | 0.33               | 12.3      | 875        |
| 102.txt  | 87             | 32             | 0.38           | 0.28               | 11.5      | 652        |

---

📌 With this setup, you have a *modular, reproducible pipeline*:

* *Extract → Clean → Ingest → Analyze → Export → CSV*

---
