import logging
import json
import nltk
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TPTK")

def ensure_nltk_data():
    """Ensure NLTK data is available — bundled first, download fallback."""
    package_dir = Path(__file__).resolve().parent
    bundled = package_dir / "nltk_data"
    if bundled.exists() and str(bundled) not in nltk.data.path:
        nltk.data.path.insert(0, str(bundled))

    resources = {
        "tokenizers/punkt": "punkt",
        "corpora/stopwords": "stopwords",
        "corpora/wordnet": "wordnet",
        "taggers/averaged_perceptron_tagger": "averaged_perceptron_tagger",
        "taggers/averaged_perceptron_tagger": "averaged_perceptron_tagger_eng",

    }

    for path, name in resources.items():
        try:
            nltk.data.find(path)
        except LookupError:
            logger.info(f"Downloading NLTK resource: {name}")
            nltk.download(name, quiet=True)

def save_report(report: dict, path: str):
    with open(path, 'w') as f:
        json.dump(report, f, indent=2)
    logger.info(f"Report saved to {path}")