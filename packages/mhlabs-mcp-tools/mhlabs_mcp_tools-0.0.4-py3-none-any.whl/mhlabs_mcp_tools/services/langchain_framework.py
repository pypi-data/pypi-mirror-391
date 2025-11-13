# Copyright (c) LangChain, Inc.
# Licensed under the MIT License.

import os
import typing
import json
import pprint
import traceback

from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.schema import Document
from langchain_experimental.data_anonymizer import PresidioReversibleAnonymizer

from core.prompts import prompt_templates
from handlers.output_generator import generate_output

from pydantic import ValidationError

from dotenv import load_dotenv
load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.1)    

class LangchainFramework:

    def __init__(self):
        pass

    def language_detection(self, input_text: str) -> typing.Dict[str, typing.Any]:
        
        language_detection_struc: typing.Dict[str, typing.Any] = {}  # deep_linguistic_struc

        prompt = PromptTemplate.from_template(prompt_templates.language_detection_template)

        chain = prompt | llm

        context = input_text
        result = chain.invoke({"context": context})
        language_detection_struc['input_text'] = str(input_text)
        language_detection_struc['detected_language'] = str(result.content)

        return language_detection_struc  
    
    def sentiment_analysis(self, input_text: str) -> typing.Dict[str, typing.Any]:
        
        response_schemas = [
            ResponseSchema(name="input_text", description="add the input text here",type="string"),
            ResponseSchema(name="document_sentiment", description="Analyze the sentiment of the following text as positive, neutral, negative and mixed and provide respective confidence_scores",type="string"),
            ResponseSchema(name="positive", description="confidence scores for positive with precision 2", type="float"),
            ResponseSchema(name="negative", description="confidence scores for negative with precision 2", type="float"),
            ResponseSchema(name="neutral", description="confidence scores for neutral with precision 2", type="float"),
            ResponseSchema(name="mixed", description="confidence scores for mixed with precision 2", type="float")
        ]

        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        format_instructions = output_parser.get_format_instructions()
        
        prompt = ChatPromptTemplate(
            messages=[
                HumanMessagePromptTemplate.from_template(prompt_templates.sentiment_analysis_template)
            ],
            input_variables=["question"],
            partial_variables={"format_instructions": format_instructions}
        )
        _input = prompt.format_prompt(question=input_text)
        chain = prompt | llm

        output  = chain.invoke({"question": _input.to_messages()})

        return output_parser.parse(output.content)
    
    def keyphrase_extraction(self, input_text: str) -> typing.Dict[str, typing.Any]:
        
        keyphrase_extraction_struc: typing.Dict[str, typing.Any] = {}  # deep_linguistic_struc

        output_parser = CommaSeparatedListOutputParser()

        format_instructions = output_parser.get_format_instructions()
        prompt = PromptTemplate(
            template=prompt_templates.keyphrase_extraction_template,
            input_variables=["context"],
            partial_variables={"format_instructions": format_instructions}
        )

        _input = prompt.format(context=input_text)
        chain = prompt | llm

        output  = chain.invoke({"context": _input})
        phrases = output_parser.parse(output.content)

        keyphrase_extraction_struc['mainPhrases'] = phrases

        return keyphrase_extraction_struc
    
    def pii_anonymization(self, document_content: str) -> typing.Dict[str, typing.Any]:
        
        pii_recognition_struc: typing.Dict[str, typing.Any] = {}  # deep_linguistic_struc
        pii_line_struc: typing.Dict[str, typing.Any] = {}  #  paragraphs_line_struc

        documents = [Document(page_content=document_content)]

        anonymizer = PresidioReversibleAnonymizer(
            add_default_faker_operators=False,
        )

        # print_colored_pii(anonymizer.anonymize(document_content))
        anonymizer.anonymize(document_content)

        pii_recognition_struc['pii_anonymizer_doc_before'] = str(anonymizer.anonymize(document_content))
        pii_recognition_struc['pii_deanonymizer_mapping_before'] = anonymizer.deanonymizer_mapping

        anonymizer = PresidioReversibleAnonymizer(
            add_default_faker_operators=True,
            # Faker seed is used here to make sure the same fake data is generated for the test purposes
            # In production, it is recommended to remove the faker_seed parameter (it will default to None)
            # faker_seed=42,
        )

        pii_recognition_struc['pii_anonymizer_doc_after'] = str(anonymizer.anonymize(document_content))
        pii_recognition_struc['pii_deanonymizer_mapping_after'] = anonymizer.deanonymizer_mapping

        return pii_recognition_struc

