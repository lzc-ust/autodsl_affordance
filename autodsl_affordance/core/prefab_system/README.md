# Prefab Function System

## 系统架构

Prefab Function System 是一个用于管理和执行预制函数的系统，为游戏AI提供战术决策支持。该系统采用分层架构，由以下核心组件组成：

### 1. 核心组件

| 组件名称 | 职责 | 文件路径 |
|---------|------|----------|
| PrefabFunctionManager | 顶层管理器，协调各组件 | manager/prefab_function_manager.py |
| PrefabFunctionHandler | 具体实现，处理函数评分和选择 | handler/prefab_function_handler.py |

### 2. 数据流

1. **初始化阶段**：PrefabFunctionManager 初始化所有组件并加载预制函数
2. **函数选择阶段**：基于游戏状态检索和评分函数，选择最优函数
3. **执行阶段**：执行选定的函数并记录执行结果
4. **反馈阶段**：基于执行结果更新函数评分和性能数据

## 统一预制函数体系

### 1. 体系概述

我们已经废弃了"协同预制函数"与"传统预制函数"的概念区分，将两者整合为统一的"预制函数"体系进行标准化处理。所有预制函数现在都通过统一的接口进行管理和执行。

### 2. 统一接口

```python
# 获取最优预制函数
optimal_functions = prefab_function_manager.get_optimal_functions(observation, game_state)
```

### 3. 参数规范

统一的预制函数调用接口使用以下参数规范：

- `observation`：游戏观察数据
- `game_state`：游戏状态信息
- `max_functions`：最大返回函数数量（默认5）

## 快速开始

### 1. 安装

确保项目依赖已安装：

```bash
# 安装依赖
pip install -r requirements.txt
```

### 2. 基本使用

```python
from autodsl_affordance.core.prefab_system.manager.prefab_function_manager import PrefabFunctionManager

# 初始化管理器
manager = PrefabFunctionManager()

# 加载预制函数库
manager.load_prefab_functions('path/to/prefab_functions.json')

# 游戏观察数据
observation = {
    'unit_info': [
        # 单位信息...
    ],
    'text': 'Game state description'
}

# 生成游戏状态信息
game_state = {
    'friendly_count': 5,
    'enemy_count': 3,
    'friendly_unit_types': {'Marine': 3, 'Medivac': 2},
    'enemy_unit_types': {'Zealot': 2, 'Stalker': 1},
    'has_low_health_units': True,
    'has_energy_units': True,
    'high_energy_units': False,
    'unit_type_diversity': 0.4
}

# 获取最优函数
optimal_functions = manager.get_optimal_functions(observation, game_state)

# 输出最优函数详细信息
for i, func in enumerate(optimal_functions, 1):
    print(f"最优预制函数 {i}: ID={func['function_id']}, Name={func['name']}, Score={func['score']}, Relevance={func['relevance']}")
```

## 核心功能

### 1. 函数管理

- **函数加载**：从JSON文件加载预制函数
- **函数检索**：基于游戏状态和种族检索相关函数
- **函数评分**：多维度评估函数适用性
- **最优选择**：选择最适合当前场景的函数

### 2. 执行管理

- **函数执行**：执行选定的预制函数
- **结果记录**：记录执行结果和效果
- **评分更新**：基于执行结果更新函数评分

### 3. 性能监控

- **使用记录**：记录函数使用历史
- **决策质量**：评估决策质量和效果
- **相关性分析**：分析函数与游戏状态的相关性
- **影响评估**：评估决策对游戏状态的影响

### 4. 缓存机制

- **结果缓存**：缓存函数选择结果
- **智能缓存**：基于游戏状态生成缓存键
- **缓存管理**：自动管理缓存大小和过期

## 数据结构

### 1. 预制函数结构

```python
{
    'function_id': str,          # 唯一标识符
    'name': str,                 # 函数名称
    'description': str,          # 函数描述
    'execution_flow': str,       # 执行流程
    'tactic_category': str,      # 战术类别
    'function_type': str,        # 函数类型
    'required_units': List[str], # 所需单位
    'confidence': float,         # 置信度
    'usage_count': int,          # 使用次数
    'success_rate': float,       # 成功率
    'score': float,              # 综合评分
    'relevance': float,          # 与当前游戏状态的相关性
}
```

### 2. 执行结果结构

```python
{
    'function_id': str,          # 函数ID
    'success': bool,             # 执行是否成功
    'actions': Dict,             # 执行的动作
    'metrics': {
        'friendly_count_change': int,    # 友方单位数量变化
        'enemy_count_change': int,       # 敌方单位数量变化
        'health_change': float,          # 生命值变化
        'resource_change': float,        # 资源变化
    },
    'timestamp': str,            # 执行时间
    'game_state_before': Dict,   # 执行前游戏状态
    'game_state_after': Dict,    # 执行后游戏状态
}
```

## 配置选项

| 配置项 | 类型 | 默认值 | 描述 |
|-------|------|-------|------|
| top_k | int | 3 | 返回前k个最优函数 |
| cache_size | int | 100 | 缓存大小 |
| enable_performance_monitor | bool | True | 是否启用性能监控 |

## 集成指南

### 1. 与VLM系统集成

