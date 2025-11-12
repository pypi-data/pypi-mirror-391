import pandas as pd
import requests
import io

# -----------------------------
# N-Gram Helper Functions
# -----------------------------
def ngram_similarity(word1, word2, n=2):
    """Calculate n-gram similarity between two words"""
    def get_ngrams(word):
        return {word[i:i+n] for i in range(len(word)-n+1)}
    
    set1, set2 = get_ngrams(word1), get_ngrams(word2)
    if not set1 or not set2:
        return 0
    return len(set1 & set2) / len(set1 | set2)


# -----------------------------
# Short Dialect Name Mapping
# -----------------------------
AREA_MAPPING = {
    "Barishal": "Barishal_bangla_speech",
    "Sylhet": "Sylhet_bangla_speech",
    "Chittagong": "Chittagong_bangla_speech",
    "Mymensingh": "Mymensingh_bangla_speech",
    "Noakhali": "Noakhali_bangla_speech",
    "General": "General"
}

def map_area(short_name):
    """Maps short area names to dataset column names"""
    return AREA_MAPPING.get(short_name, short_name)


# -----------------------------
# Translator Function
# -----------------------------
def translate(sentence, from_area, to_area, threshold=0.5):
    """
    Translates a sentence from one Bengali dialect to another based on n-gram similarity.

    Args:
        sentence (str): The input sentence to translate.
        from_area (str): Short name of the source dialect (e.g., 'General').
        to_area (str): Short name of the target dialect (e.g., 'Chittagong').
        threshold (float): Minimum n-gram similarity for a match.

    Returns:
        str: Translated sentence.
    """
    from_col = map_area(from_area)
    to_col = map_area(to_area)

    excel_url = "https://raw.githubusercontent.com/ShakirHaque/BRNLTK/refs/heads/main/PritomBanglaversion%202.2.xlsx%20-%20Sheet1.csv"

    try:
        response = requests.get(excel_url)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return sentence

    words = sentence.strip().split()
    translated_words = []

    for word in words:
        matched_row = None
        best_score = 0

        for _, row in df.iterrows():
            source_word = str(row.get(from_col, '')).strip()
            if not source_word:
                continue

            sim = ngram_similarity(word, source_word)
            if sim > best_score and sim >= threshold:
                best_score = sim
                matched_row = row

        if matched_row is not None and to_col in matched_row:
            translated_words.append(str(matched_row[to_col]))
        else:
            translated_words.append(word)

    return " ".join(translated_words)