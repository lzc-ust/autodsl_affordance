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

# 分析任务规划能力
def analyze_task_planning(experiments):
    """
    分析不同实验条件下的任务规划能力
    """
    planning_analysis = []
    
    for exp in experiments:
        # 提取任务规划相关指标
        planning_metrics = {
            "directory": exp['directory'],
            "model_type": exp['model_type'],
            "prefab_enabled": exp['prefab_enabled'],
            "scene": exp['scene'],
            "planning_efficiency": 0,  # 规划效率
            "task_decomposition_quality": 0,  # 任务分解质量
            "sequencing_quality": 0,  # 序列规划质量
            "adaptability": 0  # 适应能力
        }
        
        # 计算规划效率（基于执行步骤数和完成度）
        if len(exp['steps']) >= 2:
            # 计算敌人消灭率作为完成度指标
            initial_enemies = set(unit['unit_name'] for unit in exp['steps'][0]['unit_info'] if unit['alliance'] == 4)
            final_enemies = set(unit['unit_name'] for unit in exp['steps'][-1]['unit_info'] if unit['alliance'] == 4)
            completion_rate = 1 - (len(final_enemies) / len(initial_enemies)) if initial_enemies else 0
            
            # 规划效率 = 完成度 / 执行步骤数
            planning_efficiency = completion_rate / exp['total_steps'] if exp['total_steps'] > 0 else 0
            planning_metrics["planning_efficiency"] = planning_efficiency
        
        # 计算任务分解质量（基于单位活动多样性）
        if len(exp['steps']) > 0:
            # 分析不同单位的活动模式
            unit_activities = {}
            for step in exp['steps']:
                for unit in step['unit_info']:
                    unit_name = unit['unit_name']
                    if unit_name not in unit_activities:
                        unit_activities[unit_name] = []
                    # 记录单位健康值变化作为活动指标
                    health_ratio = unit['health'] / unit['max_health']
                    unit_activities[unit_name].append(health_ratio)
            
            # 计算单位活动多样性
            activity_diversity = len(unit_activities) / len(exp['steps'][0]['unit_info']) if exp['steps'][0]['unit_info'] else 0
            planning_metrics["task_decomposition_quality"] = activity_diversity
        
        # 计算序列规划质量（基于步骤间的过渡平滑度）
        if len(exp['steps']) >= 3:
            transition_smoothness = []
            for i in range(1, len(exp['steps']) - 1):
                # 计算单位数量变化的平滑度
                prev_count = len(exp['steps'][i-1]['unit_info'])
                curr_count = len(exp['steps'][i]['unit_info'])
                next_count = len(exp['steps'][i+1]['unit_info'])
                
                # 计算变化率
                if prev_count > 0 and next_count > 0:
                    change_rate = abs(curr_count - prev_count) / prev_count
                    transition_smoothness.append(1 - change_rate)  # 变化率越小，平滑度越高
            
            if transition_smoothness:
                planning_metrics["sequencing_quality"] = np.mean(transition_smoothness)
        
        # 计算适应能力（基于环境变化的响应）
        if len(exp['steps']) >= 2:
            # 分析敌人单位数量的变化
            enemy_counts = []
            for step in exp['steps']:
                enemy_count = len([unit for unit in step['unit_info'] if unit['alliance'] == 4])
                enemy_counts.append(enemy_count)
            
            # 计算敌人数量变化的响应
            enemy_changes = np.diff(enemy_counts)
            if len(enemy_changes) > 0:
                # 适应能力 = 敌人变化的响应程度
                adaptability = np.mean(np.abs(enemy_changes))
                planning_metrics["adaptability"] = adaptability
        
        planning_analysis.append(planning_metrics)
    
    return planning_analysis

