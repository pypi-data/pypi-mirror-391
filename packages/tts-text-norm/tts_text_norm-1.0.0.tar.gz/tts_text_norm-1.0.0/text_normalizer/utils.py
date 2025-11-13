import re
import regex
from num2words import num2words


chinese_char_pattern = re.compile(r'[\u4e00-\u9fff]+')

punctuation = ["!", "?", "…", ",", ".", "'", "-"]
rep_map = {
    "：": ",",
    "；": ",",
    "，": ",",
    "。": ".",
    "！": "!",
    "？": "?",
    "\n": ".",
    "·": ",",
    "、": ",",
    "...": "…",
    "$": ".",
    """: "'",
    """: "'",
    "'": "'",
    "'": "'",
    "《": "'",
    "》": "'",
    "【": "'",
    "】": "'",
    "[": "'",
    "]": "'",
    "—": "-",
    "～": "-",
    "~": "-",
    "「": "'",
    "」": "'",
    "'": "'",
    "U P":"up",
    "bilibili": "bili bili",
    "菈": "拉",
    "凡人修仙传": "凡人修仙赚",
}


# whether contain chinese character
def contains_chinese(text):
    return bool(chinese_char_pattern.search(text))


# replace special symbol
def replace_corner_mark(text):
    text = text.replace('²', '平方')
    text = text.replace('³', '立方')
    return text


# remove meaningless symbol
def remove_bracket(text):
    text = text.replace('【', '').replace('】', '')
    text = text.replace('`', '').replace('`', '')
    text = text.replace("——", " ")
    return text


# spell Arabic numerals
def spell_out_number(text: str, inflect_parser):
    new_text = []
    st = None
    for i, c in enumerate(text):
        if not c.isdigit():
            if st is not None:
                num_str = inflect_parser.number_to_words(text[st: i])
                new_text.append(num_str)
                st = None
            new_text.append(c)
        else:
            if st is None:
                st = i
    if st is not None and st < len(text):
        num_str = inflect_parser.number_to_words(text[st:])
        new_text.append(num_str)
    return ''.join(new_text)


# split paragrah logic：
# 1. per sentence max len token_max_n, min len token_min_n, merge if last sentence len less than merge_len
# 2. cal sentence len according to lang
# 3. split sentence according to puncatation
def split_paragraph(text: str, tokenize, lang="zh", token_max_n=80, token_min_n=60, merge_len=20, comma_split=False):
    def calc_utt_length(_text: str):
        if lang == "zh":
            return len(_text)
        else:
            return len(tokenize(_text))

    def should_merge(_text: str):
        if lang == "zh":
            return len(_text) < merge_len
        else:
            return len(tokenize(_text)) < merge_len

    if lang == "zh":
        pounc = ['。', '？', '！', '；', '：', '、', '.', '?', '!', ';']
    else:
        pounc = ['.', '?', '!', ';', ':']
    if comma_split:
        pounc.extend(['，', ','])

    if text[-1] not in pounc:
        if lang == "zh":
            text += "。"
        else:
            text += "."

    st = 0
    utts = []
    for i, c in enumerate(text):
        if c in pounc:
            if len(text[st: i]) > 0:
                utts.append(text[st: i] + c)
            if i + 1 < len(text) and text[i + 1] in ['"', '"']:
                tmp = utts.pop(-1)
                utts.append(tmp + text[i + 1])
                st = i + 2
            else:
                st = i + 1

    final_utts = []
    cur_utt = ""
    for utt in utts:
        if calc_utt_length(cur_utt + utt) > token_max_n and calc_utt_length(cur_utt) > token_min_n:
            final_utts.append(cur_utt)
            cur_utt = ""
        cur_utt = cur_utt + utt
    if len(cur_utt) > 0:
        if should_merge(cur_utt) and len(final_utts) != 0:
            final_utts[-1] = final_utts[-1] + cur_utt
        else:
            final_utts.append(cur_utt)

    return final_utts


