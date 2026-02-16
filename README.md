# SafePaste

SafePaste is a desktop application that acts as a security buffer between users and Large Language Models (LLMs). It intercepts clipboard content, automatically redacts personally identifiable information (PII) using local AI processing, and provides users with a sanitized version safe to share.

## Setup

1.  Install dependencies:
    ```bash
    py -m pip install -r requirements.txt
    ```
2.  Download spaCy model:
    ```bash
    py -m spacy download en_core_web_lg
    ```
3.  Run the application:
    ```bash
    py main.py
    ```

## Development

-   Run tests: `py -m pytest tests/`