# 分析资源分配策略
def analyze_resource_allocation(experiments):
    """
    分析不同实验条件下的资源分配策略
    """
    allocation_analysis = []
    
    for exp in experiments:
        # 提取资源分配相关指标
        allocation_metrics = {
            "directory": exp['directory'],
            "model_type": exp['model_type'],
            "prefab_enabled": exp['prefab_enabled'],
            "scene": exp['scene'],
            "resource_utilization": 0,  # 资源利用率
            "target_selection_efficiency": 0,  # 目标选择效率
            "unit_deployment_strategy": 0,  # 单位部署策略
            "priority_setting": 0  # 优先级设置
        }
        
        # 计算资源利用率（基于单位活动）
        if len(exp['steps']) > 0:
            total_unit_steps = sum(len(step['unit_info']) for step in exp['steps'])
            resource_utilization = total_unit_steps / exp['total_steps'] if exp['total_steps'] > 0 else 0
            allocation_metrics["resource_utilization"] = resource_utilization
        
        # 计算目标选择效率（基于敌人消灭率）
        if len(exp['steps']) >= 2:
            initial_enemies = set(unit['unit_name'] for unit in exp['steps'][0]['unit_info'] if unit['alliance'] == 4)
            final_enemies = set(unit['unit_name'] for unit in exp['steps'][-1]['unit_info'] if unit['alliance'] == 4)
            elimination_rate = 1 - (len(final_enemies) / len(initial_enemies)) if initial_enemies else 0
            allocation_metrics["target_selection_efficiency"] = elimination_rate
        
        # 分析单位部署策略（基于单位分布）
        if len(exp['steps']) > 0:
            unit_distributions = []
            for step in exp['steps']:
                # 计算我方单位的空间分布
                friendly_units = [unit for unit in step['unit_info'] if unit['alliance'] == 1]
                if friendly_units:
                    positions = np.array([unit['position'] for unit in friendly_units])
                    # 计算单位分布的标准差（分散程度）
                    if len(positions) > 1:
                        std_dev = np.mean(np.std(positions, axis=0))
                        unit_distributions.append(std_dev)
            
            if unit_distributions:
                avg_distribution = np.mean(unit_distributions)
                # 标准化分布指标
                normalized_distribution = min(1.0, avg_distribution / 1000)  # 假设1000是最大合理值
                allocation_metrics["unit_deployment_strategy"] = normalized_distribution
        
        # 分析优先级设置（基于单位健康值管理）
        if len(exp['steps']) >= 2:
            health_management = []
            for step in exp['steps']:
                for unit in step['unit_info']:
                    if unit['alliance'] == 1:  # 只考虑我方单位
                        health_ratio = unit['health'] / unit['max_health']
                        # 健康值越低，优先级应该越高
                        if health_ratio < 0.5:
                            health_management.append(1 - health_ratio)  # 健康值低，管理得分高
            
            if health_management:
                allocation_metrics["priority_setting"] = np.mean(health_management)
        
        allocation_analysis.append(allocation_metrics)
    
    return allocation_analysis

# 分析环境适应策略
def analyze_environment_adaptation(experiments):
    """
    分析不同实验条件下的环境适应策略
    """
    adaptation_analysis = []
    
    for exp in experiments:
        # 提取环境适应相关指标
        adaptation_metrics = {
            "directory": exp['directory'],
            "model_type": exp['model_type'],
            "prefab_enabled": exp['prefab_enabled'],
            "scene": exp['scene'],
            "environmental_awareness": 0,  # 环境感知能力
            "adaptive_response_time": 0,  # 适应响应时间
            "strategy_adaptation_quality": 0,  # 策略适应质量
            "situational_awareness": 0  # 态势感知能力
        }
        
        # 计算环境感知能力（基于单位对环境变化的响应）
        if len(exp['steps']) >= 2:
            # 分析敌人单位的变化
            enemy_changes = []
            for i in range(1, len(exp['steps'])):
                prev_enemies = set(unit['unit_name'] for unit in exp['steps'][i-1]['unit_info'] if unit['alliance'] == 4)
                curr_enemies = set(unit['unit_name'] for unit in exp['steps'][i]['unit_info'] if unit['alliance'] == 4)
                
                # 检测敌人单位的变化
                enemy_diff = len(curr_enemies) - len(prev_enemies)
                enemy_changes.append(enemy_diff)
            
            if enemy_changes:
                # 环境感知能力 = 对敌人变化的检测能力
                adaptation_metrics["environmental_awareness"] = np.mean(np.abs(enemy_changes))
        
        # 计算适应响应时间（基于决策频率）
        if len(exp['steps']) >= 2:
            # 计算执行时间
            start_time = exp['steps'][0]['timestamp']
            end_time = exp['steps'][-1]['timestamp']
            try:
                start_dt = datetime.strptime(start_time, "%Y%m%d_%H%M%S_%f")
                end_dt = datetime.strptime(end_time, "%Y%m%d_%H%M%S_%f")
                execution_time = (end_dt - start_dt).total_seconds()
                if execution_time > 0:
                    # 响应时间 = 执行步骤数 / 执行时间
                    response_time = exp['total_steps'] / execution_time
                    adaptation_metrics["adaptive_response_time"] = response_time
            except:
                pass
        
        # 分析策略适应质量（基于单位行为变化）
        if len(exp['steps']) >= 3:
            behavior_changes = []
            for i in range(1, len(exp['steps']) - 1):
                # 分析单位位置的变化
                prev_positions = {unit['unit_name']: unit['position'] for unit in exp['steps'][i-1]['unit_info']}
                curr_positions = {unit['unit_name']: unit['position'] for unit in exp['steps'][i]['unit_info']}
                next_positions = {unit['unit_name']: unit['position'] for unit in exp['steps'][i+1]['unit_info']}
                
                # 计算单位移动的变化率
                for unit_name in set(prev_positions.keys()) & set(curr_positions.keys()) & set(next_positions.keys()):
                    # 计算前一步到当前步的移动距离
                    prev_curr_dist = np.sqrt(np.sum((np.array(prev_positions[unit_name]) - np.array(curr_positions[unit_name]))**2))
                    # 计算当前步到下一步的移动距离
                    curr_next_dist = np.sqrt(np.sum((np.array(curr_positions[unit_name]) - np.array(next_positions[unit_name]))**2))
                    
                    # 计算变化率
                    if prev_curr_dist > 0:
                        change_rate = abs(curr_next_dist - prev_curr_dist) / prev_curr_dist
                        behavior_changes.append(change_rate)
            
            if behavior_changes:
                adaptation_metrics["strategy_adaptation_quality"] = np.mean(behavior_changes)
        
        # 分析态势感知能力（基于单位信息处理）
        if len(exp['steps']) > 0:
            info_processing = []
            for step in exp['steps']:
                # 计算单位信息的丰富度
                unit_info_count = len(step['unit_info'])
                # 计算文本观察的长度
                text_length = len(step['text_observation'])
                # 综合信息处理能力
                info_score = (unit_info_count + text_length / 1000) / 2  # 标准化文本长度
                info_processing.append(info_score)
            
            if info_processing:
                adaptation_metrics["situational_awareness"] = np.mean(info_processing)
        
        adaptation_analysis.append(adaptation_metrics)
    
    return adaptation_analysis

