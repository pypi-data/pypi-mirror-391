from pydantic_settings import BaseSettings

class prompts(BaseSettings):
    
    language_detection_template: str = """Detect the language in a given piece of text: {context}
        The detected language is:"""
    
    sentiment_analysis_template: str = """Analyze the sentiment of the following text as positive, neutral, negative and mixed and provide respective confidence_scores.\n{format_instructions}\n{question}"""
    keyphrase_extraction_template: str = """Extract key phrase from give text: {context}.\n{format_instructions}"""

prompt_templates =    prompts()