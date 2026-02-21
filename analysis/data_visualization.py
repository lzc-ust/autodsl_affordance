import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches

# 设置中文字体
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

# 创建可视化结果目录
def create_visualization_dir():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vis_dir = os.path.join(base_dir, "analysis", "visualizations")
    os.makedirs(vis_dir, exist_ok=True)
    return vis_dir

# 生成对比柱状图
def generate_comparison_bar_charts(data, output_dir):
    """
    生成对比柱状图
    """
    print("生成对比柱状图...")
    
    # 1. 不同场景下的轨迹相似度对比
    plt.figure(figsize=(12, 8))
    sns.barplot(data=data["trajectory_summary"], x="scene", y="average_dtw_similarity", hue="prefab_enabled_1")
    plt.title("不同场景下的轨迹相似度对比")
    plt.xlabel("场景")
    plt.ylabel("平均DTW相似度")
    plt.ylim(0, 1)
    plt.legend(title="预制函数状态")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "trajectory_similarity_comparison.png"), dpi=300)
    plt.close()
    
    # 2. 不同预制函数状态下的模型性能对比
    performance_melted = data["model_performance"].melt(id_vars=["prefab_enabled", "scene"], 
                                                     value_vars=["unit_survival_rate", "enemy_elimination_rate", "average_decision_quality"],
                                                     var_name="指标", value_name="值")
    g = sns.catplot(data=performance_melted, x="指标", y="值", hue="prefab_enabled", col="scene", col_wrap=3, kind="bar", height=6, aspect=0.8)
    g.fig.suptitle("不同预制函数状态下的模型性能对比", y=1.02, fontsize=16)
    g.tight_layout()
    g.savefig(os.path.join(output_dir, "model_performance_comparison.png"), dpi=300)
    plt.close(g.fig)
    
    # 3. 不同场景下的战术模式分布
    plt.figure(figsize=(12, 8))
    pattern_counts = data["tactical_pattern"].groupby(["scene", "tactical_pattern"]).size().reset_index(name="count")
    sns.barplot(data=pattern_counts, x="scene", y="count", hue="tactical_pattern")
    plt.title("不同场景下的战术模式分布")
    plt.xlabel("场景")
    plt.ylabel("数量")
    plt.legend(title="战术模式")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "tactical_pattern_distribution.png"), dpi=300)
    plt.close()

# 生成折线趋势图
def generate_trend_line_charts(data, output_dir):
    """
    生成折线趋势图
    """
    print("生成折线趋势图...")
    
    # 1. 不同场景下的执行步骤趋势
    plt.figure(figsize=(12, 8))
    sns.lineplot(data=data["model_architecture"], x="scene", y="average_total_steps", hue="prefab_enabled", marker="o")
    plt.title("不同场景下的平均执行步骤趋势")
    plt.xlabel("场景")
    plt.ylabel("平均执行步骤数")
    plt.legend(title="预制函数状态")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "execution_steps_trend.png"), dpi=300)
    plt.close()
    
    # 2. 任务规划能力趋势
    plt.figure(figsize=(12, 8))
    planning_melted = data["task_planning"].melt(id_vars=["prefab_enabled", "scene"], 
                                               value_vars=["planning_efficiency", "task_decomposition_quality", "sequencing_quality"],
                                               var_name="指标", value_name="值")
    sns.lineplot(data=planning_melted, x="scene", y="值", hue="指标", style="prefab_enabled", marker="o")
    plt.title("不同场景下的任务规划能力趋势")
    plt.xlabel("场景")
    plt.ylabel("指标值")
    plt.legend(title="指标")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "task_planning_trend.png"), dpi=300)
    plt.close()

