import pandas as pd
import os


def extract_from_csv(filepath: str) -> pd.DataFrame:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    data = pd.read_csv(
        filepath,
        encoding = 'ISO-8859-1',
        dtype = {'CustomerID': str, 'InvoiceNo': str, 'StockCode': str}
    )

    print(f"Extracted {len(data):,} rows, {data.shape[1]} columns from {filepath}")
    return data

if __name__ == '__main__':
    data = extract_from_csv('data/raw/online_retail.csv')
    print(data.head())