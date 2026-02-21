# races/zerg/ground_units/combat_units/zergling.py

import os
import json
from typing import Dict, Any, List
from autodsl_affordance.races.zerg import ZergCombatUnit
from autodsl_affordance.core.base_units.unit import Cost, Position

class ZergZergling(ZergCombatUnit):
    """跳虫 - 虫族基础快速近战单位"""
    
    def __init__(self, **kwargs):
        # 不要将development_mode传递给父类
        super().__init__()
        self.unique_class_name = "Zerg_Zergling"
        
        # 设置默认值
        self._set_default_values()
        
        # 尝试从JSON文件加载数据，失败则使用硬编码数据
        self._load_unit_data()
        
        # VLM优化
        self._enhance_vlm_interface()
    
    def _set_default_values(self):
        """设置默认值"""
        self.description = ""
        self.cost = None
        self.attack = {}
        self.unit_stats = {}
        self.abilities = {}
        self.requires_spawning_pool = False
        self.can_burrow = False
        self.regeneration_rate = 0.0
    
    def _load_unit_data(self):
        """从JSON文件加载单位数据"""
        # 计算JSON文件路径（向上3层目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "..", "..", "..", "sc2_unit_info", f"Zerg_Zergling.json")
        json_path = os.path.normpath(json_path)
        
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 加载基本信息
                    self.description = data.get("description", "虫族基础快速近战单位，具备高机动性和数量优势")
                    
                    # 加载成本信息
                    cost_data = data.get("cost", {})
                    self.cost = Cost(
                        mineral=cost_data.get("mineral", 25),
                        vespene=cost_data.get("vespene", 0),
                        supply=cost_data.get("supply", 0.5),
                        time=cost_data.get("time", 17)
                    )
                    
                    # 加载攻击信息
                    self.attack = data.get("attack", {
                        "targets": ["Ground"],
                        "damage": 5, "damage_upgrade": 1,
                        "dps": {"base": 8.9},
                        "cooldown": 0.497,
                        "range": 0.1
                    })
                    
                    # 加载单位属性
                    self.unit_stats = data.get("unit_stats", {
                        "health": 35, "armor": 0, "armor_upgrade": 1,
                        "attributes": ["Light", "Biological"],
                        "sight": 8, "speed": 4.13, "cargo_size": 1
                    })
                    
                    # 加载能力配置
                    self.abilities = data.get("abilities", {})
                    
                    # 加载特有属性
                    self.requires_spawning_pool = data.get("requires_spawning_pool", True)
                    self.can_burrow = data.get("can_burrow", True)
                    self.regeneration_rate = data.get("regeneration_rate", 0.273)
            else:
                print(f"警告: JSON文件不存在，使用硬编码数据: {json_path}")
                self._set_hardcoded_data()
        except Exception as e:
            print(f"加载JSON文件时出错: {e}")
            self._set_hardcoded_data()
    
    def _set_hardcoded_data(self):
        """设置硬编码的单位数据作为后备"""
        self.description = "虫族基础快速近战单位，具备高机动性和数量优势"
        
        # 游戏属性
        self.cost = Cost(mineral=25, vespene=0, supply=0.5, time=17)
        self.attack = {
            "targets": ["Ground"],
            "damage": 5, "damage_upgrade": 1,
            "dps": {"base": 8.9},
            "cooldown": 0.497,
            "range": 0.1
        }
        self.unit_stats = {
            "health": 35, "armor": 0, "armor_upgrade": 1,
            "attributes": ["Light", "Biological"],
            "sight": 8, "speed": 4.13, "cargo_size": 1
        }
        
        # 能力配置
        self.abilities = {
            "metabolic_boost": {
                "researched": False,
                "research_time": 110,
                "speed_bonus": 1.41,
                "cooldown": 0
            },
            "adrenal_glands": {
                "researched": False,
                "research_time": 130,
                "attack_speed_bonus": 0.351
            },
            "burrow": {
                "researched": False,
                "research_time": 90
            }
        }
        
        # 跳虫特有属性
        self.requires_spawning_pool = True
        self.can_burrow = True
        self.regeneration_rate = 0.273
        
        # 克制关系
        self.counter_relations = {
            "strong_against": ["Worker", "Light Infantry"],
            "weak_against": ["AOE Damage", "Armored Units"],
            "counters": []
        }
        
        # 升级信息
        self.upgrades = {
            "carapace": {"levels": 3, "current_level": 0},
            "melee_attacks": {"levels": 3, "current_level": 0}
        }
        
        # 战术信息
        self.tactical_info = {
            "strengths": ["高机动性", "低成本", "快速生产", "数量优势"],
            "weaknesses": ["脆弱", "单体伤害低", "惧怕AOE"],
            "optimal_situation": ["早期骚扰", "数量压制", "包抄后排"]
        }
    
    def _enhance_vlm_interface(self):
        """增强VLM接口，添加预置函数候选"""
        # 更新LLM接口信息
        self.llm_interface.update({
            "natural_language_aliases": ["跳虫", "zergling", "小狗", "速狗"],
            "role_description": self.description,
            "tactical_keywords": ["快速", "近战", "数量压制", "骚扰"],
            "primary_role": ["基础输出", "骚扰", "侦查"],
            "common_tactics": ["数量压制", "包抄后排", "速攻战术"]
        })
        
        # 更新视觉识别信息
        self.visual_recognition.update({
            "unit_size": "small",
            "color_scheme": ["red", "brown"],
            "silhouette": " quadrupedal insectoid",
            "animation_characteristics": ["fast movement", "jumping attack"]
        })
        
        # 更新战术上下文
        self.tactical_context.update({
            "formation_preferences": ["swarm", "flanking"],
            "engagement_distances": ["melee"],
            "micro_maneuvers": ["kiting", "surrounding"]
        })
        
        # 定义预置函数候选（符合标准模板要求）
        self.prefab_function_candidates = [
            {
                "function_name": "zergling_swarm_attack",
                "description": "跳虫群体攻击敌方单位",
                "parameters": {
                    "targets": "目标单位列表",
                    "attack_formation": "攻击阵型 (swarm/surround)"
                },
                "execution_flow": [
                    "move_to_target(targets[0])",
                    "swarm_attack(targets)",
                    "retreat_if_vulnerable()"
                ]
            },
            {
                "function_name": "zergling_rush",
                "description": "跳虫速攻敌方基地",
                "parameters": {
                    "target_location": "目标位置",
                    "enemy_base_defenses": "敌方基地防御信息"
                },
                "execution_flow": [
                    "speed_boost_attack()",
                    "priority_target_selection(enemy_base_defenses)",
                    "swarm_attack(enemy_base_defenses)",
                    "regroup_if_needed()"
                ]
            },
            {
                "function_name": "zergling_ambush",
                "description": "跳虫设置伏击",
                "parameters": {
                    "ambush_position": "伏击位置",
                    "target_path": "目标路径"
                },
                "execution_flow": [
                    "burrow_if_possible(ambush_position)",
                    "wait_for_enemy(target_path)",
                    "ambush_enemy(target_path)",
                    "retreat_after_ambush()"
                ]
            }
        ]
    
    def swarm_attack(self, targets: list) -> Dict[str, Any]:
        """群体攻击"""
        result = {
            "success": True,
            "action": "swarm_attack",
            "target_count": len(targets),
            "attack_formation": "swarm"
        }
        print(f"{self.unique_class_name} 进行群体攻击，目标数量: {len(targets)}")
        return result
    
    def speed_boost_attack(self) -> Dict[str, Any]:
        """使用代谢加速进行快速攻击"""
        result = {
            "success": False,
            "action": "speed_boost_attack",
            "speed_boosted": False,
            "reason": None
        }
        
        metabolic_boost = self.abilities.get("metabolic_boost", {})
        
        # 检查是否已研发
        if not metabolic_boost.get("researched", False):
            result["reason"] = "代谢加速尚未研究"
            return result
        
        # 应用加速效果
        result["success"] = True
        result["speed_boosted"] = True
        result["speed_bonus"] = metabolic_boost.get("speed_bonus", 1.41)
        
        if hasattr(self, 'unit_stats') and 'speed' in self.unit_stats:
            current_speed = self.unit_stats['speed']
            boosted_speed = current_speed + metabolic_boost.get("speed_bonus", 1.41)
            result["current_speed"] = boosted_speed
            print(f"{self.unique_class_name} 使用代谢加速，速度提升至: {boosted_speed}")
        
        return result
    
    def burrow_if_possible(self, position: Position) -> Dict[str, Any]:
        """如果可能，进行掘地"""
        result = {
            "success": False,
            "action": "burrow",
            "burrowed": False,
            "position": position,
            "reason": None
        }
        
        if not self.can_burrow:
            result["reason"] = "单位不具备掘地能力"
            return result
        
        burrow = self.abilities.get("burrow", {})
        if not burrow.get("researched", False):
            result["reason"] = "掘地技能尚未研究"
            return result
        
        result["success"] = True
        result["burrowed"] = True
        print(f"{self.unique_class_name} 在位置 {position} 进行掘地")
        return result
    
    def ambush_enemy(self, target_path: list) -> Dict[str, Any]:
        """伏击敌人"""
        result = {
            "success": True,
            "action": "ambush",
            "ambush_position": target_path[0],
            "target_count": len(target_path)
        }
        print(f"{self.unique_class_name} 在路径 {target_path[0]} 进行伏击")
        return result
    
    def retreat_after_ambush(self) -> Dict[str, Any]:
        """伏击后撤退"""
        result = {
            "success": True,
            "action": "retreat_after_ambush",
            "retreat_complete": True
        }
        print(f"{self.unique_class_name} 完成伏击后撤退")
        return result
    
    def regroup_if_needed(self) -> Dict[str, Any]:
        """根据需要重新集结"""
        result = {
            "success": True,
            "action": "regroup",
            "regrouped": True
        }
        print(f"{self.unique_class_name} 重新集结队伍")
        return result
    
    def retreat_if_vulnerable(self) -> Dict[str, Any]:
        """如果脆弱则撤退"""
        result = {
            "success": True,
            "action": "retreat_if_vulnerable",
            "retreated": False
        }
        
        # 简单的脆弱性检查逻辑
        if hasattr(self, 'unit_stats') and 'health' in self.unit_stats:
            current_health = getattr(self, 'current_health', self.unit_stats['health'])
            max_health = self.unit_stats['health']
            
            if current_health < max_health * 0.3:
                result["retreated"] = True
                print(f"{self.unique_class_name} 因生命值过低而撤退")
        
        return result