# 识别战术模式
def identify_tactical_patterns(experiments):
    """
    识别不同实验条件下的战术模式
    """
    pattern_analysis = []
    
    for exp in experiments:
        # 提取战术模式相关指标
        pattern_metrics = {
            "directory": exp['directory'],
            "model_type": exp['model_type'],
            "prefab_enabled": exp['prefab_enabled'],
            "scene": exp['scene'],
            "tactical_pattern": "",  # 战术模式
            "aggressiveness": 0,  # 攻击性
            "defensiveness": 0,  # 防御性
            "versatility": 0,  # 多样性
            "coordination": 0  # 协调性
        }
        
        # 分析攻击性（基于敌人消灭率和单位移动）
        if len(exp['steps']) >= 2:
            # 计算敌人消灭率
            initial_enemies = set(unit['unit_name'] for unit in exp['steps'][0]['unit_info'] if unit['alliance'] == 4)
            final_enemies = set(unit['unit_name'] for unit in exp['steps'][-1]['unit_info'] if unit['alliance'] == 4)
            elimination_rate = 1 - (len(final_enemies) / len(initial_enemies)) if initial_enemies else 0
            
            # 计算单位移动距离（进攻性移动）
            total_movement = 0
            unit_count = 0
            for unit_name, trajectory in exp['unit_trajectories'].items():
                if len(trajectory) >= 2:
                    positions = np.array([step['position'] for step in trajectory])
                    movement = np.sum(np.sqrt(np.sum(np.diff(positions, axis=0)**2, axis=1)))
                    total_movement += movement
                    unit_count += 1
            
            avg_movement = total_movement / unit_count if unit_count > 0 else 0
            
            # 综合计算攻击性
            aggressiveness = (elimination_rate + min(1.0, avg_movement / 1000)) / 2
            pattern_metrics["aggressiveness"] = aggressiveness
        
        # 分析防御性（基于单位生存率和健康值）
        if len(exp['steps']) >= 2:
            # 计算单位生存率
            initial_units = set(unit['unit_name'] for unit in exp['steps'][0]['unit_info'] if unit['alliance'] == 1)
            final_units = set(unit['unit_name'] for unit in exp['steps'][-1]['unit_info'] if unit['alliance'] == 1)
            survival_rate = len(final_units) / len(initial_units) if initial_units else 0
            
            # 计算平均健康值
            health_ratios = []
            for step in exp['steps']:
                for unit in step['unit_info']:
                    if unit['alliance'] == 1:
                        health_ratio = unit['health'] / unit['max_health']
                        health_ratios.append(health_ratio)
            
            avg_health = np.mean(health_ratios) if health_ratios else 0
            
            # 综合计算防御性
            defensiveness = (survival_rate + avg_health) / 2
            pattern_metrics["defensiveness"] = defensiveness
        
        # 分析多样性（基于单位行为模式）
        if len(exp['steps']) > 0:
            unit_behaviors = {}
            for step in exp['steps']:
                for unit in step['unit_info']:
                    unit_name = unit['unit_name']
                    if unit_name not in unit_behaviors:
                        unit_behaviors[unit_name] = []
                    # 记录单位状态
                    unit_state = {
                        "health_ratio": unit['health'] / unit['max_health'],
                        "position": unit['position']
                    }
                    unit_behaviors[unit_name].append(unit_state)
            
            # 计算行为多样性
            behavior_diversities = []
            for unit_name, states in unit_behaviors.items():
                if len(states) >= 2:
                    # 计算健康值变化的多样性
                    health_ratios = [state['health_ratio'] for state in states]
                    health_diversity = np.std(health_ratios) if len(health_ratios) > 1 else 0
                    
                    # 计算位置变化的多样性
                    positions = np.array([state['position'] for state in states])
                    position_diversity = np.mean(np.std(positions, axis=0)) if len(positions) > 1 else 0
                    
                    # 综合多样性
                    unit_diversity = (health_diversity + min(1.0, position_diversity / 1000)) / 2
                    behavior_diversities.append(unit_diversity)
            
            if behavior_diversities:
                pattern_metrics["versatility"] = np.mean(behavior_diversities)
        
        # 分析协调性（基于单位间的协作）
        if len(exp['steps']) >= 2:
            coordination_scores = []
            for i in range(1, len(exp['steps'])):
                # 分析单位间的距离变化
                units = [unit for unit in exp['steps'][i]['unit_info'] if unit['alliance'] == 1]
                if len(units) >= 2:
                    positions = np.array([unit['position'] for unit in units])
                    # 计算单位间的平均距离
                    pairwise_distances = []
                    for j in range(len(positions)):
                        for k in range(j+1, len(positions)):
                            distance = np.sqrt(np.sum((positions[j] - positions[k])**2))
                            pairwise_distances.append(distance)
                    
                    if pairwise_distances:
                        avg_distance = np.mean(pairwise_distances)
                        # 距离适中表示协调良好
                        # 假设理想距离在50-200之间
                        if 50 <= avg_distance <= 200:
                            coordination = 1.0
                        elif avg_distance < 50:
                            coordination = 1.0 - (50 - avg_distance) / 50  # 太近协调性降低
                        else:
                            coordination = 1.0 - (avg_distance - 200) / 800  # 太远协调性降低
                        coordination_scores.append(coordination)
            
            if coordination_scores:
                pattern_metrics["coordination"] = np.mean(coordination_scores)
        
        # 识别战术模式
        if pattern_metrics["aggressiveness"] > 0.6:
            pattern_metrics["tactical_pattern"] = "Aggressive"
        elif pattern_metrics["defensiveness"] > 0.6:
            pattern_metrics["tactical_pattern"] = "Defensive"
        elif pattern_metrics["versatility"] > 0.5:
            pattern_metrics["tactical_pattern"] = "Versatile"
        elif pattern_metrics["coordination"] > 0.6:
            pattern_metrics["tactical_pattern"] = "Coordinated"
        else:
            pattern_metrics["tactical_pattern"] = "Balanced"
        
        pattern_analysis.append(pattern_metrics)
    
    return pattern_analysis

