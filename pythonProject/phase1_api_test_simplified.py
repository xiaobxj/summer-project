"""
Phase 1: Simplified API Testing (No Bloomberg)

This script tests free API connectivity to provide a completely free data solution for the X-Date prediction project.
"""

import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os
from pathlib import Path
import json
import time

# Setup logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class FreeAPIConnectionTester:
    """Free API connection testing class (no Bloomberg)"""
    
    def __init__(self):
        self.test_results = {}
        self.api_keys = {}
        
    def load_api_keys(self):
        """Load API keys from environment variables"""
        self.api_keys = {
            'BEA_API_KEY': os.getenv('BEA_API_KEY'),
            'FRED_API_KEY': os.getenv('FRED_API_KEY'),
        }
    
    def test_treasury_fiscaldata_api(self) -> bool:
        """Test Treasury FiscalData API connection - free and critical"""
        logger.info("Testing Treasury FiscalData API...")
        
        # Test DTS data access
        try:
            url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/dts_table_1"
            
            # Get last 30 days of data
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            params = {
                'filter': f'record_date:gte:{start_date},record_date:lte:{end_date}',
                'page[size]': '100'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                self.test_results['Treasury_FiscalData'] = {
                    'status': 'SUCCESS',
                    'data_points': len(data['data']),
                    'latest_date': data['data'][-1].get('record_date', 'Unknown'),
                    'message': 'Treasury data access successful'
                }
                logger.info("✅ Treasury FiscalData API: SUCCESS")
                return True
            else:
                raise ValueError("No data returned")
                
        except Exception as e:
            self.test_results['Treasury_FiscalData'] = {
                'status': 'FAILED',
                'error': str(e),
                'message': 'Treasury API connection failed'
            }
            logger.error(f"❌ Treasury FiscalData API: {e}")
            return False
    
    def test_bea_api(self) -> bool:
        """Test BEA API connection - free but requires registration"""
        logger.info("Testing BEA API...")
        
        bea_key = self.api_keys.get('BEA_API_KEY')
        if not bea_key:
            self.test_results['BEA_API'] = {
                'status': 'SKIPPED',
                'message': 'BEA API key not provided'
            }
            logger.warning("⚠️  BEA API: API key not found")
            return False
        
        try:
            url = "https://apps.bea.gov/api/data"
            params = {
                'UserID': bea_key,
                'method': 'GetData',
                'datasetname': 'NIPA',
                'TableName': 'T10101',
                'Frequency': 'Q',
                'Year': '2023',
                'ResultFormat': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'BEAAPI' in data and 'Results' in data['BEAAPI']:
                self.test_results['BEA_API'] = {
                    'status': 'SUCCESS',
                    'message': 'BEA API access successful'
                }
                logger.info("✅ BEA API: SUCCESS")
                return True
            else:
                raise ValueError("Invalid response format")
                
        except Exception as e:
            self.test_results['BEA_API'] = {
                'status': 'FAILED',
                'error': str(e),
                'message': 'BEA API connection failed'
            }
            logger.error(f"❌ BEA API: {e}")
            return False
    
    def test_fred_api(self) -> bool:
        """Test FRED API connection - free but requires registration"""
        logger.info("Testing FRED API...")
        
        fred_key = self.api_keys.get('FRED_API_KEY')
        if not fred_key:
            self.test_results['FRED_API'] = {
                'status': 'SKIPPED',
                'message': 'FRED API key not provided'
            }
            logger.warning("⚠️  FRED API: API key not found")
            return False
        
        try:
            # Test getting 10-year Treasury yield
            url = "https://api.stlouisfed.org/fred/series/observations"
            params = {
                'series_id': 'DGS10',  # 10-year Treasury yield
                'api_key': fred_key,
                'file_type': 'json',
                'limit': '10'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'observations' in data and len(data['observations']) > 0:
                latest_obs = data['observations'][-1]
                self.test_results['FRED_API'] = {
                    'status': 'SUCCESS',
                    'latest_date': latest_obs.get('date', 'Unknown'),
                    'latest_value': latest_obs.get('value', 'N/A'),
                    'message': 'FRED API access successful'
                }
                logger.info("✅ FRED API: SUCCESS")
                return True
            else:
                raise ValueError("No observations returned")
                
        except Exception as e:
            self.test_results['FRED_API'] = {
                'status': 'FAILED',
                'error': str(e),
                'message': 'FRED API connection failed'
            }
            logger.error(f"❌ FRED API: {e}")
            return False
    
    def test_yahoo_finance(self) -> bool:
        """Test Yahoo Finance - completely free"""
        logger.info("Testing Yahoo Finance...")
        
        try:
            # Test getting key indicators
            symbols = ['^VIX', '^TNX', '^IRX']  # VIX, 10yr Treasury, 3mo Treasury
            
            successful_symbols = []
            
            for symbol in symbols:
                try:
                    # Get latest data
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='5d')
                    
                    if not hist.empty:
                        successful_symbols.append(symbol)
                
                except Exception:
                    continue
            
            if successful_symbols:
                self.test_results['Yahoo_Finance'] = {
                    'status': 'SUCCESS',
                    'successful_symbols': successful_symbols,
                    'total_symbols_tested': len(symbols),
                    'message': f'Yahoo Finance access successful for {len(successful_symbols)}/{len(symbols)} symbols'
                }
                logger.info(f"✅ Yahoo Finance: SUCCESS ({len(successful_symbols)}/{len(symbols)} symbols)")
                return True
            else:
                raise ValueError("No symbols could be retrieved")
                
        except Exception as e:
            self.test_results['Yahoo_Finance'] = {
                'status': 'FAILED',
                'error': str(e),
                'message': 'Yahoo Finance access failed'
            }
            logger.error(f"❌ Yahoo Finance: {e}")
            return False
    
    def test_basic_connectivity(self) -> bool:
        """Test basic network connectivity"""
        logger.info("Testing basic network connectivity...")
        
        # Test basic internet connection
        try:
            test_urls = [
                'https://www.google.com',
                'https://api.fiscaldata.treasury.gov',
                'https://finance.yahoo.com'
            ]
            
            successful_connections = 0
            
            for url in test_urls:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        successful_connections += 1
                except:
                    continue
            
            if successful_connections >= 2:
                self.test_results['Basic_Connectivity'] = {
                    'status': 'SUCCESS',
                    'successful_connections': successful_connections,
                    'total_tested': len(test_urls),
                    'message': 'Internet connectivity is good'
                }
                logger.info("✅ Basic Connectivity: SUCCESS")
                return True
            else:
                raise ValueError("Insufficient connectivity")
                
        except Exception as e:
            self.test_results['Basic_Connectivity'] = {
                'status': 'FAILED',
                'error': str(e),
                'message': 'Basic connectivity test failed'
            }
            logger.error(f"❌ Basic Connectivity: {e}")
            return False
    
    def test_free_market_data_sources(self) -> bool:
        """Test free market data sources (CDS and credit risk proxies)"""
        logger.info("Testing free market data sources...")
        
        try:
            # Test getting credit risk proxy indicators
            risk_symbols = ['^VIX', 'HYG', 'TLT', 'DX-Y.NYB']  # VIX, high-yield bonds, Treasury, US Dollar index
            
            successful_data = {}
            
            for symbol in risk_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='1mo')
                    
                    if not hist.empty:
                        successful_data[symbol] = {
                            'latest_price': float(hist['Close'].iloc[-1]),
                            'data_points': len(hist)
                        }
                        
                except Exception:
                    continue
            
            if successful_data:
                self.test_results['Free_Market_Data'] = {
                    'status': 'SUCCESS',
                    'successful_symbols': list(successful_data.keys()),
                    'data_summary': successful_data,
                    'message': f'Market data access successful for {len(successful_data)} indicators'
                }
                logger.info(f"✅ Free Market Data: SUCCESS ({len(successful_data)} indicators)")
                return True
            else:
                raise ValueError("No market data could be retrieved")
                
        except Exception as e:
            self.test_results['Free_Market_Data'] = {
                'status': 'FAILED',
                'error': str(e),
                'message': 'Free market data test failed'
            }
            logger.error(f"❌ Free Market Data: {e}")
            return False
    
    def run_all_free_tests(self) -> dict:
        """Run all free API tests"""
        logger.info("Starting comprehensive free API testing...")
        logger.info("=" * 60)
        
        # Test sequence
        tests = [
            ('Basic Connectivity', self.test_basic_connectivity),
            ('Treasury FiscalData API', self.test_treasury_fiscaldata_api),
            ('Yahoo Finance', self.test_yahoo_finance),
            ('Free Market Data Sources', self.test_free_market_data_sources),
            ('BEA API', self.test_bea_api),
            ('FRED API', self.test_fred_api),
        ]
        
        successful_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n--- Testing: {test_name} ---")
            if test_func():
                successful_tests += 1
            time.sleep(1)  # Courtesy delay between tests
        
        # Calculate critical test success count
        critical_tests = ['Basic Connectivity', 'Treasury FiscalData API', 'Yahoo Finance']
        critical_success = sum(1 for test_name, _ in tests 
                              if test_name in critical_tests 
                              and self.test_results.get(test_name.replace(' ', '_'), {}).get('status') == 'SUCCESS')
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 TEST SUMMARY")
        logger.info(f"Total tests: {successful_tests}/{total_tests}")
        logger.info(f"Critical tests (required): {critical_success}/{len(critical_tests)}")
        
        # Calculate readiness status
        if critical_success == len(critical_tests):
            readiness = "READY"
            logger.info("🎉 Status: READY FOR X-DATE PREDICTION")
        elif critical_success >= 2:
            readiness = "PARTIALLY_READY"
            logger.warning("⚠️  Status: PARTIALLY READY (some features may be limited)")
        else:
            readiness = "NOT_READY"
            logger.error("❌ Status: NOT READY (critical APIs failed)")
        
        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'critical_success': critical_success,
            'readiness': readiness,
            'test_results': self.test_results
        }
    
    def save_test_results(self, filename: str = None):
        """Save test results to file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"free_api_test_results_{timestamp}.json"
        
        # Ensure output directory exists
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"Test results saved to: {filepath}")
        return filepath
    
    def generate_setup_report(self) -> str:
        """Generate setup report"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
