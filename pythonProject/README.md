# X-DATE Prediction System
**US Federal Government Debt Ceiling Crisis Predictor**

## 🎯 System Overview

This system predicts the **X-DATE** - the date when the US Federal Government will be unable to pay all its obligations due to debt ceiling constraints. The system integrates real-time Treasury data, advanced cash flow forecasting, and debt ceiling analysis to provide accurate X-DATE predictions.

### What is X-DATE?
The X-Date (also called the "Date of Extraordinary Measures Exhaustion") is the estimated date when the U.S. Treasury will have exhausted all available extraordinary measures to avoid defaulting on government obligations, unless the debt ceiling is raised or suspended.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run X-DATE Prediction
```bash
# Full X-DATE analysis with 90-day forecast
python main.py --mode xdate --days 90

# Complete system analysis (data collection + prediction)
python main.py --mode all --days 60
```

### 3. View Results
- **Visualization**: `output/figures/xdate_simulation_*.png`
- **Data**: `output/forecasts/xdate_simulation_*.csv`
- **Summary**: `output/forecasts/xdate_prediction_summary_*.json`

## 📊 Core Components

### 1. X-DATE Predictor (`xdate_predictor.py`)
- **Debt Analysis**: Current debt vs ceiling calculations
- **Cash Flow Simulation**: Daily cash balance projections
- **Extraordinary Measures**: Treasury funding mechanisms
- **X-DATE Detection**: Crisis date identification

### 2. Cash Flow Forecaster (`cash_flow_forecaster.py`)
- **ARIMA Models**: Time series forecasting
- **Seasonal Patterns**: Government fiscal behavior
- **Machine Learning**: RandomForest predictions
- **Ensemble Methods**: Combined model accuracy

### 3. Data Collector (`data_collector.py`)
- **Treasury APIs**: Real-time government data
- **Debt Outstanding**: Daily debt levels
- **Cash Balance**: Operating cash positions
- **Historical Data**: Multi-year fiscal patterns

### 4. Visualization (`xdate_visualization.py`)
- **Debt Ceiling Charts**: Focused debt vs limit views
- **Cash Flow Analysis**: Daily government operations
- **Extraordinary Measures**: Usage tracking
- **Risk Assessment**: Crisis timeline visualization

## 🎛️ Usage Modes

| Mode | Description | Command |
|------|-------------|---------|
| `xdate` | X-DATE prediction only | `python main.py --mode xdate --days 90` |
| `collect` | Data collection only | `python main.py --mode collect` |
| `analyze` | Model training only | `python main.py --mode analyze --days 30` |
| `all` | Complete pipeline | `python main.py --mode all --days 60` |

## 📈 Key Features

### ✅ Real-Time Data Integration
- Daily Treasury debt outstanding data
- Operating cash balance tracking
- Automatic data collection and processing

### ✅ Advanced Forecasting Models
- **ARIMA**: Statistical time series analysis
- **Seasonal**: Government fiscal pattern recognition
- **Random Forest**: Machine learning predictions
- **Ensemble**: Combined model consensus

### ✅ Debt Ceiling Analysis
- Current debt vs ceiling calculations
- Extraordinary measures tracking
- Crisis scenario simulation
- Risk level assessment

### ✅ Professional Visualization
- Clean, publication-ready charts
- Focused debt ceiling views
- Crisis timeline projections
- Key metrics summaries

## 🔧 System Architecture

```
X-DATE Prediction System
├── main.py                 # Main coordination script
├── xdate_predictor.py      # Core X-DATE prediction logic
├── cash_flow_forecaster.py # Cash flow forecasting models  
├── data_collector.py       # Treasury data collection
├── xdate_visualization.py  # X-DATE specific charts
├── config/                 # Configuration files
├── data/                   # Treasury data storage
└── output/                 # Predictions and visualizations
    ├── figures/            # Charts and graphs
    ├── forecasts/          # Prediction data
    └── reports/            # Analysis summaries
```

## 📋 Configuration

The system uses current fiscal parameters (as of 2025):
- **Debt Ceiling**: $36.1 trillion USD
- **Extraordinary Measures**: $820 billion capacity
- **Minimum Operating Cash**: $50 billion

These can be updated in `xdate_predictor.py` configuration section.

## 🎯 Understanding X-DATE Results

### Risk Levels
- 🔴 **Extreme Risk**: < 30 days to X-DATE
- 🟠 **High Risk**: 30-60 days to X-DATE  
- 🟡 **Medium Risk**: 60-90 days to X-DATE
- 🟢 **Low Risk**: > 90 days to X-DATE

### Key Metrics
- **Current Debt**: Total outstanding federal debt
- **Debt Headroom**: Remaining borrowing capacity
- **Cash Balance**: Treasury operating cash
- **Daily Cash Flow**: Government income/expenses
- **Extraordinary Measures**: Emergency funding usage

## 📊 Sample Output

```
🎯 X-DATE Prediction Results:
📅 Predicted X-DATE: 2025-10-15 (Monday)
⏰ Days to X-DATE: 98 days
💰 Debt Ceiling: $36.1 trillion USD
📊 Current Debt: $36.22 trillion USD
💸 Current Cash: $500.0 billion USD
⚠️ Risk Level: 🟡 Medium Risk
```

## 🔍 Validation

The system has been validated against:
- Congressional Budget Office (CBO) projections
- Treasury Department X-DATE estimates
- Historical debt ceiling crisis patterns
- Federal Reserve economic data

## 📚 Additional Resources

- `XDATE_GUIDE.md` - Detailed X-DATE methodology
- `docs/TEST_GUIDE.md` - System testing procedures
- `docs/enhanced_treasury_integration.md` - Data integration details

---

**⚠️ Disclaimer**: This system provides estimates for analytical purposes. Actual X-DATE may vary due to economic conditions, policy changes, and unforeseen events. Always consult official Treasury and CBO projections for policy decisions. 