"""
X-Date Prediction Model - US Federal Government Debt Ceiling Crisis Predictor
Predicts the date when the US government will be unable to pay all its obligations

Core Logic:
1. Debt Headroom = Debt Ceiling - Current Outstanding Debt + Remaining Unconventional Measures
2. Daily cash flow simulation
3. When cash flow is negative and cash is depleted, increase Outstanding Debt
4. Simulate until Debt Headroom reaches 0, then output X-Date
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set English font to avoid display issues
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False


class XDatePredictor:
    """X-Date Predictor for US Federal Government"""
    
    def __init__(self, data_dir="./data/raw"):
        self.data_dir = Path(data_dir)
        
        # Core fiscal data
        self.current_debt = None
        self.current_cash = None
        self.debt_ceiling = None
        self.unconventional_measures = None
        
        # Forecast data
        self.cash_flow_forecasts = None
        self.simulation_results = None
        self.x_date = None
        
        # Configuration parameters (based on CBO March 2025 latest report)
        self.config = {
            'debt_ceiling_usd': 36.1e12,  # $36.1 trillion USD (reinstated Jan 2, 2025)
            'unconventional_measures_usd': 820e9,  # $820 billion extraordinary measures (CBO estimate)
            'min_operating_cash_usd': 50e9,  # $50 billion minimum operating cash
        }
    
    def load_current_financial_status(self):
        """Load current fiscal status"""
        print("=== Loading Current Financial Status ===")
        
        # 1. Load debt outstanding data
        debt_file = self.data_dir / "debt_outstanding_2023-06-29_to_2025-06-28.csv"
        debt_data = pd.read_csv(debt_file)
        debt_data['record_date'] = pd.to_datetime(debt_data['record_date'])
        debt_data = debt_data.sort_values('record_date')
        
        # Get latest debt outstanding (in USD)
        latest_debt = debt_data.iloc[-1]
        self.current_debt = latest_debt['tot_pub_debt_out_amt']
        
        print(f"Latest debt outstanding: ${self.current_debt:,.0f} USD (${self.current_debt/1e12:.2f} trillion)")
        
        # 2. Load cash balance data
        cash_file = self.data_dir / "treasury_cash_balance_2023-06-29_to_2025-06-28.csv"
        cash_data = pd.read_csv(cash_file)
        cash_data['record_date'] = pd.to_datetime(cash_data['record_date'])
        
        # Process cash balance data (multiple records per day, take the last one)
        cash_data_clean = cash_data.dropna(subset=['close_today_bal']).copy()
        cash_data_clean['close_today_bal'] = pd.to_numeric(cash_data_clean['close_today_bal'], errors='coerce')
        
        # Clean NaN values again
        cash_data_clean = cash_data_clean.dropna(subset=['close_today_bal'])
        
        if len(cash_data_clean) == 0:
            print("Warning: Cash balance data is empty, using default value")
            self.current_cash = 500e9  # Default $500 billion
        else:
            # Group by date, take last balance of each day
            daily_cash = cash_data_clean.groupby('record_date')['close_today_bal'].last().reset_index()
            daily_cash = daily_cash.sort_values('record_date')
            
            if len(daily_cash) == 0:
                print("Warning: Processed cash balance data is empty, using default value")
                self.current_cash = 500e9  # Default $500 billion
            else:
                # Get latest cash balance (in millions USD, convert to USD)
                latest_cash_millions = daily_cash.iloc[-1]['close_today_bal']
                self.current_cash = latest_cash_millions * 1e6  # Convert to USD
        
        print(f"Latest cash balance: ${self.current_cash:,.0f} USD (${self.current_cash/1e9:.1f} billion)")
        
        # 3. Set debt ceiling and extraordinary measures
        self.debt_ceiling = self.config['debt_ceiling_usd']
        self.unconventional_measures = self.config['unconventional_measures_usd']
        
        print(f"Debt ceiling: ${self.debt_ceiling:,.0f} USD (${self.debt_ceiling/1e12:.1f} trillion)")
        print(f"Extraordinary measures: ${self.unconventional_measures:,.0f} USD (${self.unconventional_measures/1e9:.0f} billion)")
        
        # 4. Calculate current debt headroom
        current_headroom = self.debt_ceiling - self.current_debt + self.unconventional_measures
        print(f"Current debt headroom: ${current_headroom:,.0f} USD (${current_headroom/1e9:.1f} billion)")
        
        return {
            'current_debt': self.current_debt,
            'current_cash': self.current_cash,
            'debt_ceiling': self.debt_ceiling,
            'unconventional_measures': self.unconventional_measures,
            'current_headroom': current_headroom
        }
    
    def load_cash_flow_forecasts(self):
        """Load cash flow forecast data"""
        print("\n=== Loading Cash Flow Forecasts ===")
        
        # Find latest cash flow forecast file
        forecast_dir = Path("output/forecasts")
        if not forecast_dir.exists():
            raise FileNotFoundError("Cash flow forecast results directory not found")
        
        # Get latest forecast file
        forecast_files = list(forecast_dir.glob("cash_flow_forecasts_v2_*.csv"))
        if not forecast_files:
            raise FileNotFoundError("Cash flow forecast files not found")
        
        latest_file = max(forecast_files, key=lambda x: x.stat().st_mtime)
        print(f"Loading forecast file: {latest_file.name}")
        
        # Load forecast data
        forecasts = pd.read_csv(latest_file, index_col=0, parse_dates=True)
        
        # Convert units: from millions USD to USD
        forecasts_usd = forecasts * 1e6
        
        self.cash_flow_forecasts = forecasts_usd
        
        print(f"Forecast period: {forecasts_usd.index.min()} to {forecasts_usd.index.max()}")
        print(f"Forecast days: {len(forecasts_usd)}")
        print(f"Available forecast models: {list(forecasts_usd.columns)}")
        
        return forecasts_usd
    
    def simulate_xdate(self, forecast_model='Ensemble'):
        """Simulate X-Date"""
        print(f"\n=== X-Date Simulation (using {forecast_model} forecast) ===")
        
        if self.cash_flow_forecasts is None:
            raise ValueError("Please load cash flow forecast data first")
        
        if forecast_model not in self.cash_flow_forecasts.columns:
            print(f"Warning: {forecast_model} model not found, using first available model")
            forecast_model = self.cash_flow_forecasts.columns[0]
        
        # Get forecast cash flows
        daily_cash_flows = self.cash_flow_forecasts[forecast_model].dropna()
        
        # Initialize simulation variables
        simulation_data = []
        
        # Current state
        current_date = daily_cash_flows.index[0]
        cash_balance = self.current_cash
        outstanding_debt = self.current_debt
        unconventional_remaining = self.unconventional_measures
        
        print(f"Simulation start date: {current_date}")
        print(f"Initial cash balance: ${cash_balance:,.0f}")
        print(f"Initial debt outstanding: ${outstanding_debt:,.0f}")
        
        # Daily simulation
        for i, (date, daily_flow) in enumerate(daily_cash_flows.items()):
            
            # Calculate daily cash balance change
            cash_balance += daily_flow
            
            # Check if borrowing is needed
            new_debt_issued = 0
            unconventional_used = 0
            
            # If cash balance is below minimum, need to raise funds
            if cash_balance < self.config['min_operating_cash_usd']:
                funding_needed = self.config['min_operating_cash_usd'] - cash_balance
                
                # First use extraordinary measures
                if unconventional_remaining > 0:
                    unconventional_used = min(funding_needed, unconventional_remaining)
                    unconventional_remaining -= unconventional_used
                    cash_balance += unconventional_used
                    funding_needed -= unconventional_used
                
                # If still need funding, issue new debt
                if funding_needed > 0:
                    new_debt_issued = funding_needed
                    outstanding_debt += new_debt_issued
                    cash_balance += new_debt_issued
            
            # Calculate current debt headroom
            debt_headroom = self.debt_ceiling - outstanding_debt + unconventional_remaining
            
            # Record daily data
            simulation_data.append({
                'date': date,
                'daily_cash_flow': daily_flow,
                'cash_balance': cash_balance,
                'outstanding_debt': outstanding_debt,
                'new_debt_issued': new_debt_issued,
                'unconventional_used': unconventional_used,
                'unconventional_remaining': unconventional_remaining,
                'debt_headroom': debt_headroom
            })
            
            # Check if X-Date is reached
            if debt_headroom <= 0:
                self.x_date = date
                print(f"\n🚨 X-DATE REACHED: {date.strftime('%Y-%m-%d')}")
                print(f"Debt headroom exhausted: ${debt_headroom:,.0f}")
                print(f"Total debt: ${outstanding_debt:,.0f} (${outstanding_debt/1e12:.2f} trillion)")
                print(f"Remaining extraordinary measures: ${unconventional_remaining:,.0f}")
                break
            
            # Regular progress output
            if i % 30 == 0 or i < 10:
                print(f"Day {i+1:3d} ({date.strftime('%Y-%m-%d')}): "
                      f"Cash ${cash_balance/1e9:6.1f}B, "
                      f"Debt ${outstanding_debt/1e12:5.2f}T, "
                      f"Headroom ${debt_headroom/1e9:6.1f}B")
        
        # Save simulation results
        self.simulation_results = pd.DataFrame(simulation_data)
        self.simulation_results.set_index('date', inplace=True)
        
        # Output final results
        if self.x_date:
            days_to_xdate = (self.x_date - current_date).days
            print(f"\n✅ X-Date prediction completed!")
            print(f"Predicted X-Date: {self.x_date.strftime('%B %d, %Y')}")
            print(f"Days to X-Date: {days_to_xdate}")
        else:
            print(f"\n✅ X-Date not reached within forecast period")
            print(f"Debt headroom at end of forecast: ${debt_headroom:,.0f} (${debt_headroom/1e9:.1f} billion)")
        
        return self.simulation_results
    
    def analyze_scenarios(self):
        """Analyze different scenarios"""
        print("\n=== Scenario Analysis ===")
        
        if self.cash_flow_forecasts is None:
            self.load_cash_flow_forecasts()
        
        scenarios = {}
        
        # Test all available forecast models
        for model in self.cash_flow_forecasts.columns:
            if not self.cash_flow_forecasts[model].isna().all():
                print(f"\n--- Scenario: {model} ---")
                
                # Reset state
                self.simulation_results = None
                self.x_date = None
                
                # Run simulation
                try:
                    results = self.simulate_xdate(model)
                    scenarios[model] = {
                        'x_date': self.x_date,
                        'results': results
                    }
                except Exception as e:
                    print(f"Simulation failed: {e}")
                    scenarios[model] = {'x_date': None, 'results': None}
        
        # Summarize X-Date predictions for different scenarios
        print(f"\n=== X-Date Scenario Summary ===")
        xdate_predictions = []
        
        for scenario, data in scenarios.items():
            if data['x_date']:
                days_ahead = (data['x_date'] - datetime.now()).days
                xdate_predictions.append({
                    'scenario': scenario,
                    'x_date': data['x_date'],
                    'days_ahead': days_ahead
                })
                print(f"{scenario:15s}: {data['x_date'].strftime('%Y-%m-%d')} ({days_ahead:3d} days ahead)")
            else:
                print(f"{scenario:15s}: Not reached within forecast period")
        
        if xdate_predictions:
            # Calculate average prediction
            avg_days = np.mean([x['days_ahead'] for x in xdate_predictions])
            avg_date = datetime.now() + timedelta(days=int(avg_days))
            
            print(f"\n📊 Average X-Date prediction: {avg_date.strftime('%Y-%m-%d')} ({avg_days:.0f} days ahead)")
            
            # Earliest and latest predictions
            earliest = min(xdate_predictions, key=lambda x: x['days_ahead'])
            latest = max(xdate_predictions, key=lambda x: x['days_ahead'])
            
            print(f"Earliest scenario ({earliest['scenario']}): {earliest['x_date'].strftime('%Y-%m-%d')}")
            print(f"Latest scenario ({latest['scenario']}): {latest['x_date'].strftime('%Y-%m-%d')}")
        
        return scenarios
    
    def visualize_simulation(self):
        """Visualize simulation results"""
        print("\n=== Generating X-Date Simulation Charts ===")
        
        if self.simulation_results is None:
            raise ValueError("Please run X-Date simulation first")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('X-Date Simulation Results', fontsize=16, fontweight='bold')
        
        results = self.simulation_results
        
        # 1. Cash balance over time
        axes[0, 0].plot(results.index, results['cash_balance'] / 1e9, 'b-', linewidth=2)
        axes[0, 0].axhline(y=self.config['min_operating_cash_usd']/1e9, color='red', 
                          linestyle='--', alpha=0.7, label='Minimum Operating Cash')
        axes[0, 0].set_title('Cash Balance Over Time')
        axes[0, 0].set_ylabel('Cash Balance (Billion USD)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Outstanding debt over time
        axes[0, 1].plot(results.index, results['outstanding_debt'] / 1e12, 'r-', linewidth=2)
        axes[0, 1].axhline(y=self.debt_ceiling/1e12, color='black', 
                          linestyle='--', alpha=0.7, label='Debt Ceiling')
        axes[0, 1].set_title('Outstanding Debt Over Time')
        axes[0, 1].set_ylabel('Outstanding Debt (Trillion USD)')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Debt headroom over time
        axes[1, 0].plot(results.index, results['debt_headroom'] / 1e9, 'g-', linewidth=2)
        axes[1, 0].axhline(y=0, color='red', linestyle='--', alpha=0.7, label='X-Date Threshold')
        if self.x_date:
            axes[1, 0].axvline(x=self.x_date, color='red', linestyle='-', alpha=0.8, label=f'X-Date: {self.x_date.strftime("%Y-%m-%d")}')
        axes[1, 0].set_title('Debt Headroom Over Time')
        axes[1, 0].set_ylabel('Debt Headroom (Billion USD)')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Daily cash flow and new debt issuance
        axes[1, 1].bar(results.index, results['daily_cash_flow'] / 1e9, alpha=0.6, label='Daily Cash Flow')
        axes[1, 1].bar(results.index, results['new_debt_issued'] / 1e9, alpha=0.8, label='New Debt Issued', color='red')
        axes[1, 1].set_title('Daily Cash Flow and New Debt Issuance')
        axes[1, 1].set_ylabel('Amount (Billion USD)')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save chart
        output_dir = Path("output/figures")
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plt.savefig(output_dir / f"xdate_simulation_{timestamp}.png", dpi=300, bbox_inches='tight')
        print(f"Simulation chart saved: {output_dir / f'xdate_simulation_{timestamp}.png'}")
        
        plt.show()
    
    def save_results(self):
        """Save prediction results"""
        print("\n=== Saving X-Date Prediction Results ===")
        
        if self.simulation_results is None:
            raise ValueError("No simulation results to save")
        
        output_dir = Path("output/forecasts")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save detailed simulation data
        csv_file = output_dir / f"xdate_simulation_{timestamp}.csv"
        self.simulation_results.to_csv(csv_file)
        print(f"Simulation data saved: {csv_file}")
        
        # Save prediction summary
        summary = {
            'timestamp': timestamp,
            'x_date_prediction': self.x_date.strftime('%Y-%m-%d') if self.x_date else None,
            'days_to_xdate': (self.x_date - datetime.now()).days if self.x_date else None,
            'initial_conditions': {
                'current_debt_usd': float(self.current_debt),
                'current_cash_usd': float(self.current_cash),
                'debt_ceiling_usd': float(self.debt_ceiling),
                'unconventional_measures_usd': float(self.unconventional_measures)
            },
            'final_state': {
                'final_debt_usd': float(self.simulation_results['outstanding_debt'].iloc[-1]),
                'final_cash_usd': float(self.simulation_results['cash_balance'].iloc[-1]),
                'final_headroom_usd': float(self.simulation_results['debt_headroom'].iloc[-1]),
                'total_new_debt_issued_usd': float(self.simulation_results['new_debt_issued'].sum()),
                'total_unconventional_used_usd': float(self.simulation_results['unconventional_used'].sum())
            }
        }
        
        import json
        json_file = output_dir / f"xdate_prediction_summary_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"Prediction summary saved: {json_file}")
        
        return summary


def main():
    """Main function"""
    print("X-Date Prediction System")
    print("=" * 50)
    
    predictor = XDatePredictor()
    
    try:
        # 1. Load current financial status
        status = predictor.load_current_financial_status()
        
        # 2. Load cash flow forecasts
        forecasts = predictor.load_cash_flow_forecasts()
        
        # 3. Run X-Date simulation
        simulation = predictor.simulate_xdate()
        
        # 4. Scenario analysis
        scenarios = predictor.analyze_scenarios()
        
        # 5. Visualize results
        predictor.visualize_simulation()
        
        # 6. Save results
        summary = predictor.save_results()
        
        print("\n" + "=" * 50)
        print("🎯 X-Date prediction completed!")
        
        if predictor.x_date:
            print(f"📅 Predicted X-Date: {predictor.x_date.strftime('%B %d, %Y')}")
            print(f"⏰ Days ahead: {(predictor.x_date - datetime.now()).days}")
            print(f"💰 Debt ceiling: ${predictor.debt_ceiling/1e12:.1f} trillion USD")
            print(f"📊 Current debt: ${predictor.current_debt/1e12:.1f} trillion USD")
        else:
            print("📊 X-Date not reached within forecast period")
        
        print("📁 Results saved to output/ directory")
        
    except Exception as e:
        print(f"❌ Error in prediction process: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 