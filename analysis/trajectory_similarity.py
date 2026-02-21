import os
import json
import numpy as np
from scipy.spatial.distance import euclidean
from scipy.ndimage import gaussian_filter1d
from sklearn.metrics import pairwise_distances
import pandas as pd

# 加载处理后的数据
def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "analysis", "output", "processed_experiments.json")
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data

# 动态时间规整（DTW）算法计算轨迹相似度
def calculate_dtw_similarity(trajectory1, trajectory2):
    """
    使用动态时间规整算法计算两个轨迹的相似度
    """
    # 提取位置坐标
    path1 = np.array([step['position'] for step in trajectory1])
    path2 = np.array([step['position'] for step in trajectory2])
    
    # 计算距离矩阵
    n, m = len(path1), len(path2)
    dtw_matrix = np.zeros((n+1, m+1))
    dtw_matrix[:, 0] = np.inf
    dtw_matrix[0, :] = np.inf
    dtw_matrix[0, 0] = 0
    
    # 填充距离矩阵
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = euclidean(path1[i-1], path2[j-1])
            dtw_matrix[i, j] = cost + min(dtw_matrix[i-1, j],    # 上
                                           dtw_matrix[i, j-1],    # 左
                                           dtw_matrix[i-1, j-1])  # 对角线
    
    # 计算相似度分数（归一化）
    max_dist = np.max([np.max(np.sqrt(np.sum(path1**2, axis=1))), 
                       np.max(np.sqrt(np.sum(path2**2, axis=1)))])
    similarity = 1 - (dtw_matrix[n, m] / (max_dist * max(n, m)))
    
    return similarity

# 计算路径重合度
def calculate_path_overlap(trajectory1, trajectory2, threshold=10.0):
    """
    计算两条轨迹的路径重合度
    """
    # 提取位置坐标
    path1 = np.array([step['position'] for step in trajectory1])
    path2 = np.array([step['position'] for step in trajectory2])
    
    # 计算路径点之间的距离
    distances = pairwise_distances(path1, path2)
    
    # 统计重合点数量
    overlap_count = np.sum(distances < threshold)
    
    # 计算重合度
    max_points = max(len(path1), len(path2))
    overlap_ratio = overlap_count / max_points
    
    return overlap_ratio

# 计算平均距离偏差
def calculate_average_distance_deviation(trajectory1, trajectory2):
    """
    计算两条轨迹之间的平均距离偏差
    """
    # 提取位置坐标
    path1 = np.array([step['position'] for step in trajectory1])
    path2 = np.array([step['position'] for step in trajectory2])
    
    # 确保两条轨迹长度相同
    min_len = min(len(path1), len(path2))
    path1 = path1[:min_len]
    path2 = path2[:min_len]
    
    # 计算平均距离
    distances = np.sqrt(np.sum((path1 - path2)**2, axis=1))
    avg_distance = np.mean(distances)
    
    return avg_distance

# 检测关键节点
def detect_key_nodes(experiment):
    """
    检测实验中的关键节点
    """
    key_nodes = []
    steps = experiment['steps']
    
    for i, step in enumerate(steps):
        # 检测单位死亡
        if i > 0:
            prev_units = set(unit['unit_name'] for unit in steps[i-1]['unit_info'])
            current_units = set(unit['unit_name'] for unit in step['unit_info'])
            
            # 检测死亡的单位
            dead_units = prev_units - current_units
            if dead_units:
                key_nodes.append({
                    "step": step['step'],
                    "type": "unit_death",
                    "details": f"Units died: {', '.join(dead_units)}"
                })
        
        # 检测单位健康值急剧下降
        for unit in step['unit_info']:
            health_ratio = unit['health'] / unit['max_health']
            if health_ratio < 0.3:
                key_nodes.append({
                    "step": step['step'],
                    "type": "low_health",
                    "details": f"Unit {unit['unit_name']} has low health: {health_ratio:.2f}"
                })
    
    return key_nodes

# 计算关键节点匹配率
def calculate_key_node_match_rate(key_nodes1, key_nodes2):
    """
    计算两个实验之间的关键节点匹配率
    """
    # 以步骤为键，存储关键节点类型
    nodes1 = {(node['step'], node['type']): node for node in key_nodes1}
    nodes2 = {(node['step'], node['type']): node for node in key_nodes2}
    
    # 计算匹配的节点数量
    matched_nodes = set(nodes1.keys()) & set(nodes2.keys())
    match_count = len(matched_nodes)
    
    # 计算匹配率
    max_nodes = max(len(nodes1), len(nodes2))
    match_rate = match_count / max_nodes if max_nodes > 0 else 0
    
    return match_rate

# 计算编辑距离
def calculate_edit_distance(sequence1, sequence2):
    """
    计算两个序列之间的编辑距离
    """
    n, m = len(sequence1), len(sequence2)
    
    # 创建距离矩阵
    dp = np.zeros((n+1, m+1))
    
    # 初始化第一行和第一列
    for i in range(n+1):
        dp[i, 0] = i
    for j in range(m+1):
        dp[0, j] = j
    
    # 填充矩阵
    for i in range(1, n+1):
        for j in range(1, m+1):
            if sequence1[i-1] == sequence2[j-1]:
                cost = 0
            else:
                cost = 1
            dp[i, j] = min(dp[i-1, j] + 1,      # 删除
                          dp[i, j-1] + 1,      # 插入
                          dp[i-1, j-1] + cost) # 替换
    
    return dp[n, m]

