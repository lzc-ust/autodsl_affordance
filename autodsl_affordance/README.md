# AutoDSL Affordance Module

## 模块概述

AutoDSL Affordance 是一个为 StarCraft II AI 开发的预制函数系统，提供了以下核心功能：

- **预制函数系统**：用于战术决策的预制函数管理和执行
- **链接图系统**：用于单位关系的链接图构建和分析
- **种族特定单位实现**：针对不同种族的单位特性进行优化
- **性能监控和评估**：跟踪预制函数的使用效果和性能指标

## 目录结构

```
autodsl_affordance/
├── core/               # 核心功能模块
│   ├── base_units/     # 基础单位定义
│   ├── linkage_graph/  # 链接图系统
│   ├── prefab_system/  # 预制函数系统
├── races/              # 种族特定实现
│   ├── protoss/        # 神族单位实现
│   ├── terran/         # 人族单位实现
│   ├── zerg/           # 虫族单位实现
├── sc2_unit_info/      # 单位信息数据
├── utils/              # 工具函数
├── __init__.py         # 模块初始化文件
├── requirements.txt    # 依赖文件
├── README.md           # 文档文件
```

## 安装方法

### 从源码安装

```bash
# 克隆仓库
git clone <repository_url>
cd <repository_directory>

# 安装依赖
pip install -r autodsl_affordance/requirements.txt

# 安装模块
pip install -e .
```

### 直接安装

```bash
# 直接从目录安装
pip install path/to/autodsl_affordance
```

## 基本使用

### 1. 初始化预制函数管理器

```python
from autodsl_affordance import PrefabFunctionManager

# 初始化管理器
manager = PrefabFunctionManager()

# 加载特定种族的预制函数
manager.load_race_specific_functions('terran')

# 验证所有函数
invalid_funcs = manager.validate_all_functions()
print(f"验证失败的函数: {invalid_funcs}")

# 聚合所有参数
manager.aggregate_all_parameters()
```

### 2. 使用预制函数处理器

```python
from autodsl_affordance import PrefabFunctionHandler

# 初始化处理器
handler = PrefabFunctionHandler(manager)

# 获取最优函数
observation = {"unit_info": [...]}
optimal_functions = handler.get_optimal_functions(observation)

# 执行函数
execution_result = handler.execute_function(optimal_functions[0], observation)
print(f"执行结果: {execution_result}")
```

### 3. 性能监控

```python
from autodsl_affordance import PrefabPerformanceMonitor

# 初始化性能监控器
monitor = PrefabPerformanceMonitor()

# 记录函数使用
monitor.record_function_usage(
    func_id="TERRAN_SYNERGY_0",
    func_name="terran_mm_push_synergy",
    step=100,
    selected=True,
    confidence=0.95,
    relevance=0.9
)

# 获取性能总结
summary = monitor.get_performance_summary()
print(f"性能总结: {summary}")
```

## 核心组件

### 1. PrefabFunctionManager
- **功能**：管理预制函数的加载、验证和操作
- **主要方法**：
  - `load_prefab_functions()`：从文件加载预制函数
  - `load_race_specific_functions()`：加载特定种族的预制函数
  - `validate_all_functions()`：验证所有预制函数的一致性
  - `aggregate_all_parameters()`：聚合所有函数参数
  - `search_functions()`：根据条件搜索预制函数

### 2. PrefabFunctionHandler
- **功能**：处理预制函数的检索、评分、选择和执行
- **主要方法**：
  - `retrieve_relevant_functions()`：检索相关预制函数
  - `score_functions()`：为预制函数评分
  - `select_optimal_functions()`：选择最优预制函数
  - `execute_functions()`：执行预制函数

### 3. PrefabPerformanceMonitor
- **功能**：监控预制函数的性能
- **主要方法**：
  - `record_function_usage()`：记录函数使用情况
  - `record_decision_quality()`：记录决策质量
  - `record_prefab_relevance()`：记录函数相关性
  - `get_performance_summary()`：获取性能总结

## 环境变量

- `AUTODSL_AFFORDANCE_PATH`：指定模块的安装路径
- `AUTODSL_DATA_PATH`：指定数据文件的路径

## 配置选项

### 预制函数管理器配置

```python
# 初始化配置
manager = PrefabFunctionManager()

# 加载配置
manager.load_prefab_functions(
    "path/to/functions.json",
    race="terran",  # 可选，种族过滤
    map_name="test_map",  # 可选，地图过滤
    merge=True  # 可选，是否合并到现有库中
)
```

### 预制函数处理器配置

```python
# 初始化配置
config = {
    'top_k': 3,  # 返回前k个最优函数
    'cache_size': 100,  # 缓存大小
    'enable_performance_monitor': True  # 是否启用性能监控
}

handler = PrefabFunctionHandler(config=config)
```

