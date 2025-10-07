import pandas as pd
import re

def load_data(filepath: str) -> pd.DataFrame:
    """
    Loads data from a CSV file into a pandas DataFrame.

    Args:
        filepath: The path to the CSV file.

    Returns:
        A pandas DataFrame containing the loaded data.
    """
    try:
        df = pd.read_csv(filepath)
        print(f"Data loaded successfully from {filepath}")
        return df
    except FileNotFoundError:
        print(f"Error: The file at {filepath} was not found.")
        return None

def clean_text(text: str) -> str:
    """
    A simple text cleaning function.
    - Converts text to lowercase.
    - Removes punctuation.

    Args:
        text: The input string to clean.

    Returns:
        The cleaned string.
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text

def preprocess_data(df: pd.DataFrame, text_column: str) -> pd.DataFrame:
    """
    Applies preprocessing steps to a DataFrame.

    Args:
        df: The input DataFrame.
        text_column: The name of the column containing text to be cleaned.

    Returns:
        The DataFrame with a new column 'cleaned_text'.
    """
    if text_column not in df.columns:
        print(f"Error: Column '{text_column}' not found in DataFrame.")
        return df

    df['cleaned_text'] = df[text_column].apply(clean_text)
    print("Text cleaning applied.")
    return df

if __name__ == '__main__':
    # This block demonstrates how to use the functions.
    # It will run when the script is executed directly.
    from pathlib import Path

    # Construct a path to the data file relative to this script's location
    # This makes the script runnable from any directory.
    SCRIPT_DIR = Path(__file__).parent
    DATA_FILE = SCRIPT_DIR / 'demo_data.csv'

    # Load the data
    data_df = load_data(str(DATA_FILE))

    if data_df is not None:
        # Preprocess the data
        processed_df = preprocess_data(data_df, 'text')

        # Display the first 5 rows of the processed data
        print("\nProcessed Data Head:")
        print(processed_df.head())