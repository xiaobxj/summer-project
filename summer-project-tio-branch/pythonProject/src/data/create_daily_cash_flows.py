#!/usr/bin/env python3
"""
Create Daily Cash Flows File
Generate daily_cash_flows_2023-06-29_to_2025-06-28.csv from deposits_withdrawals_operating_cash.csv
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

def create_daily_cash_flows():
    """Create daily cash flows file from deposits_withdrawals_operating_cash data"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    data_dir = Path("./data/raw")
    
    # Read the deposits_withdrawals_operating_cash data
    deposits_file = data_dir / "deposits_withdrawals_operating_cash.csv"
    
    if not deposits_file.exists():
        print(f"❌ Source file not found: {deposits_file}")
        print("💡 Please run the data collection first!")
        return False
    
    print(f"📖 Reading deposits/withdrawals data from: {deposits_file}")
    df = pd.read_csv(deposits_file)
    
    print(f"📊 Original data shape: {df.shape}")
    print(f"📅 Date range: {df['record_date'].min()} to {df['record_date'].max()}")
    
    # Filter for Treasury General Account (TGA) only
    tga_data = df[df['account_type'] == 'Treasury General Account (TGA)'].copy()
    print(f"💰 TGA data shape: {tga_data.shape}")
    
    # Convert date and amount columns
    tga_data['record_date'] = pd.to_datetime(tga_data['record_date'])
    tga_data['transaction_today_amt'] = pd.to_numeric(tga_data['transaction_today_amt'], errors='coerce')
    
    # Remove rows with missing amounts
    tga_data = tga_data.dropna(subset=['transaction_today_amt'])
    print(f"🧹 After cleaning: {tga_data.shape}")
    
    # Group by date and transaction type, sum the amounts
    daily_summary = tga_data.groupby(['record_date', 'transaction_type'])['transaction_today_amt'].sum().reset_index()
    
    print(f"📈 Daily summary shape: {daily_summary.shape}")
    print(f"🏷️  Transaction types: {daily_summary['transaction_type'].unique()}")
    
    # Create the output file
    output_file = data_dir / "daily_cash_flows_2023-06-29_to_2025-06-28.csv"
    daily_summary.to_csv(output_file, index=False)
    
    print(f"✅ Daily cash flows file created: {output_file}")
    
    # Show some statistics
    deposits_total = daily_summary[daily_summary['transaction_type'] == 'Deposits']['transaction_today_amt'].sum()
    withdrawals_total = daily_summary[daily_summary['transaction_type'] == 'Withdrawals']['transaction_today_amt'].sum()
    
    print(f"\n📋 Summary Statistics:")
    print(f"   💰 Total Deposits: ${deposits_total:,.0f} million")
    print(f"   💸 Total Withdrawals: ${withdrawals_total:,.0f} million")
    print(f"   📊 Net Cash Flow: ${deposits_total - withdrawals_total:,.0f} million")
    print(f"   📅 Number of days: {daily_summary['record_date'].nunique()}")
    
    # Verify the file was created correctly
    verification_df = pd.read_csv(output_file)
    print(f"\n✅ Verification - File contains {len(verification_df)} records")
    print(f"   Columns: {list(verification_df.columns)}")
    
    return True

def main():
    """Main function"""
    print("🚀 Creating daily cash flows file...")
    print("=" * 60)
    
    success = create_daily_cash_flows()
    
    if success:
        print("\n✅ Daily cash flows file creation completed successfully!")
        print("💡 You can now run the cash flow forecaster models.")
    else:
        print("\n❌ Failed to create daily cash flows file!")
        print("💡 Please check the error messages above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 