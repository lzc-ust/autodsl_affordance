# races/terran/ground_units/infantry_units/reaper.py

import os
import json
from typing import Dict, Any, List, Optional
from autodsl_affordance.races.terran import TerranInfantryUnit
from autodsl_affordance.core.base_units.unit import Cost, Position

class TerranReaper(TerranInfantryUnit):
    """死神 - 人族快速侦查骚扰单位
    
    特性：
    - 高机动性，可以跳跃悬崖
    - 对轻甲单位有额外伤害
    - 装备KD8炸药，可以攻击建筑和群体目标
    - 视野范围大，适合侦查
    
    功能：
    - 侦查敌方基地
    - 骚扰敌方农民和建筑
    - 利用高机动性进行战术机动
    """
    
    def __init__(self, **kwargs):
        """初始化死神单位
        
        Args:
            **kwargs: 自定义参数，将覆盖默认值
        """
        super().__init__()
        self.unique_class_name = "Terran_Reaper"
        
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
        self.can_traverse_cliffs = False
        self.current_health = None
        
    def _load_unit_data(self):
        """加载数据，从JSON文件加载单位数据，失败则使用硬编码数据
        
        首先尝试从JSON文件加载配置，若失败则使用内置的硬编码数据
        """
        # 计算JSON文件路径（向上3层目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "..", "..", "..", "sc2_unit_info", f"Terran_Reaper.json")
        json_path = os.path.normpath(json_path)
        
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 加载基本信息
                    self.description = data.get("description", "人族快速侦查骚扰单位，具备高机动性和手雷攻击")
                    
                    # 加载成本信息
                    cost_data = data.get("cost", {})
                    self.cost = Cost(
                        mineral=cost_data.get("mineral", 50),
                        vespene=cost_data.get("vespene", 50),
                        supply=cost_data.get("supply", 1),
                        time=cost_data.get("time", 32)
                    )
                    
                    # 加载攻击信息
                    self.attack = data.get("attack", {
                        "targets": ["Ground"],
                        "damage": 4, "damage_upgrade": 1,
                        "dps": {"base": 10.3, "vs_light": 20.6},
                        "cooldown": 0.39,
                        "bonus_damage": {"value": 8, "upgrade": 1, "vs": "Light"},
                        "range": 4.5
                    })
                    
                    # 加载单位属性
                    self.unit_stats = data.get("unit_stats", {
                        "health": 60, "armor": 0, "armor_upgrade": 1,
                        "attributes": ["Light", "Biological"],
                        "sight": 9, "speed": 5.25, "cargo_size": 1
                    })
                    
                    # 初始化当前生命值
                    self.current_health = self.unit_stats.get("health", 60)
                    
                    # 加载能力配置
                    self.abilities = data.get("abilities", {})
                    
                    # 加载特有属性
                    self.can_traverse_cliffs = data.get("can_traverse_cliffs", True)
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
        self.description = "人族快速侦查骚扰单位，具备高机动性和手雷攻击"
        
        # 游戏属性
        self.cost = Cost(mineral=50, vespene=50, supply=1, time=32)
        self.attack = {
            "targets": ["Ground"],
            "damage": 4, "damage_upgrade": 1,
            "dps": {"base": 10.3, "vs_light": 20.6},
            "cooldown": 0.39,
            "bonus_damage": {"value": 8, "upgrade": 1, "vs": "Light"},
            "range": 4.5
        }
        self.unit_stats = {
            "health": 60, "armor": 0, "armor_upgrade": 1,
            "attributes": ["Light", "Biological"],
            "sight": 9, "speed": 5.25, "cargo_size": 1
        }
        
        # 初始化当前生命值
        self.current_health = self.unit_stats["health"]
        
        # 能力配置
        self.abilities = {
            "kd8_charge": {
                "cooldown": 7,
                "damage": 5,
                "splash_radius": 1.5,
                "construction_damage": 30
            },
            "jetpack": {"cliff_jump": True}
        }
        
        # 步兵特有属性
        self.can_traverse_cliffs = True
        
        # 克制关系
        self.counter_relations = {
            "strong_against": ["SCV", "Probe", "Drone", "Marine"],
            "weak_against": ["Zealot", "Stalker", "Roach"],
            "counters": []
        }
        
        # 升级信息
        self.upgrades = {
            "infantry_armor": {"levels": 3, "current_level": 0},
            "infantry_weapons": {"levels": 3, "current_level": 0}
        }
        
        # 战术信息
        self.tactical_info = {
            "strengths": ["高机动性", "对轻甲高伤害", "视野大", "可跳崖"],
            "weaknesses": ["生命值低", "无法对空", "射程短"],
            "optimal_situation": ["早期侦查", "骚扰农民", "利用地形机动"]
        }
    
    def _enhance_vlm_interface(self):
        """增强VLM接口，添加预置函数候选
        
        为视觉语言模型提供更丰富的接口信息，包括自然语言别名、角色描述、战术关键词等
        """
        # 更新LLM接口信息
        self.llm_interface.update({
            "natural_language_aliases": ["死神", "reaper", "收割者", "侦查兵"],
            "role_description": self.description,
            "tactical_keywords": ["侦查", "骚扰", "高地机动", "农民杀手"],
            "primary_role": ["侦查", "骚扰", "早期压制"],
            "common_tactics": ["侦查敌军", "骚扰农民", "高地跳跃"]
        })
        
        # 更新视觉识别信息
        self.visual_recognition.update({
            "unit_size": "small",
            "color_scheme": ["blue", "red", "gray"],
            "silhouette": "small infantry with jetpack",
            "animation_characteristics": ["fast movement", "cliff jumping", "grenade throwing"]
        })
        
        # 更新战术上下文
        self.tactical_context.update({
            "formation_preferences": ["solo", "small groups"],
            "engagement_distances": ["close"],
            "micro_maneuvers": ["hit and run", "cliff jumping", "grenade kiting"]
        })
        
        # 定义预置函数候选
        self.prefab_function_candidates = [
            {
                "function_name": "reaper_scout_mission",
                "description": "死神侦查任务",
                "parameters": {
                    "target_area": "目标侦查区域"
                },
                "execution_flow": [
                    "move_to_scouting_position(target_area)",
                    "gather_intelligence()",
                    "return_to_base_with_information()"
                ]
            },
            {
                "function_name": "reaper_harass_operation",
                "description": "死神骚扰作战",
                "parameters": {
                    "enemy_worker_position": "敌方农民位置",
                    "escape_route": "撤退路线"
                },
                "execution_flow": [
                    "jump_to_high_ground_near_enemy(enemy_worker_position)",
                    "use_kd8_charge_on_workers(enemy_worker_position)",
                    "retreat_via_escape_route(escape_route)"
                ]
            }
        ]
    
    def use_kd8_charge(self, target_position: Position) -> Dict[str, Any]:
        """使用KD8炸药
        
        Args:
            target_position: 目标位置
            
        Returns:
            Dict[str, Any]: 操作结果，包含成功状态、伤害信息等
        """
        result = {
            "success": True,
            "action": "use_kd8_charge",
            "target_position": target_position,
            "damage": self.abilities.get("kd8_charge", {}).get("damage", 5),
            "construction_damage": self.abilities.get("kd8_charge", {}).get("construction_damage", 30),
            "cooldown": self.abilities.get("kd8_charge", {}).get("cooldown", 7)
        }
        
        print(f"{self.unique_class_name} 在位置 {target_position} 投掷KD8炸药")
        return result
    
    def jump_cliff(self, cliff_position: Position) -> Dict[str, Any]:
        """跳跃悬崖
        
        Args:
            cliff_position: 悬崖位置
            
        Returns:
            Dict[str, Any]: 操作结果，包含成功状态
        """
        result = {
            "success": False,
            "action": "jump_cliff",
            "cliff_position": cliff_position,
            "reason": None
        }
        
        if self.can_traverse_cliffs:
            result["success"] = True
            print(f"{self.unique_class_name} 跳跃到悬崖位置 {cliff_position}")
        else:
            result["reason"] = "无法跳跃悬崖"
            print(f"{self.unique_class_name} 无法跳跃悬崖")
        
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
            "can_traverse_cliffs": self.can_traverse_cliffs
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