# 计算执行步骤序列相似度
def calculate_sequence_similarity(experiment1, experiment2):
    """
    计算两个实验之间的执行步骤序列相似度
    """
    # 提取步骤序列特征
    sequence1 = []
    for step in experiment1['step_sequences']:
        # 提取单位数量变化作为序列特征
        sequence1.append(step['unit_count'])
    
    sequence2 = []
    for step in experiment2['step_sequences']:
        sequence2.append(step['unit_count'])
    
    # 计算编辑距离
    edit_dist = calculate_edit_distance(sequence1, sequence2)
    
    # 计算相似度
    max_len = max(len(sequence1), len(sequence2))
    similarity = 1 - (edit_dist / max_len)
    
    return similarity

# 分析轨迹相似度
def analyze_trajectory_similarity(experiments):
    """
    分析所有实验之间的轨迹相似度
    """
    results = []
    
    # 按场景分组
    scenes = {}
    for exp in experiments:
        scene = exp['scene']
        if scene not in scenes:
            scenes[scene] = []
        scenes[scene].append(exp)
    
    # 对每个场景进行分析
    for scene, scene_experiments in scenes.items():
        print(f"分析场景: {scene}")
        
        # 分析场景内的实验
        for i, exp1 in enumerate(scene_experiments):
            for j, exp2 in enumerate(scene_experiments):
                if i >= j:
                    continue
                
                # 计算轨迹相似度
                similarity_results = {
                    "scene": scene,
                    "experiment1": exp1['directory'],
                    "experiment2": exp2['directory'],
                    "model_type_1": exp1['model_type'],
                    "model_type_2": exp2['model_type'],
                    "prefab_enabled_1": exp1['prefab_enabled'],
                    "prefab_enabled_2": exp2['prefab_enabled'],
                    "trajectory_similarity": {},
                    "key_node_match_rate": 0,
                    "sequence_similarity": 0
                }
                
                # 计算单位轨迹相似度
                common_units = set(exp1['unit_trajectories'].keys()) & set(exp2['unit_trajectories'].keys())
                unit_similarities = {}
                
                for unit in common_units:
                    traj1 = exp1['unit_trajectories'][unit]
                    traj2 = exp2['unit_trajectories'][unit]
                    
                    # 计算DTW相似度
                    dtw_similarity = calculate_dtw_similarity(traj1, traj2)
                    
                    # 计算路径重合度
                    path_overlap = calculate_path_overlap(traj1, traj2)
                    
                    # 计算平均距离偏差
                    avg_distance = calculate_average_distance_deviation(traj1, traj2)
                    
                    unit_similarities[unit] = {
                        "dtw_similarity": dtw_similarity,
                        "path_overlap": path_overlap,
                        "average_distance": avg_distance
                    }
                
                similarity_results["trajectory_similarity"] = unit_similarities
                
                # 计算关键节点匹配率
                key_nodes1 = detect_key_nodes(exp1)
                key_nodes2 = detect_key_nodes(exp2)
                key_node_match_rate = calculate_key_node_match_rate(key_nodes1, key_nodes2)
                similarity_results["key_node_match_rate"] = key_node_match_rate
                
                # 计算执行步骤序列相似度
                sequence_similarity = calculate_sequence_similarity(exp1, exp2)
                similarity_results["sequence_similarity"] = sequence_similarity
                
                results.append(similarity_results)
                
                print(f"  分析实验对: {exp1['directory']} vs {exp2['directory']}")
                print(f"    关键节点匹配率: {key_node_match_rate:.4f}")
                print(f"    执行步骤序列相似度: {sequence_similarity:.4f}")
    
    return results

# 保存分析结果
def save_similarity_results(results):
    """
    保存轨迹相似度分析结果
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "analysis", "output")
    
    # 保存详细结果
    with open(os.path.join(output_dir, "trajectory_similarity_results.json"), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 保存汇总结果
    summary_data = []
    for result in results:
        # 计算平均轨迹相似度
        unit_similarities = result['trajectory_similarity'].values()
        if unit_similarities:
            avg_dtw = np.mean([u['dtw_similarity'] for u in unit_similarities])
            avg_overlap = np.mean([u['path_overlap'] for u in unit_similarities])
            avg_distance = np.mean([u['average_distance'] for u in unit_similarities])
        else:
            avg_dtw = 0
            avg_overlap = 0
            avg_distance = 0
        
        summary_data.append({
            "scene": result['scene'],
            "experiment1": result['experiment1'],
            "experiment2": result['experiment2'],
            "prefab_enabled_1": result['prefab_enabled_1'],
            "prefab_enabled_2": result['prefab_enabled_2'],
            "average_dtw_similarity": avg_dtw,
            "average_path_overlap": avg_overlap,
            "average_distance_deviation": avg_distance,
            "key_node_match_rate": result['key_node_match_rate'],
            "sequence_similarity": result['sequence_similarity']
        })
    
    # 保存为CSV
    df_summary = pd.DataFrame(summary_data)
    df_summary.to_csv(os.path.join(output_dir, "trajectory_similarity_summary.csv"), index=False, encoding='utf-8-sig')
    
    print(f"成功保存 {len(results)} 组轨迹相似度分析结果")

if __name__ == "__main__":
    print("加载实验数据...")
    experiments = load_data()
    print(f"成功加载 {len(experiments)} 个实验")
    
    print("开始轨迹相似度分析...")
    results = analyze_trajectory_similarity(experiments)
    
    print("保存分析结果...")
    save_similarity_results(results)
    print("轨迹相似度分析完成！")
