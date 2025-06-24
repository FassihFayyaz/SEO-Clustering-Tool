# utils.py
import pandas as pd

def get_keywords_from_input(text_input, file_input):
    """
    Extracts keywords from either a text area or an uploaded CSV file.
    The caller is responsible for handling exceptions from file parsing.
    """
    keywords = []
    if text_input:
        keywords = [kw.strip() for kw in text_input.split('\n') if kw.strip()]
    elif file_input:
        df = pd.read_csv(file_input)
        if not df.empty:
            keywords = [str(kw).strip() for kw in df.iloc[:, 0].dropna().tolist()]
            
    return list(set(kw.lower() for kw in keywords))

def df_to_csv(df):
    """Converts a DataFrame to a CSV in memory."""
    return df.to_csv(index=False).encode('utf-8')