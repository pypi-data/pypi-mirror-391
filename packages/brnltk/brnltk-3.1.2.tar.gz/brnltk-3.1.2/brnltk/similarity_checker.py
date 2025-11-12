import math
from difflib import SequenceMatcher
from collections import Counter

# -----------------------------
# Cosine Similarity
# -----------------------------
def cosine_similarity(text1, text2):
    """Compute cosine similarity between two texts."""
    def text_to_vector(text):
        words = text.split()
        return Counter(words)
    
    vec1, vec2 = text_to_vector(text1), text_to_vector(text2)
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum(vec1[x] * vec2[x] for x in intersection)
    denominator = math.sqrt(sum(v**2 for v in vec1.values())) * math.sqrt(sum(v**2 for v in vec2.values()))
    
    return numerator / denominator if denominator else 0.0

# -----------------------------
# N-Gram Similarity
# -----------------------------
def ngram_similarity(word1, word2, n=2):
    """Compute n-gram similarity (same as used in translator)."""
    def get_ngrams(word):
        return {word[i:i+n] for i in range(len(word)-n+1)}
    set1, set2 = get_ngrams(word1), get_ngrams(word2)
    if not set1 or not set2:
        return 0
    return len(set1 & set2) / len(set1 | set2)

# -----------------------------
# Levenshtein Similarity
# -----------------------------
def levenshtein_similarity(s1, s2):
    """Compute similarity based on Levenshtein edit distance."""
    matcher = SequenceMatcher(None, s1, s2)
    return matcher.ratio()

# -----------------------------
# Combined Function
# -----------------------------
def overall_similarity(text1, text2):
    """Compute average similarity combining cosine, n-gram, and Levenshtein."""
    cos = cosine_similarity(text1, text2)
    lev = levenshtein_similarity(text1, text2)
    ngram = ngram_similarity(text1, text2)
    return round((cos + lev + ngram) / 3, 3)
