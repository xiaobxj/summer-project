from pathlib import Path
import pandas as pd

def load_operating_cash(file_name="deposits_withdrawals_operating_cash.csv", data_dir="./data/raw"):
    data_path = Path(data_dir) / file_name
    
    if not data_path.exists():
        raise FileNotFoundError(f"❌ File not found: {data_path}")
    
    df = pd.read_csv(data_path)
    df['record_date'] = pd.to_datetime(df['record_date'])
    df['transaction_today_amt'] = pd.to_numeric(df['transaction_today_amt'], errors='coerce')
    
    return df

df_cash = load_operating_cash()

print(df_cash.head())
print(df_cash.columns)

