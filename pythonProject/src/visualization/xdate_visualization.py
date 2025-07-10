#!/usr/bin/env python3
"""
X-DATE Visualization - Clean Interface
Clean visualization for debt ceiling analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import seaborn as sns
from datetime import datetime
import matplotlib.dates as mdates

# Set style
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 10

def load_latest_xdate_data():
    """Load latest X-DATE simulation data"""
    output_dir = Path("output/forecasts")
    
    # Find latest xdate simulation file
    xdate_files = list(output_dir.glob("xdate_simulation_*.csv"))
    if not xdate_files:
        raise FileNotFoundError("No X-DATE simulation data files found")
    
    latest_file = max(xdate_files, key=lambda x: x.stat().st_mtime)
    print(f"Loading data: {latest_file.name}")
    
    df = pd.read_csv(latest_file)
    df['date'] = pd.to_datetime(df['date'])
    return df, latest_file.stem

def create_clean_visualization(df, filename_base):
    """Create clean visualization without special characters"""
    
    # Create figure
    fig = plt.figure(figsize=(16, 12))
    
    # Convert data to billions/trillions
    df['cash_balance_b'] = df['cash_balance'] / 1e9
    df['outstanding_debt_t'] = df['outstanding_debt'] / 1e12
    df['debt_headroom_b'] = df['debt_headroom'] / 1e9
    df['unconventional_used_b'] = df['unconventional_used'] / 1e9
    df['new_debt_issued_b'] = df['new_debt_issued'] / 1e9
    df['daily_cash_flow_b'] = df['daily_cash_flow'] / 1e9
    
    # 1. Cash Balance Trend
    ax1 = plt.subplot(2, 3, 1)
    plt.plot(df['date'], df['cash_balance_b'], 'b-', linewidth=2, label='Cash Balance')
    plt.fill_between(df['date'], 0, df['cash_balance_b'], alpha=0.3, color='blue')
    plt.axhline(y=50, color='red', linestyle='--', alpha=0.7, label='Minimum Cash (50B)')
    plt.title('Cash Balance Trend', fontsize=14, fontweight='bold')
    plt.ylabel('Cash Balance (Billions USD)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax1.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.xticks(rotation=45)
    
    # 2. Debt vs Ceiling - Focused view
    ax2 = plt.subplot(2, 3, 2)
    debt_ceiling = 36.1  # $36.1 trillion
    current_debt = df['outstanding_debt_t'].iloc[0]
    
    # Create focused Y-axis range
    y_min = debt_ceiling - 0.5
    y_max = current_debt + 0.2
    
    plt.axhline(y=debt_ceiling, color='red', linewidth=3, label=f'Debt Ceiling ({debt_ceiling:.1f}T)')
    plt.plot(df['date'], df['outstanding_debt_t'], 'orange', linewidth=2, label=f'Current Debt ({current_debt:.2f}T)')
    plt.fill_between(df['date'], debt_ceiling, df['outstanding_debt_t'], 
                     color='red', alpha=0.3, label=f'Over Limit {(current_debt-debt_ceiling)*1000:.0f}B')
    
    plt.title('Debt vs Ceiling (Focused View)', fontsize=14, fontweight='bold')
    plt.ylabel('Debt Amount (Trillions USD)')
    plt.ylim(y_min, y_max)
    plt.legend()
    plt.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.xticks(rotation=45)
    
    # 3. Debt Headroom Changes
    ax3 = plt.subplot(2, 3, 3)
    plt.plot(df['date'], df['debt_headroom_b'], 'green', linewidth=2, label='Remaining Debt Space')
    plt.fill_between(df['date'], 0, df['debt_headroom_b'], alpha=0.3, color='green')
    
    # Highlight changes
    headroom_change = df['debt_headroom_b'].iloc[-1] - df['debt_headroom_b'].iloc[0]
    plt.title(f'Remaining Debt Space\n(Change: {headroom_change:.1f}B)', fontsize=14, fontweight='bold')
    plt.ylabel('Remaining Space (Billions USD)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax3.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.xticks(rotation=45)
    
    # 4. Extraordinary Measures Usage
    ax4 = plt.subplot(2, 3, 4)
    
    # Find dates when extraordinary measures were used
    used_days = df[df['unconventional_used_b'] > 0]
    total_used = df['unconventional_used_b'].sum()
    
    if len(used_days) > 0:
        bars = plt.bar(used_days['date'], used_days['unconventional_used_b'], 
                      color='orange', alpha=0.7, label='Extraordinary Measures')
        plt.title(f'Extraordinary Measures Usage\n(Total: {total_used:.1f}B, {len(used_days)} days)', 
                 fontsize=14, fontweight='bold')
        
        # Add value labels
        for bar, value in zip(bars, used_days['unconventional_used_b']):
            if value > 0:
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                        f'{value:.1f}B', ha='center', va='bottom', fontsize=9)
    else:
        plt.text(0.5, 0.5, 'No Extraordinary\nMeasures Used\nThis Period', ha='center', va='center', 
                transform=ax4.transAxes, fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        plt.title('Extraordinary Measures Usage', fontsize=14, fontweight='bold')
    
    plt.ylabel('Usage Amount (Billions USD)')
    plt.grid(True, alpha=0.3)
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax4.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.xticks(rotation=45)
    
    # 5. Daily Cash Flow
    ax5 = plt.subplot(2, 3, 5)
    colors = ['red' if x < 0 else 'green' for x in df['daily_cash_flow_b']]
    bars = plt.bar(df['date'], df['daily_cash_flow_b'], color=colors, alpha=0.6)
    
    # Highlight large outflows
    large_outflows = df[df['daily_cash_flow_b'] < -100]
    if len(large_outflows) > 0:
        plt.scatter(large_outflows['date'], large_outflows['daily_cash_flow_b'], 
                   color='darkred', s=50, zorder=5, label='Large Outflows (>100B)')
    
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    plt.title('Daily Cash Flow', fontsize=14, fontweight='bold')
    plt.ylabel('Cash Flow (Billions USD)')
    plt.grid(True, alpha=0.3)
    ax5.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    ax5.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.xticks(rotation=45)
    if len(large_outflows) > 0:
        plt.legend()
    
    # 6. Key Statistics Summary
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    
    # Calculate key statistics
    initial_cash = df['cash_balance_b'].iloc[0]
    final_cash = df['cash_balance_b'].iloc[-1]
    cash_change = final_cash - initial_cash
    
    min_cash = df['cash_balance_b'].min()
    min_cash_date = df.loc[df['cash_balance_b'].idxmin(), 'date'].strftime('%m-%d')
    
    debt_over_limit = (current_debt - debt_ceiling) * 1000
    remaining_measures = df['debt_headroom_b'].iloc[-1]
    
    # Cash flow statistics
    avg_daily_flow = df['daily_cash_flow_b'].mean()
    cash_outflow_days = len(df[df['daily_cash_flow_b'] < 0])
    cash_inflow_days = len(df[df['daily_cash_flow_b'] > 0])
    
    summary_text = f"""KEY INDICATORS SUMMARY

