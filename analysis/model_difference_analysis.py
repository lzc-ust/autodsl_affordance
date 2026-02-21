import os
import json
import numpy as np
import pandas as pd
from datetime import datetime

# 加载处理后的数据
def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "analysis", "output", "processed_experiments.json")
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data

# 分析模型性能指标
def analyze_model_performance(experiments):
    """
    分析不同模型设置下的性能指标
    """
    performance_metrics = []
    
    for exp in experiments:
        # 提取基本信息
        metrics = {
            "directory": exp['directory'],
            "model_type": exp['model_type'],
            "image_input": exp['image_input'],
            "prefab_enabled": exp['prefab_enabled'],
            "scene": exp['scene'],
            "total_steps": exp['total_steps'],
            "execution_time": 0,  # 执行时间
            "unit_survival_rate": 0,  # 单位生存率
            "enemy_elimination_rate": 0,  # 敌人消灭率
            "average_decision_quality": 0,  # 平均决策质量
            "resource_efficiency": 0  # 资源利用效率
        }
        
        # 计算执行时间
        if len(exp['steps']) >= 2:
            start_time = exp['steps'][0]['timestamp']
            end_time = exp['steps'][-1]['timestamp']
            
            # 解析时间戳
            try:
                start_dt = datetime.strptime(start_time, "%Y%m%d_%H%M%S_%f")
                end_dt = datetime.strptime(end_time, "%Y%m%d_%H%M%S_%f")
                execution_time = (end_dt - start_dt).total_seconds()
                metrics["execution_time"] = execution_time
            except:
                pass
        
        # 计算单位生存率
        if len(exp['steps']) >= 2:
            initial_units = set(unit['unit_name'] for unit in exp['steps'][0]['unit_info'] if unit['alliance'] == 1)
            final_units = set(unit['unit_name'] for unit in exp['steps'][-1]['unit_info'] if unit['alliance'] == 1)
            survival_rate = len(final_units) / len(initial_units) if initial_units else 0
            metrics["unit_survival_rate"] = survival_rate
        
        # 计算敌人消灭率
        if len(exp['steps']) >= 2:
            initial_enemies = set(unit['unit_name'] for unit in exp['steps'][0]['unit_info'] if unit['alliance'] == 4)
            final_enemies = set(unit['unit_name'] for unit in exp['steps'][-1]['unit_info'] if unit['alliance'] == 4)
            elimination_rate = 1 - (len(final_enemies) / len(initial_enemies)) if initial_enemies else 0
            metrics["enemy_elimination_rate"] = elimination_rate
        
        # 计算平均决策质量（基于单位健康值变化）
        if len(exp['steps']) >= 2:
            health_changes = []
            for step in exp['steps']:
                for unit in step['unit_info']:
                    if unit['alliance'] == 1:  # 只考虑我方单位
                        health_ratio = unit['health'] / unit['max_health']
                        health_changes.append(health_ratio)
            avg_health_ratio = np.mean(health_changes) if health_changes else 0
            metrics["average_decision_quality"] = avg_health_ratio
        
        # 计算资源利用效率（基于单位活动）
        if len(exp['steps']) > 0:
            total_unit_steps = sum(len(step['unit_info']) for step in exp['steps'])
            resource_efficiency = total_unit_steps / exp['total_steps'] if exp['total_steps'] > 0 else 0
            metrics["resource_efficiency"] = resource_efficiency
        
        performance_metrics.append(metrics)
    
    return performance_metrics

