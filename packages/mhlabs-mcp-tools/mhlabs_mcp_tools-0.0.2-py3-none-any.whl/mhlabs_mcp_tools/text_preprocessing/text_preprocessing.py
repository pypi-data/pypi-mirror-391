"""
Text preprocessing functions decorated with @mcp.tool metadata.
These import the shared 'mcp' instance from server.py so tools auto-register when module is imported.
"""

import os
import regex
import string
import logging
import csv
import traceback
from functools import partial
import json

from collections import Counter
from unicodedata import normalize
from typing import List, Optional, Union
from bs4 import BeautifulSoup
from pydantic import BaseModel

from fastmcp import FastMCP
from fastmcp import Client
from mhlabs_mcp_tools.core.config import Settings
from mhlabs_mcp_tools.text_preprocessing import emo_unicode, slang_text, contractions
from mhlabs_mcp_tools.handlers.custom_exceptions import CustomJSONError
from mhlabs_mcp_tools.handlers.output_generator import generate_output
from mhlabs_mcp_tools.core.constants import constants, preprocess_operations

# import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, PunktSentenceTokenizer
# from nltk.stem import PorterStemmer, SnowballStemmer, LancasterStemmer, WordNetLemmatizer

logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(Settings.LOG_FILE_PATH)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(Settings.LOG_FILE_FORMAT)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

# Please uncomment/comment below line if you wish to stop/start logging
# logger.disabled = True

BaseModel.model_config["arbitrary_types_allowed"] = True
client = Client("http://localhost:8000/mcp")

