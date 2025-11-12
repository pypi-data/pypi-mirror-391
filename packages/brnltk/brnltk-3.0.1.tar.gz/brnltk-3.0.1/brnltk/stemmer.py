import re

def bengali_stem(word):
    """
    Perform light stemming by removing common Bengali suffixes.
    Handles plural, possessive, verb endings, emphasis, etc.
    """
    suffixes = [
        "গুলো", "গুলোর", "গুলি", "টা", "টির", "টার", "টারটা", "রা", "দের", "ের",
        "য়েছিলাম", "য়েছিলে", "য়েছিলেন", "য়েছিল", "ছিলে", "ছিলেন", "ছিলাম", "ছিল",
        "চ্ছিল", "চ্ছি", "চ্ছেন", "চ্ছে", "চ্ছিস", "চ্ছিলেন", "ছি", "ছে", "লেন", "েন",
        "তে","য়ে", "য়", "ার", "টি", "ই", "ও", "ে", "িস", "ি", "া", "েরটা",
        "েরটার", "েদের", "েগুলোর", "েরগুলো", "য়েছি", "য়েছে", "য়েছ", "েছ", "েছে", "েছেন",
        "ব", "লাম", "লো", "বে", "বো", "ছিলি", "ল", "লেম", "লান", "লা", "লুম"
    ]

    # Sort by length descending to remove longest matching suffix first
    for suf in sorted(suffixes, key=len, reverse=True):
        if word.endswith(suf) and len(word) > len(suf) + 2:
            return word[:-len(suf)]
    return word

def stem_sentence(sentence):
    """
    Apply stemming to each word in a sentence.
    Also removes punctuation except Bangla characters.
    Returns a string of stemmed words.
    """
    # Keep only Bangla letters and spaces
    cleaned = re.sub(r"[^\w\s\u0980-\u09FF]", "", sentence)
    words = cleaned.strip().split()
    stemmed_words = [bengali_stem(w) for w in words]
    return " ".join(stemmed_words)
