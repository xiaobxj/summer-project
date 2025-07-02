"""
Free Alternatives to Bloomberg BLPAPI

This module provides multiple free data sources to replace Bloomberg BLPAPI for market data,
especially key indicators needed for X-Date prediction such as CDS spreads, Treasury yields, etc.
"""

import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Union
import time
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class MarketDataAlternatives:
    """Free alternatives to Bloomberg BLPAPI"""
    
    def __init__(self):
        self.fred_api_key = None
        self.av_api_key = None  # Alpha Vantage
        self.session = requests.Session()
        
    def set_api_keys(self, fred_key: str = None, av_key: str = None):
        """Set API keys"""
        self.fred_api_key = fred_key
        self.av_api_key = av_key
    
    # === US Treasury Data (Free alternatives to Bloomberg govt bonds) ===
    
    def get_treasury_yields_fred(self, series_ids: List[str] = None, 
                                start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        从FRED获取美国国债收益率数据
        替代Bloomberg的政府债券数据
        """
        if not self.fred_api_key:
            logger.warning("FRED API key not provided")
            return pd.DataFrame()
        
        # 默认获取关键期限的国债收益率
        if series_ids is None:
            series_ids = [
                'DGS3MO',   # 3个月国债
                'DGS6MO',   # 6个月国债  
                'DGS1',     # 1年国债
                'DGS2',     # 2年国债
                'DGS5',     # 5年国债
                'DGS10',    # 10年国债
                'DGS30'     # 30年国债
            ]
        
        all_data = {}
        
        for series_id in series_ids:
            try:
                url = "https://api.stlouisfed.org/fred/series/observations"
                params = {
                    'series_id': series_id,
                    'api_key': self.fred_api_key,
                    'file_type': 'json',
                    'start_date': start_date or '2020-01-01',
                    'end_date': end_date or datetime.now().strftime('%Y-%m-%d')
                }
                
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if 'observations' in data:
                    df = pd.DataFrame(data['observations'])
                    df['date'] = pd.to_datetime(df['date'])
                    df['value'] = pd.to_numeric(df['value'], errors='coerce')
                    df = df[['date', 'value']].rename(columns={'value': series_id})
                    df = df.set_index('date')
                    
                    all_data[series_id] = df[series_id]
                    
                time.sleep(0.1)  # API礼貌延迟
                
            except Exception as e:
                logger.error(f"Error fetching {series_id}: {e}")
        
        if all_data:
            combined_df = pd.DataFrame(all_data)
            combined_df.index.name = 'date'
            return combined_df
        
        return pd.DataFrame()
    
    def get_treasury_bills_yahoo(self, symbols: List[str] = None) -> pd.DataFrame:
        """
        从Yahoo Finance获取美国短期国债数据
        """
        if symbols is None:
            symbols = [
                '^IRX',    # 13周国债
                '^FVX',    # 5年国债期货
                '^TNX',    # 10年国债
                '^TYX'     # 30年国债
            ]
        
        try:
            data = yf.download(symbols, period='1y', interval='1d')
            if 'Close' in data.columns:
                return data['Close']
            return data
        except Exception as e:
            logger.error(f"Error fetching treasury data from Yahoo: {e}")
            return pd.DataFrame()
    
    # === Credit Default Swap (CDS) Alternatives ===
    
    def get_credit_risk_indicators(self) -> Dict[str, pd.DataFrame]:
        """
        获取信用风险指标（CDS的替代指标）
        使用VIX、高收益债券利差等作为代理
        """
        indicators = {}
        
        try:
            # VIX - 市场恐慌指数
            vix = yf.download('^VIX', period='1y', interval='1d')
            if not vix.empty:
                indicators['VIX'] = vix['Close']
            
            # 高收益债券ETF (HYG) vs 国债ETF (TLT) 利差
            hyg = yf.download('HYG', period='1y', interval='1d')
            tlt = yf.download('TLT', period='1y', interval='1d')
            
            if not hyg.empty and not tlt.empty:
                # 计算收益率利差（简化版）
                hyg_yield = hyg['Close'].pct_change().rolling(30).std() * 100
                tlt_yield = tlt['Close'].pct_change().rolling(30).std() * 100
                spread = hyg_yield - tlt_yield
                indicators['HY_Treasury_Spread'] = spread
            
            # 美元指数 (DXY) - 影响主权风险感知
            dxy = yf.download('DX-Y.NYB', period='1y', interval='1d')
            if not dxy.empty:
                indicators['USD_Index'] = dxy['Close']
                
            logger.info(f"Successfully fetched {len(indicators)} credit risk indicators")
            
        except Exception as e:
            logger.error(f"Error fetching credit risk indicators: {e}")
        
        return indicators
    
    # === Economic Sentiment and News Analysis ===
    
    def get_market_sentiment_indicators(self) -> Dict[str, pd.DataFrame]:
        """
        获取市场情绪指标
        """
        sentiment_data = {}
        
        try:
            # CBOE VIX - 恐慌指数
            vix = yf.download('^VIX', period='6mo', interval='1d')
            if not vix.empty:
                sentiment_data['VIX'] = vix['Close']
            
            # 美股主要指数（反映整体市场情绪）
            indices = {
                'SPY': 'S&P500_ETF',
                'QQQ': 'NASDAQ_ETF', 
                'IWM': 'Russell2000_ETF'
            }
            
            for symbol, name in indices.items():
                data = yf.download(symbol, period='6mo', interval='1d')
                if not data.empty:
                    # 计算收益率
                    returns = data['Close'].pct_change()
                    sentiment_data[f'{name}_Returns'] = returns
            
            # 债券ETF（避险情绪指标）
            bond_etfs = ['TLT', 'IEF', 'SHY']  # 长期、中期、短期债券ETF
            for etf in bond_etfs:
                data = yf.download(etf, period='6mo', interval='1d')
                if not data.empty:
                    sentiment_data[f'{etf}_Price'] = data['Close']
            
        except Exception as e:
            logger.error(f"Error fetching sentiment indicators: {e}")
        
        return sentiment_data
    
    # === Alternative Economic Data Sources ===
    
    def get_economic_indicators_alpha_vantage(self, indicators: List[str] = None) -> Dict[str, pd.DataFrame]:
        """
        从Alpha Vantage获取经济指标（免费版有限制）
        """
        if not self.av_api_key:
            logger.warning("Alpha Vantage API key not provided")
            return {}
        
        if indicators is None:
            indicators = [
                'REAL_GDP',
                'UNEMPLOYMENT', 
                'CPI',
                'FEDERAL_FUNDS_RATE'
            ]
        
        results = {}
        
        for indicator in indicators:
            try:
                url = "https://www.alphavantage.co/query"
                params = {
                    'function': indicator,
                    'apikey': self.av_api_key,
                    'datatype': 'json'
                }
                
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Alpha Vantage的数据格式需要解析
                if 'data' in data:
                    df = pd.DataFrame(data['data'])
                    if not df.empty:
                        df['date'] = pd.to_datetime(df['date'])
                        df = df.set_index('date')
                        results[indicator] = df
                
                time.sleep(12)  # 免费版限制：每分钟5次请求
                
            except Exception as e:
                logger.error(f"Error fetching {indicator} from Alpha Vantage: {e}")
        
        return results
    
    # === News Sentiment Analysis (Free Sources) ===
    
    def get_financial_news_sentiment(self, keywords: List[str] = None) -> Dict[str, float]:
        """
        获取财经新闻情绪分析
        使用免费的新闻API（需要扩展到实际的新闻源）
        """
        if keywords is None:
            keywords = ['debt ceiling', 'fiscal crisis', 'treasury', 'government shutdown']
        
        # 这里可以集成免费的新闻API
        # 例如: NewsAPI, Reddit API, Twitter API等
        
        # 示例返回格式
        sentiment_scores = {}
        for keyword in keywords:
            # 实际实现需要调用新闻API和NLP处理
            sentiment_scores[keyword] = 0.0  # 占位符
        
        logger.info("News sentiment analysis placeholder - needs implementation")
        return sentiment_scores
    
    # === Comprehensive Data Collection Method ===
    
    def collect_all_alternative_data(self, start_date: str = None, end_date: str = None) -> Dict[str, pd.DataFrame]:
        """
        收集所有替代数据源的数据
        """
        logger.info("Starting comprehensive alternative data collection...")
        
        all_data = {}
        
        # 1. 国债收益率 (FRED)
        if self.fred_api_key:
            treasury_yields = self.get_treasury_yields_fred(start_date=start_date, end_date=end_date)
            if not treasury_yields.empty:
                all_data['treasury_yields_fred'] = treasury_yields
        
        # 2. 国债数据 (Yahoo Finance)
        treasury_yahoo = self.get_treasury_bills_yahoo()
        if not treasury_yahoo.empty:
            all_data['treasury_yahoo'] = treasury_yahoo
        
        # 3. 信用风险指标
        credit_indicators = self.get_credit_risk_indicators()
        all_data.update({f'credit_{k}': v for k, v in credit_indicators.items()})
        
        # 4. 市场情绪指标
        sentiment_indicators = self.get_market_sentiment_indicators()
        all_data.update({f'sentiment_{k}': v for k, v in sentiment_indicators.items()})
        
        # 5. 经济指标 (Alpha Vantage)
        if self.av_api_key:
            econ_indicators = self.get_economic_indicators_alpha_vantage()
            all_data.update({f'econ_{k}': v for k, v in econ_indicators.items()})
        
        logger.info(f"Collected data from {len(all_data)} alternative sources")
        return all_data
    
    # === Data Quality and Validation ===
    
    def validate_data_quality(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
        """
        验证数据质量
        """
        quality_report = {}
        
        for source, df in data.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                quality_report[source] = {
                    'rows': len(df),
                    'columns': len(df.columns) if hasattr(df, 'columns') else 1,
                    'missing_values': df.isnull().sum().sum() if hasattr(df, 'isnull') else 0,
                    'date_range': f"{df.index.min()} to {df.index.max()}" if hasattr(df.index, 'min') else "N/A",
                    'status': 'OK'
                }
            else:
                quality_report[source] = {
                    'status': 'FAILED',
                    'error': 'Empty or invalid data'
                }
        
        return quality_report


def main():
    """测试替代数据源"""
    # 创建实例
    alt_data = MarketDataAlternatives()
    
    # 设置API密钥（从环境变量获取）
    import os
    alt_data.set_api_keys(
        fred_key=os.getenv('FRED_API_KEY'),
        av_key=os.getenv('ALPHA_VANTAGE_API_KEY')
    )
    
    # 收集数据
    all_data = alt_data.collect_all_alternative_data(
        start_date='2023-01-01',
        end_date='2024-12-31'
    )
    
    # 验证数据质量
    quality_report = alt_data.validate_data_quality(all_data)
    
    # 打印报告
    print("\n=== Alternative Data Collection Report ===")
    for source, report in quality_report.items():
        print(f"\n{source}: {report['status']}")
        if report['status'] == 'OK':
            print(f"  Rows: {report['rows']}")
            print(f"  Date Range: {report['date_range']}")
        else:
            print(f"  Error: {report.get('error', 'Unknown')}")
    
    return all_data


if __name__ == "__main__":
    main() 