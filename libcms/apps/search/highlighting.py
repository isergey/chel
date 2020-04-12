import re
HL_PATTERN = re.compile(r'<em>(.*?)</em>', re.UNICODE | re.IGNORECASE | re.MULTILINE)

def get_highlighted_words_per_doc(highlighting):
    words_per_doc = {}
    for hl_id, hl_attrs in list(highlighting.items()):
        hl_words = []
        for hl_attr, hl_values in list(hl_attrs.items()):
            for hl_value in hl_values:
                for match in re.findall(HL_PATTERN, hl_value):
                    hl_words.append(match)
        words_per_doc[hl_id] = set(hl_words)
    return words_per_doc

def highlight_string(string, highlighting_words):
    highlight_string = str(string)
    for hl_word in highlighting_words:
        if len(hl_word) == 1:
            continue
        highlight_string = highlight_string.replace(hl_word, '<span class="search-highlight">%s</span>' % hl_word)
    return highlight_string