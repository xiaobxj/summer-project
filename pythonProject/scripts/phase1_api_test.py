"""
Phase 1: API Access Testing and Resource Verification

This script tests the connectivity of various data APIs to prepare for project data acquisition.
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/api_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class APITester:
    """API connection testing class"""
    
    def __init__(self):
        self.results = {}
        self.treasury_base_url = "https://api.fiscaldata.treasury.gov/services/api/v1"
        self.bea_base_url = "https://apps.bea.gov/api/data"
        self.fred_base_url = "https://api.stlouisfed.org/fred"
        
    def test_treasury_fiscal_data_api(self) -> Tuple[bool, str]:
        """Test Treasury FiscalData API connection"""
        try:
            # Test DTS data access
            endpoint = f"{self.treasury_base_url}/accounting/dts/dts_table_1"
            params = {
                'filter': 'record_date:gte:2024-01-01',
                'page[size]': '5',
                'sort': '-record_date'
            }
            
            response = requests.get(endpoint, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    logger.info(f"✓ Treasury FiscalData API: Connected successfully")
                    logger.info(f"  Latest record date: {data['data'][0].get('record_date', 'N/A')}")
                    return True, "Success"
                else:
                    return False, "No data returned"
            else:
                return False, f"HTTP {response.status_code}: {response.text[:200]}"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def test_bea_api(self, api_key: str = None) -> Tuple[bool, str]:
        """Test BEA API connection"""
        if not api_key:
            return False, "API key required but not provided"
        
        try:
            endpoint = f"{self.bea_base_url}"
            params = {
                'UserID': api_key,
                'method': 'GetParameterList',
                'datasetname': 'NIPA',
                'ResultFormat': 'JSON'
            }
            
            response = requests.get(endpoint, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'BEAAPI' in data and 'Results' in data['BEAAPI']:
                    logger.info("✓ BEA API: Connected successfully")
                    return True, "Success"
                else:
                    return False, "Unexpected response format"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def test_fred_api(self, api_key: str = None) -> Tuple[bool, str]:
        """Test FRED API connection"""
        if not api_key:
            return False, "API key required but not provided"
        
        try:
            endpoint = f"{self.fred_base_url}/series/observations"
            params = {
                'series_id': 'GDP',
                'api_key': api_key,
                'file_type': 'json',
                'limit': '1',
                'sort_order': 'desc'
            }
            
            response = requests.get(endpoint, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'observations' in data and len(data['observations']) > 0:
                    logger.info("✓ FRED API: Connected successfully")
                    return True, "Success"
                else:
                    return False, "No data returned"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def test_bloomberg_api(self) -> Tuple[bool, str]:
        """Test Bloomberg API connection (environment check only)"""
        try:
            # Try to import Bloomberg API module
            import blpapi
            logger.info("✓ Bloomberg API: Module available")
            
            # Check connection settings
            session_options = blpapi.SessionOptions()
            session_options.setServerHost("localhost")
            session_options.setServerPort(8194)
            
            # Note: Don't actually create connection here as it requires Bloomberg Terminal
            return True, "Module available (connection requires Bloomberg Terminal/Server)"
            
        except ImportError:
            return False, "Bloomberg API module not installed"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def test_general_connectivity(self) -> Tuple[bool, str]:
        """Test basic network connectivity"""
        try:
            # Test basic internet connection
            response = requests.get("https://httpbin.org/get", timeout=10)
            if response.status_code == 200:
                return True, "Internet connectivity OK"
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def run_all_tests(self, bea_api_key: str = None, fred_api_key: str = None) -> Dict[str, Any]:
        """Run all API tests"""
        logger.info("=== Phase 1: API Connectivity Testing ===")
        logger.info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        tests = [
            ("General Connectivity", self.test_general_connectivity),
            ("Treasury FiscalData API", self.test_treasury_fiscal_data_api),
            ("BEA API", lambda: self.test_bea_api(bea_api_key)),
            ("FRED API", lambda: self.test_fred_api(fred_api_key)),
            ("Bloomberg API", self.test_bloomberg_api)
        ]
        
        results = {}
        for test_name, test_func in tests:
            logger.info(f"\nTesting: {test_name}")
            try:
                success, message = test_func()
                results[test_name] = {
                    'success': success,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                }
                
                status = "✓ PASS" if success else "✗ FAIL"
                logger.info(f"{status}: {message}")
                
            except Exception as e:
                results[test_name] = {
                    'success': False,
                    'message': f"Test failed with exception: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                }
                logger.error(f"✗ FAIL: Test failed with exception: {str(e)}")
        
        return results


def save_test_results(results: Dict[str, Any], filename: str = "api_test_results.json"):
    """Save test results to file"""
    output_path = f"./output/{filename}"
    
    # Ensure output directory exists
    os.makedirs("./output", exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Test results saved to: {output_path}")


def generate_setup_report(results: Dict[str, Any]) -> str:
    """Generate setup report"""
    
    success_count = sum(1 for result in results.values() if result['success'])
    total_count = len(results)
    
    report = f"""
# Phase 1 API Testing Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
Successfully connected to {success_count}/{total_count} data sources.

## Test Results

"""
    
    for test_name, result in results.items():
        status = "✓ PASS" if result['success'] else "✗ FAIL"
        report += f"### {test_name}\n"
        report += f"Status: {status}\n"
        report += f"Message: {result['message']}\n"
        report += f"Timestamp: {result['timestamp']}\n\n"
    
    # Add recommendations
    report += "## Recommendations\n\n"
    
    if results.get('Treasury FiscalData API', {}).get('success'):
        report += "✓ **Treasury FiscalData API**: Ready for cash flow data collection.\n\n"
    else:
        report += "⚠️ **Treasury FiscalData API**: Failed. This is critical for X-Date prediction.\n\n"
    
    if results.get('BEA API', {}).get('success'):
        report += "✓ **BEA API**: Ready for economic indicators.\n\n"
    else:
        report += "⚠️ **BEA API**: Not available. Consider obtaining free API key from https://apps.bea.gov/API/signup/\n\n"
    
    if results.get('FRED API', {}).get('success'):
        report += "✓ **FRED API**: Ready for Federal Reserve economic data.\n\n"
    else:
        report += "⚠️ **FRED API**: Not available. Consider obtaining free API key from https://fred.stlouisfed.org/\n\n"
    
    if results.get('Bloomberg API', {}).get('success'):
        report += "✓ **Bloomberg API**: Available for premium market data.\n\n"
    else:
        report += "ℹ️ **Bloomberg API**: Not available. This is optional for enhanced market analysis.\n\n"
    
    return report


def main():
    """Main function"""
    logger.info("X-Date Prediction Project - Phase 1 API Testing")
    
    # Ensure log directory exists
    os.makedirs("./logs", exist_ok=True)
    
    # Try to read API keys from environment variables
    bea_api_key = os.getenv('BEA_API_KEY')
    fred_api_key = os.getenv('FRED_API_KEY')
    
    logger.info(f"BEA API Key: {'✓ Found' if bea_api_key else '✗ Not found'}")
    logger.info(f"FRED API Key: {'✓ Found' if fred_api_key else '✗ Not found'}")
    
    # Run tests
    tester = APITester()
    results = tester.run_all_tests(bea_api_key, fred_api_key)
    
    # Save results
    save_test_results(results)
    
    # Generate report
    report = generate_setup_report(results)
    
    # Save report
    with open("./output/phase1_setup_report.txt", 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info("Phase 1 testing completed. Check ./output/ for detailed results.")


if __name__ == "__main__":
    main() 