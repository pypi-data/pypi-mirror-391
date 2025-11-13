import sys
import os
import re
import inflect
import unicodedata

_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
_we_text_processing_path = os.path.join(_parent_dir, "WeTextProcessing")


from tn.chinese.normalizer import Normalizer as ZhNormalizer
from tn.japanese.normalizer import Normalizer as JpNormalizer
from .utils import (
    replace_blank, replace_corner_mark, remove_bracket, spell_out_number, 
    is_only_punctuation, remove_color_tag, remove_html_tag, 
    remove_brackets_and_content, insert_spaces_in_uppercase_words, 
    replace_punctuation, remove_emoji, remove_single_asterisk_content,
    replace_punctuation_jp, japanese_convert_numbers_to_words, 
    replace_punctuation_en, remove_isolated_hash, convert_to_lowercase, 
    replace_special_words, replace_symbols_lol, replace_special_words_with_all_languages
)


class TextNormalizer:
    def __init__(self):
        self.zh_tn_model = ZhNormalizer(
            remove_erhua=False, 
            full_to_half=False, 
            overwrite_cache=False, 
            remove_interjections=False
        )
        self.jp_tn_model = JpNormalizer()
        self.inflect_parser = inflect.engine()

    def text_normalize(self, text, language="中文", game_name=None):
        if language == "zh" or language == "hant":
            language = "中文"
        elif language == "ja":
            language = "日语"
        elif language == "en":
            language = "英语"
            
        text = self.replace_symbols_with_game_name(text, language, game_name)
        text = replace_special_words_with_all_languages(text)
        text = remove_color_tag(text)
        text = remove_html_tag(text)
        text = remove_brackets_and_content(text)
        text = remove_single_asterisk_content(text)
        if language == '中文':
            text = replace_special_words(text)
            text = self.zh_tn_model.normalize(text)
            text = remove_emoji(text)
            text = remove_bracket(text)
            
            # 数字转换为中文
            numbers = re.findall(r'(?<![A-Za-z])\d+(?:\.?\d+)?(?![A-Za-z])', text)
            for number in numbers:
                try:
                    text = text.replace(number, cn2an.an2cn(number), 1)
                except Exception as e:
                    text = text.replace(number, "")
                    
            text = insert_spaces_in_uppercase_words(text)
            text = replace_punctuation(text)
            
            text = text.replace("\n", "")
            text = replace_blank(text)
            text = replace_corner_mark(text)
            text = text.replace(".", "。")
            text = text.replace(" - ", "，")
            text = re.sub(r'[，,、]+$', '。', text)

        elif language == '日语':
            text = self.jp_tn_model.normalize(text)
            text = unicodedata.normalize("NFKC", text)

            text = japanese_convert_numbers_to_words(text)
            text = replace_punctuation_jp(text)
        elif language == '英语':
            text = remove_isolated_hash(text)
            # text = convert_to_lowercase(text)
            text = replace_punctuation_en(text)
            text = re.sub(r"([,;.\?\!])([\w])", r"\1 \2", text)
            text = remove_emoji(text)
            text = spell_out_number(text, self.inflect_parser)

        return text
    
    def replace_symbols_with_game_name(self, text, language, game_name):
        if game_name:
            if language == '中文':
                if game_name == '英雄联盟' or game_name == '金铲铲之战':
                    text = replace_symbols_lol(text)
            
        return text

