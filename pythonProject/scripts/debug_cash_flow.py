"""
调试现金流数据处理
检查数据加载和净现金流计算是否正确
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def debug_cash_flow_data():
    """调试现金流数据"""
    print("=== 调试现金流数据 ===")
    
    # 1. 加载原始数据
    cash_flow_file = Path("data/raw/daily_cash_flows_2023-06-29_to_2025-06-28.csv")
    cash_flows_raw = pd.read_csv(cash_flow_file)
    
    print(f"原始数据形状: {cash_flows_raw.shape}")
    print(f"原始数据列: {cash_flows_raw.columns.tolist()}")
    print(f"交易类型: {cash_flows_raw['transaction_type'].unique()}")
    
    # 2. 检查数据类型和转换
    cash_flows_raw['record_date'] = pd.to_datetime(cash_flows_raw['record_date'])
    cash_flows_raw['transaction_today_amt'] = pd.to_numeric(
        cash_flows_raw['transaction_today_amt'], errors='coerce'
    )
    
    print(f"\n数据期间: {cash_flows_raw['record_date'].min()} 到 {cash_flows_raw['record_date'].max()}")
    print(f"交易金额范围: {cash_flows_raw['transaction_today_amt'].min()} 到 {cash_flows_raw['transaction_today_amt'].max()}")
    
    # 3. 检查每种交易类型的统计
    print("\n=== 各交易类型统计 ===")
    for trans_type in cash_flows_raw['transaction_type'].unique():
        subset = cash_flows_raw[cash_flows_raw['transaction_type'] == trans_type]
        print(f"{trans_type}:")
        print(f"  记录数: {len(subset)}")
        print(f"  平均金额: ${subset['transaction_today_amt'].mean():,.0f}")
        print(f"  总金额: ${subset['transaction_today_amt'].sum():,.0f}")
    
    # 4. 转换为每日净现金流
    daily_flows = cash_flows_raw.pivot_table(
        index='record_date',
        columns='transaction_type',
        values='transaction_today_amt',
        aggfunc='sum'
    ).fillna(0)
    
    print(f"\n透视表形状: {daily_flows.shape}")
    print(f"透视表列: {daily_flows.columns.tolist()}")
    
    # 5. 计算净现金流
    if 'Deposits' in daily_flows.columns and 'Withdrawals' in daily_flows.columns:
        daily_flows['net_flow'] = daily_flows['Deposits'] - daily_flows['Withdrawals']
        
        print("\n=== 净现金流统计 ===")
        print(f"均值: ${daily_flows['net_flow'].mean():,.0f}")
        print(f"中位数: ${daily_flows['net_flow'].median():,.0f}")
        print(f"标准差: ${daily_flows['net_flow'].std():,.0f}")
        print(f"最小值: ${daily_flows['net_flow'].min():,.0f}")
        print(f"最大值: ${daily_flows['net_flow'].max():,.0f}")
        
        # 6. 检查正负值分布
        positive_days = (daily_flows['net_flow'] > 0).sum()
        negative_days = (daily_flows['net_flow'] < 0).sum()
        zero_days = (daily_flows['net_flow'] == 0).sum()
        
        print(f"\n=== 正负值分布 ===")
        print(f"正现金流天数: {positive_days} ({positive_days/len(daily_flows):.1%})")
        print(f"负现金流天数: {negative_days} ({negative_days/len(daily_flows):.1%})")
        print(f"零现金流天数: {zero_days} ({zero_days/len(daily_flows):.1%})")
        
        # 7. 显示前几个和后几个样本
        print(f"\n=== 前10个样本 ===")
        for i in range(min(10, len(daily_flows))):
            date = daily_flows.index[i]
            deposits = daily_flows['Deposits'].iloc[i]
            withdrawals = daily_flows['Withdrawals'].iloc[i]
            net = daily_flows['net_flow'].iloc[i]
            print(f"{date.date()}: 收入${deposits:,.0f}, 支出${withdrawals:,.0f}, 净值${net:,.0f}")
        
        print(f"\n=== 最后10个样本 ===")
        for i in range(max(0, len(daily_flows)-10), len(daily_flows)):
            date = daily_flows.index[i]
            deposits = daily_flows['Deposits'].iloc[i]
            withdrawals = daily_flows['Withdrawals'].iloc[i]
            net = daily_flows['net_flow'].iloc[i]
            print(f"{date.date()}: 收入${deposits:,.0f}, 支出${withdrawals:,.0f}, 净值${net:,.0f}")
        
        # 8. 创建简单可视化
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        
        # 净现金流时间序列
        axes[0].plot(daily_flows.index, daily_flows['net_flow'])
        axes[0].axhline(y=0, color='red', linestyle='--', alpha=0.7)
        axes[0].set_title('净现金流时间序列')
        axes[0].set_ylabel('净现金流 (百万美元)')
        axes[0].grid(True, alpha=0.3)
        
        # 净现金流分布
        axes[1].hist(daily_flows['net_flow'], bins=50, alpha=0.7, edgecolor='black')
        axes[1].axvline(x=0, color='red', linestyle='--', alpha=0.7)
        axes[1].set_title('净现金流分布')
        axes[1].set_xlabel('净现金流 (百万美元)')
        axes[1].set_ylabel('频数')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存图表
        output_dir = Path("output/figures")
        output_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_dir / "debug_cash_flow.png", dpi=300, bbox_inches='tight')
        print(f"\n调试图表已保存: {output_dir / 'debug_cash_flow.png'}")
        
        plt.show()
        
        return daily_flows
    else:
        print("错误: 未找到 Deposits 和 Withdrawals 列")
        return None

def debug_business_days_processing():
    """调试工作日处理"""
    print("\n=== 调试工作日处理 ===")
    
    # 加载并处理数据
    cash_flow_file = Path("data/raw/daily_cash_flows_2023-06-29_to_2025-06-28.csv")
    cash_flows_raw = pd.read_csv(cash_flow_file)
    cash_flows_raw['record_date'] = pd.to_datetime(cash_flows_raw['record_date'])
    cash_flows_raw['transaction_today_amt'] = pd.to_numeric(
        cash_flows_raw['transaction_today_amt'], errors='coerce'
    )
    
    # 转换为每日净现金流
    daily_flows = cash_flows_raw.pivot_table(
        index='record_date',
        columns='transaction_type',
        values='transaction_today_amt',
        aggfunc='sum'
    ).fillna(0)
    
    daily_flows['net_flow'] = daily_flows['Deposits'] - daily_flows['Withdrawals']
    
    print(f"原始数据天数: {len(daily_flows)}")
    print(f"原始数据期间: {daily_flows.index.min()} 到 {daily_flows.index.max()}")
    
    # 创建工作日序列
    start_date = daily_flows.index.min()
    end_date = daily_flows.index.max()
    business_days = pd.bdate_range(start=start_date, end=end_date)
    
    print(f"应有工作日数: {len(business_days)}")
    
    # 重新索引到工作日
    daily_flows_reindexed = daily_flows.reindex(business_days, method='ffill')
    daily_flows_reindexed = daily_flows_reindexed.fillna(0)
    
    print(f"重新索引后天数: {len(daily_flows_reindexed)}")
    print(f"重新索引后净现金流统计:")
    print(f"  均值: ${daily_flows_reindexed['net_flow'].mean():,.0f}")
    print(f"  中位数: ${daily_flows_reindexed['net_flow'].median():,.0f}")
    print(f"  标准差: ${daily_flows_reindexed['net_flow'].std():,.0f}")
    
    # 检查是否有很多零值
    zero_count = (daily_flows_reindexed['net_flow'] == 0).sum()
    print(f"  零值天数: {zero_count} ({zero_count/len(daily_flows_reindexed):.1%})")
    
    return daily_flows, daily_flows_reindexed

if __name__ == "__main__":
    # 运行调试
    daily_flows = debug_cash_flow_data()
    
    if daily_flows is not None:
        original, reindexed = debug_business_days_processing() 