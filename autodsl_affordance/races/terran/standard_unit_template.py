# standard_unit_template.py
# 人族单位类标准模板规范

"""
人族单位类标准模板

所有Terran单位类都应遵循此模板，确保代码风格、结构和功能的一致性。
"""

from typing import Dict, Any, List
from autodsl_affordance.races.terran import TerranUnit  # 根据单位类型导入相应的基类
from autodsl_affordance.core.base_units.unit import Cost, Position


class StandardTerranUnit(TerranUnit):
    """
    标准人族单位类模板
    
    注意：
    1. 每个单位类必须有清晰的中文和英文注释
    2. 严格按照模板结构组织代码
    3. 使用JSON文件加载数据作为首选，硬编码作为后备
    4. 确保所有必要的属性和方法都按照统一格式定义
    """
    
    def __init__(self, **kwargs):
        """
        初始化单位
        
        Args:
            **kwargs: 可选参数，允许传入自定义配置
        """
        # 调用父类初始化
        super().__init__(**kwargs)
        
        # 设置单位唯一标识
        self.unique_class_name = "Standard_Terran_Unit"  # 替换为实际单位名称
        
        # 设置默认值
        self._set_default_values()
        
        # 加载单位数据（优先从JSON加载，失败则使用硬编码）
        self._load_unit_data()
        
        # 应用自定义参数
        self._apply_custom_kwargs(kwargs)
        
        # 增强VLM接口
        self._enhance_vlm_interface()
    
    def _set_default_values(self):
        """
        设置所有属性的默认值
        确保所有可能的属性都有初始值，避免None值导致的错误
        """
        # 基本信息
        self.description = ""  # 单位描述
        
        # 游戏属性
        self.cost = None  # 成本对象
        self.attack = {}  # 攻击属性字典
        self.unit_stats = {}  # 单位统计信息
        self.abilities = {}  # 能力配置
        
        # 单位特有属性 - 根据具体单位类型添加
        # 例如：self.can_stimpack = False
    
    def _load_unit_data(self):
        """
        从JSON文件加载单位数据
        如果JSON文件不存在或加载失败，则使用硬编码数据
        """
        import os
        import json
        
        # 计算JSON文件路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 注意：根据实际目录结构调整路径
        json_path = os.path.join(current_dir, "..", "..", "sc2_unit_info", f"{self.unique_class_name}.json")
        json_path = os.path.normpath(json_path)
        
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 加载基本信息
                    self.description = data.get("description", "")
                    
                    # 加载成本信息
                    cost_data = data.get("cost", {})
                    self.cost = Cost(
                        mineral=cost_data.get("mineral", 0),
                        vespene=cost_data.get("vespene", 0),
                        supply=cost_data.get("supply", 0),
                        time=cost_data.get("time", 0)
                    )
                    
                    # 加载攻击信息
                    self.attack = data.get("attack", {})
                    
                    # 加载单位属性
                    self.unit_stats = data.get("unit_stats", {})
                    
                    # 加载能力配置
                    self.abilities = data.get("abilities", {})
                    
                    # 加载特有属性 - 根据具体单位类型添加
                    # 例如：self.can_stimpack = data.get("can_stimpack", False)
            else:
                # JSON文件不存在，使用硬编码数据
                self._set_hardcoded_data()
        except Exception as e:
            # 加载出错，使用硬编码数据
            print(f"警告：加载JSON文件失败 {json_path}: {e}")
            self._set_hardcoded_data()
    
    def _set_hardcoded_data(self):
        """
        设置硬编码的单位数据作为后备
        当JSON文件加载失败时使用
        """
        # 设置基本信息
        self.description = "标准人族单位"  # 替换为实际描述
        
        # 设置游戏属性
        self.cost = Cost(mineral=0, vespene=0, supply=0, time=0)  # 替换为实际值
        self.attack = {"targets": [], "damage": 0, "range": 0}  # 替换为实际值
        self.unit_stats = {"health": 0, "armor": 0, "speed": 0}  # 替换为实际值
        self.abilities = {}  # 替换为实际值
        
        # 设置特有属性 - 根据具体单位类型添加
        # 例如：self.can_stimpack = False
    
    def _apply_custom_kwargs(self, kwargs):
        """
        应用从构造函数传入的自定义参数
        
        Args:
            kwargs: 自定义参数字典
        """
        # 处理开发模式
        if kwargs.get("development_mode", False):
            # 开发模式特定的设置
            pass
        
        # 根据需要处理其他自定义参数
    
    def _enhance_vlm_interface(self):
        """
        增强VLM接口，添加自然语言描述和战术关键词
        用于大语言模型交互
        """
        self.llm_interface.update({
            "natural_language_aliases": ["标准单位", "standard unit"],  # 替换为实际别名
            "role_description": self.description,
            "tactical_keywords": ["示例", "关键词"],  # 替换为实际关键词
            "primary_role": ["示例角色"],  # 替换为实际角色
            "common_tactics": ["示例战术"]  # 替换为实际战术
        })
    
    # 单位特有方法 - 根据具体单位类型添加
    # 例如：
    # def stimpack(self) -> bool:
    #     """
    #     使用兴奋剂能力
    #     
    #     Returns:
    #         bool: 是否成功使用
    #     """
    #     pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将单位对象转换为字典表示
        
        Returns:
            Dict[str, Any]: 单位数据字典
        """
        return {
            "unique_class_name": self.unique_class_name,
            "description": self.description,
            "cost": {
                "mineral": self.cost.mineral if self.cost else 0,
                "vespene": self.cost.vespene if self.cost else 0,
                "supply": self.cost.supply if self.cost else 0,
                "time": self.cost.time if self.cost else 0
            },
            "attack": self.attack,
            "unit_stats": self.unit_stats,
            "abilities": self.abilities,
            "llm_interface": self.llm_interface
        }


# 模板使用说明
"""
使用此模板创建新的人族单位类时：

1. 复制此模板并命名为相应的单位类名（如：marine.py, marauder.py等）
2. 将类名从StandardTerranUnit更改为具体的单位类名（如：TerranMarine）
3. 根据单位类型更改父类导入（如：TerranInfantryUnit, TerranVehicleUnit等）
4. 替换unique_class_name为实际单位名称
5. 在_set_default_values()中添加单位特有的属性
6. 在_load_unit_data()中添加加载特有属性的代码
7. 在_set_hardcoded_data()中添加硬编码的特有属性值
8. 添加单位特有的方法
9. 更新_enhance_vlm_interface()中的内容
10. 根据需要扩展to_dict()方法以包含特有属性

确保遵循以下最佳实践：
- 所有方法和属性都有清晰的文档字符串
- 使用类型提示
- 保持代码风格一致
- 处理边界情况和错误
- 优先使用JSON文件加载数据
"""