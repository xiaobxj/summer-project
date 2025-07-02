"""
X-Date Prediction Project Setup Script
项目初始化脚本 - Phase 1: 项目启动与目标定义
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from config import settings, validate_project_setup


def create_directory_structure():
    """创建项目目录结构"""
    directories = [
        settings.DATA_DIR,
        settings.RAW_DATA_DIR, 
        settings.PROCESSED_DATA_DIR,
        settings.MODEL_DIR,
        settings.OUTPUT_DIR,
        settings.LOG_DIR,
        "./src",
        "./src/data_collection",
        "./src/models", 
        "./src/visualization",
        "./src/utils",
        "./notebooks",
        "./tests",
        "./scripts",
        "./docs",
        "./dashboards",
        "./models/trained",
        "./models/cache",
        "./data/external",
        "./output/reports",
        "./output/figures",
        "./output/forecasts"
    ]
    
    created_dirs = []
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(directory)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"⚠ Directory already exists: {directory}")
    
    return created_dirs


def create_initial_files():
    """创建初始文件"""
    files_to_create = {
        "src/__init__.py": "",
        "src/data_collection/__init__.py": "",
        "src/models/__init__.py": "",
        "src/visualization/__init__.py": "",
        "src/utils/__init__.py": "",
        "tests/__init__.py": "",
        "README.md": get_readme_content(),
        ".gitignore": get_gitignore_content(),
        "notebooks/01_data_exploration.ipynb": get_initial_notebook_content(),
        "docs/project_charter.md": get_project_charter_content()
    }
    
    created_files = []
    for file_path, content in files_to_create.items():
        path = Path(file_path)
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            created_files.append(file_path)
            print(f"✓ Created file: {file_path}")
        else:
            print(f"⚠ File already exists: {file_path}")
    
    return created_files


def get_readme_content():
    """生成README文件内容"""
    return f"""# {settings.PROJECT_NAME}

{settings.DESCRIPTION}

## Project Overview

This project implements a comprehensive framework for predicting the U.S. Federal Government's "X-Date" - the critical point when the Treasury Department is expected to exhaust its cash reserves and extraordinary measures, potentially leading to a default on government obligations.

## Key Features

- **Multi-source Data Integration**: Treasury daily statements, market indicators, economic data
- **Advanced Modeling**: Time series analysis, machine learning, Monte Carlo simulation
- **Uncertainty Quantification**: Probabilistic forecasts with confidence intervals
- **Real-time Monitoring**: Automated alerts and dashboard visualization
- **Scenario Analysis**: Stress testing under various economic and political conditions

## Project Structure

```
pythonProject/
├── src/                    # Source code
│   ├── data_collection/   # Data acquisition modules
│   ├── models/            # Prediction models
│   ├── visualization/     # Charts and dashboards
│   └── utils/             # Utility functions
├── data/                  # Data storage
│   ├── raw/              # Raw data from APIs
│   ├── processed/        # Cleaned and transformed data
│   └── external/         # External datasets
├── models/               # Trained models
├── notebooks/            # Jupyter notebooks for analysis
├── output/               # Results and reports
├── tests/                # Unit tests
└── docs/                 # Documentation
```

## Getting Started

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd pythonProject

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

1. Copy `env_template.txt` to `.env`
2. Fill in your API keys:
   - BEA API: Register at https://apps.bea.gov/API/signup/
   - FRED API: Register at https://fred.stlouisfed.org/docs/api/api_key.html
   - Bloomberg BLPAPI: Requires subscription

### 3. Initialize Project

```bash
python setup_project.py
```

### 4. Verify Setup

```bash
python config.py
```

## API Requirements

### Critical APIs
- **Treasury FiscalData API**: Free, no registration required
- **BEA (Bureau of Economic Analysis)**: Free with registration
- **FRED (Federal Reserve Economic Data)**: Free with registration

### Premium APIs
- **Bloomberg BLPAPI**: Subscription required (~$24,000/year)
  - Provides real-time market data and CDS spreads
  - Critical for market sentiment analysis

## Phase 1 Objectives

- [x] Project structure setup
- [x] Business objectives definition
- [x] Key metrics identification
- [x] Resource requirements assessment
- [ ] API access verification
- [ ] Data pipeline testing
- [ ] Initial data collection

## Business Objectives

### Core Outputs
1. **X-Date Prediction**: Time window with confidence intervals
2. **Uncertainty Quantification**: Probabilistic distribution of outcomes
3. **Edge Policy Probability**: 30-day, 1-week, 1-day warning thresholds
4. **Scenario Analysis**: Economic recession, political gridlock impacts
5. **Cost Assessment**: Economic costs of brinkmanship

