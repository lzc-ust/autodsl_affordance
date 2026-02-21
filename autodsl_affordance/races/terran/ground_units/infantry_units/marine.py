# races/terran/ground_units/infantry_units/marine.py

import os
import json
from typing import Dict, Any, List
from autodsl_affordance.races.terran import TerranInfantryUnit
from autodsl_affordance.core.base_units.unit import Cost, Position

class TerranMarine(TerranInfantryUnit):
    """陆战队员 - 人族基础步兵单位
    
    人族最基础的步兵单位，具有远程攻击能力和兴奋剂技能。
    适合快速生产形成大规模部队，对轻甲单位有良好的伤害输出。
    """
    
    def __init__(self, **kwargs):
        """
        初始化陆战队员单位
        
        Args:
            **kwargs: 可选参数，允许传入自定义配置
        """
        # 调用父类初始化，传递所有参数
        super().__init__(**kwargs)
        self.unique_class_name = "Terran_Marine"
        
        # 设置默认值
        self._set_default_values()
        
        # 尝试从JSON文件加载数据，失败则使用硬编码数据
        self._load_unit_data()
        
        # 应用自定义参数
        self._apply_custom_kwargs(kwargs)
        
        # VLM优化
        self._enhance_vlm_interface()
    
    def _set_default_values(self):
        """
        设置所有属性的默认值
        确保所有可能的属性都有初始值，避免None值导致的错误
        """
        self.description = ""
        self.cost = None
        self.attack = {}
        self.unit_stats = {}
        self.abilities = {}
        self.can_stimpack = False
        self.can_use_combat_shields = False
    
    def _load_unit_data(self):
        """
        从JSON文件加载单位数据
        如果JSON文件不存在或加载失败，则使用硬编码数据
        """
        # 计算JSON文件路径（向上3层目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "..", "..", "..", "sc2_unit_info", f"Terran_Marine.json")
        json_path = os.path.normpath(json_path)
        
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 加载基本信息
                    self.description = data.get("description", "人族基础步兵单位，具备远程攻击和兴奋剂能力")
                    
                    # 加载成本信息
                    cost_data = data.get("cost", {})
                    self.cost = Cost(
                        mineral=cost_data.get("mineral", 50),
                        vespene=cost_data.get("vespene", 0),
                        supply=cost_data.get("supply", 1),
                        time=cost_data.get("time", 18)
                    )
                    
                    # 加载攻击信息
                    self.attack = data.get("attack", {
                        "targets": ["Ground", "Air"],
                        "damage": 6, "damage_upgrade": 1,
                        "dps": {"base": 9.8},
                        "cooldown": 0.61,
                        "range": 5
                    })
                    
                    # 加载单位属性
                    self.unit_stats = data.get("unit_stats", {
                        "health": 45, "armor": 0, "armor_upgrade": 1,
                        "attributes": ["Light", "Biological"],
                        "sight": 9, "speed": 3.15, "cargo_size": 1
                    })
                    
                    # 加载能力配置
                    self.abilities = data.get("abilities", {})
                    
                    # 加载特有属性
                    self.can_stimpack = data.get("can_stimpack", True)
                    self.can_use_combat_shields = data.get("can_use_combat_shields", True)
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
        self.description = "人族基础步兵单位，具备远程攻击和兴奋剂能力"
        
        # 游戏属性
        self.cost = Cost(mineral=50, vespene=0, supply=1, time=18)
        self.attack = {
            "targets": ["Ground", "Air"],
            "damage": 6, "damage_upgrade": 1,
            "dps": {"base": 9.8},
            "cooldown": 0.61,
            "range": 5
        }
        self.unit_stats = {
            "health": 45, "armor": 0, "armor_upgrade": 1,
            "attributes": ["Light", "Biological"],
            "sight": 9, "speed": 3.15, "cargo_size": 1
        }
        
        # 能力配置
        self.abilities = {
            "stimpack": {
                "researched": False,
                "cooldown": 0,
                "health_cost": 10,
                "duration": 11,
                "speed_bonus": 1.5,
                "attack_speed_bonus": 1.5
            },
            "combat_shields": {
                "researched": False,
                "health_bonus": 10
            }
        }
        
        # 步兵特有属性
        self.can_stimpack = True
        self.can_use_combat_shields = True
        
        # 克制关系
        self.counter_relations = {
            "strong_against": ["Zergling", "Baneling", "Air Units"],
            "weak_against": ["Marauder", "Zealot", "Bunker"],
            "counters": []
        }
        
        # 升级信息
        self.upgrades = {
            "infantry_armor": {"levels": 3, "current_level": 0},
            "infantry_weapons": {"levels": 3, "current_level": 0},
            "stimpack": {"levels": 1, "current_level": 0},
            "combat_shields": {"levels": 1, "current_level": 0}
        }
        
        # 战术信息
        self.tactical_info = {
            "strengths": ["对空攻击", "可使用兴奋剂", "低成本", "高机动性"],
            "weaknesses": ["生命值低", "兴奋剂有生命消耗", "对重甲单位效果差"],
            "optimal_situation": ["对抗空中单位", "快速扩张防守", "使用Bunker防御"]
        }
    
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
    
    def _enhance_vlm_interface(self):
        """
        增强VLM接口，添加自然语言描述和战术关键词
        用于大语言模型交互
        """
        # 更新LLM接口信息
        self.llm_interface.update({
            "natural_language_aliases": ["陆战队员", "marine", "机枪兵", "MM"],
            "role_description": self.description,
            "tactical_keywords": ["基础输出", "对空对地", "兴奋剂", "数量压制"],
            "primary_role": ["基础输出", "防空", "前线作战"],
            "common_tactics": ["配合掠夺者", "使用兴奋剂", "数量压制"]
        })
        
        # 更新视觉识别信息
        self.visual_recognition.update({
            "unit_size": "small",
            "color_scheme": ["blue", "red", "yellow"],
            "silhouette": " infantry with helmet and rifle",
            "animation_characteristics": ["running movement", "rifle firing"]
        })
        
        # 更新战术上下文
        self.tactical_context.update({
            "formation_preferences": ["spread", "bunker defense"],
            "engagement_distances": ["medium", "close"],
            "micro_maneuvers": ["stimpack burst", "focus fire"]
        })
        
        # 定义预置函数候选（符合标准模板要求）
        self.prefab_function_candidates = [
            {
                "function_name": "marine_anti_air_defense",
                "description": "陆战队员防空防御战术",
                "parameters": {
                    "defense_position": "防御位置",
                    "air_targets": "空中目标列表"
                },
                "execution_flow": [
                    "move_to_position(defense_position)",
                    "use_stimpack_ability()",
                    "focus_fire_air_targets(air_targets)",
                    "maintain_position(defense_position)"
                ]
            },
            {
                "function_name": "marine_assault_rush",
                "description": "陆战队员突击冲锋战术",
                "parameters": {
                    "target_position": "目标位置",
                    "enemy_units": "敌方单位列表"
                },
                "execution_flow": [
                    "move_to_assault_position(target_position)",
                    "use_stimpack_ability()",
                    "charge_enemy_position(enemy_units)",
                    "retreat_if_necessary()"
                ]
            },
            {
                "function_name": "marine_bunker_defense",
                "description": "陆战队员地堡防御战术",
                "parameters": {
                    "bunker_position": "地堡位置",
                    "defense_radius": "防御半径"
                },
                "execution_flow": [
                    "enter_bunker(bunker_position)",
                    "defend_bunker_perimeter(defense_radius)",
                    "use_stimpack_ability()",
                    "focus_fire_priority_targets()"
                ]
            }
        ]
    
    def use_stimpack_ability(self) -> Dict[str, Any]:
        """
        使用兴奋剂能力，提升攻击速度和移动速度，但消耗生命值
        
        Returns:
            Dict[str, Any]: 包含使用结果和相关信息的字典
        """
        result = {
            "success": False,
            "action": "use_stimpack",
            "speed_boosted": False,
            "attack_speed_boosted": False,
            "health_cost": 0,
            "reason": None
        }
        
        if not self.can_stimpack:
            result["reason"] = "无法使用兴奋剂"
            print(f"{self.unique_class_name} 无法使用兴奋剂")
            return result
        
        # 检查兴奋剂能力是否已研发
        stimpack = self.abilities.get("stimpack", {})
        if not stimpack.get("researched", False):
            result["reason"] = "兴奋剂未研发"
            print(f"{self.unique_class_name} 兴奋剂未研发")
            return result
        
        # 检查冷却时间
        if stimpack.get("cooldown", 0) > 0:
            result["reason"] = "兴奋剂冷却中"
            print(f"{self.unique_class_name} 兴奋剂冷却中")
            return result
        
        # 获取健康值消耗
        health_cost = stimpack.get("health_cost", 10)
        
        # 检查生命值是否足够
        current_health = getattr(self, 'current_health', self.unit_stats['health'])
        if current_health <= health_cost:
            result["reason"] = "生命值不足"
            print(f"{self.unique_class_name} 生命值不足，无法使用兴奋剂")
            return result
        
        # 成功使用兴奋剂
        result["success"] = True
        result["speed_boosted"] = True
        result["attack_speed_boosted"] = True
        result["health_cost"] = health_cost
        
        # 应用效果
        self.current_health = current_health - health_cost
        stimpack["cooldown"] = stimpack.get("duration", 11)  # 设置冷却时间为持续时间
        
        print(f"{self.unique_class_name} 使用兴奋剂，提升攻击和移动速度，扣除 {health_cost} 点生命值")
        return result
    
    def move_to_position(self, position: Position) -> Dict[str, Any]:
        """
        移动到指定位置
        
        Args:
            position: 目标位置对象
            
        Returns:
            Dict[str, Any]: 移动结果信息
        """
        result = {
            "success": True,
            "action": "move_to_position",
            "position": position
        }
        print(f"{self.unique_class_name} 移动到位置: {position}")
        return result
    
    def focus_fire_air_targets(self, air_targets) -> Dict[str, Any]:
        """
        集火空中目标
        
        Args:
            air_targets: 空中目标列表
            
        Returns:
            Dict[str, Any]: 集火结果信息
        """
        result = {
            "success": True,
            "action": "focus_fire_air_targets",
            "target_count": len(air_targets) if air_targets else 0
        }
        print(f"{self.unique_class_name} 集火 {result['target_count']} 个空中目标")
        return result
    
    def maintain_position(self, position: Position) -> Dict[str, Any]:
        """
        保持在指定位置
        
        Args:
            position: 要保持的位置对象
            
        Returns:
            Dict[str, Any]: 保持位置的结果信息
        """
        result = {
            "success": True,
            "action": "maintain_position",
            "position": position
        }
        print(f"{self.unique_class_name} 保持在位置: {position}")
        return result
    
    def move_to_assault_position(self, position: Position) -> Dict[str, Any]:
        """移动到突击位置"""
        result = {
            "success": True,
            "action": "move_to_assault_position",
            "position": position
        }
        print(f"{self.unique_class_name} 移动到突击位置: {position}")
        return result
    
    def charge_enemy_position(self, enemy_units) -> Dict[str, Any]:
        """冲锋敌人位置"""
        result = {
            "success": True,
            "action": "charge_enemy_position",
            "enemy_count": len(enemy_units) if enemy_units else 0
        }
        print(f"{self.unique_class_name} 冲锋敌方位置，对抗 {result['enemy_count']} 个单位")
        return result
    
    def retreat_if_necessary(self) -> Dict[str, Any]:
        """必要时撤退"""
        result = {
            "success": True,
            "action": "retreat_if_necessary",
            "retreated": False
        }
        
        # 检查是否需要撤退（生命值过低）
        current_health = getattr(self, 'current_health', self.unit_stats['health'])
        max_health = self.unit_stats['health']
        
        if current_health < max_health * 0.3:
            result["retreated"] = True
            print(f"{self.unique_class_name} 生命值过低，撤退")
        else:
            print(f"{self.unique_class_name} 继续战斗")
        
        return result
    
    def enter_bunker(self, bunker_position: Position) -> Dict[str, Any]:
        """进入地堡"""
        result = {
            "success": True,
            "action": "enter_bunker",
            "bunker_position": bunker_position
        }
        print(f"{self.unique_class_name} 进入地堡位置: {bunker_position}")
        return result
    
    def defend_bunker_perimeter(self, defense_radius: float) -> Dict[str, Any]:
        """防御地堡周边"""
        result = {
            "success": True,
            "action": "defend_bunker_perimeter",
            "defense_radius": defense_radius
        }
        print(f"{self.unique_class_name} 防御地堡周边，半径: {defense_radius}")
        return result
    
    def focus_fire_priority_targets(self) -> Dict[str, Any]:
        """
        集火优先目标
        
        Returns:
            Dict[str, Any]: 集火结果信息
        """
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将陆战队员对象转换为字典表示
        
        Returns:
            Dict[str, Any]: 单位数据字典
        """
        result = {
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
            "llm_interface": self.llm_interface,
            "can_stimpack": self.can_stimpack,
            "can_use_combat_shields": self.can_use_combat_shields,
            "counter_relations": getattr(self, 'counter_relations', {}),
            "upgrades": getattr(self, 'upgrades', {}),
            "tactical_info": getattr(self, 'tactical_info', {})
        }
        return result
        result = {
            "success": True,
            "action": "focus_fire_priority_targets"
        }
        print(f"{self.unique_class_name} 集火优先目标")
        return result