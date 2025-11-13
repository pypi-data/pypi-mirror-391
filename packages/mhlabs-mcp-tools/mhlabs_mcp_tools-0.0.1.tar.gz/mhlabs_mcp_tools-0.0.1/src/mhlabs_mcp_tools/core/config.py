from dataclasses import dataclass
import os

@dataclass
class Settings:

    LOG_FILE_PATH : str=os.path.join('app.log')
    LOG_FILE_FORMAT: str='%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    SPACY_MODEL: str='en_core_web_lg'

    _CUSTOM_SUB_CSV_FILE_PATH : str=os.path.join('data\\raw',"custom_substitutions.csv")

settings = Settings()