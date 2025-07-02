"""
X-Date Prediction Project Configuration
预测美国联邦政府"X日"项目配置文件
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pydantic import BaseSettings
from dataclasses import dataclass


class ProjectSettings(BaseSettings):
    """项目基础设置"""
    
    # 项目基本信息
    PROJECT_NAME: str = "US Federal Government X-Date Prediction"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "预测美国联邦政府债务上限危机X日的综合分析框架"
    
    # 数据存储路径
    DATA_DIR: str = "./data"
    RAW_DATA_DIR: str = "./data/raw"
    PROCESSED_DATA_DIR: str = "./data/processed"
    MODEL_DIR: str = "./models"
    OUTPUT_DIR: str = "./output"
    LOG_DIR: str = "./logs"
    
    # API配置
    BLOOMBERG_API_HOST: str = "localhost"
    BLOOMBERG_API_PORT: int = 8194
    
    # Treasury API 配置
    TREASURY_API_BASE_URL: str = "https://api.fiscaldata.treasury.gov/services/api/v1"
    
    # BEA API 配置  
    BEA_API_BASE_URL: str = "https://apps.bea.gov/api/data"
    BEA_API_KEY: Optional[str] = None
    
    # 时间配置
    DEFAULT_START_DATE: str = "2020-01-01"
    DEFAULT_END_DATE: str = "2025-12-31"
    
    class Config:
        env_file = ".env"


@dataclass
class BusinessObjectives:
    """1.1 业务目标定义"""
    
    # 核心输出定义
    core_outputs: Dict[str, str] = None
    
    # 决策用途
    decision_purposes: List[str] = None
    
    # 目标用户
    target_users: List[str] = None
    
    def __post_init__(self):
        if self.core_outputs is None:
            self.core_outputs = {
                "x_date_prediction": "预测X日时间窗口（置信区间）",
                "uncertainty_quantification": "量化预测不确定性（概率分布）",
                "edge_policy_probability": "边缘政策触发概率（30天、1周、1天警戒线）",
                "scenario_analysis": "情景分析结果（经济衰退、政治僵局等）",
                "cost_impact_assessment": "边缘政策经济成本评估"
            }
        
        if self.decision_purposes is None:
            self.decision_purposes = [
                "应急准备和风险管理",
                "立法建议和政策制定",
                "风险沟通和公众教育", 
                "信用评级应对和市场沟通",
                "财政部非常规措施部署决策",
                "投资组合风险管理"
            ]
        
        if self.target_users is None:
            self.target_users = [
                "财政部官员和政策制定者",
                "国会预算办公室分析师",
                "金融机构风险管理团队",
                "信用评级机构",
                "学术研究机构",
                "新闻媒体和公众"
            ]


@dataclass 
class KeyMetrics:
    """1.2 关键指标定义"""
    
    # 预测精度指标
    accuracy_metrics: Dict[str, str] = None
    
    # 不确定性量化指标
    uncertainty_metrics: Dict[str, str] = None
    
    # 预警系统指标
    alert_metrics: Dict[str, str] = None
    
    # 业务价值指标
    business_metrics: Dict[str, str] = None
    
    def __post_init__(self):
        if self.accuracy_metrics is None:
            self.accuracy_metrics = {
                "MAPE": "平均绝对百分比误差 < 15%",
                "RMSE": "均方根误差（天数）< 7天",
                "MAE": "平均绝对误差（天数）< 5天",
                "Hit_Rate": "X日落在预测区间的概率 > 80%"
            }
        
        if self.uncertainty_metrics is None:
            self.uncertainty_metrics = {
                "Confidence_Interval_Coverage": "置信区间覆盖率 > 90%",
                "Prediction_Interval_Width": "预测区间宽度 < 14天",
                "Calibration_Score": "概率校准分数 > 0.85"
            }
        
        if self.alert_metrics is None:
            self.alert_metrics = {
                "Early_Warning_Lead_Time": "警报提前量 > 30天",
                "False_Positive_Rate": "误报率 < 10%", 
                "Alert_Precision": "警报精确度 > 85%"
            }
        
        if self.business_metrics is None:
            self.business_metrics = {
                "Model_Update_Frequency": "模型更新频率：每日",
                "Data_Freshness": "数据新鲜度：< 24小时",
                "Dashboard_Response_Time": "仪表板响应时间 < 3秒",
                "Stakeholder_Satisfaction": "利益相关者满意度 > 4.0/5.0"
            }


@dataclass
class ResourceRequirements:
    """1.3 资源准备清单"""
    
    # API访问权限
    api_access: Dict[str, Dict] = None
    
    # 数据源配置
    data_sources: Dict[str, Dict] = None
    
    # 计算资源
    compute_resources: Dict[str, str] = None
    
    # 团队技能要求
    team_skills: List[str] = None
    
    def __post_init__(self):
        if self.api_access is None:
            self.api_access = {
                "Bloomberg_BLPAPI": {
                    "status": "pending",
                    "priority": "high",
                    "cost_estimate": "$24,000/year",
                    "features": ["实时市场数据", "政府债券信息", "CDS利差"]
                },
                "Treasury_FiscalData": {
                    "status": "free_public_api",
                    "priority": "critical", 
                    "features": ["DTS数据", "MTS数据", "债务时间表"]
                },
                "BEA_API": {
                    "status": "free_registration_required",
                    "priority": "high",
                    "features": ["GDP数据", "经济指标", "NIPA账户"]
                },
                "FRED_API": {
                    "status": "free_public_api", 
                    "priority": "medium",
                    "features": ["联邦利率", "经济时间序列"]
                }
            }
        
        if self.data_sources is None:
            self.data_sources = {
                "Daily_Treasury_Statement": {
                    "url": "https://api.fiscaldata.treasury.gov/services/api/v1/accounting/dts",
                    "update_frequency": "daily",
                    "historical_availability": "2005-present"
                },
                "Monthly_Treasury_Statement": {
                    "url": "https://api.fiscaldata.treasury.gov/services/api/v1/accounting/mts", 
                    "update_frequency": "monthly",
                    "historical_availability": "1981-present"
                },
                "CBO_Budget_Projections": {
                    "source": "manual_collection",
                    "update_frequency": "quarterly",
                    "format": "PDF/Excel reports"
                }
            }
        
        if self.compute_resources is None:
            self.compute_resources = {
                "Development_Environment": "本地开发 + 云端训练",
                "Storage_Requirements": "500GB+ 用于历史数据存储",
                "Memory_Requirements": "32GB+ RAM 用于大规模时间序列处理",
                "GPU_Requirements": "NVIDIA GPU（深度学习模型训练）"
            }
        
        if self.team_skills is None:
            self.team_skills = [
                "Python数据科学生态系统",
                "时间序列分析和预测",
                "机器学习和深度学习",
                "金融市场和宏观经济知识",
                "API集成和数据工程",
                "数据可视化和仪表板开发",
                "统计建模和不确定性量化",
                "云计算和MLOps"
            ]


# 创建全局配置实例
settings = ProjectSettings()
business_objectives = BusinessObjectives()
key_metrics = KeyMetrics()  
resource_requirements = ResourceRequirements()


# 验证函数
def validate_project_setup():
    """验证项目设置和依赖"""
    validation_results = {
        "directories_created": False,
        "api_keys_configured": False,
        "dependencies_installed": False,
        "data_access_tested": False
    }
    
    # 检查目录结构
    required_dirs = [
        settings.DATA_DIR, settings.RAW_DATA_DIR, 
        settings.PROCESSED_DATA_DIR, settings.MODEL_DIR,
        settings.OUTPUT_DIR, settings.LOG_DIR
    ]
    
    all_dirs_exist = all(os.path.exists(d) for d in required_dirs)
    validation_results["directories_created"] = all_dirs_exist
    
    # 检查API密钥
    api_keys_present = bool(settings.BEA_API_KEY)
    validation_results["api_keys_configured"] = api_keys_present
    
    return validation_results


if __name__ == "__main__":
    print("=== X-Date Prediction Project Configuration ===")
    print(f"Project: {settings.PROJECT_NAME}")
    print(f"Version: {settings.VERSION}")
    print("\n=== Business Objectives ===")
    print("Core Outputs:", list(business_objectives.core_outputs.keys()))
    print("Decision Purposes:", len(business_objectives.decision_purposes), "identified")
    
    print("\n=== Key Metrics ===") 
    print("Accuracy Metrics:", list(key_metrics.accuracy_metrics.keys()))
    print("Alert Metrics:", list(key_metrics.alert_metrics.keys()))
    
    print("\n=== Resource Requirements ===")
    print("API Access Required:", list(resource_requirements.api_access.keys()))
    print("Team Skills:", len(resource_requirements.team_skills), "skills identified")
    
    print("\n=== Validation ===")
    results = validate_project_setup()
    for check, status in results.items():
        status_symbol = "✓" if status else "✗"
        print(f"{status_symbol} {check}") 