### Target Users
- Treasury Department officials and policymakers
- Congressional Budget Office analysts
- Financial institution risk management teams
- Credit rating agencies
- Academic research institutions
- News media and public

## Key Performance Indicators

- **Prediction Accuracy**: MAPE < 15%, RMSE < 7 days
- **Uncertainty Metrics**: Confidence interval coverage > 90%
- **Alert System**: Early warning lead time > 30 days
- **Business Value**: Model update frequency (daily), data freshness < 24 hours

## Contributing

Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- U.S. Treasury Department for providing open data APIs
- Bureau of Economic Analysis for economic indicators
- Federal Reserve Economic Data (FRED) for financial time series
- Bipartisan Policy Center for debt ceiling analysis

## Contact

For questions or collaboration opportunities, please contact [your-email@domain.com]

---
**Version**: {settings.VERSION}  
**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
"""


def get_gitignore_content():
    """生成.gitignore文件内容"""
    return """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Project specific
data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep
models/trained/*
!models/trained/.gitkeep
logs/*
!logs/.gitkeep
output/*
!output/.gitkeep

# API keys and sensitive data
*.key
secrets/
credentials/

# Large data files
*.csv
*.xlsx
*.json
*.parquet
*.h5
*.hdf5

# Model files
*.pkl
*.joblib
*.h5
*.pb

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""


def get_initial_notebook_content():
    """生成初始Jupyter notebook内容"""
    return """{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# X-Date Prediction: Data Exploration\\n",
    "\\n",
    "## Phase 1: Initial Data Analysis\\n",
    "\\n",
    "This notebook provides an initial exploration of the data sources for X-Date prediction."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\\n",
    "import numpy as np\\n",
    "import matplotlib.pyplot as plt\\n",
    "import seaborn as sns\\n",
    "from datetime import datetime, timedelta\\n",
    "\\n",
    "# Set up plotting\\n",
    "plt.style.use('seaborn-v0_8')\\n",
    "sns.set_palette('husl')\\n",
    "%matplotlib inline"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Treasury Data Overview\\n",
    "\\n",
    "Let's start by examining the structure of Treasury data sources."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# TODO: Add data loading and exploration code\\n",
    "print('Data exploration notebook initialized.')\\n",
    "print('Next steps:')\\n",
    "print('1. Connect to Treasury FiscalData API')\\n",
    "print('2. Load historical DTS data')\\n",
    "print('3. Analyze cash balance patterns')\\n",
    "print('4. Identify seasonal trends')"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}"""


def get_project_charter_content():
    """生成项目章程内容"""
    return f"""# X-Date Prediction Project Charter

## Project Information
- **Project Name**: {settings.PROJECT_NAME}
- **Version**: {settings.VERSION}
- **Start Date**: {datetime.now().strftime('%Y-%m-%d')}
- **Project Manager**: [To be assigned]
- **Stakeholders**: Treasury officials, CBO analysts, Financial institutions

## Executive Summary

{settings.DESCRIPTION}

The project aims to provide actionable intelligence for risk management, policy formulation, and financial planning related to debt ceiling crises.

## Business Case

### Problem Statement
The U.S. debt ceiling creates recurring fiscal crises with significant economic costs. Current prediction methods lack the sophistication needed for reliable forecasting in an increasingly complex fiscal environment.

### Opportunity
Develop a comprehensive prediction framework that:
- Reduces uncertainty around X-Date timing
- Enables proactive risk management
- Minimizes economic costs of brinkmanship
- Supports evidence-based policy decisions

### Success Criteria
- Prediction accuracy within 7-day window 80% of the time
- Early warning system with 30+ day lead time
- Stakeholder adoption across government and financial sector
- Measurable reduction in market volatility during debt ceiling periods

## Scope

### In Scope
- Historical data analysis (2005-present)
- Real-time data integration from Treasury, BEA, FRED APIs
- Multiple modeling approaches (time series, ML, Monte Carlo)
- Uncertainty quantification and scenario analysis
- Interactive dashboard and alerting system
- Documentation and stakeholder training

### Out of Scope
- Real-time trading recommendations
- Political outcome prediction
- International debt ceiling analysis
- High-frequency trading applications

## Project Phases

### Phase 1: Project Startup & Goal Definition ✓
- Business objectives clarification
- Key metrics definition  
- Resource preparation

### Phase 2: Data Infrastructure (Weeks 2-4)
- API access configuration
- Data pipeline development
- Quality assurance framework

### Phase 3: Data Processing & Feature Engineering (Weeks 4-6)
- Data cleaning and transformation
- Feature selection and creation
- Time series preprocessing

### Phase 4: Model Development (Weeks 6-10)
- Baseline model implementation
- Advanced model integration
- Ensemble method development

### Phase 5: Validation & Testing (Weeks 10-12)
- Cross-validation and backtesting
- Sensitivity analysis
- Scenario testing

### Phase 6: Deployment & Monitoring (Weeks 12-14)
- Production deployment
- Monitoring system setup
- Stakeholder training

## Resources

### Team Requirements
- Data Scientist (Lead)
- Financial Analyst
- Software Engineer
- Domain Expert (Fiscal Policy)

### Technology Stack
- Python ecosystem (pandas, scikit-learn, TensorFlow)
- Bloomberg BLPAPI (if accessible)
- Cloud computing platform
- Database (PostgreSQL/MongoDB)
- Visualization (Plotly, Streamlit)

### Budget Estimates
- Bloomberg BLPAPI subscription: $24,000/year
- Cloud computing: $2,000-5,000/year
- Development tools and services: $1,000/year

## Risk Assessment

### High Risk
- Bloomberg API access dependency
- Data quality and availability issues
- Model performance in extreme scenarios

### Medium Risk
- Political sensitivity of predictions
- Stakeholder adoption challenges
- Technical complexity management

### Mitigation Strategies
- Develop fallback models without Bloomberg data
- Implement robust data validation
- Engage stakeholders early and often
- Maintain transparent methodology

## Success Metrics

### Technical Metrics
- MAPE < 15% for X-Date predictions
- Model update frequency: Daily
- System uptime: >99.5%
- Data freshness: <24 hours

### Business Metrics
- Stakeholder satisfaction: >4.0/5.0
- User adoption rate: >70% of target users
- Alert accuracy: >85%
- False positive rate: <10%

## Communication Plan

### Weekly Updates
- Progress reports to project sponsor
- Technical updates to development team
- Stakeholder briefings (bi-weekly)

### Deliverables
- Data analysis reports
- Model documentation
- User training materials
- Dashboard and API documentation

## Approval

- **Project Sponsor**: [Name, Title]
- **Technical Lead**: [Name, Title]  
- **Business Analyst**: [Name, Title]

**Date**: {datetime.now().strftime('%Y-%m-%d')}

---

*This charter serves as the foundation for the X-Date prediction project and may be updated as requirements evolve.*
"""


def install_dependencies():
    """安装项目依赖"""
    print("\n=== Installing Dependencies ===")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
        return False


def run_validation():
    """运行项目验证"""
    print("\n=== Project Validation ===")
    results = validate_project_setup()
    
    all_passed = True
    for check, status in results.items():
        status_symbol = "✓" if status else "✗"
        print(f"{status_symbol} {check.replace('_', ' ').title()}")
        if not status:
            all_passed = False
    
    if all_passed:
        print("\n🎉 Project setup completed successfully!")
        print("Next steps:")
        print("1. Copy env_template.txt to .env and add your API keys")
        print("2. Run: python config.py")
        print("3. Start with data collection: python src/data_collection/")
    else:
        print("\n⚠ Some validation checks failed. Please review and fix before proceeding.")
    
    return all_passed


def main():
    """主函数"""
    print(f"=== {settings.PROJECT_NAME} Setup ===")
    print(f"Version: {settings.VERSION}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: 创建目录结构
    print("\n=== Step 1: Creating Directory Structure ===")
    created_dirs = create_directory_structure()
    
    # Step 2: 创建初始文件
    print("\n=== Step 2: Creating Initial Files ===")
    created_files = create_initial_files()
    
    # Step 3: 安装依赖（可选）
    print("\n=== Step 3: Dependencies Installation ===")
    install_deps = input("Install dependencies now? (y/n): ").lower().strip()
    if install_deps == 'y':
        install_dependencies()
    else:
        print("⚠ Skipping dependency installation. Run 'pip install -r requirements.txt' manually.")
    
    # Step 4: 运行验证
    run_validation()
    
    print(f"\n=== Summary ===")
    print(f"Directories created: {len(created_dirs)}")
    print(f"Files created: {len(created_files)}")
    print("\nProject Phase 1 initialization complete!")


if __name__ == "__main__":
    main() 