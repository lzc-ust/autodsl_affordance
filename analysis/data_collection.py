import os
import json
import pandas as pd
import numpy as np
from datetime import datetime

# 定义实验目录路径
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "log", "VLMAgentWithoutMove")
OUTPUT_DIR = os.path.join(BASE_DIR, "analysis", "output")

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 实验分类映射
experiment_mapping = {
    "vlm_attention_1": "VLM注意力机制",
    "ability_map_8marine_3marauder_1medivac_1tank": "MMM场景",
    "ability_MMM2": "MMM2场景"
}

# 收集所有实验数据
def collect_experiments():
    experiments = []
    
    # 遍历所有实验目录
    for exp_dir in os.listdir(LOG_DIR):
        if not os.path.isdir(os.path.join(LOG_DIR, exp_dir)):
            continue
        
        # 提取实验信息
        exp_parts = exp_dir.split('_')
        
        # 提取时间戳和地图名称
        timestamp = exp_parts[1] + '_' + exp_parts[2]
        map_name = exp_parts[3] if len(exp_parts) > 3 else "Unknown"
        
        # 确定实验场景
        scene_mapping = {
            "MMM": "MMM场景",
            "MMM2": "MMM2场景",
            "P5vsT8": "P5vsT8"
        }
        scene = scene_mapping.get(map_name, "Unknown")
        
        # 根据时间戳确定条件组合
        # 实验执行顺序：1)有预制函数+有视觉信息 2)有预制函数+无视觉信息 3)无预制函数+有视觉信息 4)无预制函数+无视觉信息
        time_groups = {
            # 1) 有预制函数+有视觉信息
            "20260213_160916": {"prefab_enabled": True, "image_input": True, "model_type": "VLM"},
            # 2) 有预制函数+无视觉信息
            "20260213_172642": {"prefab_enabled": True, "image_input": False, "model_type": "VLM"},
            "20260213_172646": {"prefab_enabled": True, "image_input": False, "model_type": "VLM"},
            "20260213_172649": {"prefab_enabled": True, "image_input": False, "model_type": "VLM"},
            # 3) 无预制函数+有视觉信息
            "20260213_201016": {"prefab_enabled": False, "image_input": True, "model_type": "VLM"},
            "20260213_201018": {"prefab_enabled": False, "image_input": True, "model_type": "VLM"},
            "20260213_201025": {"prefab_enabled": False, "image_input": True, "model_type": "VLM"},
            # 4) 无预制函数+无视觉信息
            "20260214_095929": {"prefab_enabled": False, "image_input": False, "model_type": "VLM"},
            "20260214_095942": {"prefab_enabled": False, "image_input": False, "model_type": "VLM"},
            "20260214_095946": {"prefab_enabled": False, "image_input": False, "model_type": "VLM"}
        }
        
        # 获取条件组合
        if timestamp in time_groups:
            prefab_enabled = time_groups[timestamp]["prefab_enabled"]
            image_input = time_groups[timestamp]["image_input"]
            model_type = time_groups[timestamp]["model_type"]
        else:
            # 默认值
            prefab_enabled = False
            image_input = False
            model_type = "VLM"
        
        # 读取complete_data.json文件
        data_path = os.path.join(LOG_DIR, exp_dir, "episode_0", "logs_file", "complete_data.json")
        if not os.path.exists(data_path):
            print(f"警告: {data_path} 不存在")
            continue
        
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 提取关键信息
            total_steps = data.get('total_steps', 0)
            steps = data.get('steps', [])
            
            # 保存实验信息
            experiment = {
                "directory": exp_dir,
                "model_type": model_type,
                "image_input": image_input,
                "prefab_enabled": prefab_enabled,
                "scene": scene,
                "timestamp": timestamp,
                "total_steps": total_steps,
                "steps": steps
            }
            
            experiments.append(experiment)
            print(f"成功加载实验: {exp_dir}")
            
        except Exception as e:
            print(f"错误加载 {data_path}: {e}")
    
    return experiments

# 预处理数据
def preprocess_data(experiments):
    processed_data = []
    
    for exp in experiments:
        # 提取单位轨迹数据
        unit_trajectories = {}
        for step in exp['steps']:
            step_num = step['step']
            for unit in step['unit_info']:
                unit_name = unit['unit_name']
                if unit_name not in unit_trajectories:
                    unit_trajectories[unit_name] = []
                
                # 提取单位状态
                unit_state = {
                    "step": step_num,
                    "timestamp": step['timestamp'],
                    "health": unit['health'],
                    "max_health": unit['max_health'],
                    "shield": unit.get('shield', 0),
                    "max_shield": unit.get('max_shield', 0),
                    "energy": unit.get('energy', 0),
                    "position": unit['position']
                }
                unit_trajectories[unit_name].append(unit_state)
        
        # 提取执行步骤序列
        step_sequences = []
        for step in exp['steps']:
            step_info = {
                "step": step['step'],
                "timestamp": step['timestamp'],
                "text_observation": step['text_observation'],
                "unit_count": len(step['unit_info'])
            }
            step_sequences.append(step_info)
        
        # 保存处理后的数据
        processed_exp = exp.copy()
        processed_exp['unit_trajectories'] = unit_trajectories
        processed_exp['step_sequences'] = step_sequences
        processed_data.append(processed_exp)
    
    return processed_data

# 保存数据
def save_data(experiments, processed_data):
    # 保存原始实验数据
    with open(os.path.join(OUTPUT_DIR, "experiments.json"), 'w', encoding='utf-8') as f:
        json.dump(experiments, f, ensure_ascii=False, indent=2)
    
    # 保存处理后的数据
    with open(os.path.join(OUTPUT_DIR, "processed_experiments.json"), 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
    
    # 创建实验汇总表
    experiment_summary = []
    for exp in processed_data:
        summary = {
            "directory": exp['directory'],
            "model_type": exp['model_type'],
            "image_input": exp['image_input'],
            "prefab_enabled": exp['prefab_enabled'],
            "scene": exp['scene'],
            "total_steps": exp['total_steps'],
            "unit_count": len(exp['unit_trajectories'])
        }
        experiment_summary.append(summary)
    
    # 保存汇总表为CSV
    df_summary = pd.DataFrame(experiment_summary)
    df_summary.to_csv(os.path.join(OUTPUT_DIR, "experiment_summary.csv"), index=False, encoding='utf-8-sig')
    
    print(f"成功保存 {len(processed_data)} 个实验的数据")

if __name__ == "__main__":
    print("开始收集实验数据...")
    experiments = collect_experiments()
    print(f"成功收集 {len(experiments)} 个实验")
    
    print("开始预处理数据...")
    processed_data = preprocess_data(experiments)
    print("预处理完成")
    
    print("保存数据...")
    save_data(experiments, processed_data)
    print("数据收集和预处理完成！")
