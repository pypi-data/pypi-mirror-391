from .utils import ensure_nltk_data
ensure_nltk_data()  # ← Only here!

from .text_preprocessor import TextPreprocessor
from .pipeline import PreprocessingPipeline
from .numerical_preprocessor import NumericalPreprocessor
from .categorical_preprocessor import CategoricalPreprocessor

__version__ = "1.0.3"
__all__ = [
    "TextPreprocessor",
    "PreprocessingPipeline",
    "NumericalPreprocessor",
    "CategoricalPreprocessor",
]