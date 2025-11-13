import traceback
import logging
import spacy
import spacy.cli
import json

from fastmcp import FastMCP
from mhlabs_mcp_tools.core.config import Settings
from mhlabs_mcp_tools.services.spacy_extractor import SpacyExtractor
from mhlabs_mcp_tools.handlers.custom_exceptions import CustomJSONError
from mhlabs_mcp_tools.handlers.output_generator import generate_output
from mhlabs_mcp_tools.core.constants import constants

# ---------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------
logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(Settings.LOG_FILE_PATH)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(Settings.LOG_FILE_FORMAT)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# logger.disabled = True   # Uncomment if you want logging disabled

# ---------------------------------------------------------------------
# Global spaCy model and extractor
# ---------------------------------------------------------------------
try:
    nlp_model = spacy.load(Settings.SPACY_MODEL)
except OSError:
    spacy.cli.download(Settings.SPACY_MODEL)
    nlp_model = spacy.load(Settings.SPACY_MODEL)

extractor = SpacyExtractor(nlp_model)

def register_nlp_tools(mcp: FastMCP) -> None:
    """
    Register NLP tools with the given FastMCP instance.
    This function is optional if using category-based lazy loading.
    """
    # mcp.register_tool(load_component)
    # mcp.register_tool(predict_component)
    # =====================================================================
    # 1. NLP Load Component (MCP Tool)
    # =====================================================================

    @mcp.tool(
        name="nlp.load_component",
        description="Load a specific NLP spaCy model component to verify availability.",
        tags={"nlp", "model", "loading"},
        meta={"version": "1.0", "author": "mhlabs"}
    )
    def load_component(component_type: str) -> dict:
        """
        Loads and verifies spaCy model component.
        """
        try:
            logger.info(f"Loading component_type: {component_type} started...")

            test_doc = nlp_model("Apple is looking at buying U.K. startup for $1 billion")
            tokens = [t.text for t in test_doc]

            return generate_output(
                True,
                data={
                    "component_type": component_type,
                    "tokens_preview": tokens,
                    "message": "Component loaded successfully"
                }
            )

        except Exception as e:
            error_message = traceback.format_exc()
            logger.error(f"Unexpected error: {error_message}")
            return generate_output(
                False,
                error_code=500,
                message="Unexpected error occurred. Check logs for details."
            )

    # =====================================================================
    # 2. NLP Predict Component (MCP Tool)
    # =====================================================================

    @mcp.tool(
        name="nlp.predict_component",
        description="Run spaCy component processing such as NER, POS, Dependency, Sentiment (if available).",
        tags={"nlp", "predict", "spacy"},
        meta={"version": "1.0", "author": "mhlabs"}
    )
    def predict_component(component_type: str, input_text: str) -> dict:
        """
        Predict NLP output for the specified component type.
        """
        try:
            # -----------------------------------------------------------------
            # Validation
            # -----------------------------------------------------------------
            if component_type is None:
                raise CustomJSONError(constants.ERROR_CODE_500, constants.VALIDATE_COMPONENT_TYPE_NONE)

            if input_text is None:
                raise CustomJSONError(constants.ERROR_CODE_500, constants.VALIDATE_INPUT_TEXT_NONE)

            if not isinstance(component_type, str):
                raise CustomJSONError(constants.ERROR_CODE_500, constants.VALIDATE_COMPONENT_TYPE_STRING)

            if not isinstance(input_text, str):
                raise CustomJSONError(constants.ERROR_CODE_500, constants.VALIDATE_INPUT_TEXT_STRING)

            if not component_type.strip():
                raise CustomJSONError(constants.ERROR_CODE_500, constants.VALIDATE_COMPONENT_TYPE_EMPTY)

            if not input_text.strip():
                raise CustomJSONError(constants.ERROR_CODE_500, constants.VALIDATE_INPUT_TEXT_EMPTY)

            # -----------------------------------------------------------------
            # Actual prediction
            # -----------------------------------------------------------------
            predicted_result = extractor.predict_nlp_component(component_type, input_text)

            # predicted_result might be None
            if predicted_result is None:
                logger.info(f"predicted_result might be None for component_type: {component_type}")
                return {
                    "success": True,
                    "data": [],
                    "message": "No entities or unsupported component."
                }

            # FIX - If predicted_result is JSON string → parse it
            if isinstance(predicted_result, str):
                predicted_result = json.loads(predicted_result)

            # Ensure dict
            if not isinstance(predicted_result, dict):
                logger.info(f"predicted_result dict: {predicted_result}")
                return {
                    "success": True,
                    "data": predicted_result
                }
            
            if predicted_result is not None and bool(predicted_result):
                logger.info(f"predicted_result: {predicted_result}")
                return predicted_result

            return generate_output(True, data=constants.COMPONENT_TYPE_UNSUPPORTED)

        except CustomJSONError as e:
            logger.error(f"Custom JSON Error: {e.to_json()}")
            return e.to_json()

        except Exception as e:
            error_message = traceback.format_exc()
            logger.error(f"Unexpected error: {error_message}")
            return generate_output(False, error_code=500, message=constants.UNEXPECTED_ERROR)