# X-Date Prediction Project - Free API Setup Report
Generated: {timestamp}

## Summary
This report validates the availability of free data sources for X-Date prediction,
providing a completely Bloomberg-free solution.

## Test Results

### Critical APIs (Required for Core Functionality)
"""
        
        critical_apis = ['Treasury_FiscalData', 'Yahoo_Finance', 'Basic_Connectivity']
        
        for api in critical_apis:
            result = self.test_results.get(api, {})
            status = result.get('status', 'NOT_TESTED')
            message = result.get('message', 'No information')
            
            if status == 'SUCCESS':
                icon = "✅"
            elif status == 'FAILED':
                icon = "❌"
            else:
                icon = "⚠️"
            
            report += f"\n{icon} **{api.replace('_', ' ')}**: {status}\n   {message}\n"
        
        report += "\n### Optional APIs (Enhanced Features)\n"
        
        optional_apis = ['BEA_API', 'FRED_API', 'Free_Market_Data']
        
        for api in optional_apis:
            result = self.test_results.get(api, {})
            status = result.get('status', 'NOT_TESTED')
            message = result.get('message', 'No information')
            
            if status == 'SUCCESS':
                icon = "✅"
            elif status == 'FAILED':
                icon = "❌"
            else:
                icon = "⚠️"
            
            report += f"\n{icon} **{api.replace('_', ' ')}**: {status}\n   {message}\n"
        
        # Add recommendations
        report += "\n## Recommendations\n"
        
        failed_critical = [api for api in critical_apis 
                          if self.test_results.get(api, {}).get('status') != 'SUCCESS']
        
        if not failed_critical:
            report += "\n✅ **All critical APIs are functional.** You can proceed with X-Date modeling using free data sources.\n"
        else:
            report += f"\n❌ **Critical API issues detected:** {', '.join(failed_critical)}\n"
            report += "   Please check your internet connection and try again.\n"
        
        # Add setup instructions for missing APIs
        missing_keys = []
        if self.test_results.get('BEA_API', {}).get('status') == 'SKIPPED':
            missing_keys.append('BEA_API_KEY')
        if self.test_results.get('FRED_API', {}).get('status') == 'SKIPPED':
            missing_keys.append('FRED_API_KEY')
        
        if missing_keys:
            report += f"\n### Optional API Setup\nTo enable enhanced features, obtain free API keys for:\n"
            for key in missing_keys:
                if 'BEA' in key:
                    report += f"- **{key}**: Register at https://apps.bea.gov/API/signup/\n"
                elif 'FRED' in key:
                    report += f"- **{key}**: Register at https://fred.stlouisfed.org/docs/api/api_key.html\n"
        
        report += f"\n## Next Steps\n"
        report += "1. Run treasury data collection: `python src/data_collection/treasury_data_collector.py`\n"
        report += "2. Generate cash flow forecasts: `python src/models/cash_flow_forecaster_v2.py`\n"
        report += "3. Predict X-Date: `python src/models/xdate_predictor.py`\n"
        
        return report


def main():
    """Main function"""
    logger.info("X-Date Prediction Project - Free API Testing")
    logger.info("=" * 60)
    
    # Ensure log directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Try to read API keys from environment variables
    logger.info("Loading API keys from environment variables...")
    
    bea_key = os.getenv('BEA_API_KEY')
    fred_key = os.getenv('FRED_API_KEY')
    
    if bea_key:
        logger.info("✅ BEA API key found")
    else:
        logger.warning("⚠️ BEA API key not found (optional)")
    
    if fred_key:
        logger.info("✅ FRED API key found")
    else:
        logger.warning("⚠️ FRED API key not found (optional)")
    
    # Run tests
    tester = FreeAPIConnectionTester()
    tester.load_api_keys()
    
    results = tester.run_all_free_tests()
    
    # Save results
    results_file = tester.save_test_results()
    
    # Generate report
    report = tester.generate_setup_report()
    
    # Save report
    report_file = Path("output") / "free_api_setup_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"Setup report saved to: {report_file}")
    
    # Output key recommendations
    if results['readiness'] == 'READY':
        logger.info("🎉 System is ready for X-Date prediction using free data sources!")
    elif results['readiness'] == 'PARTIALLY_READY':
        logger.warning("⚠️ System partially ready. Some advanced features may be limited.")
    else:
        logger.error("❌ System not ready. Please resolve critical API issues.")


if __name__ == "__main__":
    main() 