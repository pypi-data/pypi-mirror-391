from pydantic_settings import BaseSettings

class AppConstants(BaseSettings):
    COMPONENT_TYPE_TOKENIZE: str = "tokenize"
    COMPONENT_TYPE_POS: str = "pos"
    COMPONENT_TYPE_LEMMATIZER: str = "lemma"
    COMPONENT_TYPE_MORPHOLOGY: str = "morphology"
    COMPONENT_TYPE_DEPENDENCY_PARSER: str = "dep"
    COMPONENT_TYPE_NER: str = "ner"
    COMPONENT_TYPE_NORMALIZERS: str = "norm"
    COMPONENT_TYPE_UNSUPPORTED: str = "Unsupported Component Type"
    ERROR_CODE_500: str = "500"
    ERROR_CODE_400: str = "400"
    UNEXPECTED_ERROR: str = "Unexpected error occurred. Check logs for details."
    VALIDATE_COMPONENT_TYPE_NONE: str = "Component type parameter should not be None."
    VALIDATE_INPUT_TEXT_NONE: str = "Input text parameter should not be None."
    VALIDATE_COMPONENT_TYPE_STRING: str = "Component type parameter should be a string."
    VALIDATE_INPUT_TEXT_STRING: str = "Input text parameter should be a string."
    VALIDATE_COMPONENT_TYPE_EMPTY: str = "Component type should not be empty or contain only whitespace."
    VALIDATE_INPUT_TEXT_EMPTY: str = "Input text parameter should not be empty or contain only whitespace."
    VALIDATE_INPUT_TEXT_EMPTY_NONE: str = "No appropriate positional argument is provide."
    TEXTPREPROCESSING_OPERATIONS_EMPTY_NONE: str = "Operations should be a non-empty list of strings"
    TEXTPREPROCESSING_INVALID_OPERATIONS: str = "Invalid operation detected: {0}. Only predefined operations are allowed."
    TEXTPREPROCESSING_OPERATIONS_NOT_CALLABLE: str = "Operation '{0}' not found or not callable."

constants =    AppConstants()

class TextPreprocessingConstants(BaseSettings):

    to_lower: str =  'to_lower'
    to_upper: str = 'to_upper'
    remove_number: str = 'remove_number'
    remove_punctuation: str =  'remove_punctuation'
    remove_stopword: str = 'remove_stopword'
    remove_itemized_bullet_and_numbering: str = 'remove_itemized_bullet_and_numbering'
    remove_url: str = 'remove_url'
    remove_special_character: str = 'remove_special_character'
    keep_alpha_numeric: str = 'keep_alpha_numeric'
    remove_whitespace: str = 'remove_whitespace'
    normalize_unicode: str = 'normalize_unicode'
    remove_freqwords: str = 'remove_freqwords'
    remove_rarewords: str = 'remove_rarewords'
    remove_email: str = 'remove_email'
    remove_phone_number: str = 'remove_phone_number'
    remove_ssn: str = 'remove_ssn'
    remove_credit_card_number: str = 'remove_credit_card_number'
    remove_emoji: str = 'remove_emoji'
    remove_emoticons: str = 'remove_emoticons'
    convert_emoticons_to_words: str = 'convert_emoticons_to_words'
    convert_emojis_to_words: str = 'convert_emojis_to_words'
    remove_html: str = 'remove_html'
    chat_words_conversion: str = 'chat_words_conversion'
    expand_contraction: str = 'expand_contraction'
    tokenize_word: str = 'tokenize_word'
    tokenize_sentence: str = 'tokenize_sentence'
    stem_word: str = 'stem_word'
    lemmatize_word: str = 'lemmatize_word'
    substitute_token: str = 'substitute_token'

preprocess_operations =    TextPreprocessingConstants()