# 生成热力分布图
def generate_heatmaps(data, output_dir):
    """
    生成热力分布图
    """
    print("生成热力分布图...")
    
    # 1. 轨迹相似度热力图
    plt.figure(figsize=(12, 10))
    # 创建场景和预制函数状态的组合
    heatmap_data = data["trajectory_summary"].pivot_table(
        values="average_dtw_similarity", 
        index=["scene", "prefab_enabled_1"], 
        columns=["prefab_enabled_2"],
        aggfunc="mean"
    )
    sns.heatmap(heatmap_data, annot=True, cmap="YlGnBu", vmin=0, vmax=1)
    plt.title("轨迹相似度热力图")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "trajectory_similarity_heatmap.png"), dpi=300)
    plt.close()
    
    # 2. 模型性能热力图
    plt.figure(figsize=(12, 10))
    performance_heatmap = data["model_performance"].pivot_table(
        values=["unit_survival_rate", "enemy_elimination_rate", "average_decision_quality"],
        index=["scene", "prefab_enabled"],
        aggfunc="mean"
    )
    sns.heatmap(performance_heatmap, annot=True, cmap="YlOrRd", vmin=0, vmax=1)
    plt.title("模型性能热力图")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "model_performance_heatmap.png"), dpi=300)
    plt.close()

# 生成雷达图
def generate_radar_charts(data, output_dir):
    """
    生成雷达图
    """
    print("生成雷达图...")
    
    # 1. 不同预制函数状态下的模型能力雷达图
    from matplotlib.patches import Polygon
    
    # 准备数据
    # 只对数值类型的列计算平均值
    numeric_columns = data["model_architecture"].select_dtypes(include=["number"]).columns
    prefab_enabled_data = data["model_architecture"][data["model_architecture"]["prefab_enabled"] == True][numeric_columns].mean()
    prefab_disabled_data = data["model_architecture"][data["model_architecture"]["prefab_enabled"] == False][numeric_columns].mean()
    
    # 提取指标
    metrics = [
        "average_unit_survival_rate",
        "average_enemy_elimination_rate",
        "average_decision_quality",
        "average_resource_efficiency"
    ]
    
    # 标准化指标
    enabled_values = [prefab_enabled_data[metric] for metric in metrics]
    disabled_values = [prefab_disabled_data[metric] for metric in metrics]
    
    # 创建雷达图
    plt.figure(figsize=(10, 8))
    ax = plt.subplot(111, polar=True)
    
    # 设置角度
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]  # 闭合
    
    # 添加数据
    enabled_values += enabled_values[:1]
    disabled_values += disabled_values[:1]
    
    # 绘制多边形
    ax.plot(angles, enabled_values, 'o-', linewidth=2, label="启用预制函数")
    ax.fill(angles, enabled_values, alpha=0.25)
    ax.plot(angles, disabled_values, 's-', linewidth=2, label="禁用预制函数")
    ax.fill(angles, disabled_values, alpha=0.25)
    
    # 设置标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(["单位生存率", "敌人消灭率", "决策质量", "资源效率"])
    ax.set_ylim(0, 1)
    ax.set_title("不同预制函数状态下的模型能力对比")
    ax.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "model_capability_radar.png"), dpi=300)
    plt.close()
    
    # 2. 战术能力雷达图
    plt.figure(figsize=(10, 8))
    ax = plt.subplot(111, polar=True)
    
    # 提取战术指标
    tactical_metrics = [
        "aggressiveness",
        "defensiveness",
        "versatility",
        "coordination"
    ]
    
    # 计算平均战术指标
    prefab_enabled_tactical = data["tactical_pattern"][data["tactical_pattern"]["prefab_enabled"] == True][tactical_metrics].mean()
    prefab_disabled_tactical = data["tactical_pattern"][data["tactical_pattern"]["prefab_enabled"] == False][tactical_metrics].mean()
    
    # 标准化指标
    enabled_tactical_values = [prefab_enabled_tactical[metric] for metric in tactical_metrics]
    disabled_tactical_values = [prefab_disabled_tactical[metric] for metric in tactical_metrics]
    
    # 添加数据
    enabled_tactical_values += enabled_tactical_values[:1]
    disabled_tactical_values += disabled_tactical_values[:1]
    
    # 绘制多边形
    ax.plot(angles, enabled_tactical_values, 'o-', linewidth=2, label="启用预制函数")
    ax.fill(angles, enabled_tactical_values, alpha=0.25)
    ax.plot(angles, disabled_tactical_values, 's-', linewidth=2, label="禁用预制函数")
    ax.fill(angles, disabled_tactical_values, alpha=0.25)
    
    # 设置标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(["攻击性", "防御性", "多样性", "协调性"])
    ax.set_ylim(0, 1)
    ax.set_title("不同预制函数状态下的战术能力对比")
    ax.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "tactical_capability_radar.png"), dpi=300)
    plt.close()

