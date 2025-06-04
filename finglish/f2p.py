"""
f2p.py - Finglish (Persian written in Latin script) to Persian script converter.

This module provides functions to convert Finglish words and phrases into Persian script,
using configurable conversion tables and a frequency-based word list for ranking alternatives.

Files required in the same directory:
    - f2p-beginning.txt: Conversion rules for word beginnings.
    - f2p-middle.txt: Conversion rules for word middles.
    - f2p-ending.txt: Conversion rules for word endings.
    - persian-word-freq.txt: Persian words with frequency counts.
    - f2p-dict.txt: Custom dictionary for direct word mappings.
"""

import sys
import os
import re
import itertools

# Regex to split text into words, punctuation, and whitespace
word_and_punct_regex = re.compile(r'\w+|[^\w\s]|\s+')

def get_resource_path(filename):
    """Get path to resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running as an executable
        base_path = os.path.dirname(sys.executable)
        return os.path.join(base_path, 'finglish', filename)
    else:
        # Running in normal Python environment
        base_path = os.path.dirname(__file__)
        return os.path.join(base_path, filename)

def load_conversion_file(filename):
    """
    Load a conversion table from a file.

    Args:
        filename (str): The filename to load.

    Returns:
        dict: Mapping from Finglish letters to possible Persian equivalents.
    """
    filename = get_resource_path(filename)
    with open(filename, encoding='utf-8') as f:
        l = list(f)
        l = [i for i in l if i.strip()]
        l = [i.strip().split() for i in l]
    return {i[0]: i[1:] for i in l}

# Load conversion tables and word lists at module import
beginning = load_conversion_file('f2p-beginning.txt')  # type: dict
middle = load_conversion_file('f2p-middle.txt')        # type: dict
ending = load_conversion_file('f2p-ending.txt')        # type: dict

with open(get_resource_path('persian-word-freq.txt'), encoding='utf-8') as f:
    word_freq = list(f)
word_freq = [i.strip() for i in word_freq if i.strip()]
word_freq = [i.split() for i in word_freq if not i.startswith('#')]
word_freq = {i[0]: int(i[1]) for i in word_freq}  # type: dict[str, int]

with open(get_resource_path('f2p-dict.txt'), encoding='utf-8') as f:
    dictionary = [i.strip().split(' ', 1) for i in f if i.strip()]
    dictionary = {k.strip(): v.strip() for k, v in dictionary}  # type: dict[str, str]

def f2p_word_internal(word, original_word):
    """
    Internal function to convert a list of Finglish letters to Persian alternatives.

    Args:
        word (list): List of Finglish letters.
        original_word (str): The original word for fallback.

    Returns:
        list: List of (alternative, confidence) tuples.
    """
    persian = []
    for i, letter in enumerate(word):
        if i == 0:
            converter = beginning
        elif i == len(word) - 1:
            converter = ending
        else:
            converter = middle
        conversions = converter.get(letter)
        if conversions is None:
            return [(''.join(original_word), 0.0)]
        else:
            conversions = ['' if i == 'nothing' else i for i in conversions]
        persian.append(conversions)

    alternatives = itertools.product(*persian)
    alternatives = [''.join(i) for i in alternatives]

    alternatives = [(i, word_freq[i]) if i in word_freq else (i, 0)
                    for i in alternatives]

    if len(alternatives) > 0:
        max_freq = max(freq for _, freq in alternatives)
        alternatives = [(w, float(freq / max_freq)) if freq != 0 else (w, 0.0)
                        for w, freq in alternatives]
    else:
        alternatives = [(''.join(word), 1.0)]

    return alternatives

def variations(word):
    """
    Create variations of the word based on letter combinations like oo, sh, etc.

    Args:
        word (str): The Finglish word.

    Returns:
        list: List of possible segmentations as lists of letters.
    """
    if word == 'a':
        return [['A']]
    elif len(word) == 1:
        return [[word[0]]]
    elif word == 'aa':
        return [['A']]
    elif word == 'ee':
        return [['i']]
    elif word == 'ei':
        return [['ei']]
    elif word in ['oo', 'ou']:
        return [['u']]
    elif word == 'kha':
        return [['kha'], ['kh', 'a']]
    elif word in ['kh', 'gh', 'ch', 'sh', 'zh', 'ck']:
        return [[word]]
    elif word in ["'ee", "'ei"]:
        return [["'i"]]
    elif word in ["'oo", "'ou"]:
        return [["'u"]]
    elif word in ["a'", "e'", "o'", "i'", "u'", "A'"]:
        return [[word[0] + "'"]]
    elif word in ["'a", "'e", "'o", "'i", "'u", "'A"]:
        return [["'" + word[1]]]
    elif len(word) == 2 and word[0] == word[1]:
        return [[word[0]]]

    if word[:2] == 'aa':
        return [['A'] + i for i in variations(word[2:])]
    elif word[:2] == 'ee':
        return [['i'] + i for i in variations(word[2:])]
    elif word[:2] in ['oo', 'ou']:
        return [['u'] + i for i in variations(word[2:])]
    elif word[:3] == 'kha':
        return \
            [['kha'] + i for i in variations(word[3:])] + \
            [['kh', 'a'] + i for i in variations(word[3:])] + \
            [['k', 'h', 'a'] + i for i in variations(word[3:])]
    elif word[:2] in ['kh', 'gh', 'ch', 'sh', 'zh', 'ck']:
        return \
            [[word[:2]] + i for i in variations(word[2:])] + \
            [[word[0]] + i for i in variations(word[1:])]
    elif word[:2] in ["a'", "e'", "o'", "i'", "u'", "A'"]:
        return [[word[:2]] + i for i in variations(word[2:])]
    elif word[:3] in ["'ee", "'ei"]:
        return [["'i"] + i for i in variations(word[3:])]
    elif word[:3] in ["'oo", "'ou"]:
        return [["'u"] + i for i in variations(word[3:])]
    elif word[:2] in ["'a", "'e", "'o", "'i", "'u", "'A"]:
        return [[word[:2]] + i for i in variations(word[2:])]
    elif len(word) >= 2 and word[0] == word[1]:
        return [[word[0]] + i for i in variations(word[2:])]
    else:
        return [[word[0]] + i for i in variations(word[1:])]

def f2p_word(word, max_word_size=15, cutoff=1):
    """
    Convert a single word from Finglish to Persian.

    Args:
        word (str): The Finglish word to convert.
        max_word_size (int): Maximum size of the words to consider. Words larger than this will be kept unchanged.
        cutoff (int): The cut-off point. For each word, there could be many possibilities.
        By default, 3 of these possibilities are considered for each word.

    Returns:
        list: List of (persian_word, confidence) tuples.
    """
    original_word = word
    word = word.lower()

    c = dictionary.get(word)
    if c:
        return [(c, 1.0)]

    if word == '':
        return []
    elif len(word) > max_word_size:
        return [(original_word, 1.0)]

    results = []
    for w in variations(word):
        results.extend(f2p_word_internal(w, original_word))

    # Sort results based on the confidence value
    results.sort(key=lambda r: r[1], reverse=True)

    # Return the top results in order to cut down on the number of possibilities.
    return results[:cutoff]

def f2p_list(phrase, max_word_size=15, cutoff=1):
    """
    Convert a phrase from Finglish to Persian while preserving punctuation.

    Args:
        phrase (str): The phrase to convert.
        max_word_size (int): Maximum size of the words to consider.
        cutoff (int): The cut-off point for number of alternatives per word.

    Returns:
        list: List of lists, each sub-list contains possibilities for each word as (word, confidence) pairs.
    """
    # Split the phrase into words and punctuation
    tokens = word_and_punct_regex.findall(phrase)

    # Process each token: convert words, leave punctuation unchanged
    results = []
    for token in tokens:
        if token.isspace():
            results.append([(token, 1.0)])
        elif token.isalnum():  # If the token is a word
            converted = f2p_word(token, max_word_size, cutoff)
            results.append(converted)
        else:  # If the token is punctuation
            # Map ? and , to Persian equivalents
            if token == '?':
                token = '؟'
            elif token == ',':
                token = '،'
            results.append([(token, 1.0)])

    return results

def f2p(phrase, max_word_size=15, cutoff=1):
    """
    Convert a Finglish phrase to the most probable Persian phrase.

    Args:
        phrase (str): The phrase to convert.
        max_word_size (int): Maximum size of the words to consider.
        cutoff (int): The cut-off point for number of alternatives per word.

    Returns:
        str: The most probable Persian phrase.
    """
    results = f2p_list(phrase, max_word_size, cutoff)
    output = []

    for i in results:
        token = i[0][0]  # Get the most probable translation or punctuation
        output.append(token)
    
    return ''.join(output)
