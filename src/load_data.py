from pathlib import Path
import pandas as pd

from config import RAW_DATA_DIR, EXPECTED_RAW_FILES

def validate_raw_files() -> bool:
    """Check whether all expected raw CSV files exist."""
    missing_files = []

    for file_name in EXPECTED_RAW_FILES:
        file_path = RAW_DATA_DIR / file_name
        if not file_path.exists():
            missing_files.append(file_name)

    if missing_files:
        print("\nMissing raw files:")
        for file_name in missing_files:
            print(f"  - {file_name}")

        print("\nDownload the Olist dataset from Kaggle and place all CSV files in data/raw/.")
        return False

    print("\nAll expected raw files are available.")
    return True

def preview_raw_files() -> None:
    """Print shape and column names for each raw CSV file."""
    print("\nRaw file preview:")

    for file_name in EXPECTED_RAW_FILES:
        file_path = RAW_DATA_DIR / file_name
        df = pd.read_csv(file_path)
        print("\n" + "=" * 80)
        print(file_name)
        print(f"Rows: {df.shape[0]:,} | Columns: {df.shape[1]}")
        print("Columns:")
        for col in df.columns:
            print(f"  - {col}")


if __name__ == "__main__":
    if validate_raw_files():
        preview_raw_files()