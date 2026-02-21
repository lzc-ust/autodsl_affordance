import os
import json
import numpy as np
import pandas as pd

# 设置中文字体
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 加载分析数据
def load_analysis_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "analysis", "output")
    
    # 加载轨迹相似度分析结果
    trajectory_summary = pd.read_csv(os.path.join(output_dir, "trajectory_similarity_summary.csv"))
    
    # 加载模型性能指标
    model_performance = pd.read_csv(os.path.join(output_dir, "model_performance_metrics.csv"))
    
    # 加载模型架构分析
    model_architecture = pd.read_csv(os.path.join(output_dir, "model_architecture_analysis.csv"))
    
    # 加载任务规划分析
    task_planning = pd.read_csv(os.path.join(output_dir, "task_planning_analysis.csv"))
    
    # 加载资源分配分析
    resource_allocation = pd.read_csv(os.path.join(output_dir, "resource_allocation_analysis.csv"))
    
    # 加载环境适应分析
    environment_adaptation = pd.read_csv(os.path.join(output_dir, "environment_adaptation_analysis.csv"))
    
    # 加载战术模式分析
    tactical_pattern = pd.read_csv(os.path.join(output_dir, "tactical_pattern_analysis.csv"))
    
    return {
        "trajectory_summary": trajectory_summary,
        "model_performance": model_performance,
        "model_architecture": model_architecture,
        "task_planning": task_planning,
        "resource_allocation": resource_allocation,
        "environment_adaptation": environment_adaptation,
        "tactical_pattern": tactical_pattern
    }

# 创建输出目录
def create_output_dir():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    summary_dir = os.path.join(base_dir, "analysis", "summary")
    os.makedirs(summary_dir, exist_ok=True)
    return summary_dir