## 示例场景

### 场景 1：人族 MM 推进

```python
# 加载人族预制函数
manager.load_race_specific_functions('terran')

# 初始化处理器
handler = PrefabFunctionHandler(manager)

# 模拟游戏观察数据
observation = {
    "unit_info": [
        {"unit_name": "TerranMarine", "alliance": 1, "health": 45, "position": (10, 10)},
        {"unit_name": "TerranMarine", "alliance": 1, "health": 45, "position": (12, 10)},
        {"unit_name": "TerranMarauder", "alliance": 1, "health": 125, "position": (11, 12)},
        {"unit_name": "TerranMedivac", "alliance": 1, "health": 150, "position": (15, 15)},
        {"unit_name": "ZergZergling", "alliance": 4, "health": 35, "position": (30, 20)}
    ]
}

# 获取最优函数
optimal_functions = handler.get_optimal_functions(observation)

# 执行函数
execution_result = handler.execute_function(optimal_functions[0], observation)
print(f"执行结果: {execution_result}")
```

### 场景 2：神族地空协同

```python
# 加载神族预制函数
manager.load_race_specific_functions('protoss')

# 初始化处理器
handler = PrefabFunctionHandler(manager)

# 模拟游戏观察数据
observation = {
    "unit_info": [
        {"unit_name": "ProtossZealot", "alliance": 1, "health": 100, "position": (10, 10)},
        {"unit_name": "ProtossStalker", "alliance": 1, "health": 80, "position": (12, 10)},
        {"unit_name": "ProtossPhoenix", "alliance": 1, "health": 120, "position": (15, 15)},
        {"unit_name": "ZergHydralisk", "alliance": 4, "health": 80, "position": (30, 20)}
    ]
}

# 获取最优函数
optimal_functions = handler.get_optimal_functions(observation)

# 执行函数
execution_result = handler.execute_function(optimal_functions[0], observation)
print(f"执行结果: {execution_result}")
```

## 开发指南

### 添加新的预制函数

1. **创建预制函数字符串**：
   ```python
   new_function = {
       "function_id": "NEW_FUNCTION_0",
       "function_type": "synergy",
       "name": "new_tactic_synergy",
       "description": "新的战术协同",
       "linkage_type": "support_dps_coordination",
       "execution_type": "attack",
       "prerequisites": {
           "min_units": 3,
           "required_units": ["TerranMarine", "TerranMarauder"],
           "optional_units": ["TerranMedivac"]
       },
       "execution_flow": [
           "use_stim_pack(TerranMarine, TerranMarauder)",
           "focus_fire(TerranMarine, highest_threat_enemy)"
       ],
       "confidence": 0.9
   }
   ```

2. **添加到管理器**：
   ```python
   manager.add_prefab_function(new_function)
   ```

3. **保存到文件**：
   ```python
   manager.save_prefab_functions("path/to/new_functions.json")
   ```

### 扩展核心组件

1. **继承现有类**：
   ```python
   class CustomPrefabFunctionManager(PrefabFunctionManager):
       def custom_method(self):
           # 自定义方法
           pass
   ```

2. **重写方法**：
   ```python
   class CustomPrefabFunctionHandler(PrefabFunctionHandler):
       def score_functions(self, prefab_functions, observation):
           # 自定义评分逻辑
           pass
   ```

## 故障排除

### 1. 导入错误

**问题**：`ModuleNotFoundError: No module named 'autodsl_affordance'`

**解决方案**：
- 确保模块已正确安装
- 检查 Python 路径是否包含模块目录
- 尝试重新安装模块

### 2. 验证失败

**问题**：预制函数验证失败

**解决方案**：
- 检查函数是否符合 JSON Schema 规范
- 确保所有必要字段都已提供
- 验证字段类型是否正确

### 3. 执行失败

**问题**：函数执行失败

**解决方案**：
- 检查游戏观察数据格式是否正确
- 验证函数的前提条件是否满足
- 确保所有必要的单位都存在

## 版本历史

### v1.0.0
- 初始版本
- 实现预制函数系统
- 支持种族特定单位
- 提供性能监控功能

## 贡献指南

1. ** Fork 仓库
2. ** 创建功能分支
3. ** 提交更改
4. ** 推送到分支
5. ** 创建 Pull Request

## 许可证

本项目采用 Apache License 2.0 许可证。详见 LICENSE 文件。

## 联系方式

- **作者**：AutoDSL Team
- **邮箱**：autodsl@example.com
- **项目地址**：https://github.com/autodsl/affordance

---

**注意**：本模块专为 StarCraft II AI 开发设计，可根据需要扩展到其他游戏或领域。
