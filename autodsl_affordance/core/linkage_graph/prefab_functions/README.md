# 预制函数系统文档

## 系统架构

预制函数系统是 StarCraft 2 AI 项目中的核心组件，用于封装和管理游戏中的各种战术和战略函数。该系统基于 AutoDSL Affordance Tech.md 文档中的设计核心理念，通过标准化的结构和接口，为 AI 决策提供高质量的战术选择。

### 设计理念

- **链接类型**：基于五种链接类型组织预制函数：interaction（交互）、combination（组合）、association（关联）、invocation（调用）、dependency（依赖）
- **模块化**：按种族和功能类型模块化组织预制函数
- **标准化**：使用 JSON Schema 确保预制函数结构的一致性
- **可扩展性**：支持通过标准化接口添加新的预制函数

## 目录结构

```
autodsl_affordance/core/linkage_graph/prefab_functions/
├── README.md                    # 预制函数系统说明文档
├── schema/                      # 预制函数 JSON Schema 定义
│   └── prefab_function.schema.json
├── protoss_prefab_functions.json  # 神族预制函数
├── terran_prefab_functions.json   # 人族预制函数
├── zerg_prefab_functions.json     # 虫族预制函数
├── tests/                       # 单元测试目录
│   └── test_prefab_functions.py
└── utils/                       # 工具函数目录
    └── schema_validator.py      # JSON Schema 验证工具
```

## 命名约定

### 文件命名

- 按种族分类：`{race}_prefab_functions.json`
- 示例：`terran_prefab_functions.json`、`protoss_prefab_functions.json`

### 函数 ID 命名

- 格式：`{RACE}_{TYPE}_{ID}`
- 示例：`TERRAN_INTERACTION_001`、`PROTOSS_COMBINATION_002`
- 其中 `TYPE` 为链接类型的缩写：INTERACTION、COMBINATION、ASSOCIATION、INVOCATION、DEPENDENCY

### 字段命名

- 使用蛇形命名法：`function_id`、`function_type` 等
- 统一字段名称：移除冗余字段，如 `synergy_type`（与 `linkage_type` 重复）
- 标准化枚举值：统一 `execution_type`、`tactic_category` 等字段的可能取值

## 预制函数结构

每个预制函数包含以下核心字段：

```json
{
  "function_id": "TERRAN_INTERACTION_001",
  "function_type": "interaction",
  "name": "focus_fire_on_highest_threat",
  "description": "集中火力攻击最高威胁的敌方单位",
  "strategy_description": "优先攻击对我方威胁最大的敌方单位，如高伤害或高优先级目标",
  "tactic_category": "offense",
  "linkage_type": "interaction",
  "execution_type": "attack",
  "source_unit": "all_friendly",
  "target_unit": "highest_threat_enemy",
  "execution_flow": [
    "set_target(all_friendly, highest_threat_enemy)",
    "attack(all_friendly, highest_threat_enemy)"
  ],
  "evidence": [
    "集中火力可以快速消除敌方威胁",
    "优先攻击高价值目标可以提高战斗效率"
  ],
  "confidence": 0.9
}
```

### 字段说明

- **function_id**：预制函数的唯一标识符
- **function_type**：预制函数类型，基于链接类型
- **name**：预制函数名称
- **description**：预制函数描述
- **strategy_description**：详细的策略描述
- **tactic_category**：战术类别
- **linkage_type**：链接类型
- **execution_type**：执行类型
- **source_unit**：源单位（交互类型函数）
- **target_unit**：目标单位（交互类型函数）
- **units**：涉及的单位列表（组合类型函数）
- **prerequisites**：前提条件
- **tactical_effects**：战术效果
- **execution_flow**：执行流程
- **parameters**：参数列表
- **evidence**：支持证据
- **confidence**：置信度

## 使用方法

### 加载预制函数

```python
from autodsl_affordance.core.linkage_graph.manager.prefab_function_manager import PrefabFunctionManager

# 创建预制函数管理器
manager = PrefabFunctionManager()

# 加载人族预制函数
manager.load_prefab_functions('path/to/terran_prefab_functions.json')

# 获取所有预制函数
all_functions = list(manager.prefab_functions.values())
print(f"Loaded {len(all_functions)} prefab functions")
```

### 获取最优预制函数

```python
# 生成游戏状态信息
game_state = {
    'friendly_count': 10,
    'enemy_count': 8,
    'friendly_unit_types': {'Marine': 5, 'Marauder': 3, 'Medivac': 2},
    'enemy_unit_types': {'Zealot': 4, 'Stalker': 4},
    'has_low_health_units': False,
    'has_energy_units': True
}

# 获取最优预制函数
optimal_functions = manager.get_optimal_functions(observation, game_state, max_functions=5)

# 输出最优函数
for i, func in enumerate(optimal_functions, 1):
    print(f"{i}. {func['name']} (ID: {func['function_id']}, Score: {func['score']:.2f})")
```

## 集成指南

### 与 VLM Agent 集成

在 VLM Agent 中使用预制函数系统：

```python
from vlm_attention.run_env.agent.vlm_agent_without_move_v5 import VLMAgentWithoutMove

# 初始化 Agent
agent = VLMAgentWithoutMove(
    action_space={'attack': [(10,), (10,)]},
    config_path='',
    save_dir='./test_output'
)

# Agent 会自动加载和使用预制函数
# 在 get_action 方法中，会根据游戏状态选择最优预制函数
```

### 自定义预制函数

1. **创建新的预制函数**：按照 JSON Schema 格式创建新的预制函数
2. **验证结构**：使用 `schema_validator.py` 验证预制函数结构
3. **添加到文件**：将新的预制函数添加到对应种族的预制函数文件中
4. **测试功能**：运行单元测试确保功能正常

## 测试

### 运行单元测试

```bash
python -m pytest autodsl_affordance/core/linkage_graph/prefab_functions/tests/test_prefab_functions.py -v
```

### 验证 JSON Schema

```bash
python autodsl_affordance/core/linkage_graph/prefab_functions/utils/schema_validator.py
```

## 最佳实践

1. **保持一致性**：遵循命名约定和字段结构
2. **详细文档**：为每个预制函数提供清晰的描述和策略说明
3. **测试验证**：在添加新函数后运行测试
4. **性能考虑**：避免创建过于复杂的执行流程
5. **协同效应**：设计函数时考虑与其他函数的协同效应

## 故障排除

### 常见问题

1. **加载失败**：检查 JSON 文件格式是否正确，字段是否完整
2. **验证错误**：使用 JSON Schema 验证工具检查结构
3. **性能问题**：减少预制函数数量或简化执行流程
4. **兼容性问题**：确保与现有系统的兼容性

### 解决方案

1. **使用验证工具**：运行 `schema_validator.py` 检查预制函数结构
2. **查看日志**：检查系统日志了解具体错误信息
3. **测试隔离**：单独测试预制函数加载和执行
4. **回滚机制**：保留原始预制函数文件作为备份

## 版本历史

### 重构版本

- **当前版本**：重构后的预制函数系统
- **主要改进**：标准化结构、增强模块化设计、完善文档
- **兼容性**：保持与现有系统的完全兼容

## 贡献指南

1. **遵循命名约定**：确保新函数符合命名规范
2. **验证结构**：使用 JSON Schema 验证工具检查新函数
3. **添加测试**：为新函数添加相应的测试用例
4. **更新文档**：更新 README.md 文档以反映更改
5. **提交请求**：提交代码审查请求

## 联系方式

如有问题或建议，请联系项目维护者。