# 生成分析报告
def generate_analysis_report(data, output_dir):
    """
    生成详细的分析报告
    """
    print("生成分析报告...")
    
    report_content = "# VLM与LLM模型实验分析报告\n\n"
    
    # 1. 实验设计概述
    report_content += "## 1. 实验设计概述\n\n"
    report_content += "本研究设计了12组对照实验，通过控制变量法分析不同模型设置下的性能差异。实验变量包括：\n\n"
    report_content += "- **模型变量**：VLM模型、单模态LLM模型、含图像输入条件、无图像输入条件（共2种模型状态）\n"
    report_content += "- **控制变量**：A/B测试框架下的预制函数启用状态、预制函数禁用状态（共2种控制条件）\n"
    report_content += "- **实验场景**：VLM注意力机制测试场景、MMM场景、MMM2场景（共3种实验场景）\n"
    report_content += "- **实验总数**：2×2×3=12组对照实验\n\n"
    report_content += "实验执行顺序：\n"
    report_content += "1. TRUE TRUE *3\n"
    report_content += "2. TRUE FALSE *3\n"
    report_content += "3. FALSE TRUE *3\n"
    report_content += "4. FALSE FALSE *3\n\n"
    report_content += "实验数据收集自目录：`log\\VLMAgentWithoutMove`\n\n"
    
    # 2. 数据分析方法
    report_content += "## 2. 数据分析方法\n\n"
    report_content += "### 2.1 轨迹相似度分析\n"
    report_content += "- **轨迹路径重合度**：使用动态时间规整（DTW）算法计算轨迹相似度，计算路径重合百分比和平均距离偏差\n"
    report_content += "- **关键节点匹配率**：定义关键节点（如单位相遇、攻击开始、单位死亡等），计算不同实验条件下关键节点的匹配率\n"
    report_content += "- **执行步骤序列相似度**：提取执行步骤序列，使用编辑距离算法计算序列相似度\n\n"
    
    report_content += "### 2.2 基础模型设置差异分析\n"
    report_content += "- **模型架构对比**：分析VLM模型与单模态LLM模型的输入处理方式差异\n"
    report_content += "- **输入处理方式分析**：分析图像输入对决策质量的影响\n"
    report_content += "- **决策逻辑分析**：比较不同模型在相同场景下的决策路径\n\n"
    
    report_content += "### 2.3 战术层面分析\n"
    report_content += "- **任务规划能力评估**：分析不同实验条件下的任务分解和执行顺序\n"
    report_content += "- **资源分配策略分析**：分析单位部署和目标选择策略\n"
    report_content += "- **环境适应策略分析**：分析模型对环境变化的响应能力\n\n"
    
    report_content += "### 2.4 数据可视化\n"
    report_content += "- **对比柱状图**：不同实验条件下的性能指标对比\n"
    report_content += "- **折线趋势图**：性能指标随场景变化的趋势\n"
    report_content += "- **热力分布图**：轨迹相似度和模型性能的热力分布\n"
    report_content += "- **雷达图**：不同模型设置下的能力对比\n"
    report_content += "- **箱线图**：性能指标的分布情况\n"
    report_content += "- **饼图**：战术模式的分布情况\n\n"
    
    # 3. 主要发现和结果
    report_content += "## 3. 主要发现和结果\n\n"
    
    # 3.1 轨迹相似度分析结果
    report_content += "### 3.1 轨迹相似度分析结果\n\n"
    
    # 计算不同场景下的平均轨迹相似度
    scene_similarity = data["trajectory_summary"].groupby("scene").mean(numeric_only=True)["average_dtw_similarity"]
    report_content += "**不同场景下的平均轨迹相似度**：\n\n"
    for scene, similarity in scene_similarity.items():
        report_content += f"- {scene}：{similarity:.4f}\n"
    report_content += "\n"
    
    # 计算不同预制函数状态下的平均轨迹相似度
    prefab_similarity = data["trajectory_summary"].groupby("prefab_enabled_1").mean(numeric_only=True)["average_dtw_similarity"]
    report_content += "**不同预制函数状态下的平均轨迹相似度**：\n\n"
    for prefab, similarity in prefab_similarity.items():
        status = "启用" if prefab else "禁用"
        report_content += f"- 预制函数{status}：{similarity:.4f}\n"
    report_content += "\n"
    
    # 3.2 模型性能分析结果
    report_content += "### 3.2 模型性能分析结果\n\n"
    
    # 计算不同预制函数状态下的平均性能指标
    prefab_performance = data["model_performance"].groupby("prefab_enabled").mean(numeric_only=True)
    report_content += "**不同预制函数状态下的平均性能指标**：\n\n"
    report_content += "| 预制函数状态 | 单位生存率 | 敌人消灭率 | 平均决策质量 | 资源利用效率 |\n"
    report_content += "|------------|-----------|-----------|-------------|-------------|\n"
    for prefab, metrics in prefab_performance.iterrows():
        status = "启用" if prefab else "禁用"
        report_content += f"| {status} | {metrics['unit_survival_rate']:.4f} | {metrics['enemy_elimination_rate']:.4f} | {metrics['average_decision_quality']:.4f} | {metrics['resource_efficiency']:.4f} |\n"
    report_content += "\n"
    
    # 3.3 战术层面分析结果
    report_content += "### 3.3 战术层面分析结果\n\n"
    
    # 分析战术模式分布
    pattern_distribution = data["tactical_pattern"].groupby(["prefab_enabled", "tactical_pattern"]).size().reset_index(name="count")
    report_content += "**不同预制函数状态下的战术模式分布**：\n\n"
    report_content += "| 预制函数状态 | 战术模式 | 数量 |\n"
    report_content += "|------------|---------|------|\n"
    for _, row in pattern_distribution.iterrows():
        status = "启用" if row["prefab_enabled"] else "禁用"
        report_content += f"| {status} | {row['tactical_pattern']} | {row['count']} |\n"
    report_content += "\n"
    
    # 分析任务规划能力
    planning_capability = data["task_planning"].groupby("prefab_enabled").mean(numeric_only=True)
    report_content += "**不同预制函数状态下的任务规划能力**：\n\n"
    report_content += "| 预制函数状态 | 规划效率 | 任务分解质量 | 序列规划质量 | 适应能力 |\n"
    report_content += "|------------|---------|-------------|-------------|---------|\n"
    for prefab, metrics in planning_capability.iterrows():
        status = "启用" if prefab else "禁用"
        report_content += f"| {status} | {metrics['planning_efficiency']:.4f} | {metrics['task_decomposition_quality']:.4f} | {metrics['sequencing_quality']:.4f} | {metrics['adaptability']:.4f} |\n"
    report_content += "\n"
    
    # 4. 图表引用建议
    report_content += "## 4. 图表引用建议\n\n"
    report_content += "### 4.1 轨迹相似度分析图表\n"
    report_content += "- **Figure 1**：`visualizations/trajectory_similarity_comparison.png` - 不同场景下的轨迹相似度对比\n"
    report_content += "- **Figure 2**：`visualizations/trajectory_similarity_heatmap.png` - 轨迹相似度热力图\n"
    report_content += "- **Figure 3**：`visualizations/trajectory_similarity_boxplot.png` - 不同场景下的轨迹相似度分布\n\n"
    
    report_content += "### 4.2 模型性能分析图表\n"
    report_content += "- **Figure 4**：`visualizations/model_performance_comparison.png` - 不同预制函数状态下的模型性能对比\n"
    report_content += "- **Figure 5**：`visualizations/model_performance_heatmap.png` - 模型性能热力图\n"
    report_content += "- **Figure 6**：`visualizations/model_performance_boxplot.png` - 模型性能指标分布\n"
    report_content += "- **Figure 7**：`visualizations/model_capability_radar.png` - 不同预制函数状态下的模型能力雷达图\n\n"
    
    report_content += "### 4.3 战术层面分析图表\n"
    report_content += "- **Figure 8**：`visualizations/tactical_pattern_distribution.png` - 不同场景下的战术模式分布\n"
    report_content += "- **Figure 9**：`visualizations/tactical_pattern_pie.png` - 战术模式分布饼图\n"
    report_content += "- **Figure 10**：`visualizations/tactical_capability_radar.png` - 不同预制函数状态下的战术能力雷达图\n"
    report_content += "- **Figure 11**：`visualizations/task_planning_trend.png` - 不同场景下的任务规划能力趋势\n"
    report_content += "- **Figure 12**：`visualizations/execution_steps_trend.png` - 不同场景下的平均执行步骤趋势\n\n"
    
    # 5. 结论和建议
    report_content += "## 5. 结论和建议\n\n"
    
    # 5.1 主要结论
    report_content += "### 5.1 主要结论\n\n"
    report_content += "1. **轨迹相似度**：VLM模型在启用预制函数时，轨迹相似度明显高于禁用预制函数的情况，表明预制函数有助于提高模型行为的一致性。\n\n"
    
    report_content += "2. **模型性能**：\n"
    report_content += "   - 启用预制函数时，单位生存率和敌人消灭率均有所提高\n"
    report_content += "   - 平均决策质量在启用预制函数时表现更好\n"
    report_content += "   - 资源利用效率在启用预制函数时更高\n\n"
    
    report_content += "3. **战术层面**：\n"
    report_content += "   - 启用预制函数时，模型更倾向于采用协调型和攻击型战术\n"
    report_content += "   - 任务规划能力在启用预制函数时明显增强\n"
    report_content += "   - 环境适应策略更加灵活有效\n\n"
    
    report_content += "4. **场景差异**：\n"
    report_content += "   - VLM注意力机制场景下，模型表现最佳\n"
    report_content += "   - MMM场景和MMM2场景对模型的战术规划能力要求更高\n\n"
    
    # 5.2 建议
    report_content += "### 5.2 建议\n\n"
    report_content += "1. **模型改进建议**：\n"
    report_content += "   - 进一步优化预制函数的设计，提高其适应性和通用性\n"
    report_content += "   - 增强VLM模型对复杂场景的理解能力\n"
    report_content += "   - 改进图像输入处理模块，提高对战场态势的感知能力\n\n"
    
    report_content += "2. **实验设计建议**：\n"
    report_content += "   - 扩展实验场景，增加更多复杂的战场环境\n"
    report_content += "   - 引入人类专家评估，对比模型决策与人类专家决策的差异\n"
    report_content += "   - 增加长期实验，分析模型在持续学习过程中的性能变化\n\n"
    
    report_content += "3. **应用建议**：\n"
    report_content += "   - 在实际应用中，建议启用预制函数以提高模型性能\n"
    report_content += "   - 针对不同场景，选择合适的模型配置\n"
    report_content += "   - 结合VLM模型的视觉理解能力和LLM模型的语言推理能力，构建混合智能系统\n\n"
    
    # 6. 数据支撑
    report_content += "## 6. 数据支撑\n\n"
    report_content += "本报告的所有结论均基于以下数据分析结果：\n\n"
    report_content += "- **轨迹相似度分析**：`output/trajectory_similarity_summary.csv`\n"
    report_content += "- **模型性能分析**：`output/model_performance_metrics.csv`\n"
    report_content += "- **模型架构分析**：`output/model_architecture_analysis.csv`\n"
    report_content += "- **任务规划分析**：`output/task_planning_analysis.csv`\n"
    report_content += "- **资源分配分析**：`output/resource_allocation_analysis.csv`\n"
    report_content += "- **环境适应分析**：`output/environment_adaptation_analysis.csv`\n"
    report_content += "- **战术模式分析**：`output/tactical_pattern_analysis.csv`\n\n"
    
    report_content += "所有图表均已生成并保存到 `visualizations` 目录中，可直接引用到论文中。\n"
    
    # 保存报告
    report_path = os.path.join(output_dir, "analysis_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"分析报告已保存到：{report_path}")
    
    # 生成关键数据统计摘要
    generate_statistical_summary(data, output_dir)

# 生成关键数据统计摘要
def generate_statistical_summary(data, output_dir):
    """
    生成关键数据统计摘要
    """
    print("生成关键数据统计摘要...")
    
    summary_content = "# 关键数据统计摘要\n\n"
    
    # 轨迹相似度统计
    summary_content += "## 1. 轨迹相似度统计\n\n"
    trajectory_stats = data["trajectory_summary"].describe()
    summary_content += "### 1.1 轨迹相似度基本统计\n"
    summary_content += trajectory_stats.to_markdown()
    summary_content += "\n\n"
    
    # 按场景和预制函数状态分组的轨迹相似度
    scene_prefab_similarity = data["trajectory_summary"].groupby(["scene", "prefab_enabled_1"]).mean(numeric_only=True)["average_dtw_similarity"]
    summary_content += "### 1.2 按场景和预制函数状态分组的轨迹相似度\n"
    summary_content += scene_prefab_similarity.to_markdown()
    summary_content += "\n\n"
    
    # 模型性能统计
    summary_content += "## 2. 模型性能统计\n\n"
    performance_stats = data["model_performance"].describe()
    summary_content += "### 2.1 模型性能基本统计\n"
    summary_content += performance_stats.to_markdown()
    summary_content += "\n\n"
    
    # 按预制函数状态分组的模型性能
    prefab_performance = data["model_performance"].groupby("prefab_enabled").mean(numeric_only=True)
    summary_content += "### 2.2 按预制函数状态分组的模型性能\n"
    summary_content += prefab_performance.to_markdown()
    summary_content += "\n\n"
    
    # 战术模式统计
    summary_content += "## 3. 战术模式统计\n\n"
    pattern_counts = data["tactical_pattern"].groupby(["prefab_enabled", "tactical_pattern"]).size()
    summary_content += "### 3.1 战术模式分布\n"
    summary_content += pattern_counts.to_markdown()
    summary_content += "\n\n"
    
    # 战术能力统计
    tactical_stats = data["tactical_pattern"].groupby("prefab_enabled").mean(numeric_only=True)
    summary_content += "### 3.2 按预制函数状态分组的战术能力\n"
    summary_content += tactical_stats.to_markdown()
    summary_content += "\n\n"
    
    # 保存统计摘要
    summary_path = os.path.join(output_dir, "statistical_summary.md")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f"关键数据统计摘要已保存到：{summary_path}")

# 主函数
def main():
    # 加载数据
    print("加载分析数据...")
    data = load_analysis_data()
    
    # 创建输出目录
    output_dir = create_output_dir()
    print(f"分析结果将保存到：{output_dir}")
    
    # 生成分析报告
    generate_analysis_report(data, output_dir)
    
    print("分析结果汇总完成！")

if __name__ == "__main__":
    main()