```python
class VLMAgent:
    def __init__(self):
        self.prefab_manager = PrefabFunctionManager()
    
    def make_decision(self, observation):
        # 获取当前友方单位和敌方单位
        friendly_units = [unit for unit in observation['unit_info'] if unit['alliance'] == 1]
        enemy_units = [unit for unit in observation['unit_info'] if unit['alliance'] != 1]
        
        # 生成游戏状态信息
        game_state = {
            'friendly_count': len(friendly_units),
            'enemy_count': len(enemy_units),
            'friendly_unit_types': {},
            'enemy_unit_types': {},
            'has_low_health_units': any(unit['health'] < unit['max_health'] * 0.5 for unit in friendly_units),
            'has_energy_units': any(unit['energy'] > 0 for unit in friendly_units),
            'high_energy_units': any(unit['energy'] > 50 for unit in friendly_units),
            'unit_type_diversity': len(set(unit['unit_name'].split('_')[0] for unit in friendly_units)) / len(friendly_units) if friendly_units else 0
        }
        
        # 统计单位类型
        for unit in friendly_units:
            unit_type = unit['unit_name'].split('_')[0]
            game_state['friendly_unit_types'][unit_type] = game_state['friendly_unit_types'].get(unit_type, 0) + 1
        
        for unit in enemy_units:
            unit_type = unit['unit_name'].split('_')[0]
            game_state['enemy_unit_types'][unit_type] = game_state['enemy_unit_types'].get(unit_type, 0) + 1
        
        # 获取最优预制函数
        optimal_functions = self.prefab_manager.get_optimal_functions(observation, game_state)
        
        # 将函数信息整合到VLM提示中
        prompt = self._generate_prompt(optimal_functions, observation)
        
        # 使用VLM生成决策
        decision = self.vlm.generate(prompt)
        return decision
```

### 2. 与游戏环境集成

```python
def game_loop():
    prefab_manager = PrefabFunctionManager()
    
    while not game_over:
        observation = env.step(action)
        
        # 获取当前友方单位和敌方单位
        friendly_units = [unit for unit in observation['unit_info'] if unit['alliance'] == 1]
        enemy_units = [unit for unit in observation['unit_info'] if unit['alliance'] != 1]
        
        # 生成游戏状态信息
        game_state = {
            'friendly_count': len(friendly_units),
            'enemy_count': len(enemy_units),
            'friendly_unit_types': {},
            'enemy_unit_types': {},
        }
        
        # 统计单位类型
        for unit in friendly_units:
            unit_type = unit['unit_name'].split('_')[0]
            game_state['friendly_unit_types'][unit_type] = game_state['friendly_unit_types'].get(unit_type, 0) + 1
        
        for unit in enemy_units:
            unit_type = unit['unit_name'].split('_')[0]
            game_state['enemy_unit_types'][unit_type] = game_state['enemy_unit_types'].get(unit_type, 0) + 1
        
        # 获取最优函数
        functions = prefab_manager.get_optimal_functions(observation, game_state)
        
        if functions:
            # 执行最佳函数
            result = prefab_manager.execute_function(functions[0], observation)
            action = result['actions']
        else:
            # 没有合适的函数，使用默认策略
            action = default_strategy(observation)
```

## 扩展系统

### 1. 添加自定义预制函数

1. **创建预制函数文件**：在 `linkage_graph/prefab_functions/` 目录下创建JSON文件
2. **定义函数结构**：按照预制函数结构定义函数
3. **加载函数**：PrefabFunctionManager 会自动加载新的函数

### 2. 自定义评分逻辑

继承 PrefabFunctionHandler 并覆盖评分方法：

```python
class CustomFunctionHandler(PrefabFunctionHandler):
    def score_functions(self, functions, observation):
        # 自定义评分逻辑
        # ...
        return scored_functions

# 使用自定义处理器
manager = PrefabFunctionManager()
manager.function_handler = CustomFunctionHandler()
```

## 测试

运行测试套件验证系统功能：

```bash
# 运行测试
python -m pytest autodsl_affordance/core/prefab_system/test_prefab_function_manager.py -v
```

## 性能优化

1. **启用缓存**：通过配置 `cache_size` 启用结果缓存
2. **并行处理**：对于大量函数评分，考虑使用并行处理
3. **懒加载**：对于大型预制函数库，考虑实现懒加载机制

## 日志记录机制

预制函数系统实现了完善的日志记录机制，确保问题可追溯，提升系统可维护性和问题排查效率。日志记录包括：

- 函数加载和验证
- 函数评分和选择
- 函数执行和性能
- 系统错误和警告

系统使用Python标准日志模块，可通过以下方式配置日志级别：

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 故障排除

### 常见问题

1. **函数加载失败**：检查预制函数文件格式是否正确
2. **性能问题**：调整缓存大小和并行处理设置
3. **评分不准确**：检查游戏状态分析逻辑和评分权重

## 贡献指南

欢迎贡献代码和改进！请遵循以下步骤：

1. **Fork 仓库**
2. **创建分支**：`git checkout -b feature/your-feature`
3. **提交更改**：`git commit -m "Add your feature"`
4. **推送分支**：`git push origin feature/your-feature`
5. **创建 Pull Request**

## 许可证

本项目采用 MIT 许可证。
