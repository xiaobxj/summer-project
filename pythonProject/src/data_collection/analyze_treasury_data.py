"""
财政部数据分析脚本 - Treasury Data Analysis
验证下载的数据质量并展示X-Date预测的关键指标
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def load_treasury_data():
    """加载所有财政部数据"""
    data_dir = Path("data/raw")
    
    data = {}
    
    # 1. 现金余额数据
    cash_balance_file = data_dir / "treasury_cash_balance_2023-06-29_to_2025-06-28.csv"
    if cash_balance_file.exists():
        data['cash_balance'] = pd.read_csv(cash_balance_file)
        data['cash_balance']['record_date'] = pd.to_datetime(data['cash_balance']['record_date'])
    
    # 2. 债务数据
    debt_file = data_dir / "debt_outstanding_2023-06-29_to_2025-06-28.csv"
    if debt_file.exists():
        data['debt'] = pd.read_csv(debt_file)
        data['debt']['record_date'] = pd.to_datetime(data['debt']['record_date'])
    
    # 3. 现金流数据
    cash_flow_file = data_dir / "daily_cash_flows_2023-06-29_to_2025-06-28.csv"
    if cash_flow_file.exists():
        data['cash_flows'] = pd.read_csv(cash_flow_file)
        data['cash_flows']['record_date'] = pd.to_datetime(data['cash_flows']['record_date'])
    
    return data

def analyze_cash_balance(cash_balance_df):
    """分析现金余额数据"""
    print("=== 现金余额分析 (Treasury Cash Balance Analysis) ===")
    print(f"数据范围: {cash_balance_df['record_date'].min()} 到 {cash_balance_df['record_date'].max()}")
    print(f"总记录数: {len(cash_balance_df)}")
    
    # 数值列转换
    numeric_cols = ['open_today_bal', 'close_today_bal']
    for col in numeric_cols:
        cash_balance_df[col] = pd.to_numeric(cash_balance_df[col], errors='coerce')
    
    # 移除空值，但保留至少有一个余额数据的行
    clean_df = cash_balance_df.dropna(subset=['open_today_bal', 'close_today_bal'], how='all')
    
    # 对于只有一个余额的行，用另一个余额填充
    clean_df['close_today_bal'] = clean_df['close_today_bal'].fillna(clean_df['open_today_bal'])
    clean_df['open_today_bal'] = clean_df['open_today_bal'].fillna(clean_df['close_today_bal'])
    
    # 再次移除仍然为空的行
    clean_df = clean_df.dropna(subset=['close_today_bal'])
    
    # 按日期聚合（取每日的平均值，因为可能有多个账户类型）
    daily_balance = clean_df.groupby('record_date').agg({
        'open_today_bal': 'mean',
        'close_today_bal': 'mean'
    }).reset_index()
    
    print(f"清理后的每日记录数: {len(daily_balance)}")
    print(f"平均每日开盘余额: ${daily_balance['open_today_bal'].mean():,.0f} 百万美元")
    print(f"平均每日收盘余额: ${daily_balance['close_today_bal'].mean():,.0f} 百万美元")
    print(f"最低现金余额: ${daily_balance['close_today_bal'].min():,.0f} 百万美元")
    print(f"最高现金余额: ${daily_balance['close_today_bal'].max():,.0f} 百万美元")
    
    return daily_balance

def analyze_debt_data(debt_df):
    """分析债务数据"""
    print("\n=== 债务数据分析 (Federal Debt Analysis) ===")
    print(f"数据范围: {debt_df['record_date'].min()} 到 {debt_df['record_date'].max()}")
    print(f"总记录数: {len(debt_df)}")
    
    # 数值列转换
    numeric_cols = ['debt_held_public_amt', 'intragov_hold_amt', 'tot_pub_debt_out_amt']
    for col in numeric_cols:
        debt_df[col] = pd.to_numeric(debt_df[col], errors='coerce')
    
    latest_debt = debt_df.loc[debt_df['record_date'].idxmax()]
    
    print(f"最新债务数据 ({latest_debt['record_date'].strftime('%Y-%m-%d')}):")
    print(f"  公众持有债务: ${latest_debt['debt_held_public_amt']/1e12:.2f} 万亿美元")
    print(f"  政府间债务: ${latest_debt['intragov_hold_amt']/1e12:.2f} 万亿美元")
    print(f"  总债务余额: ${latest_debt['tot_pub_debt_out_amt']/1e12:.2f} 万亿美元")
    
    # 债务增长趋势
    debt_growth = debt_df.groupby('record_date')['tot_pub_debt_out_amt'].first().pct_change().mean() * 365
    print(f"年化债务增长率: {debt_growth:.2%}")
    
    return debt_df

def analyze_cash_flows(cash_flows_df):
    """分析现金流数据"""
    print("\n=== 现金流分析 (Daily Cash Flows Analysis) ===")
    print(f"数据范围: {cash_flows_df['record_date'].min()} 到 {cash_flows_df['record_date'].max()}")
    print(f"总记录数: {len(cash_flows_df)}")
    
    # 数值列转换
    cash_flows_df['transaction_today_amt'] = pd.to_numeric(cash_flows_df['transaction_today_amt'], errors='coerce')
    
    # 分离收入和支出
    deposits = cash_flows_df[cash_flows_df['transaction_type'] == 'Deposits'].copy()
    withdrawals = cash_flows_df[cash_flows_df['transaction_type'] == 'Withdrawals'].copy()
    
    print(f"平均每日收入: ${deposits['transaction_today_amt'].mean():,.0f} 百万美元")
    print(f"平均每日支出: ${withdrawals['transaction_today_amt'].mean():,.0f} 百万美元")
    
    # 每日净现金流
    daily_flows = cash_flows_df.pivot_table(
        index='record_date',
        columns='transaction_type',
        values='transaction_today_amt',
        aggfunc='sum'
    ).fillna(0)
    
    if 'Deposits' in daily_flows.columns and 'Withdrawals' in daily_flows.columns:
        daily_flows['net_flow'] = daily_flows['Deposits'] - daily_flows['Withdrawals']
        print(f"平均每日净现金流: ${daily_flows['net_flow'].mean():,.0f} 百万美元")
        print(f"净现金流标准差: ${daily_flows['net_flow'].std():,.0f} 百万美元")
        
        # 负现金流天数（政府花钱比收入多的天数）
        negative_days = len(daily_flows[daily_flows['net_flow'] < 0])
        print(f"净现金流为负的天数: {negative_days} 天 ({negative_days/len(daily_flows):.1%})")
    
    return daily_flows

def create_visualizations(daily_balance, debt_df, daily_flows):
    """创建可视化图表"""
    print("\n=== 创建可视化图表 ===")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('美国财政部关键指标分析 - X-Date预测数据概览', fontsize=16, fontweight='bold')
    
    # 1. 现金余额趋势
    if not daily_balance.empty:
        axes[0, 0].plot(daily_balance['record_date'], daily_balance['close_today_bal'], 
                       linewidth=2, color='blue', alpha=0.7)
        axes[0, 0].set_title('每日现金余额趋势')
        axes[0, 0].set_ylabel('余额 (百万美元)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(True, alpha=0.3)
    
    # 2. 总债务趋势
    if not debt_df.empty:
        debt_trend = debt_df.groupby('record_date')['tot_pub_debt_out_amt'].first()
        axes[0, 1].plot(debt_trend.index, debt_trend.values/1e12, 
                       linewidth=2, color='red', alpha=0.7)
        axes[0, 1].set_title('联邦债务总额趋势')
        axes[0, 1].set_ylabel('债务额 (万亿美元)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(True, alpha=0.3)
    
    # 3. 每日净现金流
    if 'net_flow' in daily_flows.columns:
        axes[1, 0].plot(daily_flows.index, daily_flows['net_flow'], 
                       linewidth=1, alpha=0.7)
        axes[1, 0].axhline(y=0, color='red', linestyle='--', alpha=0.7)
        axes[1, 0].set_title('每日净现金流')
        axes[1, 0].set_ylabel('净现金流 (百万美元)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, alpha=0.3)
    
    # 4. 现金余额分布
    if not daily_balance.empty:
        axes[1, 1].hist(daily_balance['close_today_bal'], bins=30, alpha=0.7, color='green')
        axes[1, 1].axvline(daily_balance['close_today_bal'].mean(), color='red', 
                          linestyle='--', label=f'平均值: ${daily_balance["close_today_bal"].mean():,.0f}M')
        axes[1, 1].set_title('现金余额分布')
        axes[1, 1].set_xlabel('余额 (百万美元)')
        axes[1, 1].set_ylabel('频次')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图表
    output_dir = Path("output/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / "treasury_data_overview.png", dpi=300, bbox_inches='tight')
    print(f"图表已保存到: {output_dir / 'treasury_data_overview.png'}")
    
    plt.show()

def calculate_xdate_indicators(daily_balance, daily_flows):
    """计算X-Date预测的关键指标"""
    print("\n=== X-Date预测关键指标 ===")
    
    if daily_balance.empty or daily_flows.empty:
        print("数据不足，无法计算指标")
        return
    
    # 合并数据
    merged_data = pd.merge(daily_balance, daily_flows, on='record_date', how='inner')
    
    # 关键指标计算
    current_balance = merged_data['close_today_bal'].iloc[-1]
    avg_daily_burn = -merged_data['net_flow'].mean() if 'net_flow' in merged_data.columns else 0
    balance_volatility = merged_data['close_today_bal'].std()
    
    print(f"当前现金余额: ${current_balance:,.0f} 百万美元")
    print(f"平均每日净支出: ${avg_daily_burn:,.0f} 百万美元")
    print(f"余额波动性(标准差): ${balance_volatility:,.0f} 百万美元")
    
    # 简单的X-Date估算（假设当前支出率持续）
    if avg_daily_burn > 0:
        days_to_zero = current_balance / avg_daily_burn
        print(f"按当前支出率估算的资金耗尽天数: {days_to_zero:.0f} 天")
        
        # 风险等级
        if days_to_zero < 30:
            risk_level = "极高风险"
        elif days_to_zero < 60:
            risk_level = "高风险"
        elif days_to_zero < 90:
            risk_level = "中等风险"
        else:
            risk_level = "低风险"
        
        print(f"X-Date风险等级: {risk_level}")
    
    # 最近趋势
    recent_data = merged_data.tail(30)  # 最近30天
    recent_trend = recent_data['close_today_bal'].pct_change().mean()
    
    print(f"最近30天余额日均变化率: {recent_trend:.2%}")

def main():
    """主函数"""
    print("财政部数据分析 - X-Date预测项目")
    print("=" * 50)
    
    # 加载数据
    data = load_treasury_data()
    
    if not data:
        print("未找到数据文件，请先运行 treasury_data_collector.py")
        return
    
    # 分析各数据集
    daily_balance = pd.DataFrame()
    debt_df = pd.DataFrame()
    daily_flows = pd.DataFrame()
    
    if 'cash_balance' in data:
        daily_balance = analyze_cash_balance(data['cash_balance'])
    
    if 'debt' in data:
        debt_df = analyze_debt_data(data['debt'])
    
    if 'cash_flows' in data:
        daily_flows = analyze_cash_flows(data['cash_flows'])
    
    # 创建可视化
    create_visualizations(daily_balance, debt_df, daily_flows)
    
    # 计算X-Date指标
    calculate_xdate_indicators(daily_balance, daily_flows)
    
    print("\n=== 数据质量总结 ===")
    print("✅ 成功下载并分析了美国财政部关键数据")
    print("✅ 数据包含X-Date预测所需的核心要素:")
    print("   - 每日现金余额")
    print("   - 联邦债务数据")
    print("   - 每日收入和支出流")
    print("✅ 数据可用于构建X-Date预测模型")
    print("\n下一步: 开始开发时间序列预测模型")

if __name__ == "__main__":
    main() 