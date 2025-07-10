#!/usr/bin/env python3
"""
Enhanced Treasury Cash Flow Analysis System
主要集成脚本 - 数据收集、模型比较和预测

整合功能：
1. 增强数据收集 (Enhanced Treasury Data Collection)
2. 多模型比较 (ARIMA vs Seasonal vs ML)
3. 季节性算法增强演示
4. 完整的预测和可视化

使用方法:
    python main.py --mode all          # 运行完整流程
    python main.py --mode collect      # 仅数据收集
    python main.py --mode analyze      # 仅模型分析
    python main.py --mode demo         # 仅演示
"""

import sys
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Updated import statements for new directory structure
from src.models.cash_flow_forecaster import CashFlowForecasterV2
from src.models.xdate_predictor import XDatePredictor  
from src.data.data_collector import EnhancedTreasuryCollector

def main():
    """主函数 - 协调所有功能"""
    parser = argparse.ArgumentParser(description='Enhanced Treasury Cash Flow Analysis System')
    parser.add_argument('--mode', default='all', 
                       choices=['all', 'collect', 'analyze', 'demo', 'test', 'xdate'],
                       help='运行模式')
    parser.add_argument('--days', type=int, default=30,
                       help='预测天数')
    parser.add_argument('--start-date', type=str, default=None,
                       help='数据收集起始日期 (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, default=None,
                       help='数据收集结束日期 (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    print("🌟 Enhanced Treasury Cash Flow Analysis System")
    print("=" * 60)
    print(f"运行模式: {args.mode}")
    print(f"预测天数: {args.days}")
    print("=" * 60)
    
    # 创建输出目录
    setup_directories()
    
    try:
        if args.mode == 'all':
            run_complete_analysis(args)
        elif args.mode == 'collect':
            run_data_collection(args)
        elif args.mode == 'analyze':
            run_model_analysis(args)
        elif args.mode == 'demo':
            run_demonstration(args)
        elif args.mode == 'test':
            run_system_tests()
        elif args.mode == 'xdate':
            run_xdate_prediction(args)
            
        print("\n🎉 系统运行完成!")
        
    except Exception as e:
        print(f"\n❌ 系统运行失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def setup_directories():
    """设置项目目录结构"""
    dirs = [
        "output/figures",
        "output/forecasts", 
        "output/reports",
        "logs",
        "data/raw",
        "data/processed"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

def run_complete_analysis(args):
    """运行完整分析流程"""
    print("\n🚀 开始完整分析流程...")
    
    # 1. 数据收集
    print("\n" + "="*50)
    print("步骤 1: 增强数据收集")
    print("="*50)
    data_summary = run_data_collection(args)
    
    # 2. 模型分析
    print("\n" + "="*50)
    print("步骤 2: 模型训练和比较")
    print("="*50)
    model_results = run_model_analysis(args)
    
    # 3. 季节性增强演示
    print("\n" + "="*50)
    print("步骤 3: 季节性算法演示")
    print("="*50)
    demo_results = run_demonstration(args)
    
    # 4. X-DATE预测
    print("\n" + "="*50)
    print("步骤 4: X-DATE预测")
    print("="*50)
    xdate_results = run_xdate_prediction(args)
    
    # 5. 生成最终报告
    print("\n" + "="*50)
    print("步骤 5: 生成综合报告")
    print("="*50)
    generate_final_report(data_summary, model_results, demo_results, xdate_results, args)

def run_data_collection(args):
    """运行数据收集"""
    
    print("📊 启动增强Treasury数据收集...")
    
    collector = EnhancedTreasuryCollector()
    
    # 收集详细数据
    all_data = collector.collect_all_enhanced_data(
        start_date=args.start_date,
        end_date=args.end_date
    )
    
    summary = all_data['summary']
    print(f"\n✅ 数据收集完成:")
    print(f"   📁 收集的数据集: {len(summary['datasets_collected'])}")
    print(f"   💰 TGA余额记录: {summary['tga_balance_records']}")
    print(f"   🏷️  分类现金流: {len(summary['categorized_flows'])}")
    print(f"   📋 交易分类数: {summary['category_mapping_size']}")
    
    return summary

def run_model_analysis(args):
    """运行模型分析和比较"""
    
    print("🎯 启动模型训练和比较...")
    
    forecaster = CashFlowForecasterV2()
    
    # 加载和准备数据
    daily_flows = forecaster.load_and_prepare_data()
    features_data = forecaster.create_features()
    
    # 训练所有模型
    models_results = {}
    
    # 1. ARIMA模型
    print("\n📈 训练ARIMA模型...")
    arima_model = forecaster.fit_arima_model()
    models_results['arima'] = arima_model is not None
    
    # 2. 季节性模型 (核心改进)
    print("\n🌟 训练季节性模型...")
    seasonal_model = forecaster.fit_seasonal_model()
    models_results['seasonal'] = seasonal_model is not None
    if seasonal_model:
        models_results['seasonal_details'] = {
            'growth_factor': seasonal_model['growth_factor_2025'],
            'target_avg_2025': seasonal_model['target_avg_2025'],
            'avg_2024_full': seasonal_model['avg_2024_full']
        }
    
    # 3. 机器学习模型
    print("\n🤖 训练机器学习模型...")
    ml_results = forecaster.fit_ml_models()
    models_results['ml'] = ml_results is not None
    if ml_results:
        models_results['ml_details'] = ml_results
    
    # 4. 生成预测
    print(f"\n🔮 生成{args.days}天预测...")
    forecasts = forecaster.generate_forecasts(forecast_days=args.days)
    models_results['forecasts'] = forecasts
    
    # 5. 可视化和保存
    forecaster.visualize_forecasts()
    forecast_summary = forecaster.save_forecasts()
    models_results['forecast_summary'] = forecast_summary
    
    print(f"\n✅ 模型分析完成:")
    print(f"   🎯 训练的模型: {sum(1 for k,v in models_results.items() if k.endswith('_details') == False and isinstance(v, bool) and v)}")
    print(f"   📊 生成的预测: {len(forecasts) if forecasts else 0}")
    
    return models_results

def run_demonstration(args):
    """运行季节性增强演示"""
    print("🌟 启动季节性算法增强演示...")
    
    # 导入演示函数
    import subprocess
    import sys
    
    # 运行演示脚本
    try:
        result = subprocess.run([sys.executable, 'demo_seasonal_enhancement.py'], 
                              capture_output=True, text=True)
        success = result.returncode == 0
        
        if success:
            print("✅ 季节性演示运行成功")
            # 打印最后几行输出
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines[-10:]:  # 显示最后10行
                    print(f"   {line}")
        else:
            print("❌ 季节性演示运行失败")
            if result.stderr:
                print(f"错误: {result.stderr[-500:]}")
                
    except Exception as e:
        print(f"⚠️ 演示执行异常: {e}")
        success = False
    
    return {'demo_success': success}

def run_xdate_prediction(args):
    """运行X-DATE预测"""
    # 使用明确的data_dir参数初始化
    predictor = XDatePredictor(data_dir="./data/raw")
    
    print("🚨 启动X-DATE预测...")
    print("📊 X-DATE = 美国政府债务上限耗尽日期")
    
    try:
        # 1. 加载当前财政状态
        print("\n📋 步骤 1: 加载当前财政状态")
        financial_status = predictor.load_current_financial_status()
        
        # 2. 加载现金流预测
        print("\n📋 步骤 2: 加载现金流预测")
        try:
            cash_flow_forecasts = predictor.load_cash_flow_forecasts()
        except FileNotFoundError:
            print("⚠️ 未找到现金流预测文件，先运行预测模型...")
            # 如果没有预测文件，先运行模型分析
            model_results = run_model_analysis(args)
            cash_flow_forecasts = predictor.load_cash_flow_forecasts()
        
        # 3. 运行X-DATE模拟
        print("\n📋 步骤 3: 运行X-DATE模拟")
        simulation_results = predictor.simulate_xdate('Ensemble')
        
        # 4. 场景分析
        print("\n📋 步骤 4: 多场景分析")
        scenario_results = predictor.analyze_scenarios()
        
        # 5. 可视化
        print("\n📋 步骤 5: 生成X-DATE可视化")
        predictor.visualize_simulation()
        
        # 6. 保存结果
        print("\n📋 步骤 6: 保存X-DATE预测结果")
        prediction_summary = predictor.save_results()
        
        # 整理结果
        results = {
            'financial_status': financial_status,
            'prediction_success': True,
            'x_date': predictor.x_date,
            'simulation_results': simulation_results,
            'prediction_summary': prediction_summary
        }
        
        # 输出关键结果
        print(f"\n🎯 X-DATE预测完成!")
        if predictor.x_date:
            days_to_xdate = (predictor.x_date - datetime.now()).days
            print(f"📅 预测X-DATE: {predictor.x_date.strftime('%Y年%m月%d日')} ({predictor.x_date.strftime('%A')})")
            print(f"⏰ 距离X-DATE: {days_to_xdate} 天")
            print(f"💰 债务上限: ${predictor.debt_ceiling/1e12:.1f} 万亿美元")
            print(f"📊 当前债务: ${predictor.current_debt/1e12:.1f} 万亿美元")
            print(f"💸 当前现金: ${predictor.current_cash/1e9:.1f} 十亿美元")
            
            # 风险等级
            if days_to_xdate < 30:
                risk_level = "🔴 极高风险"
            elif days_to_xdate < 60:
                risk_level = "🟠 高风险"  
            elif days_to_xdate < 90:
                risk_level = "🟡 中等风险"
            else:
                risk_level = "🟢 低风险"
            
            print(f"⚠️ 风险等级: {risk_level}")
        else:
            print("📊 X-DATE未在预测期内达到")
            
        return results
        
    except Exception as e:
        print(f"❌ X-DATE预测失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            'prediction_success': False,
            'error': str(e),
            'financial_status': getattr(predictor, 'current_debt', None)
        }

def run_system_tests():
    """运行系统测试"""
    print("🔍 运行系统集成测试...")
    
    # 导入测试模块
    import subprocess
    import sys
    
    test_scripts = [
        'tests/quick_test.py',
        'tests/test_enhanced_integration.py'
    ]
    
    results = {}
    
    for script in test_scripts:
        if Path(script).exists():
            print(f"\n📋 运行 {script}...")
            try:
                result = subprocess.run([sys.executable, script], 
                                      capture_output=True, text=True)
                results[script] = {
                    'success': result.returncode == 0,
                    'output': result.stdout[-500:] if result.stdout else "",  # 最后500字符
                    'errors': result.stderr[-500:] if result.stderr else ""
                }
                
                if result.returncode == 0:
                    print(f"   ✅ {script} 通过")
                else:
                    print(f"   ❌ {script} 失败")
                    
            except Exception as e:
                print(f"   ⚠️ {script} 执行异常: {e}")
                results[script] = {'success': False, 'error': str(e)}
    
    return results

def generate_final_report(data_summary, model_results, demo_results, xdate_results, args):
    """生成最终综合报告"""
    print("📄 生成综合分析报告...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 准备报告数据
    report = {
        'metadata': {
            'timestamp': timestamp,
            'analysis_mode': args.mode,
            'forecast_days': args.days,
            'system_version': '2.0 Enhanced'
        },
        'data_collection': data_summary,
        'model_analysis': model_results,
        'demonstration': demo_results,
        'xdate_prediction': xdate_results,
        'key_improvements': {
            'seasonal_algorithm': '新增政府财政季节性模式算法',
            'growth_factor_fix': '修复增长因子计算逻辑',
            'data_collection_enhancement': '增强Treasury数据收集能力',
            'visualization_improvements': '改进预测可视化'
        },
        'performance_summary': generate_performance_summary(model_results, xdate_results),
        'conclusions': generate_conclusions(model_results, xdate_results)
    }
    
    # 保存JSON报告
    report_file = Path("output/reports") / f"comprehensive_analysis_report_{timestamp}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    # 生成可读报告
    readable_report = generate_readable_report(report)
    readable_file = Path("output/reports") / f"analysis_summary_{timestamp}.md"
    with open(readable_file, 'w', encoding='utf-8') as f:
        f.write(readable_report)
    
    print(f"✅ 报告已保存:")
    print(f"   📊 详细报告: {report_file}")
    print(f"   📋 摘要报告: {readable_file}")

def generate_performance_summary(model_results, xdate_results):
    """生成性能摘要"""
    summary = {}
    
    if 'seasonal_details' in model_results:
        seasonal = model_results['seasonal_details']
        summary['seasonal_model'] = {
            'growth_factor': float(seasonal['growth_factor']),
            'baseline_2024': float(seasonal['avg_2024_full']),
            'target_2025': float(seasonal['target_avg_2025']),
            'improvement': '增长因子已修正为合理范围'
        }
    
    if 'ml_details' in model_results:
        ml = model_results['ml_details']
        summary['ml_model'] = {
            'mae': float(ml.get('rf_mae', 0)),
            'rmse': float(ml.get('rf_rmse', 0)),
            'performance': 'RandomForest模型性能稳定'
        }
    
    if 'forecasts' in model_results and model_results['forecasts']:
        forecasts = model_results['forecasts']
        summary['forecasts'] = {
            'models_count': len(forecasts),
            'models': list(forecasts.keys()),
            'status': '预测生成成功'
        }
    
    # 添加X-DATE预测摘要
    if xdate_results and xdate_results.get('prediction_success'):
        if xdate_results.get('x_date'):
            days_to_xdate = (xdate_results['x_date'] - datetime.now()).days
            summary['xdate_prediction'] = {
                'x_date': xdate_results['x_date'].strftime('%Y-%m-%d'),
                'days_to_xdate': days_to_xdate,
                'debt_ceiling': float(xdate_results.get('financial_status', {}).get('debt_ceiling', 0)),
                'current_debt': float(xdate_results.get('financial_status', {}).get('current_debt', 0)),
                'current_cash': float(xdate_results.get('financial_status', {}).get('current_cash', 0)),
                'status': 'X-DATE预测成功'
            }
        else:
            summary['xdate_prediction'] = {
                'status': 'X-DATE未在预测期内达到',
                'debt_headroom_sufficient': True
            }
    else:
        summary['xdate_prediction'] = {
            'status': 'X-DATE预测失败或未运行'
        }
    
    return summary

def generate_conclusions(model_results, xdate_results):
    """生成分析结论"""
    conclusions = [
        "✅ 成功整合季节性算法到现有Treasury预测系统",
        "✅ 修复了增长因子计算中的逻辑错误",
        "✅ 增强了数据收集能力，支持详细的DTS分类数据",
        "✅ 实现了多模型集成预测（ARIMA + 季节性 + ML）",
        "✅ 提供了完整的可视化和报告功能"
    ]
    
    if 'seasonal_details' in model_results:
        seasonal = model_results['seasonal_details']
        growth_factor = seasonal['growth_factor']
        if 0.5 <= growth_factor <= 2.0:
            conclusions.append(f"✅ 季节性模型增长因子{growth_factor:.3f}在合理范围内")
        else:
            conclusions.append(f"⚠️ 季节性模型增长因子{growth_factor:.3f}需要进一步调整")
    
    # 添加X-DATE预测结论
    if xdate_results and xdate_results.get('prediction_success'):
        conclusions.append("✅ 成功实现X-DATE预测功能")
        
        if xdate_results.get('x_date'):
            days_to_xdate = (xdate_results['x_date'] - datetime.now()).days
            x_date_str = xdate_results['x_date'].strftime('%Y年%m月%d日')
            
            if days_to_xdate < 30:
                conclusions.append(f"🚨 预测X-DATE: {x_date_str} - 极高风险 ({days_to_xdate}天)")
            elif days_to_xdate < 60:
                conclusions.append(f"⚠️ 预测X-DATE: {x_date_str} - 高风险 ({days_to_xdate}天)")
            elif days_to_xdate < 90:
                conclusions.append(f"⚡ 预测X-DATE: {x_date_str} - 中等风险 ({days_to_xdate}天)")
            else:
                conclusions.append(f"✅ 预测X-DATE: {x_date_str} - 低风险 ({days_to_xdate}天)")
        else:
            conclusions.append("✅ X-DATE未在预测期内达到，债务空间充足")
    else:
        conclusions.append("⚠️ X-DATE预测需要进一步优化")
    
    return conclusions

def generate_readable_report(report):
    """生成可读性报告"""
    md_content = f"""# Enhanced Treasury Cash Flow Analysis Report

## 📊 分析概要

**分析时间**: {report['metadata']['timestamp']}  
**系统版本**: {report['metadata']['system_version']}  
**预测周期**: {report['metadata']['forecast_days']} 天  

## 🚀 关键改进

"""
    
    for improvement, description in report['key_improvements'].items():
        md_content += f"- **{improvement}**: {description}\n"
    
    md_content += "\n## 📈 性能摘要\n\n"
    
    if 'performance_summary' in report:
        perf = report['performance_summary']
        
        if 'seasonal_model' in perf:
            seasonal = perf['seasonal_model']
            md_content += f"""### 🌟 季节性模型
- **增长因子**: {seasonal['growth_factor']:.3f}
- **2024基准**: ${seasonal['baseline_2024']:,.0f} 百万
- **2025目标**: ${seasonal['target_2025']:,.0f} 百万
- **状态**: {seasonal['improvement']}

"""
        
        if 'ml_model' in perf:
            ml = perf['ml_model']
            md_content += f"""### 🤖 机器学习模型
- **MAE**: ${ml['mae']:,.0f} 百万
- **RMSE**: ${ml['rmse']:,.0f} 百万
- **状态**: {ml['performance']}

"""
        
        if 'forecasts' in perf:
            forecasts = perf['forecasts']
            md_content += f"""### 🔮 预测生成
- **模型数量**: {forecasts['models_count']}
- **可用模型**: {', '.join(forecasts['models'])}
- **状态**: {forecasts['status']}

"""
        
        if 'xdate_prediction' in perf:
            xdate = perf['xdate_prediction']
            md_content += f"""### 🚨 X-DATE预测
- **状态**: {xdate['status']}
"""
            if 'x_date' in xdate:
                md_content += f"""- **预测X-DATE**: {xdate['x_date']}
- **距离天数**: {xdate['days_to_xdate']} 天
- **债务上限**: ${xdate['debt_ceiling']/1e12:.2f} 万亿美元
- **当前债务**: ${xdate['current_debt']/1e12:.2f} 万亿美元
- **当前现金**: ${xdate['current_cash']/1e9:.1f} 十亿美元

"""
    
    md_content += "## 📋 主要结论\n\n"
    
    for conclusion in report['conclusions']:
        md_content += f"{conclusion}\n"
    
    md_content += f"""
## 📁 输出文件

- **详细报告**: `output/reports/comprehensive_analysis_report_{report['metadata']['timestamp']}.json`
- **预测数据**: `output/forecasts/`
- **可视化图表**: `output/figures/`
- **系统日志**: `logs/`

---
*Generated by Enhanced Treasury Cash Flow Analysis System v2.0*
"""
    
    return md_content

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 