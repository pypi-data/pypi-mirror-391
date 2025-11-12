import re

def word_tokenize(text):
    """Tokenize Bengali text into words."""
    # Split by space and punctuation
    tokens = re.findall(r"[\u0980-\u09FF]+|[.,!?;]", text)
    return tokens

def sentence_tokenize(text):
    """Split Bengali text into sentences."""
    sentences = re.split(r"(?<=[।!?])\s+", text.strip())
    return [s for s in sentences if s]
