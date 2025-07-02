"""
Treasury Data Collector - US Treasury Data Collection System
Specialized collection of US Treasury key data required for X-Date prediction

Data Sources:
1. Daily Treasury Statement (DTS) - Daily Treasury Reports
2. Monthly Treasury Statement (MTS) - Monthly Treasury Reports  
3. Debt to the Penny - Daily Debt Data
4. Treasury Reporting Rates of Exchange - Exchange Rate Data
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
import time
import logging
from typing import Dict, Optional, Any


class TreasuryDataCollector:
    """US Treasury Data Collector"""
    
    def __init__(self, data_dir: str = "./data/raw"):
        """
        Initialize collector
        
        Args:
            data_dir: Data storage directory
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # API base URL
        self.base_url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
        
        # Set request headers
        self.headers = {
            'User-Agent': 'X-Date-Predictor/1.0 (Educational Research)',
            'Accept': 'application/json'
        }
        
        # API rate limiting
        self.request_delay = 0.5  # seconds between requests
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict:
        """
        Send API request
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            
        Returns:
            API response data
        """
        url = f"{self.base_url}/{endpoint}"
        
        if params is None:
            params = {}
        
        # Add pagination and format parameters
        params.setdefault('format', 'json')
        params.setdefault('page[size]', '10000')  # Get more data
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Add delay to avoid rate limiting
            time.sleep(self.request_delay)
            
            return data
            
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
            raise
    
    def get_daily_treasury_statement(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get Daily Treasury Statement data (DTS)
        Contains cash balance, income, expenses and other key information
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Daily Treasury Statement data
        """
        endpoint = "v1/accounting/dts/dts_table_1"
        
        # Set default date range
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # DTS API endpoint
        params = {
            'filter': f'record_date:gte:{start_date},record_date:lte:{end_date}',
            'sort': 'record_date'
        }
        
        try:
            response_data = self._make_request(endpoint, params)
            
            if 'data' not in response_data:
                logging.warning("No data returned from DTS API")
                return pd.DataFrame()
            
            df = pd.DataFrame(response_data['data'])
            
            # Save data
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"daily_treasury_statement_{start_date}_to_{end_date}.csv"
            filepath = self.data_dir / filename
            df.to_csv(filepath, index=False)
            
            logging.info(f"DTS data saved: {filepath}")
            return df
            
        except Exception as e:
            logging.error(f"Failed to get DTS data: {e}")
            return pd.DataFrame()
    
    def get_treasury_cash_balance(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get daily Treasury cash balance (DTS Table 1)
        This is a key indicator for X-Date prediction
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Cash balance data
        """
        endpoint = "v1/accounting/dts/dts_table_1"
        
        # Set default date range
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')  # 2 years data
        
        params = {
            'filter': f'record_date:gte:{start_date},record_date:lte:{end_date}',
            'fields': 'record_date,open_today_bal,close_today_bal',
            'sort': 'record_date'
        }
        
        try:
            response_data = self._make_request(endpoint, params)
            
            if 'data' not in response_data:
                logging.warning("No cash balance data returned")
                return pd.DataFrame()
            
            df = pd.DataFrame(response_data['data'])
            
            # Convert numeric columns
            numeric_cols = ['open_today_bal', 'close_today_bal']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Save data
            filename = f"treasury_cash_balance_{start_date}_to_{end_date}.csv"
            filepath = self.data_dir / filename
            df.to_csv(filepath, index=False)
            
            logging.info(f"Cash balance data saved: {filepath}")
            return df
            
        except Exception as e:
            logging.error(f"Failed to get cash balance data: {e}")
            return pd.DataFrame()
    
    def get_debt_outstanding(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get total outstanding federal debt data
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Debt outstanding data
        """
        endpoint = "v1/accounting/od/debt_to_penny"
        
        # Set default date range
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        params = {
            'filter': f'record_date:gte:{start_date},record_date:lte:{end_date}',
            'sort': 'record_date'
        }
        
        try:
            response_data = self._make_request(endpoint, params)
            
            if 'data' not in response_data:
                logging.warning("No debt outstanding data returned")
                return pd.DataFrame()
            
            df = pd.DataFrame(response_data['data'])
            
            # Convert numeric columns
            numeric_cols = ['debt_held_public_amt', 'intragov_hold_amt', 'tot_pub_debt_out_amt']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Save data
            filename = f"debt_outstanding_{start_date}_to_{end_date}.csv"
            filepath = self.data_dir / filename
            df.to_csv(filepath, index=False)
            
            logging.info(f"Debt outstanding data saved: {filepath}")
            return df
            
        except Exception as e:
            logging.error(f"Failed to get debt outstanding data: {e}")
            return pd.DataFrame()
    
    def get_daily_cash_flows(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get daily income and expense details (Inflows/Outflows)
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Cash flow data
        """
        endpoint = "v1/accounting/dts/dts_table_6"
        
        # Set default date range
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        
        params = {
            'filter': f'record_date:gte:{start_date},record_date:lte:{end_date}',
            'sort': 'record_date'
        }
        
        try:
            response_data = self._make_request(endpoint, params)
            
            if 'data' not in response_data:
                logging.warning("No cash flow data returned")
                return pd.DataFrame()
            
            df = pd.DataFrame(response_data['data'])
            
            # Convert numeric columns
            numeric_cols = ['net_operating_amt', 'total_deposits_today_amt', 'total_withdrawals_today_amt']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Save data
            filename = f"daily_cash_flows_{start_date}_to_{end_date}.csv"
            filepath = self.data_dir / filename
            df.to_csv(filepath, index=False)
            
            logging.info(f"Cash flow data saved: {filepath}")
            return df
            
        except Exception as e:
            logging.error(f"Failed to get cash flow data: {e}")
            return pd.DataFrame()
    
    def get_monthly_treasury_statement(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get Monthly Treasury Statement data (MTS)
        Contains more detailed income and expense categories
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Monthly Treasury Statement data
        """
        endpoint = "v1/accounting/mts/mts_table_1"
        
        # Set default date range
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=1095)).strftime('%Y-%m-%d')  # 3 years data
        
        params = {
            'filter': f'record_date:gte:{start_date},record_date:lte:{end_date}',
            'sort': 'record_date'
        }
        
        try:
            response_data = self._make_request(endpoint, params)
            
            if 'data' not in response_data:
                logging.warning("No MTS data returned")
                return pd.DataFrame()
            
            df = pd.DataFrame(response_data['data'])
            
            # Save data
            filename = f"monthly_treasury_statement_{start_date}_to_{end_date}.csv"
            filepath = self.data_dir / filename
            df.to_csv(filepath, index=False)
            
            logging.info(f"MTS data saved: {filepath}")
            return df
            
        except Exception as e:
            logging.error(f"Failed to get MTS data: {e}")
            return pd.DataFrame()
    
    def get_treasury_securities_data(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Get Treasury securities issuance and maturity data
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Treasury securities data
        """
        endpoint = "v1/accounting/od/auctions_query"
        
        # Set default date range
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        params = {
            'filter': f'auction_date:gte:{start_date},auction_date:lte:{end_date}',
            'sort': 'auction_date'
        }
        
        try:
            response_data = self._make_request(endpoint, params)
            
            if 'data' not in response_data:
                logging.warning("No Treasury securities data returned")
                return pd.DataFrame()
            
            df = pd.DataFrame(response_data['data'])
            
            # Save data
            filename = f"treasury_securities_{start_date}_to_{end_date}.csv"
            filepath = self.data_dir / filename
            df.to_csv(filepath, index=False)
            
            logging.info(f"Treasury securities data saved: {filepath}")
            return df
            
        except Exception as e:
            logging.error(f"Failed to get Treasury securities data: {e}")
            return pd.DataFrame()
    
    def collect_all_data(self, start_date: str = None, end_date: str = None) -> Dict[str, pd.DataFrame]:
        """
        Collect all Treasury-related data
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary containing all data
        """
        
        logging.info("Starting comprehensive Treasury data collection...")
        
        data_collection = {}
        
        # 1. Daily Treasury cash balance
        logging.info("Collecting Treasury cash balance data...")
        data_collection['cash_balance'] = self.get_treasury_cash_balance(start_date, end_date)
        
        # 2. Total outstanding federal debt
        logging.info("Collecting debt outstanding data...")
        data_collection['debt_outstanding'] = self.get_debt_outstanding(start_date, end_date)
        
        # 3. Daily cash flows
        logging.info("Collecting daily cash flow data...")
        data_collection['cash_flows'] = self.get_daily_cash_flows(start_date, end_date)
        
        # 4. Complete Daily Treasury Statement
        logging.info("Collecting Daily Treasury Statement...")
        data_collection['daily_treasury_statement'] = self.get_daily_treasury_statement(start_date, end_date)
        
        # 5. Monthly Treasury Statement
        logging.info("Collecting Monthly Treasury Statement...")
        data_collection['monthly_treasury_statement'] = self.get_monthly_treasury_statement(start_date, end_date)
        
        # 6. Treasury securities data
        logging.info("Collecting Treasury securities data...")
        data_collection['treasury_securities'] = self.get_treasury_securities_data(start_date, end_date)
        
        # Save data collection summary
        self._save_collection_summary(data_collection, start_date, end_date)
        
        logging.info("Treasury data collection completed!")
        return data_collection
    
    def _save_collection_summary(self, data: Dict[str, pd.DataFrame], start_date: str, end_date: str):
        """
        Save data collection summary
        
        Args:
            data: Collected data
            start_date: Start date
            end_date: End date
        """
        summary = {
            'collection_timestamp': datetime.now().isoformat(),
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'datasets': {}
        }
        
        for name, df in data.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                summary['datasets'][name] = {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'size_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
                }
        
        # Save summary
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_file = self.data_dir / f"treasury_data_collection_summary_{timestamp}.json"
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logging.info(f"Collection summary saved: {summary_file}")


def main():
    """Main function - Demonstrates how to use Treasury Data Collector"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create collector
    collector = TreasuryDataCollector()
    
    # Set date range (last 2 years of data)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    
    print(f"Starting Treasury data collection...")
    print(f"Date range: {start_date} to {end_date}")
    print("-" * 50)
    
    # Collect all data
    data = collector.collect_all_data(start_date, end_date)
    
    # Display collection results
    print("\nData collection completed!")
    print("=" * 50)
    
    for name, df in data.items():
        if isinstance(df, pd.DataFrame) and not df.empty:
            print(f"{name}: {len(df)} rows of data")
            if 'record_date' in df.columns:
                print(f"  Date range: {df['record_date'].min()} to {df['record_date'].max()}")
        else:
            print(f"{name}: No data collected")
    
    print(f"\nAll data saved to: {collector.data_dir}")


if __name__ == "__main__":
    main() 