# remove blank between chinese character
def replace_blank(text: str):
    out_str = []
    for i, c in enumerate(text):
        if c == " ":
            if (i > 0 and i < len(text) - 1 and
                (text[i - 1].isascii() and text[i - 1] != " ") and
                (text[i + 1].isascii() and text[i + 1] != " ")):
                out_str.append(c)
        else:
            out_str.append(c)
    return "".join(out_str)


def is_only_punctuation(text):
    # Regular expression: Match strings that consist only of punctuation marks or are empty.
    punctuation_pattern = r'^[\p{P}\p{S}]*$'
    return bool(regex.fullmatch(punctuation_pattern, text))

def remove_color_tag(text):
    cleaned_text = re.sub(r'<color=#([0-9A-Fa-f]{8})>', '', text)
    cleaned_text = re.sub(r'</color>', '', cleaned_text)
    return cleaned_text

def remove_html_tag(text):
    # 正则表达式匹配 HTML 标签
    pattern = r'<[^>]+>'
    # 去除 HTML 标签
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text

def remove_brackets_and_content(text):
    # 匹配中文括号及其内容的正则表达式
    pattern_cn = r'（.*?）'
    # 匹配英文括号及其内容的正则表达式
    pattern_en = r'\(.*?\)'
    pattern_mixed_cn_en = r'（.*?\)'
    pattern_mixed_en_cn = r'\(.*?）'

    # 首先移除中文括号及其内容
    result = re.sub(pattern_cn, '', text, flags=re.DOTALL)
    # 然后移除英文括号及其内容
    result = re.sub(pattern_en, '', result, flags=re.DOTALL)
    
    result = re.sub(pattern_mixed_cn_en, '', result, flags=re.DOTALL)
    result = re.sub(pattern_mixed_en_cn, '', result, flags=re.DOTALL)
    
    return result

def remove_single_asterisk_content(text):
    # 匹配由双星号包围的内容的正则表达式（即不希望处理的部分）
    pattern_double_asterisk = r'\*\*(.*?)\*\*'

    # 暂时替换双星号包围的内容为不含星号的占位符，以保护它们
    placeholder = re.findall(pattern_double_asterisk, text)
    protected_text = re.sub(pattern_double_asterisk, '\uffff', text)  # \uffff 是一个很少用到的占位符

    # 匹配由单个星号包围的内容的正则表达式
    pattern_single_asterisk = r'\*(.*?)\*'

    # 删除单个星号包围的内容
    without_single_asterisk = re.sub(pattern_single_asterisk, '', protected_text)

    # 将占位符替换为原本的双星号内容
    for ph_text in placeholder:
        without_single_asterisk = without_single_asterisk.replace('\uffff', f'**{ph_text}**', 1)

    return without_single_asterisk

def replace_punctuation(text):
    # text = text.replace("嗯", "恩").replace("呣", "母")
    text = text.replace("——", "-")
    pattern = re.compile("|".join(re.escape(p) for p in rep_map.keys()))

    replaced_text = pattern.sub(lambda x: rep_map[x.group()], text)
    
    # 这里会剔除非中文字符和特殊符号
    replaced_text = re.sub(
        r"[^a-zA-Z\u4e00-\u9fa5\s\d" + "".join(punctuation) + r"]+", "", replaced_text
    )
    
    return replaced_text

def insert_spaces_in_uppercase_words(text):
    uppercase_words = re.findall(r'(?<![A-Za-z])[A-Z\d]+(?![A-Za-z])', text)
    for word in uppercase_words:
        spaced_word = ' '.join(list(word))
        text = text.replace(word, spaced_word)
    return text

