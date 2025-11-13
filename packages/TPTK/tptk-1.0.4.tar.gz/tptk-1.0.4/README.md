# Text Preprocessing Toolkit (TPTK)

[![PyPI version](https://badge.fury.io/py/TPTK.svg)](https://badge.fury.io/py/TPTK)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/downloads/)

TPTK is a Python package designed to automate data preprocessing tasks for machine learning and data analysis. It supports text cleaning, numerical data handling (imputation, outlier removal, scaling), and categorical encoding (label or one-hot). The package provides both a programmatic API and a command-line interface (CLI) for ease of use. It processes large datasets in chunks to handle memory efficiently and generates reports on preprocessing steps.

## Features

- **Text Preprocessing**: Clean, tokenize, remove stopwords, lemmatize, and spell-check text data.
- **Numerical Preprocessing**: Impute missing values (mean/median), remove outliers (IQR/Z-score), and scale features (standard/min-max).
- **Categorical Preprocessing**: Label encoding or one-hot encoding with support for saving/loading encoders.
- **Pipeline**: Configurable preprocessing pipeline using YAML/JSON files for batch processing CSV files.
- **Chunked Processing**: Handles large datasets by processing in chunks.
- **Reporting**: Generates JSON reports summarizing preprocessing actions.


## Installation

### From PyPI

Install the package using pip:

```bash
pip install TPTK
```

### From Source

Clone the repository and install:

```bash
git clone https://github.com/Gaurav-Jaiswal-1/Text-Preprocessing-Toolkit.git
cd Text-Preprocessing-Toolkit
pip install .
```

During installation, NLTK resources (e.g., stopwords, wordnet) are automatically downloaded.

### Dependencies

- `nltk >= 3.6.0`
- `pyspellchecker >= 0.7.1`
- `pandas >= 1.2.0`
- `scikit-learn` (for encoding and scaling)
- `joblib` (for saving encoders)

## Quick Start

### Step 1: Prepare Your Data

Assume you have a CSV file `input.csv` with columns like `review` (text), `age` (numerical), `rating` (numerical), `gender` (categorical).

Example `input.csv`:

```
review,age,rating,gender
"This is a great product!",35,4.5,Male
"Bad experience, won't buy again.",,3.0,Female
"Excellent quality.",42,,Male
```

### Step 2: Programmatic Usage

For more control, use the API in your Python scripts.

#### Example: Text Preprocessing Only

```python

from tptk.text_preprocessor import TextPreprocessor
import pandas as pd

# Download
url = "https://raw.githubusercontent.com/Ankit152/IMDB-sentiment-analysis/master/IMDB-Dataset.csv"
df = pd.read_csv(url)
df = df.head(1000)  # Small sample
df.to_csv(r"imdb_raw.csv", index=False)

# Clean
tp = TextPreprocessor(spell_correction=False)
tp.process_csv(
    input_path=r"imdb_raw.csv",
    text_column="review",
    output_path=r"imdb_clean.csv",
    steps=['clean', 'punctuation', 'lowercase', 'tokenize', 'stopwords', 'lemmatize']
)

```

#### Example: Numerical Preprocessing Only

```python
import pandas as pd
from tptk.numerical_preprocessor import NumericalPreprocessor
import seaborn as sns
import matplotlib.pyplot as plt
import os

# If you are downlaoding the dataset
INPUT_DIR = "Input directory path"
OUTPUT_DIR = "Output directory path"

# If you haven't made a input and output dir
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Download
from sklearn.datasets import fetch_california_housing
data = fetch_california_housing(as_frame=True)
df = data.frame.sample(1000, random_state=42)
df.to_csv(f"{INPUT_DIR}/housing_raw.csv", index=False)

# Process
np_prep = NumericalPreprocessor()
df_clean = np_prep.fit_transform(
    df, columns=['MedInc', 'HouseAge', 'AveRooms', 'Population', 'AveOccup'],
    impute="median", scale="standard", remove_outliers="iqr"
)
df_clean.to_csv(f"{OUTPUT_DIR}/housing_clean.csv", index=False)

# Plot
plt.figure(figsize=(10,4))
plt.subplot(1,2,1); sns.boxplot(data=df[['MedInc']]); plt.title("Before")
plt.subplot(1,2,2); sns.boxplot(data=df_clean[['MedInc']]); plt.title("After")
plt.savefig(f"{OUTPUT_DIR}/housing_plot.png")
plt.close()

print("Housing: Done")
```

#### Example: Categorical Preprocessing Only

```python
from tptk.categorical_preprocessor import CategoricalPreprocessor
import pandas as pd
import os

# If you are downlaoding the dataset

INPUT_DIR = "Input directory path"
OUTPUT_DIR = "Output directory path"
os.makedirs(INPUT_DIR, exist_ok=True); os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")
df = df[['Pclass', 'Sex', 'Embarked', 'Survived']].dropna().head(500)
df.to_csv(f"{INPUT_DIR}/titanic_raw.csv", index=False)

# Label
label_enc = CategoricalPreprocessor("label", save_dir="../encoders")
label_enc.fit(df, ['Pclass', 'Sex', 'Embarked'])
df_label = label_enc.transform(df, ['Pclass', 'Sex', 'Embarked'])
df_label.to_csv(f"{OUTPUT_DIR}/titanic_label.csv", index=False)

# One-Hot
ohe_enc = CategoricalPreprocessor("onehot", save_dir="../encoders")
ohe_enc.fit(df, ['Pclass', 'Sex', 'Embarked'])
df_ohe = ohe_enc.transform(df, ['Pclass', 'Sex', 'Embarked'])
df_ohe.to_csv(f"{OUTPUT_DIR}/titanic_ohe.csv", index=False)

print("Titanic: Label →", df_label['Sex'].iloc[0], "| OHE →", df_ohe.filter(like='Sex_').columns)
```


### Troubleshooting NLTK Data
TPTK bundles punkt_tab, stopwords, wordnet, and averaged_perceptron_tagger_eng.
On first import, it:

Checks bundled data
Falls back to nltk.download(..., quiet=True)

## If you see LookupError or download fails:
```python
pythonimport nltk
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger_eng')
```

### Step 5: View Reports

After processing, check `preprocessing_report.json` for details like imputed values, outliers removed, etc.

Example Report:

```json
{
  "steps": ["text", "numerical", "categorical"],
  "stats": {
    "numerical": {
      "age": {"imputed_with": 38.5, "outliers_removed": 0},
      "rating": {"imputed_with": 3.75, "outliers_removed": 1}
    }
  }
}
```

## Development and Testing

- **Setup**: Run `./init_setup.sh` to create a virtual environment and install dev dependencies.
- **Linting and Testing**: Use `tox` or manually:
  ```bash
  flake8 src/
  mypy src/
  pytest -v tests/unit
  pytest -v tests/integration
  ```
- **Build Package**: `python setup.py sdist bdist_wheel`

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/Gaurav-Jaiswal-1/Text-Preprocessing-Toolkit).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions, contact [Gaurav Jaiswal](mailto:jaiswalgaurav863@gmail.com).