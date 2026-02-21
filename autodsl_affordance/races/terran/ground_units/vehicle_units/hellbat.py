# races/terran/ground_units/vehicle_units/hellbat.py

import os
import json
from typing import Dict, Any, List, Optional
from autodsl_affordance.races.terran import TerranVehicleUnit
from autodsl_affordance.core.base_units.unit import Cost, Position

class TerranHellbat(TerranVehicleUnit):
    """恶火战车 - 人族反轻甲车辆单位
    
    特性：
    - 对轻甲单位有额外伤害
    - 具备火焰喷射器的范围伤害能力
    - 可以变形为恶火模式（高速移动模式）
    - 装甲单位，具备机械属性
    
    功能：
    - 对抗敌方轻甲单位（如小狗、追猎者等）
    - 提供前排火力支援
    - 通过变形适应不同战场需求
    """
    
    def __init__(self, **kwargs):
        """初始化恶火战车单位
        
        Args:
            **kwargs: 自定义参数，将覆盖默认值
        """
        super().__init__()
        self.unique_class_name = "Terran_Hellbat"
        
        # 设置默认值
        self._set_default_values()
        
        # 尝试从JSON文件加载数据，失败则使用硬编码数据
        self._load_unit_data()
        
        # 应用自定义参数
        self._apply_custom_kwargs(**kwargs)
        
        # VLM优化
        self._enhance_vlm_interface()
        
    def _set_default_values(self):
        """设置单位的默认值
        
        初始化所有必要的属性为空或默认状态
        """
        self.description = ""
        self.cost = None
        self.attack = {}
        self.unit_stats = {}
        self.abilities = {}
        self.can_transform = False
        self.current_health = None
        
    def _load_unit_data(self):
        """加载数据，从JSON文件加载单位数据，失败则使用硬编码数据
        
        首先尝试从JSON文件加载配置，若失败则使用内置的硬编码数据
        """
        # 计算JSON文件路径（向上3层目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "..", "..", "..", "sc2_unit_info", f"Terran_Hellbat.json")
        json_path = os.path.normpath(json_path)
        
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 加载基本信息
                    self.description = data.get("description", "人族反轻甲车辆单位，恶火战车的战斗模式")
                    
                    # 加载成本信息
                    cost_data = data.get("cost", {})
                    self.cost = Cost(
                        mineral=cost_data.get("mineral", 100),
                        vespene=cost_data.get("vespene", 0),
                        supply=cost_data.get("supply", 2),
                        time=cost_data.get("time", 21)
                    )
                    
                    # 加载攻击信息
                    self.attack = data.get("attack", {
                        "targets": ["Ground"],
                        "damage": 18, "damage_upgrade": 2,
                        "dps": {"base": 16.4, "vs_light": 32.7},
                        "cooldown": 1.1,
                        "bonus_damage": {"value": 6, "upgrade": 1, "vs": "Light"},
                        "range": 2
                    })
                    
                    # 加载单位属性
                    self.unit_stats = data.get("unit_stats", {
                        "health": 135, "armor": 0, "armor_upgrade": 1,
                        "attributes": ["Armored", "Mechanical"],
                        "sight": 10, "speed": 3.15, "cargo_size": 4
                    })
                    
                    # 初始化当前生命值
                    self.current_health = self.unit_stats.get("health", 135)
                    
                    # 加载能力配置
                    self.abilities = data.get("abilities", {})
                    
                    # 加载特有属性
                    self.can_transform = data.get("can_transform", True)
            else:
                print(f"警告: JSON文件不存在，使用硬编码数据: {json_path}")
                self._set_hardcoded_data()
        except json.JSONDecodeError as e:
            print(f"JSON文件解析错误: {e}")
            self._set_hardcoded_data()
        except Exception as e:
            print(f"加载JSON文件时出错: {e}")
            self._set_hardcoded_data()
    
    def _set_hardcoded_data(self):
        """设置硬编码的单位数据作为后备
        
        当JSON文件加载失败时，使用内置的默认数据初始化单位
        """
        self.description = "人族反轻甲车辆单位，恶火战车的战斗模式"
        
        # 游戏属性
        self.cost = Cost(mineral=100, vespene=0, supply=2, time=21)
        self.attack = {
            "targets": ["Ground"],
            "damage": 18, "damage_upgrade": 2,
            "dps": {"base": 16.4, "vs_light": 32.7},
            "cooldown": 1.1,
            "bonus_damage": {"value": 6, "upgrade": 1, "vs": "Light"},
            "range": 2
        }
        self.unit_stats = {
            "health": 135, "armor": 0, "armor_upgrade": 1,
            "attributes": ["Armored", "Mechanical"],
            "sight": 10, "speed": 3.15, "cargo_size": 4
        }
        
        # 初始化当前生命值
        self.current_health = self.unit_stats["health"]
        
        # 能力配置
        self.abilities = {
            "transform_to_hellion": {"transform_time": 2},
            "flame_attack": {"splash": True}
        }
        
        # 车辆特有属性
        self.can_transform = True
        
        # 克制关系
        self.counter_relations = {
            "strong_against": ["Zergling", "Stalker", "Reaper", "Marine"],
            "weak_against": ["Marauder", "Roach", "Immortal"],
            "counters": []
        }
        
        # 升级信息
        self.upgrades = {
            "vehicle_armor": {"levels": 3, "current_level": 0},
            "vehicle_weapons": {"levels": 3, "current_level": 0}
        }
        
        # 战术信息
        self.tactical_info = {
            "strengths": ["对轻甲高伤害", "范围攻击", "可变形", "装甲保护"],
            "weaknesses": ["射程短", "移动速度一般", "造价较高"],
            "optimal_situation": ["对抗轻甲单位", "前排推进", "与坦克配合"]
        }
    
    def _enhance_vlm_interface(self):
        """增强VLM接口，添加预置函数候选
        
        为视觉语言模型提供更丰富的接口信息，包括自然语言别名、角色描述、战术关键词等
        """
        # 更新LLM接口信息
        self.llm_interface.update({
            "natural_language_aliases": ["恶火战车", "hellbat", "战斗模式", "反轻甲"],
            "role_description": self.description,
            "tactical_keywords": ["反轻甲", "近战", "范围伤害", "变形"],
            "primary_role": ["反轻甲", "前排", "范围输出"],
            "common_tactics": ["对抗小狗", "配合坦克", "模式切换"]
        })
        
        # 更新视觉识别信息
        self.visual_recognition.update({
            "unit_size": "medium",
            "color_scheme": ["blue", "red", "gray", "orange"],
            "silhouette": "armored vehicle with flamethrower",
            "animation_characteristics": ["flame attack", "transforming", "clunky movement"]
        })
        
        # 更新战术上下文
        self.tactical_context.update({
            "formation_preferences": ["front line", "clustered for aoe"],
            "engagement_distances": ["melee"],
            "micro_maneuvers": ["flame kiting", "transform timing"]
        })
        
        # 定义预置函数候选
        self.prefab_function_candidates = [
            {
                "function_name": "hellbat_light_infantry_counter",
                "description": "恶火战车对抗轻甲步兵",
                "parameters": {
                    "target_group_position": "目标轻甲单位集群位置",
                    "retreat_position": "撤退位置"
                },
                "execution_flow": [
                    "advance_to_engagement_range(target_group_position)",
                    "apply_flame_attack_to_group(target_group_position)",
                    "retreat_if_damaged(retreat_position)"
                ]
            },
            {
                "function_name": "hellbat_hellion_transform_tactics",
                "description": "恶火战车变形战术",
                "parameters": {
                    "battle_position": "战场位置",
                    "movement_position": "移动位置"
                },
                "execution_flow": [
                    "evaluate_combat_situation(battle_position)",
                    "transform_to_hellbat_for_combat(battle_position)",
                    "transform_to_hellion_for_maneuver(movement_position)"
                ]
            }
        ]
    
    def transform_to_hellion(self) -> Dict[str, Any]:
        """变形为恶火模式
        
        Returns:
            Dict[str, Any]: 操作结果，包含成功状态
        """
        result = {
            "success": False,
            "action": "transform_to_hellion",
            "transform_time": self.abilities.get("transform_to_hellion", {}).get("transform_time", 2),
            "reason": None
        }
        
        if self.can_transform:
            result["success"] = True
            print(f"{self.unique_class_name} 变形为恶火模式")
        else:
            result["reason"] = "无法变形"
            print(f"{self.unique_class_name} 无法变形为恶火模式")
        
        return result
        
    def _apply_custom_kwargs(self, **kwargs):
        """应用自定义参数覆盖默认值
        
        Args:
            **kwargs: 自定义参数
        """
        # 处理cost对象的自定义参数
        if 'mineral' in kwargs or 'vespene' in kwargs or 'supply' in kwargs or 'time' in kwargs:
            if self.cost:
                if 'mineral' in kwargs:
                    self.cost.mineral = kwargs.pop('mineral')
                if 'vespene' in kwargs:
                    self.cost.vespene = kwargs.pop('vespene')
                if 'supply' in kwargs:
                    self.cost.supply = kwargs.pop('supply')
                if 'time' in kwargs:
                    self.cost.time = kwargs.pop('time')
        
        # 直接覆盖其他属性
        for key, value in kwargs.items():
            setattr(self, key, value)
            
    def to_dict(self) -> Dict[str, Any]:
        """将单位信息转换为字典格式
        
        Returns:
            Dict[str, Any]: 单位的字典表示
        """
        unit_dict = {
            "unique_class_name": self.unique_class_name,
            "description": self.description,
            "unit_stats": self.unit_stats,
            "attack": self.attack,
            "abilities": self.abilities,
            "can_transform": self.can_transform
        }
        
        # 添加cost信息
        if self.cost:
            unit_dict["cost"] = {
                "mineral": self.cost.mineral,
                "vespene": self.cost.vespene,
                "supply": self.cost.supply,
                "time": self.cost.time
            }
        
        # 添加当前生命值
        if hasattr(self, 'current_health'):
            unit_dict["current_health"] = self.current_health
        
        # 添加其他可选属性
        if hasattr(self, 'counter_relations'):
            unit_dict["counter_relations"] = self.counter_relations
        if hasattr(self, 'upgrades'):
            unit_dict["upgrades"] = self.upgrades
        if hasattr(self, 'tactical_info'):
            unit_dict["tactical_info"] = self.tactical_info
        
        return unit_dict