# 分析模型架构差异
def analyze_model_architecture_differences(experiments):
    """
    分析不同模型架构的差异
    """
    # 按场景和预制函数状态分组
    grouped_experiments = {}
    for exp in experiments:
        key = (exp['scene'], exp['prefab_enabled'])
        if key not in grouped_experiments:
            grouped_experiments[key] = []
        grouped_experiments[key].append(exp)
    
    architecture_analysis = []
    
    for (scene, prefab_enabled), group in grouped_experiments.items():
        # 分析组内实验的平均表现
        avg_metrics = {
            "scene": scene,
            "prefab_enabled": prefab_enabled,
            "model_type": group[0]['model_type'],
            "average_total_steps": 0,
            "average_execution_time": 0,
            "average_unit_survival_rate": 0,
            "average_enemy_elimination_rate": 0,
            "average_decision_quality": 0,
            "average_resource_efficiency": 0,
            "experiment_count": len(group)
        }
        
        # 计算平均值
        total_steps = []
        execution_times = []
        survival_rates = []
        elimination_rates = []
        decision_qualities = []
        resource_efficiencies = []
        
        for exp in group:
            # 计算执行时间
            exec_time = 0
            if len(exp['steps']) >= 2:
                start_time = exp['steps'][0]['timestamp']
                end_time = exp['steps'][-1]['timestamp']
                try:
                    start_dt = datetime.strptime(start_time, "%Y%m%d_%H%M%S_%f")
                    end_dt = datetime.strptime(end_time, "%Y%m%d_%H%M%S_%f")
                    exec_time = (end_dt - start_dt).total_seconds()
                except:
                    pass
            
            # 计算单位生存率
            survival_rate = 0
            if len(exp['steps']) >= 2:
                initial_units = set(unit['unit_name'] for unit in exp['steps'][0]['unit_info'] if unit['alliance'] == 1)
                final_units = set(unit['unit_name'] for unit in exp['steps'][-1]['unit_info'] if unit['alliance'] == 1)
                survival_rate = len(final_units) / len(initial_units) if initial_units else 0
            
            # 计算敌人消灭率
            elimination_rate = 0
            if len(exp['steps']) >= 2:
                initial_enemies = set(unit['unit_name'] for unit in exp['steps'][0]['unit_info'] if unit['alliance'] == 4)
                final_enemies = set(unit['unit_name'] for unit in exp['steps'][-1]['unit_info'] if unit['alliance'] == 4)
                elimination_rate = 1 - (len(final_enemies) / len(initial_enemies)) if initial_enemies else 0
            
            # 计算平均决策质量
            decision_quality = 0
            if len(exp['steps']) >= 2:
                health_changes = []
                for step in exp['steps']:
                    for unit in step['unit_info']:
                        if unit['alliance'] == 1:
                            health_ratio = unit['health'] / unit['max_health']
                            health_changes.append(health_ratio)
                decision_quality = np.mean(health_changes) if health_changes else 0
            
            # 计算资源利用效率
            resource_efficiency = 0
            if len(exp['steps']) > 0:
                total_unit_steps = sum(len(step['unit_info']) for step in exp['steps'])
                resource_efficiency = total_unit_steps / exp['total_steps'] if exp['total_steps'] > 0 else 0
            
            # 添加到列表
            total_steps.append(exp['total_steps'])
            execution_times.append(exec_time)
            survival_rates.append(survival_rate)
            elimination_rates.append(elimination_rate)
            decision_qualities.append(decision_quality)
            resource_efficiencies.append(resource_efficiency)
        
        # 计算平均值
        avg_metrics["average_total_steps"] = np.mean(total_steps)
        avg_metrics["average_execution_time"] = np.mean(execution_times)
        avg_metrics["average_unit_survival_rate"] = np.mean(survival_rates)
        avg_metrics["average_enemy_elimination_rate"] = np.mean(elimination_rates)
        avg_metrics["average_decision_quality"] = np.mean(decision_qualities)
        avg_metrics["average_resource_efficiency"] = np.mean(resource_efficiencies)
        
        architecture_analysis.append(avg_metrics)
    
    return architecture_analysis

# 分析输入处理方式差异
def analyze_input_processing_differences(experiments):
    """
    分析不同输入处理方式的差异
    """
    # 由于所有实验都使用VLM模型，我们分析有无预制函数对输入处理的影响
    input_analysis = []
    
    # 按场景分组
    scenes = {}
    for exp in experiments:
        scene = exp['scene']
        if scene not in scenes:
            scenes[scene] = []
        scenes[scene].append(exp)
    
    for scene, scene_experiments in scenes.items():
        # 分离有无预制函数的实验
        prefab_enabled_exps = [exp for exp in scene_experiments if exp['prefab_enabled']]
        prefab_disabled_exps = [exp for exp in scene_experiments if not exp['prefab_enabled']]
        
        # 分析有无预制函数的差异
        if prefab_enabled_exps and prefab_disabled_exps:
            # 计算启用预制函数的平均指标
            enabled_metrics = {
                "scene": scene,
                "prefab_status": "enabled",
                "average_total_steps": np.mean([exp['total_steps'] for exp in prefab_enabled_exps]),
                "average_unit_count": np.mean([len(exp['unit_trajectories']) for exp in prefab_enabled_exps]),
                "experiment_count": len(prefab_enabled_exps)
            }
            
            # 计算禁用预制函数的平均指标
            disabled_metrics = {
                "scene": scene,
                "prefab_status": "disabled",
                "average_total_steps": np.mean([exp['total_steps'] for exp in prefab_disabled_exps]),
                "average_unit_count": np.mean([len(exp['unit_trajectories']) for exp in prefab_disabled_exps]),
                "experiment_count": len(prefab_disabled_exps)
            }
            
            input_analysis.append(enabled_metrics)
            input_analysis.append(disabled_metrics)
    
    return input_analysis

