### **X-Date Prediction Project: Detailed Execution Plan**
### **X-Date 预测项目: 详细执行计划**

This document outlines the step-by-step plan to complete the X-Date prediction project, from environment setup to final deployment.
本文件概述了完成X-Date预测项目的详细步骤，从环境设置到最终部署。

---

### **Phase 1: Project Initialization & Environment Setup (项目初始化与环境配置)**
**Goal:** Prepare a fully functional development environment and verify all data sources.
**目标:** 准备功能齐全的开发环境，并验证所有数据源。

*   **Step 1.1: Install Python Dependencies (安装Python依赖) - `[IMMEDIATE ACTION]`**
    *   **Description (中文):** 您的虚拟环境已创建但为空。此步骤将安装 `requirements.txt` 中定义的所有76个Python包。
    *   **Description (English):** Your virtual environment is created but empty. This step will install all 76 Python packages defined in `requirements.txt`.
    *   **Command (命令):**
        ```bash
        # 1. Activate virtual environment (if not already active)
        # 1. 激活虚拟环境 (如果尚未激活)
        .venv\Scripts\Activate.ps1

        # 2. Install all required packages
        # 2. 安装所有必需的包
        pip install -r requirements.txt
        ```

*   **Step 1.2: Obtain Free API Keys (获取免费API密钥)**
    *   **Description (中文):** 项目需要访问外部数据。请访问以下链接注册并获取免费的API密钥。
    *   **Description (English):** The project requires access to external data. Please visit the following links to register and obtain your free API keys.
    *   **Action (行动):**
        1.  **FRED API Key:** [https://fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html) (For economic data / 用于经济数据)
        2.  **BEA API Key:** [https://apps.bea.gov/API/signup/](https://apps.bea.gov/API/signup/) (For GDP data / 用于GDP数据)

*   **Step 1.3: Configure Environment Variables (配置环境变量)**
    *   **Description (中文):** 将您获取的API密钥安全地存储在本地环境变量文件中。
    *   **Description (English):** Securely store your newly acquired API keys in a local environment file.
    *   **Command (命令):**
        ```bash
        # 1. Copy the template file
        # 1. 复制模板文件
        copy env_template.txt .env

        # 2. Edit the .env file with a text editor and add your API keys
        # 2. 使用文本编辑器编辑 .env 文件并填入您的API密钥
        ```

*   **Step 1.4: Verify API Connectivity (验证API连通性)**
    *   **Description (中文):** 运行我们创建的简化版API测试脚本，确保所有免费数据源都可访问。
    *   **Description (English):** Run the simplified API test script we created to ensure all free data sources are accessible.
    *   **Command (命令):**
        ```bash
        python phase1_api_test_simplified.py
        ```
    *   **Expected Outcome (预期结果):** A report showing that Treasury, Yahoo Finance, FRED, and BEA APIs are connected successfully. (一份报告显示财政部、雅虎财经、FRED和BEA的API已成功连接。)

---

### **Phase 2: Data Infrastructure Development (数据基础设施开发)**
**Goal:** Collect, clean, and process all necessary data for modeling.
**目标:** 收集、清洗并处理所有建模所需的数据。

*   **Step 2.1: Historical Data Collection (历史数据收集)**
    *   **Description (中文):** 使用 `src/data_collection/market_data_alternatives.py` 脚本下载所有相关历史数据。
    *   **Description (English):** Use the `src/data_collection/market_data_alternatives.py` script to download all relevant historical data.
    *   **Action (行动):** Modify and run the script to save data into the `data/raw/` directory. (修改并运行脚本，将数据保存到 `data/raw/` 目录。)

*   **Step 2.2: Data Cleaning & Preprocessing (数据清洗与预处理)**
    *   **Description (中文):** 创建一个新的Jupyter Notebook或Python脚本来处理原始数据，包括处理缺失值、统一日期格式等。
    *   **Description (English):** Create a new Jupyter Notebook or Python script to process the raw data, including handling missing values, standardizing date formats, etc.
    *   **Action (行动):** Save the cleaned data to the `data/processed/` directory. (将清洗后的数据保存到 `data/processed/` 目录。)

*   **Step 2.3: Feature Engineering (特征工程)**
    *   **Description (中文):** 基于清洗后的数据创建新的特征，例如计算信用利差代理指标 (VIX, HYG/TLT spread)，移动平均线等。
    *   **Description (English):** Create new features from the cleaned data, such as credit spread proxies (VIX, HYG/TLT spread), moving averages, etc.

---

### **Phase 3: Predictive Modeling (预测建模)**
**Goal:** Develop and evaluate models to predict the X-Date.
**目标:** 开发和评估用于预测X-Date的模型。

*   **Step 3.1: Develop Baseline Models (开发基线模型)**
    *   **Description (中文):** 从简单的模型开始，如线性回归或ARIMA，为性能设定一个基准。
    *   **Description (English):** Start with simple models like Linear Regression or ARIMA to set a performance benchmark.

*   **Step 3.2: Advanced Time Series Modeling (高级时间序列建模)**
    *   **Description (中文):** 应用更复杂的模型，如VAR, GARCH，来捕捉变量间的动态关系和波动性。
    *   **Description (English):** Apply more sophisticated models like VAR or GARCH to capture dynamic relationships and volatility.

*   **Step 3.3: Machine Learning & Deep Learning Models (机器学习与深度学习模型)**
    *   **Description (中文):** 探索如Gradient Boosting, LSTM, or Transformer等模型，以发现非线性模式。
    *   **Description (English):** Explore models like Gradient Boosting, LSTMs, or Transformers to find non-linear patterns.

*   **Step 3.4: Model Evaluation & Selection (模型评估与选择)**
    *   **Description (中文):** 使用交叉验证和我们定义好的关键指标 (MAPE <15%, RMSE <7 days) 来评估和选择最佳模型。
    *   **Description (English):** Use cross-validation and our defined Key Metrics (MAPE <15%, RMSE <7 days) to evaluate and select the best performing model.

---

### **Phase 4 & 5: Analysis, Visualization & Deployment (分析、可视化与部署)**
**Goal:** Interpret model results, create a user-friendly dashboard, and deploy the solution.
**目标:** 解读模型结果，创建用户友好的仪表盘，并部署解决方案。

*   **Step 4.1: Scenario Analysis (情景分析)**
    *   **Description (中文):** 使用最终模型分析不同宏观经济情景对X-Date的影响。
    *   **Description (English):** Use the final model to analyze the impact of different macroeconomic scenarios on the X-Date.

*   **Step 4.2: Develop Interactive Dashboard (开发交互式仪表盘)**
    *   **Description (中文):** 使用Streamlit或Plotly Dash在 `dashboards/` 目录中创建一个仪表盘来展示预测结果和分析。
    *   **Description (English):** Create a dashboard in the `dashboards/` directory using Streamlit or Plotly Dash to present predictions and analysis.

*   **Step 5.1: Deployment (部署)**
    *   **Description (中文):** 将仪表盘和模型部署到云平台（如Heroku, AWS）或本地服务器。
    *   **Description (English):** Deploy the dashboard and model to a cloud platform (like Heroku, AWS) or a local server. 