# 生成箱线图
def generate_box_plots(data, output_dir):
    """
    生成箱线图
    """
    print("生成箱线图...")
    
    # 1. 轨迹相似度箱线图
    plt.figure(figsize=(12, 8))
    sns.boxplot(data=data["trajectory_summary"], x="scene", y="average_dtw_similarity", hue="prefab_enabled_1")
    plt.title("不同场景下的轨迹相似度分布")
    plt.xlabel("场景")
    plt.ylabel("DTW相似度")
    plt.ylim(0, 1)
    plt.legend(title="预制函数状态")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "trajectory_similarity_boxplot.png"), dpi=300)
    plt.close()
    
    # 2. 模型性能箱线图
    plt.figure(figsize=(12, 8))
    performance_melted = data["model_performance"].melt(id_vars=["prefab_enabled", "scene"], 
                                                     value_vars=["unit_survival_rate", "enemy_elimination_rate", "average_decision_quality"],
                                                     var_name="指标", value_name="值")
    sns.boxplot(data=performance_melted, x="指标", y="值", hue="prefab_enabled")
    plt.title("模型性能指标分布")
    plt.xlabel("指标")
    plt.ylabel("值")
    plt.ylim(0, 1)
    plt.legend(title="预制函数状态")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "model_performance_boxplot.png"), dpi=300)
    plt.close()

# 生成饼图
def generate_pie_charts(data, output_dir):
    """
    生成饼图
    """
    print("生成饼图...")
    
    # 1. 战术模式分布饼图
    plt.figure(figsize=(12, 8))
    
    # 按预制函数状态分组
    prefab_enabled_patterns = data["tactical_pattern"][data["tactical_pattern"]["prefab_enabled"] == True]["tactical_pattern"].value_counts()
    prefab_disabled_patterns = data["tactical_pattern"][data["tactical_pattern"]["prefab_enabled"] == False]["tactical_pattern"].value_counts()
    
    # 绘制两个子图
    plt.subplot(1, 2, 1)
    plt.pie(prefab_enabled_patterns, labels=prefab_enabled_patterns.index, autopct='%1.1f%%', startangle=90)
    plt.title("启用预制函数的战术模式分布")
    plt.axis('equal')
    
    plt.subplot(1, 2, 2)
    plt.pie(prefab_disabled_patterns, labels=prefab_disabled_patterns.index, autopct='%1.1f%%', startangle=90)
    plt.title("禁用预制函数的战术模式分布")
    plt.axis('equal')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "tactical_pattern_pie.png"), dpi=300)
    plt.close()

# 主函数
def main():
    # 加载数据
    print("加载分析数据...")
    data = load_analysis_data()
    
    # 创建可视化目录
    output_dir = create_visualization_dir()
    print(f"可视化结果将保存到: {output_dir}")
    
    # 生成各种图表
    generate_comparison_bar_charts(data, output_dir)
    generate_trend_line_charts(data, output_dir)
    generate_heatmaps(data, output_dir)
    generate_radar_charts(data, output_dir)
    generate_box_plots(data, output_dir)
    generate_pie_charts(data, output_dir)
    
    print("数据可视化完成！所有图表已保存到 visualizations 目录。")

if __name__ == "__main__":
    main()
