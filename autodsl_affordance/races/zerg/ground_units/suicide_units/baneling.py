# races/zerg/ground_units/suicide_units/baneling.py

import os
import json
from typing import Dict, Any, List
from autodsl_affordance.races.zerg import ZergSuicideUnit
from autodsl_affordance.core.base_units.unit import Cost, Position

class ZergBaneling(ZergSuicideUnit):
    """爆虫 - 虫族自杀爆炸单位"""
    
    def __init__(self, **kwargs):
        # 不要将development_mode传递给父类
        super().__init__()
        self.unique_class_name = "Zerg_Baneling"
        
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
        self.is_suicide_unit = False
        self.explosion_damage = 0
        self.explosion_radius = 0.0
        self.bonus_vs_light = 0
        self.can_burrow = False
        self.regeneration_rate = 0.0
    
    def _load_unit_data(self):
        """从JSON文件加载单位数据"""
        # 计算JSON文件路径（向上3层目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "..", "..", "..", "sc2_unit_info", f"Zerg_Baneling.json")
        json_path = os.path.normpath(json_path)
        
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 加载基本信息
                    self.description = data.get("description", "虫族自杀爆炸单位，通过自爆造成范围伤害")
                    
                    # 加载成本信息
                    cost_data = data.get("cost", {})
                    self.cost = Cost(
                        mineral=cost_data.get("mineral", 25),
                        vespene=cost_data.get("vespene", 25),
                        supply=cost_data.get("supply", 0.5),
                        time=cost_data.get("time", 14)
                    )
                    
                    # 加载攻击信息
                    self.attack = data.get("attack", {
                        "targets": ["Ground"],
                        "damage": 0,  # 特殊攻击方式
                        "dps": {"base": 0},
                        "cooldown": 0,
                        "range": 0.1
                    })
                    
                    # 加载单位属性
                    self.unit_stats = data.get("unit_stats", {
                        "health": 30, "armor": 0, "armor_upgrade": 1,
                        "attributes": ["Biological"],
                        "sight": 6, "speed": 3.94, "cargo_size": 2
                    })
                    
                    # 加载能力配置
                    self.abilities = data.get("abilities", {})
                    
                    # 加载特有属性
                    self.is_suicide_unit = data.get("is_suicide_unit", True)
                    self.explosion_damage = data.get("explosion_damage", 20)
                    self.explosion_radius = data.get("explosion_radius", 2.2)
                    self.bonus_vs_light = data.get("bonus_vs_light", 15)
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
        self.description = "虫族自杀爆炸单位，通过自爆造成范围伤害"
        
        # 游戏属性
        self.cost = Cost(mineral=25, vespene=25, supply=0.5, time=14)
        self.attack = {
            "targets": ["Ground"],
            "damage": 0,  # 特殊攻击方式
            "dps": {"base": 0},
            "cooldown": 0,
            "range": 0.1
        }
        self.unit_stats = {
            "health": 30, "armor": 0, "armor_upgrade": 1,
            "attributes": ["Biological"],
            "sight": 6, "speed": 3.94, "cargo_size": 2
        }
        
        # 能力配置
        self.abilities = {
            "explosion": {
                "researched": True,
                "damage": 20,
                "splash_radius": 2.2,
                "bonus_vs_light": 15,
                "full_damage_radius": 0.6
            },
            "centrifugal_hooks": {
                "researched": False,
                "research_time": 110,
                "speed_bonus": 1.57
            },
            "baneling_burrow": {
                "researched": False,
                "research_time": 110,
                "burrow_enabled": True
            }
        }
        
        # 爆虫特有属性
        self.is_suicide_unit = True
        self.explosion_damage = 20
        self.explosion_radius = 2.2
        self.bonus_vs_light = 15
        self.can_burrow = True
        self.regeneration_rate = 0.273
        
        # 克制关系
        self.counter_relations = {
            "strong_against": ["Marine", "Zealot", "Light Units", "Bunker"],
            "weak_against": ["Marauder", "Stalker", "Air Units"],
            "counters": []
        }
        
        # 升级信息
        self.upgrades = {
            "carapace": {"levels": 3, "current_level": 0},
            "centrifugal_hooks": {"levels": 1, "current_level": 0},
            "baneling_burrow": {"levels": 1, "current_level": 0}
        }
        
        # 战术信息
        self.tactical_info = {
            "strengths": ["对轻甲单位高伤害", "范围伤害", "低成本", "速度快"],
            "weaknesses": ["生命值低", "只能使用一次", "对重甲单位效果差"],
            "optimal_situation": ["对抗大量轻甲单位", "摧毁防御工事", "伏击战术"]
        }
    
    def _enhance_vlm_interface(self):
        """增强VLM接口，添加预置函数候选"""
        # 更新LLM接口信息
        self.llm_interface.update({
            "natural_language_aliases": ["爆虫", "baneling", "自爆虫", "炸弹虫"],
            "role_description": self.description,
            "tactical_keywords": ["自杀攻击", "范围伤害", "反轻甲", "埋伏"],
            "primary_role": ["反轻甲", "范围清除", "自杀攻击"],
            "common_tactics": ["埋伏战术", "对抗步兵", "破阵"]
        })
        
        # 更新视觉识别信息
        self.visual_recognition.update({
            "unit_size": "small",
            "color_scheme": ["green", "yellow"],
            "silhouette": " round explosive unit",
            "animation_characteristics": ["rolling movement", "explosion animation"]
        })
        
        # 更新战术上下文
        self.tactical_context.update({
            "formation_preferences": ["clustered", "ambush"],
            "engagement_distances": ["very close", "close"],
            "micro_maneuvers": ["burst movement", "burrow ambush"]
        })
        
        # 定义预置函数候选（符合标准模板要求）
        self.prefab_function_candidates = [
            {
                "function_name": "baneling_anti_infantry_ambush",
                "description": "爆虫反步兵伏击战术",
                "parameters": {
                    "ambush_position": "伏击位置",
                    "enemy_infantry": "敌方步兵单位列表"
                },
                "execution_flow": [
                    "burrow_ambush(ambush_position)",
                    "wait_for_enemy_clustering(enemy_infantry)",
                    "detonate(ambush_position)",
                    "evaluate_damage(enemy_infantry)"
                ]
            },
            {
                "function_name": "baneling_defense_breakthrough",
                "description": "爆虫防御突破战术",
                "parameters": {
                    "defense_position": "防御位置",
                    "defense_structures": "防御建筑列表"
                },
                "execution_flow": [
                    "roll_attack(defense_position)",
                    "detonate(defense_position)",
                    "clear_defense_gap(defense_structures)",
                    "allow_main_force_advance()"
                ]
            },
            {
                "function_name": "baneling_scouting_explosion",
                "description": "爆虫侦察爆炸战术",
                "parameters": {
                    "scout_position": "侦察位置",
                    "enemy_threats": "敌方威胁信息"
                },
                "execution_flow": [
                    "move_to_scout_position(scout_position)",
                    "detonate(scout_position)",
                    "reveal_enemy_position(enemy_threats)",
                    "provide_intelligence()"
                ]
            }
        ]
    
    def detonate(self, target_position: Position) -> Dict[str, Any]:
        """引爆自身"""
        result = {
            "success": True,
            "action": "detonate",
            "position": target_position,
            "damage": self.explosion_damage,
            "splash_radius": self.explosion_radius,
            "bonus_vs_light": self.bonus_vs_light,
            "unit_destroyed": True
        }
        
        print(f"{self.unique_class_name} 在位置 {target_position} 引爆，造成 {result['damage']} 点伤害，范围 {result['splash_radius']}")
        self.get_destroyed()
        return result
    
    def roll_attack(self, target_position: Position) -> Dict[str, Any]:
        """滚动攻击"""
        result = {
            "success": True,
            "action": "roll_attack",
            "target_position": target_position,
            "speed_boosted": False
        }
        
        # 检查离心钩爪升级
        centrifugal_hooks = self.abilities.get("centrifugal_hooks", {})
        if centrifugal_hooks.get("researched", False):
            result["speed_boosted"] = True
            result["speed_bonus"] = centrifugal_hooks.get("speed_bonus", 1.57)
            
        print(f"{self.unique_class_name} 向位置 {target_position} 滚动攻击{'(速度提升)' if result['speed_boosted'] else ''}")
        return result
    
    def burrow_ambush(self, ambush_position: Position) -> Dict[str, Any]:
        """潜地埋伏"""
        result = {
            "success": False,
            "action": "burrow_ambush",
            "position": ambush_position,
            "burrowed": False,
            "reason": None
        }
        
        if not self.can_burrow:
            result["reason"] = "单位不具备掘地能力"
            return result
        
        baneling_burrow = self.abilities.get("baneling_burrow", {})
        if not baneling_burrow.get("researched", False):
            result["reason"] = "爆虫掘地尚未研究"
            return result
        
        result["success"] = True
        result["burrowed"] = True
        print(f"{self.unique_class_name} 在位置 {ambush_position} 潜地埋伏")
        return result
    
    def wait_for_enemy_clustering(self, enemy_units) -> Dict[str, Any]:
        """等待敌人集结"""
        result = {
            "success": True,
            "action": "wait_for_enemy_clustering",
            "enemy_count": len(enemy_units) if enemy_units else 0
        }
        print(f"{self.unique_class_name} 等待敌人集结，观察到 {result['enemy_count']} 个敌方单位")
        return result
    
    def evaluate_damage(self, enemy_units) -> Dict[str, Any]:
        """评估造成的伤害"""
        result = {
            "success": True,
            "action": "evaluate_damage",
            "affected_units": len(enemy_units) if enemy_units else 0,
            "estimated_damage": self.explosion_damage
        }
        print(f"{self.unique_class_name} 评估爆炸影响，预计影响 {result['affected_units']} 个单位")
        return result
    
    def clear_defense_gap(self, defense_structures) -> Dict[str, Any]:
        """清除防御缺口"""
        result = {
            "success": True,
            "action": "clear_defense_gap",
            "structures_affected": len(defense_structures) if defense_structures else 0
        }
        print(f"{self.unique_class_name} 清除防御缺口，影响 {result['structures_affected']} 个防御建筑")
        return result
    
    def allow_main_force_advance(self) -> Dict[str, Any]:
        """允许主力推进"""
        result = {
            "success": True,
            "action": "allow_main_force_advance",
            "advance_path_opened": True
        }
        print(f"{self.unique_class_name} 为主力部队打开推进路径")
        return result
    
    def move_to_scout_position(self, scout_position: Position) -> Dict[str, Any]:
        """移动到侦察位置"""
        result = {
            "success": True,
            "action": "move_to_scout_position",
            "position": scout_position
        }
        print(f"{self.unique_class_name} 移动到侦察位置: {scout_position}")
        return result
    
    def reveal_enemy_position(self, enemy_threats) -> Dict[str, Any]:
        """揭示敌人位置"""
        result = {
            "success": True,
            "action": "reveal_enemy_position",
            "threats_revealed": len(enemy_threats) if enemy_threats else 0
        }
        print(f"{self.unique_class_name} 揭示 {result['threats_revealed']} 个敌方威胁位置")
        return result
    
    def provide_intelligence(self) -> Dict[str, Any]:
        """提供情报"""
        result = {
            "success": True,
            "action": "provide_intelligence",
            "intelligence_gathered": True
        }
        print(f"{self.unique_class_name} 提供战场情报")
        return result