# 保存战术分析结果
def save_tactical_analysis(planning_analysis, allocation_analysis, adaptation_analysis, pattern_analysis):
    """
    保存战术分析结果
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "analysis", "output")
    
    # 保存任务规划分析
    df_planning = pd.DataFrame(planning_analysis)
    df_planning.to_csv(os.path.join(output_dir, "task_planning_analysis.csv"), index=False, encoding='utf-8-sig')
    
    # 保存资源分配分析
    df_allocation = pd.DataFrame(allocation_analysis)
    df_allocation.to_csv(os.path.join(output_dir, "resource_allocation_analysis.csv"), index=False, encoding='utf-8-sig')
    
    # 保存环境适应分析
    df_adaptation = pd.DataFrame(adaptation_analysis)
    df_adaptation.to_csv(os.path.join(output_dir, "environment_adaptation_analysis.csv"), index=False, encoding='utf-8-sig')
    
    # 保存战术模式分析
    df_pattern = pd.DataFrame(pattern_analysis)
    df_pattern.to_csv(os.path.join(output_dir, "tactical_pattern_analysis.csv"), index=False, encoding='utf-8-sig')
    
    print("成功保存战术分析结果")

if __name__ == "__main__":
    print("加载实验数据...")
    experiments = load_data()
    print(f"成功加载 {len(experiments)} 个实验")
    
    print("分析任务规划能力...")
    planning_analysis = analyze_task_planning(experiments)
    
    print("分析资源分配策略...")
    allocation_analysis = analyze_resource_allocation(experiments)
    
    print("分析环境适应策略...")
    adaptation_analysis = analyze_environment_adaptation(experiments)
    
    print("识别战术模式...")
    pattern_analysis = identify_tactical_patterns(experiments)
    
    print("保存战术分析结果...")
    save_tactical_analysis(planning_analysis, allocation_analysis, adaptation_analysis, pattern_analysis)
    print("战术层面分析完成！")
