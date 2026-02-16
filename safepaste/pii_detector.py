import logging
from typing import List, Dict, Any
from presidio_analyzer import AnalyzerEngine, RecognizerResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PiiDetector:
    """
    Wrapper class for Microsoft Presidio Analyzer to detect PII in text.
    """
    def __init__(self, language: str = "en"):
        """
        Initialize the PII Detector with the specified language.
        
        Args:
            language (str): Language code (default: "en").
        """
        self.language = language
        try:
            # Initialize Presidio Analyzer
            # Note: This requires the spaCy model to be downloaded:
            # python -m spacy download en_core_web_lg
            self.analyzer = AnalyzerEngine()
            logger.info("Presidio Analyzer initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Presidio Analyzer: {e}")
            raise

    def detect(self, text: str) -> List[RecognizerResult]:
        """
        Detect PII in the given text.

        Args:
            text (str): The text to analyze.

        Returns:
            List[RecognizerResult]: A list of detected entities.
        """
        if not text:
            return []

        try:
            # Detect PII
            # We focus on the requested categories: Email, Phone, Person, API Key, Credit Card
            # Presidio's default recognizers cover: 
            # EMAIL_ADDRESS, PHONE_NUMBER, PERSON, CREDIT_CARD
            # We might need custom logic for API keys if defaults aren't sufficient,
            # but for MVP we'll start with defaults.
            
            entities = ["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "CREDIT_CARD", "CRYPTO"] # CRYPTO often catches keys
            
            results = self.analyzer.analyze(
                text=text,
                entities=entities,
                language=self.language
            )
            
            logger.debug(f"Detected {len(results)} entities in text.")
            return results

        except Exception as e:
            logger.error(f"Error during PII detection: {e}")
            return []

if __name__ == "__main__":
    # Quick test
    detector = PiiDetector()
    sample_text = "My name is John Doe and my email is john.doe@example.com."
    results = detector.detect(sample_text)
    print(f"Text: {sample_text}")
    print("Results:")
    for result in results:
        print(result)
