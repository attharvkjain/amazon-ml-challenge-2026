import re
import pandas as pd

def clean_text(text):
    if pd.isna(text) or text is None:
        return ""
    text = str(text).lower()
    # Normalize common suffixes
    text = re.sub(r'\b(pvt|private|pvt\.)\b', 'private', text)
    text = re.sub(r'\b(ltd|limited|ltd\.)\b', 'limited', text)
    text = re.sub(r'\b(inc|incorporated)\b', 'inc', text)
    text = re.sub(r'\b(llc)\b', 'llc', text)
    text = re.sub(r'\b(co|company|co\.)\b', 'company', text)
    
    # Remove special chars but keep spaces
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def preprocess_dataframe(df):
    """Applies basic cleaning to name and address columns."""
    df = df.copy()
    df['clean_name'] = df['business_name'].apply(clean_text)
    df['clean_address'] = df['business_address'].apply(clean_text)
    df['name_address'] = df['clean_name'] + " " + df['clean_address']
    return df
