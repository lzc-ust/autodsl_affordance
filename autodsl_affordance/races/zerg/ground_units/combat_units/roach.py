# races/zerg/ground_units/combat_units/roach.py

import os
import json
from typing import Dict, Any, List
from autodsl_affordance.races.zerg import ZergCombatUnit
from autodsl_affordance.core.base_units.unit import Cost, Position

class ZergRoach(ZergCombatUnit):
    """蟑螂 - 虫族重甲远程单位"""
    
    def __init__(self, **kwargs):
        # 不要将development_mode传递给父类
        super().__init__()
        self.unique_class_name = "Zerg_Roach"
        
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
        self.can_tunnel = False
        self.regeneration_rate = 0.0
    
    def _load_unit_data(self):
        """从JSON文件加载单位数据"""
        # 计算JSON文件路径（向上3层目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "..", "..", "..", "sc2_unit_info", f"Zerg_Roach.json")
        json_path = os.path.normpath(json_path)
        
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 加载基本信息
                    self.description = data.get("description", "虫族重甲远程单位，具备高生命恢复和地道移动能力")
                    
                    # 加载成本信息
                    cost_data = data.get("cost", {})
                    self.cost = Cost(
                        mineral=cost_data.get("mineral", 75),
                        vespene=cost_data.get("vespene", 25),
                        supply=cost_data.get("supply", 2),
                        time=cost_data.get("time", 19)
                    )
                    
                    # 加载攻击信息
                    self.attack = data.get("attack", {
                        "targets": ["Ground"],
                        "damage": 16, "damage_upgrade": 2,
                        "dps": {"base": 13.7},
                        "cooldown": 2.0,
                        "range": 4
                    })
                    
                    # 加载单位属性
                    self.unit_stats = data.get("unit_stats", {
                        "health": 145, "armor": 1, "armor_upgrade": 1,
                        "attributes": ["Biological"],
                        "sight": 9, "speed": 3.15, "cargo_size": 2
                    })
                    
                    # 加载能力配置
                    self.abilities = data.get("abilities", {})
                    
                    # 加载特有属性
                    self.requires_spawning_pool = data.get("requires_spawning_pool", True)
                    self.can_burrow = data.get("can_burrow", True)
                    self.can_tunnel = data.get("can_tunnel", True)
                    self.regeneration_rate = data.get("regeneration_rate", 5.34)
            else:
                print(f"警告: JSON文件不存在，使用硬编码数据: {json_path}")
                self._set_hardcoded_data()
        except Exception as e:
            print(f"加载JSON文件时出错: {e}")
            self._set_hardcoded_data()
    
    def _set_hardcoded_data(self):
        """设置硬编码的单位数据作为后备"""
        self.description = "虫族重甲远程单位，具备高生命恢复和地道移动能力"
        
        # 游戏属性
        self.cost = Cost(mineral=75, vespene=25, supply=2, time=19)
        self.attack = {
            "targets": ["Ground"],
            "damage": 16, "damage_upgrade": 2,
            "dps": {"base": 13.7},
            "cooldown": 2.0,
            "range": 4
        }
        self.unit_stats = {
            "health": 145, "armor": 1, "armor_upgrade": 1,
            "attributes": ["Biological"],
            "sight": 9, "speed": 3.15, "cargo_size": 2
        }
        
        # 能力配置
        self.abilities = {
            "burrow_move": {
                "researched": False,
                "cooldown": 0,
                "move_speed": 4.0,
                "energy_cost": 50
            },
            "glial_reconstitution": {
                "researched": False,
                "research_time": 110,
                "speed_bonus": 1.41
            },
            "tunneling_claws": {
                "researched": False,
                "research_time": 110,
                "burrow_move_enabled": True
            },
            "burrow": {
                "researched": False,
                "research_time": 90
            }
        }
        
        # 蟑螂特有属性
        self.requires_spawning_pool = True
        self.can_burrow = True
        self.can_tunnel = True
        self.regeneration_rate = 5.34  # 蟑螂特有的高恢复率
        
        # 克制关系
        self.counter_relations = {
            "strong_against": ["Marine", "Zealot", "Light Units"],
            "weak_against": ["Marauder", "Stalker", "Armored Counters"],
            "counters": []
        }
        
        # 升级信息
        self.upgrades = {
            "carapace": {"levels": 3, "current_level": 0},
            "missile_attacks": {"levels": 3, "current_level": 0}
        }
        
        # 战术信息
        self.tactical_info = {
            "strengths": ["高生命值", "高恢复率", "重甲", "远程攻击"],
            "weaknesses": ["对重甲单位伤害一般", "机动性中等"],
            "optimal_situation": ["前排坦克", "持续作战", "地道突袭"]
        }
    
    def _enhance_vlm_interface(self):
        """增强VLM接口，添加预置函数候选"""
        # 更新LLM接口信息
        self.llm_interface.update({
            "natural_language_aliases": ["蟑螂", "roach", "重甲单位", "地道单位"],
            "role_description": self.description,
            "tactical_keywords": ["重甲", "远程", "高恢复", "地道移动"],
            "primary_role": ["前排坦克", "持续作战", "地道突袭"],
            "common_tactics": ["正面推进", "地道偷袭", "配合刺蛇"]
        })
        
        # 更新视觉识别信息
        self.visual_recognition.update({
            "unit_size": "medium",
            "color_scheme": ["brown", "orange"],
            "silhouette": " quadrupedal armored insect",
            "animation_characteristics": ["ground pounding attack", "burrowing animation"]
        })
        
        # 更新战术上下文
        self.tactical_context.update({
            "formation_preferences": ["front line", "defensive"],
            "engagement_distances": ["medium", "short"],
            "micro_maneuvers": ["burrow to heal", "tunnel movement"]
        })
        
        # 定义预置函数候选（符合标准模板要求）
        self.prefab_function_candidates = [
            {
                "function_name": "roach_frontline_defense",
                "description": "蟑螂前排防御阵型",
                "parameters": {
                    "defense_position": "防御位置",
                    "threat_units": "威胁单位列表"
                },
                "execution_flow": [
                    "move_to_defensive_position(defense_position)",
                    "form_frontline()",
                    "burrow_if_vulnerable()",
                    "regroup_after_healing()"
                ]
            },
            {
                "function_name": "roach_tunnel_ambush",
                "description": "蟑螂地道伏击战术",
                "parameters": {
                    "ambush_position": "伏击位置",
                    "target_units": "目标单位列表"
                },
                "execution_flow": [
                    "use_burrow_move(ambush_position)",
                    "wait_for_enemy(target_units)",
                    "unburrow_and_attack(target_units)",
                    "retreat_and_burrow()"
                ]
            },
            {
                "function_name": "roach_rapid_assault",
                "description": "蟑螂快速突击战术",
                "parameters": {
                    "target_location": "目标位置",
                    "enemy_defenses": "敌方防御信息"
                },
                "execution_flow": [
                    "rapid_regeneration()",
                    "advance_to_position(target_location)",
                    "focus_fire_on_structure(enemy_defenses)",
                    "withdraw_if_necessary()"
                ]
            }
        ]
    
    def use_burrow_move(self, target_position: Position) -> Dict[str, Any]:
        """使用地道移动"""
        result = {
            "success": False,
            "action": "use_burrow_move",
            "moved": False,
            "reason": None
        }
        
        if not self.can_tunnel:
            result["reason"] = "单位不具备地道能力"
            return result
        
        tunneling_claws = self.abilities.get("tunneling_claws", {})
        if not tunneling_claws.get("researched", False):
            result["reason"] = "隧道利爪尚未研究"
            return result
        
        burrow_move = self.abilities.get("burrow_move", {})
        
        result["success"] = True
        result["moved"] = True
        result["target_position"] = target_position
        result["move_speed"] = burrow_move.get("move_speed", 4.0)
        result["energy_cost"] = burrow_move.get("energy_cost", 50)
        
        print(f"{self.unique_class_name} 使用地道移动到位置 {target_position}，速度: {result['move_speed']}")
        return result
    
    def rapid_regeneration(self) -> Dict[str, Any]:
        """快速恢复生命值"""
        result = {
            "success": True,
            "action": "rapid_regeneration",
            "healing": True,
            "heal_rate": self.regeneration_rate
        }
        
        # 检查神经重组升级
        glial_reconstitution = self.abilities.get("glial_reconstitution", {})
        if glial_reconstitution.get("researched", False):
            result["heal_rate"] += glial_reconstitution.get("speed_bonus", 1.41)
            result["enhanced"] = True
        
        print(f"{self.unique_class_name} 快速恢复生命值，恢复速率: {result['heal_rate']}/秒")
        return result
    
    def move_to_defensive_position(self, position: Position) -> Dict[str, Any]:
        """移动到防御位置"""
        result = {
            "success": True,
            "action": "move_to_defensive_position",
            "position": position
        }
        print(f"{self.unique_class_name} 移动到防御位置: {position}")
        return result
    
    def form_frontline(self) -> Dict[str, Any]:
        """形成前线阵型"""
        result = {
            "success": True,
            "action": "form_frontline",
            "formation_completed": True
        }
        print(f"{self.unique_class_name} 形成前线防御阵型")
        return result
    
    def burrow_if_vulnerable(self) -> Dict[str, Any]:
        """如果脆弱则掘地"""
        result = {
            "success": True,
            "action": "burrow_if_vulnerable",
            "burrowed": False
        }
        
        # 简单的脆弱性检查逻辑
        if hasattr(self, 'unit_stats') and 'health' in self.unit_stats:
            current_health = getattr(self, 'current_health', self.unit_stats['health'])
            max_health = self.unit_stats['health']
            
            if current_health < max_health * 0.4 and self.can_burrow:
                burrow = self.abilities.get("burrow", {})
                if burrow.get("researched", False):
                    result["burrowed"] = True
                    print(f"{self.unique_class_name} 因生命值过低而掘地")
        
        return result
    
    def regroup_after_healing(self) -> Dict[str, Any]:
        """治愈后重新集结"""
        result = {
            "success": True,
            "action": "regroup_after_healing",
            "regrouped": True
        }
        print(f"{self.unique_class_name} 治愈后重新集结")
        return result
    
    def advance_to_position(self, position: Position) -> Dict[str, Any]:
        """前进到指定位置"""
        result = {
            "success": True,
            "action": "advance_to_position",
            "position": position
        }
        print(f"{self.unique_class_name} 前进到位置: {position}")
        return result
    
    def focus_fire_on_structure(self, enemy_defenses) -> Dict[str, Any]:
        """集中火力攻击建筑"""
        result = {
            "success": True,
            "action": "focus_fire_on_structure",
            "targets": enemy_defenses
        }
        print(f"{self.unique_class_name} 集中火力攻击敌方防御: {enemy_defenses}")
        return result
    
    def withdraw_if_necessary(self) -> Dict[str, Any]:
        """必要时撤退"""
        result = {
            "success": True,
            "action": "withdraw_if_necessary",
            "withdrew": False
        }
        
        # 简单的撤退判断逻辑
        if hasattr(self, 'unit_stats') and 'health' in self.unit_stats:
            current_health = getattr(self, 'current_health', self.unit_stats['health'])
            max_health = self.unit_stats['health']
            
            if current_health < max_health * 0.25:
                result["withdrew"] = True
                print(f"{self.unique_class_name} 生命值过低，执行撤退")
        
        return result