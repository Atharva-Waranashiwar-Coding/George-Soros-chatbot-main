# rag_data.py

import os
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "Soros_Questions.xlsx"


def load_qa_dataframe(path: Path | str = DATA_PATH) -> pd.DataFrame:
    """
    Load Soros Q&A from the Excel file and clean it.

    Assumes columns: 'Label', 'Question', 'Answer'.
    Drops rows with missing Question/Answer.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Could not find data file at: {path}")

    df = pd.read_excel(path)

    expected_cols = ["Label", "Question", "Answer"]
    for col in expected_cols:
        if col not in df.columns:
            raise ValueError(f"Expected column '{col}' not found in Excel file.")

    df = df[expected_cols].copy()
    df = df.dropna(subset=["Question", "Answer"]).reset_index(drop=True)

    return df


if __name__ == "__main__":
    qa_df = load_qa_dataframe()
    print(qa_df.head())
    print(f"\nLoaded {len(qa_df)} Q&A rows.")