def register_textprep_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="textprep.to_lower",
        description="Convert input text to lowercase.",
        tags={"textprep", "case"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def to_lower(input_text: str) -> str:
        """ Convert input text to lower case """
        return input_text.lower()


    @mcp.tool(
        name="textprep.to_upper",
        description="Convert input text to uppercase.",
        tags={"textprep", "case"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def to_upper(input_text: str) -> str:
        """ Convert input text to upper case """
        return input_text.upper()


    @mcp.tool(
        name="textprep.expand_contraction",
        description="Expand simple contractions (can't -> cannot).",
        tags={"textprep", "normalization"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def expand_contraction(input_text: str) -> str:
        """ Expand contractions in input text """
        return contractions.fix(input_text)    


    @mcp.tool(
        name="textprep.remove_number",
        description="Remove numeric characters from text.",
        tags={"textprep", "cleaning"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def remove_number(input_text: str) -> str:
        """ Remove number in the input text """
        processed_text = regex.sub(r'\d+', '', input_text)
        return processed_text


    @mcp.tool(
        name="textprep.remove_itemized_bullet_and_numbering",
        description="Remove itemized bullets and numbering.",
        tags={"textprep", "cleaning"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def remove_itemized_bullet_and_numbering(input_text: str) -> str:
        """ Remove bullets or numbering in itemized input """
        processed_text = regex.sub(r'[(\s][0-9a-zA-Z][.)]\s+|[(\s][ivxIVX]+[.)]\s+', ' ', input_text)
        return processed_text

    @mcp.tool(
        name="textprep.remove_url",
        description="Remove URLs from text.",
        tags={"textprep", "cleaning"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def remove_url(input_text: str) -> str:
        
        return regex.sub(r'(www|http)\S+', '', input_text)


    @mcp.tool(
        name="textprep.remove_punctuation",
        description="Remove punctuation from text.",
        tags={"textprep", "cleaning"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def remove_punctuation(input_text: str, punctuations: Optional[str] = None) -> str:
        """
        Removes all punctuations from a string, as defined by string.punctuation or a custom list.
        For reference, Python's string.punctuation is equivalent to '!"#$%&\'()*+,-./:;<=>?@[\\]^_{|}~'
        """
        if punctuations is None:
            punctuations = string.punctuation
        processed_text = input_text.translate(str.maketrans('', '', punctuations))
        return processed_text


    @mcp.tool(
        name="textprep.remove_special_character",
        description="Remove special characters (keep basic punctuation).",
        tags={"textprep", "cleaning"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def remove_special_character(input_text: str, special_characters: Optional[str] = None) -> str:
        """ Removes special characters """
        if special_characters is None:
            # TODO: add more special characters
            special_characters = 'å¼«¥ª°©ð±§µæ¹¢³¿®ä£'
        processed_text = input_text.translate(str.maketrans('', '', special_characters))
        return processed_text


    @mcp.tool(
        name="textprep.keep_alpha_numeric",
        description="Keep only alphanumeric characters and spaces.",
        tags={"textprep", "cleaning"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def keep_alpha_numeric(input_text: str) -> str:
        """ Remove any character except alphanumeric characters """
        return ''.join(c for c in input_text if c.isalnum())


    @mcp.tool(
        name="textprep.remove_whitespace",
        description="Collapse and trim whitespace.",
        tags={"textprep", "cleaning"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def remove_whitespace(input_text: str, remove_duplicate_whitespace: bool = True) -> str:
        """ Removes leading, trailing, and (optionally) duplicated whitespace """
        if remove_duplicate_whitespace:
            return ' '.join(regex.split(r'\s+', input_text.strip(), flags=regex.UNICODE))
        return input_text.strip()


    @mcp.tool(
        name="textprep.normalize_unicode",
        description="Normalize unicode characters using NFKC.",
        tags={"textprep", "unicode"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def normalize_unicode(input_text: str) -> str:
        """ Normalize unicode data to remove umlauts, and accents, etc. """
        processed_tokens = normalize('NFKD', input_text).encode('ASCII', 'ignore').decode('utf8')
        return processed_tokens


    @mcp.tool(
        name="textprep.remove_stopword",
        description="Remove stopwords for a language (default english).",
        tags={"textprep", "stopwords"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def remove_stopword(input_text_or_list: Union[str, List[str]], stop_words: Optional[set] = None) -> List[str]:
        """ Remove stop words """

        if stop_words is None:
            stop_words = set(stopwords.words('english'))
        if isinstance(stop_words, list):
            stop_words = set(stop_words)
        if isinstance(input_text_or_list, str):
            tokens = word_tokenize(input_text_or_list)
            processed_tokens = [token for token in tokens if token not in stop_words]
        else:
            processed_tokens = [token for token in input_text_or_list
                                if (token not in stop_words and token is not None and len(token) > 0)]
        return processed_tokens


    @mcp.tool(
        name="textprep.remove_freqwords",
        description="Remove frequently occurring words above threshold.",
        tags={"textprep", "frequency"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def remove_freqwords(input_text_or_list: Union[str, List[str]], freq_words: Optional[set] = None) -> List[str]:
        """ Remove freq words """

        cnt = Counter()

        if freq_words is None:
            freq_words = set([w for (w, wc) in cnt.most_common(10)])
        if isinstance(freq_words, list):
            freq_words = set(freq_words)
        if isinstance(input_text_or_list, str):
            tokens = word_tokenize(input_text_or_list)
            processed_tokens = [token for token in tokens if token not in freq_words]
        else:
            processed_tokens = [token for token in input_text_or_list
                                if (token not in freq_words and token is not None and len(token) > 0)]
        return processed_tokens


    @mcp.tool(
        name="textprep.remove_rarewords",
        description="Remove rare words below threshold.",
        tags={"textprep", "frequency"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def remove_rarewords(input_text_or_list: Union[str, List[str]], rare_words: Optional[set] = None) -> List[str]:
        """ Remove freq words """

        cnt = Counter()
        n_rare_words = 10

        if rare_words is None:
            rare_words = set([w for (w, wc) in cnt.most_common()[:-n_rare_words-1:-1]])
        if isinstance(rare_words, list):
            rare_words = set(rare_words)
        if isinstance(input_text_or_list, str):
            tokens = word_tokenize(input_text_or_list)
            processed_tokens = [token for token in tokens if token not in rare_words]
        else:
            processed_tokens = [token for token in input_text_or_list
                                if (token not in rare_words and token is not None and len(token) > 0)]
        return processed_tokens


    @mcp.tool(
        name="textprep.remove_email",
        description="Mask email addresses.",
        tags={"textprep", "pii"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def remove_email(input_text: str) -> str:
        """ Remove email in the input text """
        regex_pattern = r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}"
        return regex.sub(regex_pattern, '', input_text)


    @mcp.tool(
        name="textprep.remove_phone_number",
        description="Mask phone numbers.",
        tags={"textprep", "pii"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def remove_phone_number(input_text: str) -> str:
        """ Remove phone number in the input text """
        regex_pattern = r"(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?"
        return regex.sub(regex_pattern, '', input_text)


    @mcp.tool(
        name="textprep.remove_ssn",
        description="Mask SSN patterns.",
        tags={"textprep", "pii"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def remove_ssn(input_text: str) -> str:
        """ Remove social security number in the input text """
        regex_pattern = r"(?!219-09-9999|078-05-1120)(?!666|000|9\d{2})\d{3}-(?!00)\d{2}-(?!0{4})\d{4}|(' \
                        '?!219099999|078051120)(?!666|000|9\d{2})\d{3}(?!00)\d{2}(?!0{4})\d{4}"
        return regex.sub(regex_pattern, '', input_text)


    @mcp.tool(
        name="textprep.remove_credit_card_number",
        description="Mask credit card number patterns.",
        tags={"textprep", "pii"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def remove_credit_card_number(input_text: str) -> str:
        """ Remove credit card number in the input text """
        regex_pattern = r"(4[0-9]{12}(?:[0-9]{3})?|(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][' \
                        '0-9]|2720)[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(' \
                        '?:2131|1800|35\d{3})\d{11})"
        return regex.sub(regex_pattern, '', input_text)


    @mcp.tool(
        name="textprep.remove_emoji",
        description="Remove emoji characters.",
        tags={"textprep", "emoji"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def remove_emoji(input_text: str) -> str:
        """ Remove Emoji in the input text """
        regex_pattern = regex.compile("["
                            u"\U0001F600-\U0001F64F"  # emoticons
                            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                            u"\U0001F680-\U0001F6FF"  # transport & map symbols
                            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                            u"\U00002702-\U000027B0"
                            u"\U000024C2-\U0001F251"
                            "]+", flags=regex.UNICODE)
        return regex_pattern.sub(r'', input_text)


    @mcp.tool(
        name="textprep.remove_emoticons",
        description="Remove common ASCII emoticons.",
        tags={"textprep", "emoji"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def remove_emoticons(input_text: str) -> str:
        """ Remove emoticons in the input text """
        regex_pattern = regex.compile(u'(' + u'|'.join(k for k in emo_unicode.EMOTICONS) + u')')
        return regex_pattern.sub(r'', input_text)


    @mcp.tool(
        name="textprep.convert_emoticons_to_words",
        description="Convert some emoticons to words (e.g. ':)' -> 'smile').",
        tags={"textprep", "emoji"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def convert_emoticons_to_words(input_text: str) -> str:
        """ Convert emoticons to words in the input text """
        for emot in emo_unicode.EMOTICONS:
            input_text = regex.sub(u'('+emot+')', "_".join(emo_unicode.EMOTICONS[emot].replace(",","").split()), input_text)

        return input_text


    @mcp.tool(
        name="textprep.convert_emojis_to_words",
        description="Convert emojis to textual descriptions using emoji.demojize.",
        tags={"textprep", "emoji"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def convert_emojis_to_words(input_text: str) -> str:
        """ Convert emojis to words in the input text """
        for emot in emo_unicode.UNICODE_EMO:
            input_text = regex.sub(r'('+emot+')', "_".join(emo_unicode.UNICODE_EMO[emot].replace(",","").replace(":","").split()), input_text)

        return input_text


    @mcp.tool(
        name="textprep.remove_html",
        description="Strip HTML tags and unescape entities.",
        tags={"textprep", "html"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def remove_html(input_text: str) -> str:
        """ Remove html/xml in the input text """
        for emot in emo_unicode.UNICODE_EMO:
            return BeautifulSoup(input_text, "lxml").text


    @mcp.tool(
        name="textprep.chat_words_conversion",
        description="Convert common chat abbreviations to standard English.",
        tags={"textprep", "chat"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def chat_words_conversion(input_text: str) -> str:
        """ Chat Words Conversion in the input text """
        chat_words_map_dict = {}
        chat_words_list = []
        for line in slang_text.chat_words_str.split("\n"):
            if line != "":
                cw = line.split("=")[0]
                cw_expanded = line.split("=")[1]
                chat_words_list.append(cw)
                chat_words_map_dict[cw] = cw_expanded
        chat_words_list = set(chat_words_list)

        new_text = []
        for w in input_text.split():
            if w.upper() in chat_words_list:
                new_text.append(chat_words_map_dict[w.upper()])
            else:
                new_text.append(w)
        return " ".join(new_text)

    @mcp.tool(
        name="textprep.tokenize_word",
        description="Tokenize text into words (NLTK).",
        tags={"textprep", "tokenize"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def tokenize_word(input_text: str) -> List[str]:
        """ Converts a text into a list of word tokens """
        if input_text is None or len(input_text) == 0:
            return []
        return word_tokenize(input_text)

    @mcp.tool(
        name="textprep.tokenize_sentence",
        description="Tokenize text into sentences (NLTK).",
        tags={"textprep", "tokenize"},
        meta={"version": "0.1", "author": "mhlabs"}
    )
    def tokenize_sentence(input_text: str) -> List[str]:
        """ Converts a text into a list of sentence tokens """
        if input_text is None or len(input_text) == 0:
            return []
        tokenizer = PunktSentenceTokenizer()
        return tokenizer.tokenize(input_text)


    # @mcp.tool(
    #     name="textprep.stem_word",
    #     description="Return stemmed tokens joined as a string.",
    #     tags={"textprep", "stem"},
    #     meta={"version": "0.1", "author": "mhlabs"}
    # )
    # def stem_word(input_text_or_list: Union[str, List[str]],
    #             stemmer: Optional[Union[PorterStemmer, SnowballStemmer, LancasterStemmer]] = None
    #             ) -> List[str]:
    #     """ Stem each token in a text """
    #     if stemmer is None:
    #         stemmer = PorterStemmer()
    #     if isinstance(input_text_or_list, str):
    #         tokens = word_tokenize(input_text_or_list)
    #         processed_tokens = [stemmer.stem(token) for token in tokens]
    #     else:
    #         processed_tokens = [stemmer.stem(token) for token in input_text_or_list if token is not None and len(token) > 0]
    #     return processed_tokens


    # @mcp.tool(
    #     name="textprep.lemmatize_word",
    #     description="Return lemmatized tokens joined as a string.",
    #     tags={"textprep", "lemma"},
    #     meta={"version": "0.1", "author": "mhlabs"}
    # )
    # def lemmatize_word(input_text_or_list: Union[str, List[str]],
    #                 lemmatizer: Optional[WordNetLemmatizer] = None
    #                 ) -> List[str]:
    #     """ Lemmatize each token in a text by finding its base form """
    #     if lemmatizer is None:
    #         lemmatizer = WordNetLemmatizer()
    #     if isinstance(input_text_or_list, str):
    #         tokens = word_tokenize(input_text_or_list)
    #         processed_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    #     else:
    #         processed_tokens = [lemmatizer.lemmatize(token)
    #                             for token in input_text_or_list if token is not None and len(token) > 0]
    #     return processed_tokens

    @mcp.tool(
        name="textprep.substitute_token",
        description="Substitute each token by another token (e.g., 'vs' → 'versus') using a substitution dictionary or custom CSV file.",
        tags={"textprep", "substitution", "normalization"},
        meta={"version": "1.0", "author": "mhlabs"}
    )
    def substitute_token(token_list: List[str], sub_dict: Optional[dict] = None) -> List[str]:
        """ Substitute each token by another token, e.g., 'vs' -> 'versus' """
        # TODO: add more custom substitutions in the csv file specified by _CUSTOM_SUB_CSV_FILE_PATH
        if token_list is None or len(token_list) == 0:
            return []
        if sub_dict is None:
            with open(Settings._CUSTOM_SUB_CSV_FILE_PATH, 'r') as f:
                csv_file = csv.reader(f)
                sub_dict = dict(csv_file)
        processed_tokens = list()
        for token in token_list:
            if token in sub_dict:
                processed_tokens.append(sub_dict[token])
            else:
                processed_tokens.append(token)
        return processed_tokens
    
    