# 分析决策逻辑差异
def analyze_decision_logic_differences(experiments):
    """
    分析不同决策逻辑的差异
    """
    decision_analysis = []
    
    # 按场景和预制函数状态分组
    grouped_experiments = {}
    for exp in experiments:
        key = (exp['scene'], exp['prefab_enabled'])
        if key not in grouped_experiments:
            grouped_experiments[key] = []
        grouped_experiments[key].append(exp)
    
    for (scene, prefab_enabled), group in grouped_experiments.items():
        # 分析决策模式
        decision_patterns = {
            "scene": scene,
            "prefab_enabled": prefab_enabled,
            "average_decision_frequency": 0,  # 平均决策频率
            "decision_consistency": 0,  # 决策一致性
            "adaptability_score": 0  # 适应性评分
        }
        
        # 计算平均决策频率
        decision_frequencies = []
        for exp in group:
            # 决策频率 = 总步骤数 / 执行时间
            if len(exp['steps']) >= 2:
                start_time = exp['steps'][0]['timestamp']
                end_time = exp['steps'][-1]['timestamp']
                try:
                    start_dt = datetime.strptime(start_time, "%Y%m%d_%H%M%S_%f")
                    end_dt = datetime.strptime(end_time, "%Y%m%d_%H%M%S_%f")
                    execution_time = (end_dt - start_dt).total_seconds()
                    if execution_time > 0:
                        decision_frequency = exp['total_steps'] / execution_time
                        decision_frequencies.append(decision_frequency)
                except:
                    pass
        
        if decision_frequencies:
            decision_patterns["average_decision_frequency"] = np.mean(decision_frequencies)
        
        # 计算决策一致性（基于单位行为模式）
        consistency_scores = []
        for exp in group:
            # 分析单位轨迹的一致性
            unit_consistencies = []
            for unit_name, trajectory in exp['unit_trajectories'].items():
                # 计算单位移动的一致性
                if len(trajectory) >= 2:
                    positions = np.array([step['position'] for step in trajectory])
                    # 计算移动距离的标准差
                    distances = np.sqrt(np.sum(np.diff(positions, axis=0)**2, axis=1))
                    if len(distances) > 0:
                        consistency = 1 / (1 + np.std(distances))  # 标准差越小，一致性越高
                        unit_consistencies.append(consistency)
            
            if unit_consistencies:
                consistency_scores.append(np.mean(unit_consistencies))
        
        if consistency_scores:
            decision_patterns["decision_consistency"] = np.mean(consistency_scores)
        
        # 计算适应性评分（基于环境变化的响应）
        adaptability_scores = []
        for exp in group:
            # 分析单位对敌人变化的响应
            if len(exp['steps']) >= 2:
                # 计算敌人单位数量的变化
                enemy_counts = []
                for step in exp['steps']:
                    enemy_count = len([unit for unit in step['unit_info'] if unit['alliance'] == 4])
                    enemy_counts.append(enemy_count)
                
                # 计算敌人数量变化率
                enemy_changes = np.diff(enemy_counts)
                if len(enemy_changes) > 0:
                    # 适应性评分 = 敌人变化率的绝对值的平均值
                    adaptability = np.mean(np.abs(enemy_changes))
                    adaptability_scores.append(adaptability)
        
        if adaptability_scores:
            decision_patterns["adaptability_score"] = np.mean(adaptability_scores)
        
        decision_analysis.append(decision_patterns)
    
    return decision_analysis

# 保存分析结果
def save_analysis_results(performance_metrics, architecture_analysis, input_analysis, decision_analysis):
    """
    保存分析结果
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "analysis", "output")
    
    # 保存性能指标
    df_performance = pd.DataFrame(performance_metrics)
    df_performance.to_csv(os.path.join(output_dir, "model_performance_metrics.csv"), index=False, encoding='utf-8-sig')
    
    # 保存架构分析
    df_architecture = pd.DataFrame(architecture_analysis)
    df_architecture.to_csv(os.path.join(output_dir, "model_architecture_analysis.csv"), index=False, encoding='utf-8-sig')
    
    # 保存输入处理分析
    df_input = pd.DataFrame(input_analysis)
    df_input.to_csv(os.path.join(output_dir, "input_processing_analysis.csv"), index=False, encoding='utf-8-sig')
    
    # 保存决策逻辑分析
    df_decision = pd.DataFrame(decision_analysis)
    df_decision.to_csv(os.path.join(output_dir, "decision_logic_analysis.csv"), index=False, encoding='utf-8-sig')
    
    print("成功保存模型差异分析结果")

if __name__ == "__main__":
    print("加载实验数据...")
    experiments = load_data()
    print(f"成功加载 {len(experiments)} 个实验")
    
    print("分析模型性能指标...")
    performance_metrics = analyze_model_performance(experiments)
    
    print("分析模型架构差异...")
    architecture_analysis = analyze_model_architecture_differences(experiments)
    
    print("分析输入处理方式差异...")
    input_analysis = analyze_input_processing_differences(experiments)
    
    print("分析决策逻辑差异...")
    decision_analysis = analyze_decision_logic_differences(experiments)
    
    print("保存分析结果...")
    save_analysis_results(performance_metrics, architecture_analysis, input_analysis, decision_analysis)
    print("模型差异分析完成！")
