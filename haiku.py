import textstat
import re
from itertools import accumulate

def clean_sentence(sentence, lower):
    """Removes punctuation except apostrophes in contractions and hyphens in words."""
    if lower is False:
        sentence = sentence.strip()
    else:
        sentence = sentence.lower().strip()
        
    sentence = re.sub(r"[^\w\s'-]", "", sentence)  # Remove all punctuation except apostrophes and hyphens
    return sentence


def count_syllables(word):
    """Counts syllables in a word using textstat."""
    return textstat.syllable_count(word)


def split_into_haiku(sentence, lower=False):
    """Attempts to split a cleaned sentence into a 5-7-5 Haiku structure and return the formatted Haiku."""
    sentence = clean_sentence(sentence, lower)
    words = sentence.split()
    syllables = [count_syllables(word) for word in words]
    
    # Compute cumulative sums to find breakpoints
    cumulative_sums = list(accumulate(syllables))

    # Ensure the sentence has exactly 17 syllables in a 5-7-5 pattern
    if len(cumulative_sums) < 3 or cumulative_sums[-1] != 17:
        return None  # Not exactly 17 syllables, not a valid Haiku
    
    try:
        idx1 = cumulative_sums.index(5) + 1  # End of first line
        idx2 = cumulative_sums.index(12) + 1  # End of second line (5+7=12)
    except ValueError:
        return None  # Couldn't form a valid Haiku pattern
    
    # Ensure the last group is exactly 5 syllables
    if cumulative_sums[-1] - cumulative_sums[idx2 - 1] != 5:
        return None  # Third line isn't exactly 5 syllables
    
    # Format the Haiku with line breaks
    return "\n".join([" ".join(words[:idx1]), " ".join(words[idx1:idx2]), " ".join(words[idx2:])])


def is_valid_haiku(sentence):
    """Checks if a sentence can be rearranged into a valid Haiku."""
    return split_into_haiku(sentence, lower=True) is not None
