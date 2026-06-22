# rag_data.py

import os
import pandas as pd

# Path to your Excel file inside the data folder
DATA_PATH = os.path.join("data", "Soros_Questions.xlsx")

def load_qa_dataframe(path: str = DATA_PATH) -> pd.DataFrame:
    """
    Load Soros Q&A from the Excel file and clean it.

    Assumes columns: 'Label', 'Question', 'Answer', plus an extra 'Unnamed: 3'.
    We keep only the useful columns and drop rows with missing Question/Answer.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Could not find data file at: {path}")

    df = pd.read_excel(path)

    # Keep only the main columns we care about
    expected_cols = ["Label", "Question", "Answer"]
    for col in expected_cols:
        if col not in df.columns:
            raise ValueError(f"Expected column '{col}' not found in Excel file.")

    df = df[expected_cols].copy()

    # Drop rows where Question or Answer is missing
    df = df.dropna(subset=["Question", "Answer"]).reset_index(drop=True)

    return df


if __name__ == "__main__":
    # Simple test to verify everything loads correctly
    qa_df = load_qa_dataframe()
    print(qa_df.head())
    print(f"\nLoaded {len(qa_df)} Q&A rows.")
