import pandas as pd
try:
    from indic_transliteration import sanscript
    from indic_transliteration.sanscript import SchemeMap, SCHEMES, transliterate
except ImportError:
    sanscript = None

def transliterate_indic_to_latin(text):
    if pd.isna(text) or not text:
        return text
    if sanscript is None:
        return text
        
    # We will assume Devanagari for simplicity as a heuristic, 
    # but a full solution would detect script block.
    # To keep it fast, we can check if there are chars in the devanagari unicode range.
    has_indic = any(0x0900 <= ord(c) <= 0x0D7F for c in str(text))
    if not has_indic:
        return text
        
    try:
        # A basic mapping to IAST (Latin)
        return transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
    except Exception:
        return text

def apply_transliteration(df):
    """Applies transliteration to business names and addresses in the dataframe."""
    if sanscript is None:
        print("indic_transliteration not installed. Skipping transliteration.")
        return df
        
    df = df.copy()
    print("Applying transliteration...")
    df['clean_name'] = df['clean_name'].apply(transliterate_indic_to_latin)
    df['clean_address'] = df['clean_address'].apply(transliterate_indic_to_latin)
    # Re-combine since clean_name/address might have changed
    df['name_address'] = df['clean_name'] + " " + df['clean_address']
    return df
