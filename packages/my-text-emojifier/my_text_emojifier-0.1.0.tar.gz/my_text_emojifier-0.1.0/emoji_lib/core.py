# File: emoji_lib/core.py

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.tokenize.treebank import TreebankWordDetokenizer

# A dictionary mapping keywords (as lemmas) to emojis
EMOJI_MAP = {
    "love": "❤️",
    "heart": "❤️",
    "dog": "🐶",
    "cat": "🐱",
    "happy": "😄",
    "sad": "😢",
    "python": "🐍",
    "star": "⭐",
    "coffee": "☕",
    "book": "📖",
    "fire": "🔥",
    "thumbsup": "👍",
    "yay": "🎉",
    "rocket": "🚀",
    "brain": "🧠",
    "world": "🌍",
    "money": "💰",
    "sun": "☀️",
    "moon": "🌙",
    "cloud": "☁️",
    "rain": "🌧️",
    "pizza": "🍕",
    "car": "🚗",
    "computer": "💻",
    "be": "😊", # Example for 'is', 'are', 'was'
}

# NLTK's Lemmatizer is much better if it knows the part of speech.
def get_wordnet_pos(treebank_tag):
    """
    Converts Penn Treebank POS tags to WordNet POS tags.
    """
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

# We need a lemmatizer and a detokenizer
lemmatizer = WordNetLemmatizer()
detokenizer = TreebankWordDetokenizer()

def _emojify(text: str, mode: str = 'replace'):
    """
    Internal generator function to process and yield emojified tokens.
    """
    # 1. Tokenize: Smartly splits text into words and punctuation
    try:
        tokens = nltk.word_tokenize(text)
    except LookupError:
        print("NLTK data not found. Please run the NLTK setup script.")
        print("Or in Python, run: import nltk; nltk.download('punkt')")
        # Re-raise the error to stop execution
        raise
        
    # 2. Tag: Get the Part-of-Speech for each token
    try:
        tagged_tokens = nltk.pos_tag(tokens)
    except LookupError:
        print("NLTK 'averaged_perceptron_tagger' not found. Please run the NLTK setup script.")
        print("Or in Python, run: import nltk; nltk.download('averaged_perceptron_tagger')")
        raise
    
    for word, tag in tagged_tokens:
        # 3. Lemmatize: Convert word to its base form
        wn_tag = get_wordnet_pos(tag)
        lemma = lemmatizer.lemmatize(word.lower(), pos=wn_tag)
        
        emoji = EMOJI_MAP.get(lemma)
        
        if mode == 'replace':
            if emoji:
                yield emoji  # Replace the word with the emoji
            else:
                yield word   # Keep the original word
        
        elif mode == 'append':
            yield word # Always yield the original word
            if emoji:
                yield emoji # And add the emoji after it

def replace_with_emoji(text: str) -> str:
    """
    Replaces known words in a string with their corresponding emoji.
    Handles plurals and verb conjugations.
    Example: "I loved my dogs" -> "I ❤️ my 🐶"
    """
    processed_tokens = list(_emojify(text, mode='replace'))
    # 4. Detokenize: Re-joins tokens into a natural sentence
    return detokenizer.detokenize(processed_tokens)

def append_emoji(text: str) -> str:
    """
    Appends emojis to known words in a string.
    Handles plurals and verb conjugations.
    Example: "I loved my dogs" -> "I loved ❤️ my dogs 🐶"
    """
    processed_tokens = list(_emojify(text, mode='append'))
    # 4. Detokenize: Re-joins tokens into a natural sentence
    return detokenizer.detokenize(processed_tokens)

# --- This block only runs when you execute `python emoji_lib/core.py` directly ---
if __name__ == "__main__":
    test_string = "I loved Python, my dogs, and my cats. This is happy news!"
    
    print("--- Replace (NLTK) ---")
    print(f"Original: {test_string}")
    print(f"Modified: {replace_with_emoji(test_string)}")

    print("\n--- Append (NLTK) ---")
    print(f"Original: {test_string}")
    print(f"Modified: {append_emoji(test_string)}")