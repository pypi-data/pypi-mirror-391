# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import typing
from typing import Dict, List
import spacy
from spacy.language import Language

import nltk
from nltk.tokenize import BlanklineTokenizer

from mhlabs_mcp_tools.handlers.output_generator import generate_output
from mhlabs_mcp_tools.core.constants import constants
from mhlabs_mcp_tools.core.config import Settings


class SpacyExtractor:
    """class SpacyExtractor encapsulates logic to pipe Records with an id and text body
    through a spacy model and return entities separated by Entity Type
    """

    def __init__(
        self, nlp: Language, input_id_col: str = "id", input_text_col: str = "text"
    ):
        """Initialize the SpacyExtractor pipeline.
        
        nlp (spacy.language.Language): pre-loaded spacy language model
        input_text_col (str): property on each document to run the model on
        input_id_col (str): property on each document to correlate with request

        RETURNS (EntityRecognizer): The newly constructed object.
        """
        self.nlp = nlp
        self.input_id_col = input_id_col
        self.input_text_col = input_text_col

    def _name_to_id(self, text: str):
        """Utility function to do a messy normalization of an entity name

        text (str): text to create "id" from
        """
        return "-".join([s.lower() for s in text.split()])

    def extract_entities(self, records: List[Dict[str, str]]):
        """Apply the pre-trained model to a batch of records
        
        records (list): The list of "document" dictionaries each with an
            `id` and `text` property
        
        RETURNS (list): List of responses containing the id of 
            the correlating document and a list of entities.
        """
        ids = (doc[self.input_id_col] for doc in records)
        texts = (doc[self.input_text_col] for doc in records)

        res = []

        for doc_id, spacy_doc in zip(ids, self.nlp.pipe(texts)):
            entities = {}
            for ent in spacy_doc.ents:
                ent_id = ent.kb_id
                if not ent_id:
                    ent_id = ent.ent_id
                if not ent_id:
                    ent_id = self._name_to_id(ent.text)

                if ent_id not in entities:
                    if ent.text.lower() == ent.text:
                        ent_name = ent.text.capitalize()
                    else:
                        ent_name = ent.text
                    entities[ent_id] = {
                        "name": ent_name,
                        "label": ent.label_,
                        "matches": [],
                    }
                entities[ent_id]["matches"].append(
                    {"start": ent.start_char, "end": ent.end_char, "text": ent.text}
                )

            res.append({"id": doc_id, "entities": list(entities.values())})
        return res
    
    def predict_nlp_component(self, component_type: str, input_text: str):

        doc = self.nlp(input_text)

        if component_type.lower() == constants.COMPONENT_TYPE_TOKENIZE.lower():
            token_data = []

            for token in doc:
                token_data.append(token.text)

            return generate_output(True, data=token_data)
        
        elif component_type.lower() == constants.COMPONENT_TYPE_POS.lower():
            pos_data = []
            pos_token: typing.Dict[str, typing.Any] = {}

            for token in doc:
                pos_token['text'] = str(token.text)
                pos_token['pos'] = str(token.pos_)

                pos_data.append(pos_token.copy())

            return generate_output(True, data=pos_data)
        
        elif component_type.lower() == constants.COMPONENT_TYPE_LEMMATIZER.lower():
            lemma_data = []
            lemma_token: typing.Dict[str, typing.Any] = {}

            for token in doc:
                lemma_token['text'] = str(token.text)
                lemma_token['lemma'] = str(token.lemma_)

                lemma_data.append(lemma_token.copy())

            return generate_output(True, data=lemma_data)
        
        elif component_type.lower() == constants.COMPONENT_TYPE_MORPHOLOGY.lower():
            morphology_data = []
            morphology_token: typing.Dict[str, typing.Any] = {}

            for token in doc:
                morphology_token['text'] = str(token.text)
                morphology_token['morphology'] = str(token.morph)

                morphology_data.append(morphology_token.copy())
                
            return generate_output(True, data=morphology_data)
        
        elif component_type.lower() == constants.COMPONENT_TYPE_DEPENDENCY_PARSER.lower():
            dep_data = []
            dep_token: typing.Dict[str, typing.Any] = {}

            for token in doc:
                dep_token['text'] = str(token.text)
                dep_token['head'] = str(token.head.text)
                dep_token['head_pos'] = str(token.head.pos_)
                dep_token['children'] = [str(child) for child in token.children]

                dep_data.append(dep_token.copy())
                
            return generate_output(True, data=dep_data)
        
        elif component_type.lower() == constants.COMPONENT_TYPE_NER.lower():
            ner_data = []
            ner_token: typing.Dict[str, typing.Any] = {}

            for ent in doc.ents:
                ner_token['text'] = str(ent.text)
                ner_token['start'] = str(ent.start_char)
                ner_token['end'] = str(ent.end_char)
                ner_token['entity'] = str(ent.label_)

                ner_data.append(ner_token.copy())
                
            return generate_output(True, data=ner_data)
        
        elif component_type.lower() == constants.COMPONENT_TYPE_NORMALIZERS.lower():
            norm_data = []
            norm_token: typing.Dict[str, typing.Any] = {}

            for token in doc:
                norm_token['text'] = str(token.text)
                norm_token['norm'] = str(token.norm_)

                norm_data.append(norm_token.copy())
                
            return generate_output(True, data=norm_data)
        
    def deep_linguistic_analysis(self, input_text: str) -> typing.Dict[str, typing.Any]:
        
        deep_linguistic_struc: typing.Dict[str, typing.Any] = {}  # deep_linguistic_struc

        nlp = spacy.load(Settings.SPACY_MODEL)
        doc = nlp(input_text)
        assert doc.has_annotation("SENT_START")

        paragraphs_line_struc: typing.Dict[str, typing.Any] = {}  #  paragraphs_line_struc
        sentence_line_struc: typing.Dict[str, typing.Any] = {}  #  sentence_line_struc
        token_line_struc: typing.Dict[str, typing.Any] = {}  #  sentence_line_struc
        dependency_line_struc: typing.Dict[str, typing.Any] = {}  #  dependency_line_struc

        deep_linguistic_struc['paragraphs'] = []
        deep_linguistic_struc['sentences'] = []
        deep_linguistic_struc['token'] = []

        tokenized_paragraphs = BlanklineTokenizer().tokenize(input_text)

        for paragraph in tokenized_paragraphs:
            paragraphs_line_struc['paragraph'] = str(paragraph)
            deep_linguistic_struc['paragraphs'].append(paragraphs_line_struc.copy())

        for sentence in doc.sents:
            sentence_line_struc['phrase'] = str(sentence)
            sentence_line_struc['start'] = int(sentence.start_char)
            sentence_line_struc['end'] = int(sentence.end_char)
            deep_linguistic_struc['sentences'].append(sentence_line_struc.copy())

        for token in doc:
            token_line_struc['name'] = str(token.text)
            token_line_struc['index'] = str(token.i)
            token_line_struc['pos'] = str(token.pos_)
            token_line_struc['lemma'] = str(token.lemma_)
            token_line_struc['norm'] = str(token.norm_)
            token_line_struc['tag'] = str(token.tag_)
            token_line_struc['shape'] = str(token.shape_)
            token_line_struc['is_alpha'] = str(token.is_alpha)
            token_line_struc['is_stop'] = str(token.is_stop)
            token_line_struc['morphology'] = str(token.morph)

            dependency_line_struc['dep'] = str(token.dep_)
            dependency_line_struc['head'] = str(token.head.text)
            dependency_line_struc['head_pos'] = str(token.head.pos_)
            dependency_line_struc['children'] = [str(child) for child in token.children]
            token_line_struc['dependency'] = dependency_line_struc.copy()

            deep_linguistic_struc['token'].append(token_line_struc.copy())

        return deep_linguistic_struc
    
    def entity_recognition(self, input_text: str) -> typing.Dict[str, typing.Any]:
        
        entity_recognition_struc: typing.Dict[str, typing.Any] = {}  # deep_linguistic_struc
        entity_line_struc: typing.Dict[str, typing.Any] = {}  #  paragraphs_line_struc

        nlp = spacy.load(Settings.SPACY_MODEL)
        doc = nlp(input_text)
        assert doc.has_annotation("SENT_START")

        entity_recognition_struc['entities'] = []

        for ent in doc.ents:
            entity_line_struc['entity'] = str(ent.text)
            entity_line_struc['category'] = str(ent.label_)
            entity_line_struc['start'] = str(ent.start_char)
            entity_line_struc['end'] = str(ent.end_char)
            
            entity_recognition_struc['entities'].append(entity_line_struc.copy())
            
        return entity_recognition_struc
