# races/terran/ground_units/vehicle_units/siege_tank.py

import os
import json
from typing import Dict, Any, List, Optional
from autodsl_affordance.races.terran import TerranVehicleUnit
from autodsl_affordance.core.base_units.unit import Cost, Position

class TerranSiegeTank(TerranVehicleUnit):
    """攻城坦克 - 重型装甲单位，可切换为攻城模式，提供远程火力支援"""
    
    def __init__(self, **kwargs):
        """初始化攻城坦克单位
        
        Args:
            **kwargs: 自定义参数，将覆盖默认值
        """
        
        super().__init__()
        self.unique_class_name = "Terran_SiegeTank"
        
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
        self.is_in_siege_mode = False
        self.current_health = None
        
    def _load_unit_data(self):
        """加载数据，从JSON文件加载单位数据，失败则使用硬编码数据
        
        首先尝试从JSON文件加载配置，若失败则使用内置的硬编码数据
        """
        # 计算JSON文件路径（向上3层目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "..", "..", "..", "sc2_unit_info", f"Terran_SiegeTank.json")
        json_path = os.path.normpath(json_path)
        
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 加载基本信息
                    self.description = data.get("description", "人族重型装甲单位，可切换为攻城模式，提供远程火力支援")
                    
                    # 加载成本信息
                    cost_data = data.get("cost", {})
                    self.cost = Cost(
                        mineral=cost_data.get("mineral", 150),
                        vespene=cost_data.get("vespene", 125),
                        supply=cost_data.get("supply", 3),
                        time=cost_data.get("time", 42)
                    )
                    
                    # 加载攻击信息
                    self.attack = data.get("attack", {
                        "siege_mode": {
                            "damage": 35,
                            "bonus_damage": {"value": 30, "vs": "Armored"},
                            "range": 13,
                            "cooldown": 1.5
                        },
                        "tank_mode": {
                            "damage": 10,
                            "bonus_damage": {"value": 5, "vs": "Light"},
                            "range": 6,
                            "cooldown": 1.2
                        }
                    })
                    
                    # 加载单位属性
                    self.unit_stats = data.get("unit_stats", {
                        "health": 170,
                        "armor": 1,
                        "armor_upgrade": 1,
                        "attributes": ["Armored", "Mechanical"],
                        "sight": 12,
                        "speed": 2.25,
                        "siege_mode_speed": 0,
                        "cargo_size": 4
                    })
                    
                    # 初始化当前生命值
                    self.current_health = self.unit_stats.get("health", 170)
                    
                    # 加载能力配置
                    self.abilities = data.get("abilities", {
                        "siege_mode": {"transform_time": 15},
                        "unsiege": {"transform_time": 15}
                    })
                    
                    # 加载特有属性
                    self.is_in_siege_mode = data.get("is_in_siege_mode", False)
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
        self.description = "人族重型装甲单位，可切换为攻城模式，提供远程火力支援"
        
        # 游戏属性
        self.cost = Cost(mineral=150, vespene=125, supply=3, time=42)
        self.attack = {
            "siege_mode": {
                "damage": 35,
                "bonus_damage": {"value": 30, "vs": "Armored"},
                "range": 13,
                "cooldown": 1.5
            },
            "tank_mode": {
                "damage": 10,
                "bonus_damage": {"value": 5, "vs": "Light"},
                "range": 6,
                "cooldown": 1.2
            }
        }
        self.unit_stats = {
            "health": 170,
            "armor": 1,
            "armor_upgrade": 1,
            "attributes": ["Armored", "Mechanical"],
            "sight": 12,
            "speed": 2.25,
            "siege_mode_speed": 0,
            "cargo_size": 4
        }
        
        # 初始化当前生命值
        self.current_health = self.unit_stats["health"]
        
        # 能力配置
        self.abilities = {
            "siege_mode": {"transform_time": 15},
            "unsiege": {"transform_time": 15}
        }
        
        # 特有属性
        self.is_in_siege_mode = False
        
        # 克制关系
        self.counter_relations = {
            "strong_against": ["Armored Units", "Buildings", "Clustered Infantry"],
            "weak_against": ["Air Units", "Mobile Units in Tank Mode"],
            "counters": ["Immortal", "Ultralisk", "Battlecruiser"]
        }
        
        # 升级信息
        self.upgrades = {
            "vehicle_armor": {"levels": 3, "current_level": 0},
            "vehicle_weapons": {"levels": 3, "current_level": 0}
        }
        
        # 战术信息
        self.tactical_info = {
            "strengths": ["远程范围攻击", "高伤害", "装甲保护", "可切换模式"],
            "weaknesses": ["变形时间长", "攻城模式无法移动", "视野有限"],
            "optimal_situation": ["防守阵地", "对集群单位", "对建筑"]
        }
    
    def _enhance_vlm_interface(self):
        """增强VLM接口，添加预置函数候选
        
        为视觉语言模型提供更丰富的接口信息，包括自然语言别名、角色描述、战术关键词等
        """
        # 更新LLM接口信息
        self.llm_interface.update({
            "natural_language_aliases": ["攻城坦克", "siege tank", "坦克", "远程支援"],
            "role_description": self.description,
            "tactical_keywords": ["远程", "范围伤害", "装甲", "变形"],
            "primary_role": ["远程支援", "反装甲", "阵地防守"],
            "common_tactics": ["攻城模式", "坦克阵", "防守高地"]
        })
        
        # 更新视觉识别信息
        self.visual_recognition.update({
            "unit_size": "large",
            "color_scheme": ["blue", "red", "gray", "green"],
            "silhouette": "armored tank with large cannon",
            "animation_characteristics": ["siege transformation", "cannon firing", "slow movement"]
        })
        
        # 更新战术上下文
        self.tactical_context.update({
            "formation_preferences": ["tank line", "siege positions", "high ground"],
            "engagement_distances": ["long range"],
            "micro_maneuvers": ["siege timing", "positioning", "unsiege to retreat"]
        })
        
        # 定义预置函数候选
        self.prefab_function_candidates = [
            {
                "function_name": "siege_tank_position_attack",
                "description": "攻城坦克阵地攻击",
                "parameters": {
                    "siege_position": "攻城位置",
                    "target_area": "目标区域"
                },
                "execution_flow": [
                    "move_to_position(siege_position)",
                    "enter_siege_mode(siege_position)",
                    "attack_area(target_area)"
                ]
            },
            {
                "function_name": "siege_tank_defensive_line",
                "description": "攻城坦克防线防守",
                "parameters": {
                    "defensive_position": "防守位置",
                    "retreat_point": "撤退点"
                },
                "execution_flow": [
                    "form_defensive_line(defensive_position)",
                    "enter_siege_mode(defensive_position)",
                    "retreat_if_threatened(retreat_point)"
                ]
            }
        ]
    
    def toggle_siege_mode(self) -> Dict[str, Any]:
        """切换攻城模式
        
        Returns:
            Dict[str, Any]: 操作结果，包含成功状态
        """
        result = {
            "success": False,
            "action": "toggle_siege_mode",
            "transform_time": self.abilities.get("siege_mode", {}).get("transform_time", 15),
            "reason": None,
            "new_mode": "siege" if not self.is_in_siege_mode else "tank"
        }
        
        # 切换模式
        self.is_in_siege_mode = not self.is_in_siege_mode
        result["success"] = True
        print(f"{self.unique_class_name} 切换为{'攻城模式' if self.is_in_siege_mode else '普通模式'}")
        
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
            "is_in_siege_mode": self.is_in_siege_mode
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