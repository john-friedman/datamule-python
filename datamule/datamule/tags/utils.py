import re
from .regex import cusip_regex, isin_regex, figi_regex, ticker_regex_list
from .regex import particles
from flashtext import KeywordProcessor

def get_cusip_using_regex(text,keywords=None):
    matches = []
    for match in re.finditer(cusip_regex, text):
        if keywords is not None:
            if match.group() in keywords:
                matches.append((match.group(), match.start(), match.end()))
        else:
            matches.append((match.group(), match.start(), match.end()))
    return matches

def get_isin_using_regex(text,keywords=None):
    matches = []
    for match in re.finditer(isin_regex, text):
        if keywords is not None:
            if match.group() in keywords:
                matches.append((match.group(), match.start(), match.end()))
        else:
            matches.append((match.group(), match.start(), match.end()))
    return matches

def get_figi_using_regex(text,keywords=None):
    matches = []
    for match in re.finditer(figi_regex, text):
        if keywords is not None:
            if match.group() in keywords:
                matches.append((match.group(), match.start(), match.end()))
        else:
            matches.append((match.group(), match.start(), match.end()))
    return matches

def get_tickers_using_regex(text, regex_pattern):
    """Extract tickers using the given regex pattern with position information"""
    matches = []
    for match in re.finditer(regex_pattern, text):
        # Handle tuples from regex groups - take the first capture group
        if match.groups():
            ticker = match.group(1) if match.group(1) else match.group(0)
        else:
            ticker = match.group(0)
        matches.append((ticker, match.start(), match.end()))
    return matches

def get_all_tickers(text):
    """Get all tickers from all exchanges organized by exchange with position info"""
    result = {}
    all_tickers = []
    
    for exchange_name, regex_pattern in ticker_regex_list:
        tickers = get_tickers_using_regex(text, regex_pattern)
        result[exchange_name] = tickers
        all_tickers.extend(tickers)
    
    # Remove duplicates while preserving order for 'all'
    # Keep track of seen ticker values (first element of tuple)
    seen = set()
    result['all'] = [x for x in all_tickers if not (x[0] in seen or seen.add(x[0]))]
    
    return result

def get_ticker_regex_dict():
    """Return ticker regex list as a dictionary for easy lookup"""
    return dict(ticker_regex_list)

# will change in future to accomodate other datasets
def validate_full_name(full_name, keywords):
    if len(full_name) == 1:
        return False
    
    # Clean punctuation before validation
    cleaned_name = [word.rstrip(".,;:!?()[]") for word in full_name]
    
    # Skip validation if cleaning removed everything
    if not all(cleaned_name):
        return False
    
    # Apply existing checks to cleaned words
    if all(word.isupper() for word in cleaned_name):
        return False
    
    # check if any number in word
    if any(any(char.isdigit() for char in word) for word in cleaned_name):
        return False
    
    # add optional set lookups
    if keywords is not None:
        # return false if first word is not in keywords set
        if cleaned_name[0] not in keywords:
            return False
    
    return True

def get_full_names(text,keywords=None):
    words = text.split()
    full_names = []
    current_pos = None
    word_start_positions = []
    
    # Calculate word positions in the original text
    pos = 0
    for word in words:
        start = text.find(word, pos)
        word_start_positions.append(start)
        pos = start + len(word)
    
    for idx, word in enumerate(words):
        if current_pos is None:
            if word[0].isupper():
                current_pos = idx
        else:
            if word[0].isupper() or word.lower() in particles:
                continue
            else:
                full_name = words[current_pos:idx]
                if validate_full_name(full_name,keywords):
                    name_text = ' '.join(full_name)
                    start_pos = word_start_positions[current_pos]
                    # Calculate end position of the last word in the name
                    last_word_idx = idx - 1
                    end_pos = word_start_positions[last_word_idx] + len(words[last_word_idx])
                    full_names.append((name_text, start_pos, end_pos))
                
                current_pos = None

    # handle last case - if we're still tracking a name when we reach the end
    if current_pos is not None:
        full_name = words[current_pos:]
        if validate_full_name(full_name,keywords):
            name_text = ' '.join(full_name)
            start_pos = word_start_positions[current_pos]
            # Calculate end position of the last word
            last_word_idx = len(words) - 1
            end_pos = word_start_positions[last_word_idx] + len(words[last_word_idx])
            full_names.append((name_text, start_pos, end_pos))

    return full_names

# add dictionary lookup based on precomputed lists
def get_full_names_dictionary_lookup(text, processor):
    """Use pre-built KeywordProcessor instead of creating new one"""
    matches = []
    keywords_found = processor.extract_keywords(text, span_info=True)
    
    for keyword, start_pos, end_pos in keywords_found:
        matches.append((keyword, start_pos, end_pos))
    
    return matches


def create_lm_processors(lm_dict):
    processors = {}
    
    for category_key, word_set in lm_dict.items():
        processor = KeywordProcessor(case_sensitive=False)
        for word in word_set:
            processor.add_keyword(word)
        processors[category_key] = processor
    
    return processors

def analyze_lm_sentiment_fragment(text, processors):
    """Analyze sentiment for a single text fragment"""
    if not text or not text.strip():
        return {}
    
    word_count = len(text.split())
    results = {}
    
    for category, processor in processors.items():
        matches = processor.extract_keywords(text.lower(), span_info=True)
        results[category] = len(matches)
    
    results['total_words'] = word_count
    return results