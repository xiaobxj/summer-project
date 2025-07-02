# US Federal Government X-Date Prediction System

A comprehensive machine learning system for predicting the "X-Date" - the critical moment when the US Treasury will exhaust its cash reserves and extraordinary measures, potentially leading to government debt default.

## 🎯 Project Overview

This project implements a sophisticated forecasting framework that combines cash flow prediction with debt ceiling simulation to predict when the United States federal government might be unable to meet all its financial obligations. The system uses multiple data sources and advanced modeling techniques to provide accurate X-Date predictions with uncertainty quantification.

### Key Features

- **Multi-Model Cash Flow Forecasting**: ARIMA, Random Forest, and ensemble models
- **Real-Time Treasury Data Integration**: Automated collection from Treasury FiscalData API
- **X-Date Simulation Engine**: Daily debt headroom tracking and simulation
- **Comprehensive Visualization**: Interactive charts and scenario analysis
- **Free Data Sources**: Complete solution using publicly available APIs
- **Uncertainty Quantification**: Confidence intervals and probability distributions

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+ required
python --version

# Clone the repository
git clone <repository-url>
cd pythonProject
```

### Installation

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Copy environment template**:
   ```bash
   cp config/env_template.txt .env
   ```

2. **Add API keys** (optional for enhanced features):
   ```
   BEA_API_KEY=your_bea_api_key_here
   FRED_API_KEY=your_fred_api_key_here
   ```

### Test Setup

```bash
# Run API connectivity tests
python scripts/phase1_api_test_simplified.py

# Verify Treasury data access
python src/data_collection/treasury_data_collector.py
```

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    X-Date Prediction System                 │
├─────────────────────────────────────────────────────────────┤
│  Data Collection → Cash Flow Forecasting → X-Date Simulation │
└─────────────────────────────────────────────────────────────┘

Data Sources:
├── Treasury FiscalData API (FREE) - Daily cash flows & debt data
├── Federal Reserve FRED API (FREE) - Economic indicators  
├── Yahoo Finance (FREE) - Market sentiment indicators
└── Bureau of Economic Analysis (FREE) - Economic data
```

## 🔄 Workflow

### 1. Data Collection
```bash
python src/data_collection/treasury_data_collector.py
```
- Fetches daily Treasury cash balances
- Collects debt outstanding data
- Downloads cash flow statements
- Saves historical data for modeling

### 2. Cash Flow Forecasting
```bash
python src/models/cash_flow_forecaster_v2.py
```
- Preprocesses historical cash flow data
- Trains multiple forecasting models (ARIMA, Random Forest)
- Generates 120-day cash flow predictions
- Creates ensemble forecasts with confidence intervals

### 3. X-Date Prediction
```bash
python src/models/xdate_predictor.py
```
- Simulates daily debt ceiling scenarios
- Models extraordinary measures depletion
- Predicts X-Date with scenario analysis
- Generates comprehensive risk assessments

## 📈 Model Performance

### Cash Flow Forecasting Results
- **Random Forest Model**: MAE < $15,000M, realistic distribution preservation
- **Ensemble Approach**: Combines ARIMA and ML models for robust predictions
- **Data Integrity**: Fixed business day reindexing bias from original 50/50 to realistic distribution

### X-Date Prediction Accuracy
- **Current Prediction**: September 6, 2025 (66 days from June 27, 2025)
- **Debt Ceiling**: $36.1 trillion (CBO March 2025 data)
- **Extraordinary Measures**: $820 billion total capacity
- **Validation**: Aligned with Congressional Budget Office estimates

## 📁 Project Structure

```
pythonProject/
├── src/                           # Source code
│   ├── data_collection/           # Data acquisition modules
│   │   ├── treasury_data_collector.py    # Treasury API client
│   │   └── market_data_alternatives.py   # Free market data sources
│   ├── models/                    # Prediction models
│   │   ├── cash_flow_forecaster_v2.py    # Cash flow forecasting
│   │   └── xdate_predictor.py            # X-Date prediction engine
│   └── utils/                     # Utility functions
├── data/                          # Data storage
│   ├── raw/                       # Raw API data
│   ├── processed/                 # Cleaned datasets
│   └── external/                  # External data sources
├── output/                        # Results and reports
│   ├── figures/                   # Visualization charts
│   ├── forecasts/                 # Prediction results
│   └── reports/                   # Analysis reports
├── config/                        # Configuration files
├── scripts/                       # Utility scripts
├── notebooks/                     # Jupyter analysis notebooks
├── tests/                         # Unit tests
├── docs/                          # Documentation
└── requirements.txt               # Python dependencies
```

## 🔧 Key Components

### TreasuryDataCollector
Automated data collection from US Treasury APIs:
- Daily Treasury Statement (DTS)
- Debt to the Penny
- Monthly Treasury Statement (MTS)
- Cash balance tracking

### CashFlowForecasterV2
Advanced cash flow prediction system:
- **Fixed Data Bias**: Resolved business day reindexing issues
- **Multi-Model Ensemble**: ARIMA + Random Forest + Historical Average
- **Feature Engineering**: 16 optimized features including lags and rolling statistics
- **Robust Validation**: Proper train/test splits with time series integrity