CASH STATUS:
  Initial: ${initial_cash:.1f}B
  Final: ${final_cash:.1f}B
  Change: ${cash_change:+.1f}B
  Minimum: ${min_cash:.1f}B ({min_cash_date})

DEBT STATUS:
  Current Debt: ${current_debt:.2f}T
  Debt Ceiling: ${debt_ceiling:.1f}T
  Over Limit: ${debt_over_limit:.1f}B
  Remaining Space: ${remaining_measures:.1f}B

CASH FLOW:
  Daily Average: ${avg_daily_flow:.1f}B
  Outflow Days: {cash_outflow_days}
  Inflow Days: {cash_inflow_days}
  
EXTRAORDINARY MEASURES:
  Total Used: ${total_used:.1f}B
  Usage Days: {len(used_days)}
"""
    
    plt.text(0.05, 0.95, summary_text, transform=ax6.transAxes, fontsize=10,
             verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
    
    # Overall title
    simulation_days = len(df)
    start_date = df['date'].iloc[0].strftime('%Y-%m-%d')
    end_date = df['date'].iloc[-1].strftime('%Y-%m-%d')
    
    fig.suptitle(f'X-DATE Simulation Analysis\n'
                f'Period: {start_date} to {end_date} ({simulation_days} days)', 
                fontsize=16, fontweight='bold', y=0.95)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.9, hspace=0.3, wspace=0.3)
    
    # Save chart
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"output/figures/simple_xdate_analysis_{timestamp}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"\nClean X-DATE analysis chart saved: {output_path}")
    
    return output_path

def main():
    """Main function"""
    print("X-DATE Prediction Visualization")
    print("="*50)
    
    try:
        # Load data
        df, filename_base = load_latest_xdate_data()
        print(f"Data period: {df['date'].iloc[0].strftime('%Y-%m-%d')} to {df['date'].iloc[-1].strftime('%Y-%m-%d')}")
        print(f"Simulation days: {len(df)}")
        
        # Create visualization
        output_path = create_clean_visualization(df, filename_base)
        
        print("\nVisualization completed!")
        print("Key findings:")
        
        # Analyze key findings
        current_debt = df['outstanding_debt'].iloc[0] / 1e12
        debt_ceiling = 36.1
        debt_over = (current_debt - debt_ceiling) * 1000
        
        total_measures_used = df['unconventional_used'].sum() / 1e9
        used_days = len(df[df['unconventional_used'] > 0])
        
        print(f"  - Debt over limit: ${debt_over:.1f} billion")
        print(f"  - Extraordinary measures used: ${total_measures_used:.1f} billion ({used_days} days)")
        print(f"  - Cash balance change: ${(df['cash_balance'].iloc[-1] - df['cash_balance'].iloc[0])/1e9:.1f} billion")
        
        if total_measures_used == 0 and debt_over > 0:
            print(f"  - Note: Due to debt exceeding limit by ${debt_over:.1f} billion, no new debt can be issued")
            print(f"  - System relies mainly on existing cash balance for operations")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 