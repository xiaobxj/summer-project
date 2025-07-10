"""
Enhanced Treasury Data Collector - Extended DTS Data Collection
整合用户提供的详细Treasury API数据收集功能
结合现有系统的改进版本

基于原有treasury_data_collector.py扩展，增加更详细的现金流分析数据
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
import time
import logging
from typing import Dict, Optional, Any, List
import numpy as np


class EnhancedTreasuryCollector:
    """增强版Treasury数据收集器 - 包含详细的DTS分类数据"""
    
    def __init__(self, data_dir: str = "./data/raw"):
        """
        初始化收集器
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # API基础URL
        self.base_url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
        
        # 请求头设置
        self.headers = {
            'User-Agent': 'Enhanced-Treasury-Collector/2.0 (Research)',
            'Accept': 'application/json'
        }
        
        # API限速
        self.request_delay = 0.5
        
        # 详细数据端点配置
        self.detailed_endpoints = {
            'operating_cash_balance': 'v1/accounting/dts/operating_cash_balance',
            'deposits_withdrawals_operating_cash': 'v1/accounting/dts/deposits_withdrawals_operating_cash',
            'public_debt_transactions': 'v1/accounting/dts/public_debt_transactions',
            'adjustment_public_debt_transactions_cash_basis': 'v1/accounting/dts/adjustment_public_debt_transactions_cash_basis',
            'debt_subject_to_limit': 'v1/accounting/dts/debt_subject_to_limit',
            'inter_agency_tax_transfers': 'v1/accounting/dts/inter_agency_tax_transfers',
            'income_tax_refunds_issued': 'v1/accounting/dts/income_tax_refunds_issued',
            'federal_tax_deposits': 'v1/accounting/dts/federal_tax_deposits',
            'short_term_cash_investments': 'v1/accounting/dts/short_term_cash_investments'
        }
        
        # 交易分类映射
        self.category_mapping = self._get_transaction_categories()
    
    def _get_transaction_categories(self) -> Dict[str, str]:
        """获取交易分类映射"""
        return {
            # Social Security & Retirement
            'SSA - Benefits Payments': 'Social Security & Retirement',
            'SSA - Supplemental Security Income': 'Social Security & Retirement',
            'Social Security Admin (SSA) - misc': 'Social Security & Retirement',
            'RRB - Benefit Payments': 'Social Security & Retirement',
            'Railroad Retirement Board (RRB) - misc': 'Social Security & Retirement',
            'RRB - Natl Railroad Retirement Inv Trust': 'Social Security & Retirement',
            'RRB - Unemployment Insurance': 'Social Security & Retirement',
            'OPM - Civil Serv Retirement & Disability': 'Social Security & Retirement',
            'OPM - Federal Employee Insurance Payment': 'Social Security & Retirement',
            'Federal Retirement Thrift Savings Plan': 'Social Security & Retirement',
            'DoD - Military Retirement': 'Social Security & Retirement',

            # Healthcare & Medicare/Medicaid
            'HHS - Grants to States for Medicaid': 'Healthcare & Medicare/Medicaid',
            'HHS - Federal Hospital Insr Trust Fund': 'Healthcare & Medicare/Medicaid',
            'HHS - Federal Supple Med Insr Trust Fund': 'Healthcare & Medicare/Medicaid',
            'HHS - Medicare Prescription Drugs': 'Healthcare & Medicare/Medicaid',
            'HHS - Marketplace Payments': 'Healthcare & Medicare/Medicaid',
            'HHS - Medicare Premiums': 'Healthcare & Medicare/Medicaid',
            'HHS - Misc': 'Healthcare & Medicare/Medicaid',
            'HHS - Other Public Health Services': 'Healthcare & Medicare/Medicaid',
            'HHS - Othr Cent Medicare & Medicaid Serv': 'Healthcare & Medicare/Medicaid',
            'HHS - Health Resources & Services Admin': 'Healthcare & Medicare/Medicaid',
            'HHS - Indian Health Service': 'Healthcare & Medicare/Medicaid',
            'HHS - Centers for Disease Control (CDC)': 'Healthcare & Medicare/Medicaid',
            'DoD - Health': 'Healthcare & Medicare/Medicaid',

            # Defense & Security
            'Dept of Defense (DoD)': 'Defense & Security',
            'Dept of Defense (DoD) - misc': 'Defense & Security',
            'DoD - Military Active Duty Pay': 'Defense & Security',
            'DHS - Customs & Border Protection (CBP)': 'Defense & Security',
            'DHS - Customs and Certain Excise Taxes': 'Defense & Security',
            'DHS - Fed Emergency Mgmt Agency (FEMA)': 'Defense & Security',
            'DHS - Transportation Security Admn (TSA)': 'Defense & Security',
            'IAP - Foreign Military Sales': 'Defense & Security',
            'US Army Corps of Engineers': 'Defense & Security',
            'Defense Vendor Payments (EFT)': 'Defense & Security',

            # Federal Salaries & Operating Expenses
            'Federal Salaries (EFT)': 'Federal Salaries & Ops',
            'Dept of Agriculture (USDA) - misc': 'Federal Salaries & Ops',
            'Dept of Commerce (DOC)': 'Federal Salaries & Ops',
            'Dept of Education (ED)': 'Federal Salaries & Ops',
            'Dept of Energy (DOE)': 'Federal Salaries & Ops',
            'Dept of Interior (DOI) - misc': 'Federal Salaries & Ops',
            'Dept of Labor (DOL) - misc': 'Federal Salaries & Ops',
            'Dept of State (DOS)': 'Federal Salaries & Ops',
            'Dept of Transportation (DOT)': 'Federal Salaries & Ops',
            'Dept of Transportation (DOT) - Misc': 'Federal Salaries & Ops',
            'Dept of Veterans Affairs (VA)': 'Federal Salaries & Ops',
            'VA - Benefits': 'Federal Salaries & Ops',
            'Environmental Protection Agency (EPA)': 'Federal Salaries & Ops',
            'General Services Administration (GSA)': 'Federal Salaries & Ops',
            'Independent Agencies - misc': 'Federal Salaries & Ops',
            'Judicial Branch - Courts': 'Federal Salaries & Ops',
            'Justice Department programs': 'Federal Salaries & Ops',
            'Dept of Justice (DOJ)': 'Federal Salaries & Ops',
            'Legislative Branch - misc': 'Federal Salaries & Ops',
            'Legislative Branch - Library of Congress': 'Federal Salaries & Ops',
            'NASA': 'Federal Salaries & Ops',
            'National Science Foundation (NSF)': 'Federal Salaries & Ops',
            'Securities and Exchange Commission (SEC)': 'Federal Salaries & Ops',
            'Small Business Administration (SBA)': 'Federal Salaries & Ops',
            'Postal Service': 'Federal Salaries & Ops',
            'United States Postal Service (USPS)': 'Federal Salaries & Ops',
            'Other Withdrawals': 'Federal Salaries & Ops',
            'Unclassified': 'Federal Salaries & Ops',

            # Housing & Community Support
            'Housing and Urban Development programs': 'Housing & Community',
            'Dept of Housing & Urban Dev (HUD) - misc': 'Housing & Community',
            'HUD - Federal Housing Admin (FHA)': 'Housing & Community',
            'Emergency Rental Assistance': 'Housing & Community',
            'TREAS - Troubled Asset Relief Pro (TARP)': 'Housing & Community',

            # Tax Refunds & Credits
            'IRS Tax Refunds Individual (EFT)': 'Tax Refunds & Credits',
            'IRS Tax Refunds Business (EFT)': 'Tax Refunds & Credits',
            'IRS - Economic Impact Payments (EFT)': 'Tax Refunds & Credits',
            'IRS - Advanced Child Tax Credit (EFT)': 'Tax Refunds & Credits',
            'Taxes - Business Tax Refunds (EFT)': 'Tax Refunds & Credits',
            'Taxes - Individual Tax Refunds (EFT)': 'Tax Refunds & Credits',
            'TREAS - IRS Refunds for Puerto Rico': 'Tax Refunds & Credits',

            # Agriculture & Food Support
            'USDA - Commodity Credit Corporation': 'Agriculture & Food',
            'USDA - Federal Crop Insurance Corp Fund': 'Agriculture & Food',
            'USDA - Loan Payments': 'Agriculture & Food',
            'USDA - Loan Repayments': 'Agriculture & Food',
            'USDA - Other Farm Service': 'Agriculture & Food',
            'USDA - Child Nutrition': 'Agriculture & Food',
            'USDA - Supp Nutrition Assist Prog (SNAP)': 'Agriculture & Food',
            'USDA - Supp Nutrition Assist Prog (WIC)': 'Agriculture & Food',

            # International Programs
            "Int'l Assistance Programs (IAP) - misc": 'International Programs',
            "IAP - Agency for Int'l Development (AID)": 'International Programs',
            "IAP - US Int'l Devlop Finance Corp (DFC)": 'International Programs',
            'IAP - Multilateral Assistance': 'International Programs',
            'International Monetary Fund (IMF)': 'International Programs',

            # Interest Payments
            'Interest on Treasury Securities': 'Interest Payments',

            # Financial & Special Programs
            'Federal Deposit Insurance Corp (FDIC)': 'Financial & Special',
            'Federal Communications Commission (FCC)': 'Financial & Special',
            'FCC - Universal Service Fund': 'Financial & Special',
            'Export-Import Bank': 'Financial & Special',
            'Farm Credit System Insurance Cor (FCSIC)': 'Financial & Special',
            'National Credit Union Admin (NCUA)': 'Financial & Special',
            'Federal Reserve Earnings': 'Financial & Special',
            'General Services Administration (GSA)': 'Financial & Special',
            'Emergency Capital Investment Program': 'Financial & Special',
            'ESF - Economic Recovery Programs': 'Financial & Special',
            'TREAS - Federal Financing Bank': 'Financial & Special',
            'TREAS - Comptroller of the Currency': 'Financial & Special',
            'TREAS - United States Mint': 'Financial & Special',
            'TREAS - Bureau of Engraving and Printing': 'Financial & Special',
            'TREAS - Claims Judgments and Relief Acts': 'Financial & Special',
            'TREAS - Pmt to Resolution Funding Corp': 'Financial & Special',
            'Public Debt Cash Redemp. (Table III-B)': 'Financial & Special',
            'Public Debt Cash Redemp. (Table IIIB)': 'Financial & Special',
            'Public Debt Cash Issues (Table III-B)': 'Financial & Special',
            'Public Debt Cash Issues (Table IIIB)': 'Financial & Special',
            'TREAS - GSE Proceeds': 'Financial & Special',

            # Other
            'Other Deposits': 'Other',
            'Unclassified - Deposits': 'Other',
            'Change in Balance of Uncollected Funds': 'Other',
            'Transfers to Depositaries': 'Other',
            'Transfers from Depositaries': 'Other',
            'Sub-Total Deposits': 'Other',
            'Sub-Total Withdrawals': 'Other',
        }
    
    def _make_paginated_request(self, endpoint: str, params: Dict[str, Any] = None) -> pd.DataFrame:
        """
        发送分页API请求并获取所有数据
        
        Args:
            endpoint: API端点
            params: 请求参数
            
        Returns:
            完整数据的DataFrame
        """
        if params is None:
            params = {}
        
        # 设置分页参数
        params.setdefault('page[size]', 1000)
        
        all_data = []
        page_number = 1
        
        while True:
            params["page[number]"] = page_number
            
            try:
                url = f"{self.base_url}/{endpoint}"
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                records = data.get("data", [])
                
                if not records:
                    break
                
                all_data.extend(records)
                
                # 检查是否有下一页
                if data.get("links", {}).get("next"):
                    page_number += 1
                else:
                    break
                
                # 添加延迟避免限速
                time.sleep(self.request_delay)
                
            except requests.exceptions.RequestException as e:
                logging.error(f"API请求失败: {e}")
                break
        
        return pd.DataFrame(all_data)
    
    def collect_detailed_cash_flows(self, start_date: str = None, end_date: str = None) -> Dict[str, pd.DataFrame]:
        """
        收集详细的现金流数据 - 核心功能
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            包含所有详细现金流数据的字典
        """
        logging.info("开始收集详细Treasury现金流数据...")
        
        # 设置默认日期范围
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        
        collected_data = {}
        
        for data_name, endpoint in self.detailed_endpoints.items():
            logging.info(f"收集 {data_name} 数据...")
            
            try:
                # 设置日期过滤参数
                params = {}
                if 'record_date' in endpoint or 'dts' in endpoint:
                    params['filter'] = f'record_date:gte:{start_date},record_date:lte:{end_date}'
                    params['sort'] = 'record_date'
                
                # 获取数据
                df = self._make_paginated_request(endpoint, params)
                
                if not df.empty:
                    # 转换数值列
                    for col in df.columns:
                        if 'amt' in col or 'bal' in col:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # 保存到文件
                    filename = f"{data_name}.csv"
                    filepath = self.data_dir / filename
                    df.to_csv(filepath, index=False)
                    
                    collected_data[data_name] = df
                    logging.info(f"✅ {data_name}: {len(df)} 行数据已保存")
                else:
                    logging.warning(f"❌ {data_name}: 未获取到数据")
                    
            except Exception as e:
                logging.error(f"❌ {data_name} 数据收集失败: {e}")
        
        return collected_data
    
    def analyze_tga_balance(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """分析Treasury General Account余额"""
        if 'operating_cash_balance' not in data:
            return pd.DataFrame()
        
        df = data['operating_cash_balance'].copy()
        
        # 筛选TGA余额数据
        tga_df = df[
            df['account_type'] == 'Treasury General Account (TGA) Closing Balance'
        ].copy()
        
        if tga_df.empty:
            return pd.DataFrame()
        
        # 数据处理
        tga_df['record_date'] = pd.to_datetime(tga_df['record_date'])
        tga_df['tga_balance'] = pd.to_numeric(tga_df['open_today_bal'], errors='coerce')
        tga_df = tga_df.sort_values('record_date')
        
        return tga_df[['record_date', 'tga_balance']].copy()
    
    def categorize_cash_flows(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """对现金流进行分类处理"""
        result = {}
        
        if 'deposits_withdrawals_operating_cash' in data:
            df = data['deposits_withdrawals_operating_cash'].copy()
            
            # 分离存款和提款
            deposits_df = df[
                (df['account_type'] == 'Treasury General Account (TGA)') &
                (df['transaction_type'] == 'Deposits')
            ].copy()
            
            withdrawals_df = df[
                (df['account_type'] == 'Treasury General Account (TGA)') &
                (df['transaction_type'] == 'Withdrawals')
            ].copy()
            
            # 添加分类
            for df_subset, name in [(deposits_df, 'deposits'), (withdrawals_df, 'withdrawals')]:
                if not df_subset.empty:
                    df_subset['transaction_group'] = df_subset['transaction_catg'].map(
                        self.category_mapping
                    ).fillna('Other')
                    result[name] = df_subset
        
        return result
    
    def collect_all_enhanced_data(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        收集所有增强Treasury数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            包含所有数据和分析结果的字典
        """
        logging.info("开始增强Treasury数据收集和分析...")
        
        # 收集原始数据
        raw_data = self.collect_detailed_cash_flows(start_date, end_date)
        
        # 分析TGA余额
        tga_balance = self.analyze_tga_balance(raw_data)
        
        # 分类现金流
        categorized_flows = self.categorize_cash_flows(raw_data)
        
        # 保存收集摘要
        summary = {
            'collection_timestamp': datetime.now().isoformat(),
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'datasets_collected': list(raw_data.keys()),
            'tga_balance_records': len(tga_balance),
            'categorized_flows': list(categorized_flows.keys()),
            'category_mapping_size': len(self.category_mapping)
        }
        
        # 保存摘要
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_file = self.data_dir / f"enhanced_treasury_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return {
            'raw_data': raw_data,
            'tga_balance': tga_balance,
            'categorized_flows': categorized_flows,
            'summary': summary
        }


def main():
    """主函数 - 演示增强Treasury数据收集器的使用"""
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 创建收集器
    collector = EnhancedTreasuryCollector()
    
    # 设置日期范围（最近2年数据）
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    
    print(f"🚀 开始增强Treasury数据收集...")
    print(f"📅 日期范围: {start_date} 到 {end_date}")
    print("=" * 60)
    
    # 收集所有数据
    all_data = collector.collect_all_enhanced_data(start_date, end_date)
    
    # 显示收集结果
    print("\n✅ 数据收集完成!")
    print("=" * 60)
    
    raw_data = all_data['raw_data']
    for name, df in raw_data.items():
        if isinstance(df, pd.DataFrame) and not df.empty:
            print(f"📊 {name}: {len(df)} 行数据")
        else:
            print(f"❌ {name}: 无数据")
    
    tga_balance = all_data['tga_balance']
    if not tga_balance.empty:
        print(f"💰 TGA余额记录: {len(tga_balance)} 条")
    
    categorized_flows = all_data['categorized_flows']
    print(f"🏷️  分类现金流: {list(categorized_flows.keys())}")
    
    print(f"\n📁 所有数据已保存到: {collector.data_dir}")


if __name__ == "__main__":
    main() 