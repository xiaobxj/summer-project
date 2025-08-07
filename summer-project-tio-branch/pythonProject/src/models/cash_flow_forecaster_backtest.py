"""
Fixed Cash Flow Forecaster V2 - Cash Flow Prediction Model
Solves issues from original version:
1. ARIMA/SARIMA model predictions returning NaN
2. Machine learning model predictions abnormally large  
3. Time series frequency issues
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Time series analysis
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# Machine learning
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split

# Set Chinese font to avoid display issues
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Arial']
plt.rcParams['axes.unicode_minus'] = False


class CashFlowForecasterV2:
    """Fixed Cash Flow Forecaster"""
    
    def __init__(self, data_dir="./data/backtest"):
        self.data_dir = Path(data_dir)
        self.daily_flows = None
        self.models = {}
        self.forecasts = {}
        self.feature_columns = []
        self.scaler = None
        
    def load_and_prepare_data(self):
        """Load and prepare cash flow data"""
        print("=== Loading Cash Flow Data ===")
        
        # Load cash flow data
        cash_flow_file = self.data_dir / "daily_cash_flows_backtest_2023.csv"
        
        if not cash_flow_file.exists():
            raise FileNotFoundError(f"Cash flow data file not found: {cash_flow_file}")
        
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
        
        # 计算净现金流 (收入 - 支出)
        if 'Deposits' in daily_flows.columns and 'Withdrawals' in daily_flows.columns:
            daily_flows['net_flow'] = daily_flows['Deposits'] - daily_flows['Withdrawals']
        else:
            raise ValueError("数据中未找到 Deposits 和 Withdrawals 列")
        
        # 确保数据按日期排序
        daily_flows = daily_flows.sort_index()
        
        # *** Key Fix: Don't reindex to business days, maintain original data integrity ***
        # Keep original date distribution, avoid forward fill bias
        # Don't force frequency setting, let pandas auto-infer
        
        self.daily_flows = daily_flows
        
        print(f"Data period: {daily_flows.index.min()} to {daily_flows.index.max()}")
        print(f"Total days: {len(daily_flows)}")
        print(f"Average net cash flow: ${daily_flows['net_flow'].mean():,.0f} million USD")
        print(f"Net cash flow std dev: ${daily_flows['net_flow'].std():,.0f} million USD")
        print(f"Positive cash flow days: {(daily_flows['net_flow'] > 0).sum()} ({(daily_flows['net_flow'] > 0).mean():.1%})")
        print(f"Negative cash flow days: {(daily_flows['net_flow'] < 0).sum()} ({(daily_flows['net_flow'] < 0).mean():.1%})")
        
        return daily_flows
    
    def create_features(self):
        """Create feature engineering"""
        print("\n=== Feature Engineering ===")
        
        df = self.daily_flows.copy()
        
        # Basic time features
        df['day_of_week'] = df.index.dayofweek
        df['day_of_month'] = df.index.day
        df['month'] = df.index.month
        df['quarter'] = df.index.quarter
        
        # Seasonal features
        df['is_month_end'] = (df.index == df.index.to_period('M').end_time).astype(int)
        df['is_quarter_end'] = (df.index == df.index.to_period('Q').end_time).astype(int)
        
        # Special dates
        df['is_friday'] = (df.index.dayofweek == 4).astype(int)
        df['is_monday'] = (df.index.dayofweek == 0).astype(int)
        
        # Simplified lag features
        for lag in [1, 2, 3, 7]:
            df[f'lag_{lag}'] = df['net_flow'].shift(lag)
        
        # Simplified rolling features
        for window in [7, 30]:
            df[f'rolling_mean_{window}'] = df['net_flow'].rolling(window).mean()
            df[f'rolling_std_{window}'] = df['net_flow'].rolling(window).std()
        
        # Feature list
        self.feature_columns = [
            'day_of_week', 'day_of_month', 'month', 'quarter',
            'is_month_end', 'is_quarter_end', 'is_friday', 'is_monday',
            'lag_1', 'lag_2', 'lag_3', 'lag_7',
            'rolling_mean_7', 'rolling_mean_30', 'rolling_std_7', 'rolling_std_30'
        ]
        
        print(f"Created {len(self.feature_columns)} features")
        
        # Remove NaN values
        df_clean = df.dropna()
        print(f"Data after cleaning: {len(df_clean)} rows")
        
        self.daily_flows_with_features = df_clean
        return df_clean
    
    def fit_arima_model(self):
        """Fit ARIMA model using auto_arima for automatic parameter selection"""
        print("\n=== ARIMA Model Training ===")
        
        net_flow = self.daily_flows['net_flow'].dropna()

        # Check data quality
        if len(net_flow) < 30:
            print("Insufficient data for ARIMA modeling")
            self.models['ARIMA'] = None
            return None
        
        try:
            # Use auto_arima for automatic parameter selection
            from pmdarima import auto_arima
            print("🔍 Using auto_arima to find optimal parameters...")
            
            auto_model = auto_arima(
                net_flow,
                start_p=0, start_q=0,
                max_p=3, max_q=3, max_d=2,
                seasonal=False,  # Set to True if you want seasonal ARIMA
                stepwise=True,
                suppress_warnings=True,
                error_action='ignore',
                trace=True
            )
            
            print(f"Auto ARIMA selected: {auto_model.order}")
            print(f"   AIC: {auto_model.aic():.2f}")
            
            # Test forecast to ensure no NaN
            test_forecast = auto_model.predict(n_periods=5)
            if not np.isnan(test_forecast).any():
                self.models['ARIMA'] = auto_model
                print(f"ARIMA model ready for forecasting")
                return auto_model
            else:
                print("Auto ARIMA forecast contains NaN values")
                self.models['ARIMA'] = None
                return None
                
        except Exception as e:
            print(f"Auto ARIMA failed, falling back to manual selection: {e}")
            
            # Fallback to original simple approach
            arima_configs = [(1,0,1), (1,1,1), (2,0,1), (1,0,2)]
            
            best_model = None
            best_aic = float('inf')
            
            for order in arima_configs:
                try:
                    model = ARIMA(net_flow, order=order)
                    fitted_arima = model.fit()
                    
                    # Test forecast to ensure no NaN
                    test_forecast = fitted_arima.forecast(steps=5)
                    if not np.isnan(test_forecast).any() and fitted_arima.aic < best_aic:
                        best_model = fitted_arima
                        best_aic = fitted_arima.aic
                        print(f"ARIMA{order} AIC: {fitted_arima.aic:.2f} - Valid")
                    else:
                        print(f"ARIMA{order} - Invalid (NaN forecast)")
                        
                except Exception as e:
                    print(f"ARIMA{order} failed: {e}")
                    continue
            
            if best_model is not None:
                self.models['ARIMA'] = best_model
                print(f"Best ARIMA model selected with AIC: {best_aic:.2f}")
                return best_model
            else:
                print("All ARIMA configurations failed")
                self.models['ARIMA'] = None
                return None
    
    def fit_seasonal_model(self):
        """Fit seasonal pattern model - based on user's enhanced algorithm"""
        print("\n=== Seasonal Pattern Model Training ===")
        
        net_flow = self.daily_flows['net_flow'].copy()
        net_flow.index = pd.to_datetime(net_flow.index)
        
        # Create dataframe with year, day_of_year for analysis
        df_seasonal = pd.DataFrame({
            'net_flow': net_flow,
            'year': net_flow.index.year,
            'day_of_year': net_flow.index.dayofyear,
            'date': net_flow.index
        })
        
        # Get the last date for determining current position
        last_date = df_seasonal['date'].max()
        last_doy = last_date.dayofyear
        
        try:
            # Analyze 2023 full-year pattern
            df_2023 = df_seasonal[df_seasonal['year'] == 2023]
            if df_2023.empty:
                print("No 2023 data available for seasonal analysis")
                self.models['Seasonal'] = None
                return None
            
            avg_2023_full = df_2023['net_flow'].mean()
            
            # Calculate 2024 YTD average (up to current date)
            df_2024 = df_seasonal[df_seasonal['year'] == 2024]
            if not df_2024.empty:
                avg_2024_ytd = df_2024['net_flow'].mean()
            else:
                avg_2024_ytd = avg_2023_full  # fallback
            
            # Calculate 2023 YTD average (up to same day of year as current)
            df_2023_ytd = df_2023[df_2023['day_of_year'] <= last_doy]
            avg_2023_ytd = df_2023_ytd['net_flow'].mean() if not df_2023_ytd.empty else avg_2023_full
            
            # Calculate growth factor for 2024 (comparing same period year-over-year)
            growth_factor_2024 = avg_2024_ytd / avg_2023_ytd if avg_2023_ytd != 0 else 1.0
            
            # Apply reasonable bounds to growth factor (prevent extreme values)
            growth_factor_2024 = np.clip(growth_factor_2024, 0.5, 2.0)  # Limit to ±100% change
            
            # Target average for 2024 full year (project current YTD growth to full year)
            target_avg_2024 = avg_2023_full * growth_factor_2024 if avg_2023_full != 0 else avg_2024_ytd
            
            # Build 2023 seasonal pattern (daily factors)
            daily_factors_2023 = df_2023.groupby('day_of_year')['net_flow'].mean() / avg_2023_full if avg_2023_full != 0 else pd.Series()
            
            # Extend to full 366 days using interpolation
            full_days = pd.Series(index=np.arange(1, 367), dtype=float)
            daily_factors_2023 = daily_factors_2023.reindex(full_days.index, method='nearest').fillna(1.0)
            
            # Store seasonal model parameters
            seasonal_model = {
                'daily_factors': daily_factors_2023,
                'avg_2023_full': avg_2023_full,
                'avg_2024_ytd': avg_2024_ytd,
                'avg_2023_ytd': avg_2023_ytd,
                'growth_factor_2024': growth_factor_2024,
                'target_avg_2024': target_avg_2024,
                'last_date': last_date,
                'last_doy': last_doy
            }
            
            self.models['Seasonal'] = seasonal_model
            
            print(f"✅ Seasonal model trained successfully:")
            print(f"   2023 full year average: ${avg_2023_full:,.0f}")
            print(f"   2024 YTD average: ${avg_2024_ytd:,.0f}")
            print(f"   Growth factor: {growth_factor_2024:.3f}")
            print(f"   Target 2024 average: ${target_avg_2024:,.0f}")
            print(f"   Seasonal factors range: {daily_factors_2023.min():.3f} - {daily_factors_2023.max():.3f}")
            
            return seasonal_model
            
        except Exception as e:
            print(f"❌ Seasonal model training failed: {e}")
            self.models['Seasonal'] = None
            return None

    def fit_ml_models(self):
        """Fit machine learning models - simplified version"""
        print("\n=== Machine Learning Model Training ===")
        
        df = self.daily_flows_with_features.copy()
        
        X = df[self.feature_columns]
        y = df['net_flow']
        
        # Check data ranges
        print(f"Target variable range: {y.min():.0f} to {y.max():.0f}")
        print(f"Feature range example - lag_1: {X['lag_1'].min():.0f} to {X['lag_1'].max():.0f}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, shuffle=False
        )
        
        # Only use Random Forest to avoid over-complexity
        model = RandomForestRegressor(
            n_estimators=50,  # Reduce trees
            max_depth=10,     # Limit depth
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        # Performance metrics
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        print(f"Random Forest performance:")
        print(f"  MAE: ${mae:,.0f} million USD")
        print(f"  RMSE: ${rmse:,.0f} million USD")
        print(f"  Prediction range: ${y_pred.min():,.0f} to ${y_pred.max():,.0f}")
        
        self.models['RandomForest'] = model
        return {'rf_mae': mae, 'rf_rmse': rmse}
    
    def generate_forecasts(self, forecast_days=120):
        """Generate predictions"""
        print(f"\n=== Generate Future {forecast_days} Days Forecast ===")
        
        last_date = self.daily_flows.index.max()
        future_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=forecast_days,
            freq='D'  # Keep daily frequency
        )
        
        forecasts = {}
        
        # ARIMA forecast
        if 'ARIMA' in self.models and self.models['ARIMA'] is not None:
            try:
                arima_model = self.models['ARIMA']
                
                # Check if it's auto_arima model or statsmodels ARIMA
                if hasattr(arima_model, 'predict'):
                    # auto_arima model
                    arima_forecast = arima_model.predict(n_periods=len(future_dates))
                else:
                    # statsmodels ARIMA model
                    arima_forecast = arima_model.forecast(steps=len(future_dates))
                
                # Debug information
                print(f"ARIMA forecast shape: {arima_forecast.shape}")
                print(f"ARIMA forecast contains NaN: {np.isnan(arima_forecast).any()}")
                print(f"ARIMA forecast range: ${arima_forecast.min():,.0f} to ${arima_forecast.max():,.0f}")
                
                if not np.isnan(arima_forecast).any():
                    forecasts['ARIMA'] = pd.Series(arima_forecast, index=future_dates)
                    print(f"✅ ARIMA forecast completed: mean ${arima_forecast.mean():,.0f}")
                else:
                    print("❌ ARIMA forecast contains NaN values, skipping")
                    
            except Exception as e:
                print(f"❌ ARIMA forecast failed: {e}")
        else:
            print("❌ ARIMA model not available")
        
        # Seasonal forecast - based on user's enhanced algorithm
        if 'Seasonal' in self.models and self.models['Seasonal'] is not None:
            try:
                seasonal_model = self.models['Seasonal']
                
                # Generate forecasts for 2024 and 2026
                seasonal_forecast = []
                
                for date in future_dates:
                    year = date.year
                    day_of_year = date.dayofyear
                    
                    if year == 2024:
                        # Use target 2024 average with seasonal pattern
                        target_avg = seasonal_model['target_avg_2024']
                        seasonal_factor = seasonal_model['daily_factors'].get(day_of_year, 1.0)
                        forecast_value = target_avg * seasonal_factor
                        
                    elif year == 2026:
                        # Calculate 2026 growth factor based on 2024 vs 2023
                        growth_factor_2026 = seasonal_model['target_avg_2024'] / seasonal_model['avg_2023_full'] if seasonal_model['avg_2023_full'] != 0 else 1.0
                        target_avg_2026 = seasonal_model['target_avg_2024'] * growth_factor_2026
                        seasonal_factor = seasonal_model['daily_factors'].get(day_of_year, 1.0)
                        forecast_value = target_avg_2026 * seasonal_factor
                        
                    else:
                        # For years beyond 2026, use compound growth
                        years_beyond = year - 2024
                        growth_factor_2026 = seasonal_model['target_avg_2024'] / seasonal_model['avg_2023_full'] if seasonal_model['avg_2023_full'] != 0 else 1.0
                        target_avg = seasonal_model['target_avg_2024'] * (growth_factor_2026 ** years_beyond)
                        seasonal_factor = seasonal_model['daily_factors'].get(day_of_year, 1.0)
                        forecast_value = target_avg * seasonal_factor
                    
                    seasonal_forecast.append(forecast_value)
                
                forecasts['Seasonal'] = pd.Series(seasonal_forecast, index=future_dates)
                print(f"✅ Seasonal forecast completed: mean ${np.mean(seasonal_forecast):,.0f}")
                print(f"   Forecast range: ${np.min(seasonal_forecast):,.0f} to ${np.max(seasonal_forecast):,.0f}")
                
            except Exception as e:
                print(f"❌ Seasonal forecast failed: {e}")
        else:
            print("❌ Seasonal model not available")

        # Random Forest forecast
        if 'RandomForest' in self.models and self.models['RandomForest'] is not None:
            try:
                # Create future features
                future_features = self._create_future_features(future_dates)
                if future_features is not None:
                    rf_forecast = self.models['RandomForest'].predict(future_features)
                    forecasts['RandomForest'] = pd.Series(rf_forecast, index=future_dates)
                    print(f"✅ Random Forest forecast completed: mean ${rf_forecast.mean():,.0f}")
            except Exception as e:
                print(f"❌ Random Forest forecast failed: {e}")
        
        # Simple historical average backup method
        if not forecasts:
            print("Using historical average method...")
            hist_mean = self.daily_flows['net_flow'].mean()
            hist_std = self.daily_flows['net_flow'].std()
            
            # Add some randomness
            np.random.seed(42)
            simple_forecast = np.random.normal(hist_mean, hist_std * 0.5, len(future_dates))
            forecasts['HistoricalAvg'] = pd.Series(simple_forecast, index=future_dates)
        
        # Ensemble forecast
        if len(forecasts) > 1:
            ensemble = pd.DataFrame(forecasts).mean(axis=1)
            forecasts['Ensemble'] = ensemble
        
        self.forecasts = forecasts
        
        # Display summary
        print(f"\nForecast Summary:")
        for name, forecast in forecasts.items():
            if not forecast.isna().any():  # Only show non-NaN forecasts
                positive_days = (forecast > 0).sum()
                negative_days = (forecast < 0).sum()
                print(f"{name}: mean ${forecast.mean():,.0f}, range ${forecast.min():,.0f} ~ ${forecast.max():,.0f}")
                print(f"  Positive cash flow days: {positive_days} ({positive_days/len(forecast):.1%})")
                print(f"  Negative cash flow days: {negative_days} ({negative_days/len(forecast):.1%})")
            else:
                print(f"{name}: Forecast contains NaN values, skipping display")
        
        return forecasts
    
    def _create_future_features(self, future_dates):
        """Create simplified future features"""
        
        # Use recent historical average for features that require lag data
        recent_data = self.daily_flows['net_flow'].tail(30)
        recent_mean = recent_data.mean()
        
        future_features = []
        
        for date in future_dates:
            features = {}
            
            # Time-based features
            features['day_of_week'] = date.dayofweek
            features['day_of_month'] = date.day
            features['month'] = date.month
            features['quarter'] = date.quarter
            features['is_month_end'] = 1 if date == pd.Period(date, 'M').end_time else 0
            features['is_quarter_end'] = 1 if date == pd.Period(date, 'Q').end_time else 0
            features['is_friday'] = 1 if date.dayofweek == 4 else 0
            features['is_monday'] = 1 if date.dayofweek == 0 else 0
            
            # Use historical averages for lag and rolling features
            for lag in [1, 2, 3, 7]:
                features[f'lag_{lag}'] = recent_mean
            
            for window in [7, 30]:
                features[f'rolling_mean_{window}'] = recent_mean
                features[f'rolling_std_{window}'] = recent_data.std()
            
            future_features.append(features)
        
        future_df = pd.DataFrame(future_features)
        future_df = future_df[self.feature_columns]
        
        return future_df
    
    def visualize_forecasts(self):
        """Visualize forecast results"""
        print("\n=== Generating Forecast Charts ===")
        
        if not self.forecasts:
            print("No forecasts to visualize")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Cash Flow Forecasting Results', fontsize=16, fontweight='bold')
        
        # 1. Historical data and forecasts
        hist_data = self.daily_flows['net_flow'].tail(30)
        axes[0, 0].plot(hist_data.index, hist_data.values, 'k-', linewidth=2, label='Historical Data')
        
        colors = ['blue', 'red', 'green', 'orange']
        for i, (name, forecast) in enumerate(self.forecasts.items()):
            axes[0, 0].plot(forecast.index, forecast.values, 
                        color=colors[i % len(colors)], linestyle='--', label=f'{name} Forecast')
        
        axes[0, 0].axhline(y=0, color='gray', linestyle=':', alpha=0.7)
        axes[0, 0].set_title('Cash Flow: Historical + Forecasts')
        axes[0, 0].set_ylabel('Net Cash Flow (Million USD)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Forecast distribution
        if 'Ensemble' in self.forecasts:
            ensemble_data = self.forecasts['Ensemble'].dropna()
            axes[0, 1].hist(ensemble_data, bins=30, alpha=0.7, edgecolor='black')
            axes[0, 1].axvline(x=ensemble_data.mean(), color='red', linestyle='--', 
                              label=f'Mean: ${ensemble_data.mean():,.0f}M')
            axes[0, 1].set_title('Ensemble Forecast Distribution')
            axes[0, 1].set_xlabel('Net Cash Flow (Million USD)')
            axes[0, 1].set_ylabel('Frequency')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Model comparison
        if len(self.forecasts.keys()) > 1:
            model_means = pd.DataFrame(self.forecasts).mean()
            axes[1, 0].bar(range(len(model_means)), model_means.values)
            axes[1, 0].set_xticks(range(len(model_means)))
            axes[1, 0].set_xticklabels(model_means.index, rotation=45)
            axes[1, 0].set_title('Average Forecast by Model')
            axes[1, 0].set_ylabel('Average Net Cash Flow (Million USD)')
            axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Cumulative cash flow
        if 'Ensemble' in self.forecasts:
            cumulative = self.forecasts['Ensemble'].cumsum()
            axes[1, 1].plot(cumulative.index, cumulative.values, linewidth=2, color='green')
            axes[1, 1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
            axes[1, 1].set_title('Cumulative Cash Flow Forecast')
            axes[1, 1].set_ylabel('Cumulative Cash Flow (Million USD)')
            axes[1, 1].grid(True, alpha=0.3)
        

                # === Optional: Add actual 2024 data for comparison ===
        try:
            actual_file = self.data_dir / "daily_cash_flows_backtest_2024.csv"
            if actual_file.exists():
                actual_df = pd.read_csv(actual_file)
                actual_df['record_date'] = pd.to_datetime(actual_df['record_date'])
                actual_df['transaction_today_amt'] = pd.to_numeric(actual_df['transaction_today_amt'], errors='coerce')
                
                # Pivot to net flow
                actual_pivot = actual_df.pivot_table(
                    index='record_date',
                    columns='transaction_type',
                    values='transaction_today_amt',
                    aggfunc='sum'
                ).fillna(0)
                
                if 'Deposits' in actual_pivot.columns and 'Withdrawals' in actual_pivot.columns:
                    actual_pivot['net_flow'] = actual_pivot['Deposits'] - actual_pivot['Withdrawals']
                    
                    # Filter to 2024 only
                    actual_2024 = actual_pivot.loc[(actual_pivot.index >= '2024-01-01') & (actual_pivot.index <= '2024-12-31')]
                    
                    # Plot as additional line
                    axes[0, 0].plot(actual_2024.index, actual_2024['net_flow'], color='black', linewidth=1.8, linestyle='-', label='Actual 2024')
                    print("✅ Added actual 2024 net flow to plot.")
                else:
                    print("❌ Actual file missing 'Deposits' or 'Withdrawals' column.")
            else:
                print(f"❌ Actual 2024 CSV not found: {actual_file}")
        except Exception as e:
            print(f"❌ Error loading actual 2024 data: {e}")

                # === Cumulative Forecast vs Actual: Detailed Comparison ===
        print("\n=== Cumulative Net Cash Flow Comparison (Forecast vs Actual) ===")
        try:
            actual_file = self.data_dir / "daily_cash_flows_backtest_2024.csv"
            if actual_file.exists():
                actual_df = pd.read_csv(actual_file)
                actual_df['record_date'] = pd.to_datetime(actual_df['record_date'])
                actual_df['transaction_today_amt'] = pd.to_numeric(actual_df['transaction_today_amt'], errors='coerce')
                
                # Compute daily net flow
                actual_pivot = actual_df.pivot_table(
                    index='record_date',
                    columns='transaction_type',
                    values='transaction_today_amt',
                    aggfunc='sum'
                ).fillna(0)
                if 'Deposits' not in actual_pivot.columns or 'Withdrawals' not in actual_pivot.columns:
                    print("❌ Missing required columns in actual data.")
                    return
                actual_pivot['net_flow'] = actual_pivot['Deposits'] - actual_pivot['Withdrawals']
                
                # Filter actual from July 1 onward
                forecast_start = pd.Timestamp("2024-07-01")
                actual_cum = actual_pivot['net_flow'].loc[actual_pivot.index >= forecast_start].cumsum()
                
                # Compute cumulative forecasts
                forecast_cum = {}
                for name, forecast in self.forecasts.items():
                    f_sub = forecast.loc[forecast.index >= forecast_start]
                    if not f_sub.empty:
                        forecast_cum[name] = f_sub.cumsum()

                # Plot comparison
                plt.figure(figsize=(12, 6))
                plt.plot(actual_cum.index, actual_cum.values, label='Actual', color='black', linewidth=2)
                for name, series in forecast_cum.items():
                    plt.plot(series.index, series.values, label=name, linestyle='--')

                plt.title("Cumulative Net Cash Flow: Actual vs Forecasts (from July 1, 2024)")
                # Add vertical line at forecast start
                forecast_start = pd.Timestamp("2024-07-01")
                plt.axvline(x=forecast_start, color='gray', linestyle=':', linewidth=2, label='Forecast Start')

                plt.xlabel("Date")
                plt.ylabel("Cumulative Net Cash Flow (Million USD)")
                plt.legend()
                plt.grid(True, alpha=0.3)

                # Save and show
                cum_path = Path("output/figures")
                cum_path.mkdir(parents=True, exist_ok=True)
                fname = cum_path / f"cumulative_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                plt.savefig(fname, dpi=300, bbox_inches='tight')
                print(f"📈 Cumulative comparison plot saved to: {fname}")
                plt.show()

                # Print final cumulative totals and errors
                actual_final = actual_cum.iloc[-1]
                print(f"\n🟩 Actual Final Cumulative Net Cash Flow: ${actual_final:,.0f}")
                for name, series in forecast_cum.items():
                    final = series.iloc[-1]
                    err = abs(final - actual_final)
                    pct = err / abs(actual_final) if actual_final != 0 else float('inf')
                    print(f"🔹 {name:15}: ${final:,.0f} | Error: ${err:,.0f} ({pct:.2%})")
            else:
                print("❌ Actual file not found for cumulative comparison.")
        except Exception as e:
            print(f"❌ Error during cumulative comparison: {e}")


        plt.tight_layout()
        
        # Save chart
        output_dir = Path("output/figures")
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plt.savefig(output_dir / f"cash_flow_forecasts_v2_{timestamp}.png", dpi=300, bbox_inches='tight')
        print(f"Forecast chart saved: {output_dir / f'cash_flow_forecasts_v2_{timestamp}.png'}")
        
        plt.show()
        # plt.close('all')



                # === Evaluation: Compare cumulative net cash flow from July 1, 2024 ===
        print("\n=== Net Cash Flow Comparison: July 1, 2024 to Forecast Horizon ===")
        try:
            # Load actual 2024 data
            actual_file = self.data_dir / "daily_cash_flows_backtest_2024.csv"
            if actual_file.exists():
                actual_df = pd.read_csv(actual_file)
                actual_df['record_date'] = pd.to_datetime(actual_df['record_date'])
                actual_df['transaction_today_amt'] = pd.to_numeric(actual_df['transaction_today_amt'], errors='coerce')
                
                # Pivot to daily format
                actual_pivot = actual_df.pivot_table(
                    index='record_date',
                    columns='transaction_type',
                    values='transaction_today_amt',
                    aggfunc='sum'
                ).fillna(0)

                # Compute net flow
                if 'Deposits' in actual_pivot.columns and 'Withdrawals' in actual_pivot.columns:
                    actual_pivot['net_flow'] = actual_pivot['Deposits'] - actual_pivot['Withdrawals']
                    
                    # Determine forecast range
                    forecast_start = pd.Timestamp("2024-07-01")
                    # forecast_end = min(
                        # max(forecast.index.max() for forecast in self.forecasts.values() if not forecast.empty),
                        # pd.Timestamp("2024-12-31")
                    # )
                    forecast_end = pd.Timestamp("2024-12-31")

                    
                    # Subset actual
                    actual_subset = actual_pivot.loc[(actual_pivot.index >= forecast_start) & (actual_pivot.index <= forecast_end)]
                    actual_sum = actual_subset['net_flow'].sum()
                    print(f"🟩 Actual Net Flow ({forecast_start.date()} to {forecast_end.date()}): ${actual_sum:,.0f}")
                    
                    for name, forecast in self.forecasts.items():
                        if not forecast.empty:
                            forecast_range = forecast.loc[(forecast.index >= forecast_start) & (forecast.index <= forecast_end)]
                            forecast_sum = forecast_range.sum()
                            abs_err = abs(forecast_sum - actual_sum)
                            pct_err = abs_err / abs(actual_sum) if actual_sum != 0 else float('inf')
                            print(f"🔹 {name:15}: ${forecast_sum:,.0f} | Error: ${abs_err:,.0f} ({pct_err:.2%})")
                        else:
                            print(f"⚠️  {name:15}: No forecast data available in range")
                else:
                    print("❌ Missing 'Deposits' or 'Withdrawals' in actual data")

            else:
                print("❌ File not found: daily_cash_flows_backtest_2024.csv")

        except Exception as e:
            print(f"❌ Error during net cash flow comparison: {e}")

    
    def save_forecasts(self):
        """Save forecast results"""
        print("\n=== Saving Forecast Results ===")
        
        if not self.forecasts:
            print("No forecasts to save")
            return
        
        output_dir = Path("output/forecasts")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save to CSV
        forecast_df = pd.DataFrame(self.forecasts)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_file = output_dir / f"cash_flow_forecasts_v2_{timestamp}.csv"
        forecast_df.to_csv(csv_file)
        print(f"Forecasts saved to: {csv_file}")
        
        # Save summary
        summary = {
            'timestamp': timestamp,
            'forecast_period': {
                'start_date': forecast_df.index.min().strftime('%Y-%m-%d'),
                'end_date': forecast_df.index.max().strftime('%Y-%m-%d'),
                'total_days': len(forecast_df)
            },
            'models_used': list(forecast_df.columns),
            'forecast_summary': {}
        }
        
        for name, forecast in forecast_df.items():
            if not forecast.isna().all():
                data = forecast
                summary['forecast_summary'][name] = {
                    'mean_usd_millions': float(data.mean()),
                    'std_usd_millions': float(data.std()),
                    'min_usd_millions': float(data.min()),
                    'max_usd_millions': float(data.max()),
                    'positive_days': int((data > 0).sum()),
                    'negative_days': int((data < 0).sum()),
                    'positive_percentage': float((data > 0).mean())
                }
        
        import json
        json_file = output_dir / f"forecast_summary_v2_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Forecast summary saved to: {json_file}")
        return summary


def main():
    """Main execution function"""
    print("Cash Flow Forecasting System V2")
    print("=" * 50)
    
    forecaster = CashFlowForecasterV2()
    
    try:
        # 1. Load data
        forecaster.load_and_prepare_data()
        
        # 2. Create features
        forecaster.create_features()
        
        # 3. Train models
        forecaster.fit_arima_model()
        forecaster.fit_seasonal_model()
        forecaster.fit_ml_models()
        
        # 4. Generate forecasts
        forecasts = forecaster.generate_forecasts(forecast_days=184)
        
        # 5. Visualize results
        forecaster.visualize_forecasts()
        
        # 6. Save results
        # summary = forecaster.save_forecasts()
        
        print("\n" + "=" * 50)
        print("✅ Cash flow forecasting completed!")
        print(f"📊 Generated {len(forecasts)} days of forecasts")
        print(f"🎯 Models used: {list(forecasts.keys())}")
        print(f"📁 Results saved to output/ directory")
        
    except Exception as e:
        print(f"❌ Error in forecasting process: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