### XDatePredictor
Comprehensive X-Date simulation engine:
- **Debt Headroom Calculation**: `Debt Ceiling - Outstanding Debt + Extraordinary Measures`
- **Daily Simulation**: Cash flow consumption and debt issuance modeling
- **Scenario Analysis**: Multiple forecast model testing
- **Risk Assessment**: Probability distributions and confidence intervals

## 📊 Current Predictions (Latest Run)

### Financial Status Summary
- **Current Debt**: $36.22 trillion
- **Debt Ceiling**: $36.1 trillion  
- **Cash Balance**: $500 billion
- **Extraordinary Measures**: $820 billion
- **Effective Headroom**: $704 billion

### X-Date Forecast
- **Predicted X-Date**: September 6, 2025
- **Days Until X-Date**: 66 days
- **Confidence Level**: High (based on CBO-validated parameters)
- **Trigger Event**: Debt headroom exhaustion + extraordinary measures depletion

## 🆓 Free Data Sources

This project uses entirely free, publicly available data sources:

### Primary Sources (Critical)
- **Treasury FiscalData API**: Real-time federal cash flows and debt data
- **Yahoo Finance**: Market sentiment and Treasury yield proxies
- **Federal Reserve Economic Data (FRED)**: Economic indicators

### Optional Sources (Enhanced Features)
- **Bureau of Economic Analysis (BEA)**: GDP and economic statistics
- **Alpha Vantage**: Additional economic indicators

### Bloomberg Alternative Strategy
The system provides a complete Bloomberg-free solution using:
- FRED for Treasury yields instead of Bloomberg government bonds
- Yahoo Finance for market indicators instead of Bloomberg market data
- VIX and credit spreads as CDS proxies

## 🧪 Testing & Validation

### API Connectivity Testing
```bash
python scripts/phase1_api_test_simplified.py
```

### Model Validation
- **Historical Backtesting**: Validated against known Treasury patterns
- **Cross-Validation**: Time series-aware validation splits
- **Benchmark Comparison**: Aligned with CBO and Treasury projections

### Quality Assurance
- **Data Integrity Checks**: Automated validation of data completeness
- **Model Performance Monitoring**: MAE, RMSE tracking
- **Prediction Confidence**: Uncertainty quantification

## 📈 Recent Improvements

### Fixed Cash Flow Forecasting Issues
1. **Resolved Business Day Bias**: Eliminated forward-fill distortion that artificially skewed data
2. **Preserved Natural Distribution**: Maintained realistic 49.6% positive / 50.4% negative cash flow pattern
3. **Simplified Model Architecture**: Reduced overfitting with streamlined feature set
4. **Enhanced Error Handling**: Robust NaN value management

### Updated Debt Ceiling Parameters
- **Real-Time Accuracy**: Updated to CBO March 2025 parameters
- **Precise X-Date Modeling**: Aligned with official Treasury projections
- **Scenario Testing**: Multiple economic conditions modeled

## 🔮 Future Enhancements

### Planned Features
- **Real-Time Dashboard**: Web-based monitoring interface
- **Alert System**: Automated X-Date proximity warnings
- **Enhanced Scenarios**: Economic recession and political gridlock modeling
- **API Integration**: REST API for external system integration

### Research Extensions
- **Machine Learning Enhancement**: Deep learning and ensemble methods
- **Economic Factor Integration**: GDP, unemployment, and market volatility
- **Political Risk Modeling**: Congressional approval and policy impact analysis

## 📚 Documentation

### Technical Documentation
- [API Setup Guide](docs/api_setup_guide.md)
- [Model Architecture](docs/model_architecture.md)
- [Data Sources](docs/data_sources.md)
- [Troubleshooting](docs/troubleshooting.md)

### Research Papers
- [Cash Flow Forecasting Methodology](docs/cash_flow_methodology.md)
- [X-Date Prediction Theory](docs/xdate_theory.md)
- [Validation and Benchmarking](docs/validation_report.md)

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push branch: `git push origin feature/new-feature`
5. Submit Pull Request

### Code Standards
- **Python Style**: PEP 8 compliance
- **Documentation**: Comprehensive docstrings
- **Testing**: Unit tests for all modules
- **Type Hints**: Full type annotation coverage

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **US Treasury Department**: For providing comprehensive public APIs
- **Congressional Budget Office**: For validation data and methodology guidance
- **Federal Reserve**: For economic data and research resources
- **Academic Community**: For time series analysis and forecasting research

## 📞 Support

### Getting Help
- **Issues**: Open GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check the docs/ directory for detailed guides

### Contact
- **Project Maintainer**: [Your Name]
- **Email**: [your.email@domain.com]
- **LinkedIn**: [Your LinkedIn Profile]

---

**⚠️ Disclaimer**: This system is for educational and research purposes. Financial decisions should not be based solely on these predictions. Always consult official Treasury and CBO projections for authoritative guidance.

**🔄 Last Updated**: July 1, 2025  
**📊 Current Model Version**: v2.1  
**🎯 Prediction Accuracy**: Validated against CBO estimates 