def remove_emoji(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
        "\U0001F680-\U0001F6FF"  # Transport & Map Symbols
        "\U0001F700-\U0001F77F"  # Alchemical Symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002600-\U000026FF"  # Miscellaneous Symbols
        "\U00002700-\U000027BF"  # Dingbats
        "\U0001F1E6-\U0001F1FF"  # Flags (iOS)
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

_NUMBER_WITH_SEPARATOR_RX = re.compile("[0-9]{1,3}(,[0-9]{3})+")
_CURRENCY_MAP = {"$": "ドル", "¥": "円", "£": "ポンド", "€": "ユーロ"}
_CURRENCY_RX = re.compile(r"([$¥£€])([0-9.]*[0-9])")
_NUMBER_RX = re.compile(r"[0-9]+(\.[0-9]+)?")

rep_map_jp = {
    "—": "-",
    "−": "-",
    "～": "-",
    "~": "-",
    "原神": "げんしん",
    "玉桃": "たまもも",
    "仙人": "せんにん",
    # "シクサルズ・F・リン": "しくさるず・えふ・りん",
    # "シクサルズ": "しくさるず",
    "シューイ": "しゅーい",
}

def japanese_convert_numbers_to_words(text: str) -> str:
    res = _NUMBER_WITH_SEPARATOR_RX.sub(lambda m: m[0].replace(",", ""), text)
    res = _CURRENCY_RX.sub(lambda m: m[2] + _CURRENCY_MAP.get(m[1], m[1]), res)
    res = _NUMBER_RX.sub(lambda m: num2words(m[0], lang="ja"), res)
    return res

def replace_punctuation_jp(text):
    pattern = re.compile("|".join(re.escape(p) for p in rep_map_jp.keys()))

    replaced_text = pattern.sub(lambda x: rep_map_jp[x.group()], text)

    # replaced_text = re.sub(
    #     r"[^\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u3400-\u4DBF\u3005"
    #     + "".join(punctuation)
    #     + r"]+",
    #     "",
    #     replaced_text,
    # )

    return replaced_text


rep_map_en = {
    "：": ",",
    "；": ",",
    "，": ",",
    "。": ".",
    "！": "!",
    "？": "?",
    "\n": ".",
    "．": ".",
    "…": "...",
    "···": "...",
    "・・・": "...",
    "·": ",",
    "・": ",",
    "、": ",",
    "$": ".",
    """: "'",
    """: "'",
    '"': "'",
    "'": "'",
    "'": "'",
    "（": "'",
    "）": "'",
    "(": "'",
    ")": "'",
    "《": "'",
    "》": "'",
    "【": "'",
    "】": "'",
    "[": "'",
    "]": "'",
    "—": "-",
    "−": "-",
    "～": "-",
    "~": "-",
    "「": "'",
    "」": "'",
}

def replace_punctuation_en(text):
    pattern = re.compile("|".join(re.escape(p) for p in rep_map_en.keys()))
    replaced_text = pattern.sub(lambda x: rep_map_en[x.group()], text)

    return replaced_text

def remove_isolated_hash(text):
    pattern = r'#(?!\d)'
    return re.sub(pattern, '', text)

def convert_to_lowercase(text):
    return text.lower()


def replace_special_words(text):
    pattern = r'(?<![a-zA-Z])UP(?![a-zA-Z])'
    text = re.sub(pattern, 'up', text)
    pattern = r'(?<![a-zA-Z])vs(?![a-zA-Z])'
    text = re.sub(pattern, 'VS', text)
    return text


def replace_symbols_lol(text):
    symbols = ['/', ':', '-']
    
    result = text
    
    for symbol in symbols:
        escaped_symbol = re.escape(symbol)
        pattern = r'(\d+)\s*' + escaped_symbol + r'\s*(\d+)'
        
        while re.search(pattern, result):
            result = re.sub(pattern, r'\1杠\2', result)
    
    return result


def replace_special_words_with_all_languages(text):
    pattern = r'(?<![a-zA-Z])gameplay(?![a-zA-Z])'
    text = re.sub(pattern, 'game play', text, flags=re.IGNORECASE)
    pattern = r'(?<![a-zA-Z])teamwork(?![a-zA-Z])'
    text = re.sub(pattern, 'team work', text, flags=re.IGNORECASE)
    return text

