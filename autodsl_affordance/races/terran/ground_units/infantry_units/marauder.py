# races/terran/ground_units/infantry_units/marauder.py

import os
import json
from typing import Dict, Any, List, Optional
from autodsl_affordance.races.terran import TerranInfantryUnit
from autodsl_affordance.core.base_units.unit import Cost, Position

class TerranMarauder(TerranInfantryUnit):
    """掠夺者 - 人族反重甲步兵单位
    
    特性：
    - 对装甲单位有额外伤害
    - 可以使用兴奋剂提升攻击和移动速度
    - 装备震荡弹可减速敌人
    - 需要科技实验室生产
    
    功能：
    - 反装甲作战能力
    - 前线坦克角色
    - 提供减速控制效果
    """
    
    def __init__(self, **kwargs):
        """初始化掠夺者单位
        
        Args:
            **kwargs: 自定义参数，将覆盖默认值
        """
        # 不要将development_mode传递给父类
        super().__init__()
        self.unique_class_name = "Terran_Marauder"
        
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
        self.can_stimpack = False
        self.requires_tech_lab = False
        self.current_health = None
    
    def _load_unit_data(self):
        """加载数据，从JSON文件加载单位数据，失败则使用硬编码数据
        
        首先尝试从JSON文件加载配置，若失败则使用内置的硬编码数据
        """
        # 计算JSON文件路径（向上3层目录）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "..", "..", "..", "sc2_unit_info", f"Terran_Marauder.json")
        json_path = os.path.normpath(json_path)
        
        try:
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 加载基本信息
                    self.description = data.get("description", "人族反重甲步兵单位，具备减速攻击和兴奋剂能力")
                    
                    # 加载成本信息
                    cost_data = data.get("cost", {})
                    self.cost = Cost(
                        mineral=cost_data.get("mineral", 100),
                        vespene=cost_data.get("vespene", 25),
                        supply=cost_data.get("supply", 2),
                        time=cost_data.get("time", 21)
                    )
                    
                    # 加载攻击信息
                    self.attack = data.get("attack", {
                        "targets": ["Ground"],
                        "damage": 10, "damage_upgrade": 1,
                        "dps": {"base": 9.8, "vs_armored": 19.6},
                        "cooldown": 1.03,
                        "bonus_damage": {"value": 10, "upgrade": 1, "vs": "Armored"},
                        "range": 6
                    })
                    
                    # 加载单位属性
                    self.unit_stats = data.get("unit_stats", {
                        "health": 125, "armor": 1, "armor_upgrade": 1,
                        "attributes": ["Biological"],
                        "sight": 9, "speed": 3.15, "cargo_size": 2
                    })
                    
                    # 初始化当前生命值
                    self.current_health = self.unit_stats.get("health", 125)
                    
                    # 加载能力配置
                    self.abilities = data.get("abilities", {})
                    
                    # 加载特有属性
                    self.can_stimpack = data.get("can_stimpack", True)
                    self.requires_tech_lab = data.get("requires_tech_lab", True)
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
        self.description = "人族反重甲步兵单位，具备减速攻击和兴奋剂能力"
        
        # 游戏属性
        self.cost = Cost(mineral=100, vespene=25, supply=2, time=21)
        self.attack = {
            "targets": ["Ground"],
            "damage": 10, "damage_upgrade": 1,
            "dps": {"base": 9.8, "vs_armored": 19.6},
            "cooldown": 1.03,
            "bonus_damage": {"value": 10, "upgrade": 1, "vs": "Armored"},
            "range": 6
        }
        self.unit_stats = {
            "health": 125, "armor": 1, "armor_upgrade": 1,
            "attributes": ["Biological"],
            "sight": 9, "speed": 3.15, "cargo_size": 2
        }
        
        # 初始化当前生命值
        self.current_health = self.unit_stats["health"]
        
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
            "concussive_shells": {
                "researched": True,
                "slow_duration": 3,
                "slow_amount": 0.5
            }
        }
        
        # 步兵特有属性
        self.can_stimpack = True
        self.requires_tech_lab = True
        
        # 克制关系
        self.counter_relations = {
            "strong_against": ["Roach", "Zealot", "Immortal"],
            "weak_against": ["Stalker", "Hydralisk", "Viking"],
            "counters": []
        }
        
        # 升级信息
        self.upgrades = {
            "infantry_armor": {"levels": 3, "current_level": 0},
            "infantry_weapons": {"levels": 3, "current_level": 0},
            "stimpack": {"levels": 1, "current_level": 0}
        }
        
        # 战术信息
        self.tactical_info = {
            "strengths": ["反重甲", "减速效果", "较高生命值", "前排坦克"],
            "weaknesses": ["对轻甲效果差", "无法对空", "成本较高"],
            "optimal_situation": ["对抗重型单位", "配合陆战队员", "前排阻挡"]
        }
    
    def _enhance_vlm_interface(self):
        """增强VLM接口，添加预置函数候选
        
        为视觉语言模型提供更丰富的接口信息，包括自然语言别名、角色描述、战术关键词等
        """
        # 更新LLM接口信息
        self.llm_interface.update({
            "natural_language_aliases": ["掠夺者", "marauder", "光头", "反重甲"],
            "role_description": self.description,
            "tactical_keywords": ["反重甲", "减速", "前排", "配合机枪兵"],
            "primary_role": ["反重甲", "前排坦克", "控制"],
            "common_tactics": ["对抗不朽者", "配合陆战队员", "使用减速"]
        })
        
        # 更新视觉识别信息
        self.visual_recognition.update({
            "unit_size": "medium",
            "color_scheme": ["blue", "red", "yellow"],
            "silhouette": "large infantry with heavy armor and missile launcher",
            "animation_characteristics": ["slow movement", "missile firing"]
        })
        
        # 更新战术上下文
        self.tactical_context.update({
            "formation_preferences": ["front line", "mixed with marines"],
            "engagement_distances": ["medium"],
            "micro_maneuvers": ["stimpack burst", "slow kiting"]
        })
        
        # 定义预置函数候选（符合标准模板要求）
        self.prefab_function_candidates = [
            {
                "function_name": "marauder_anti_armored_defense",
                "description": "掠夺者反重甲防御战术",
                "parameters": {
                    "defense_position": "防御位置",
                    "armored_targets": "装甲目标列表"
                },
                "execution_flow": [
                    "move_to_defensive_position(defense_position)",
                    "use_stimpack_ability()",
                    "focus_fire_armored_targets(armored_targets)",
                    "apply_concussive_shells_to_enemies(armored_targets)"
                ]
            },
            {
                "function_name": "marauder_marine_combined_assault",
                "description": "掠夺者陆战队员混合突击战术",
                "parameters": {
                    "assault_position": "突击位置",
                    "enemy_composition": "敌方单位构成"
                },
                "execution_flow": [
                    "form_combined_forces(assault_position)",
                    "use_stimpack_ability()",
                    "charge_enemy_lines(enemy_composition)",
                    "maintain_front_line_position()"
                ]
            },
            {
                "function_name": "marauder_slow_and_destroy",
                "description": "掠夺者减速摧毁战术",
                "parameters": {
                    "priority_targets": "优先目标列表",
                    "retreat_position": "撤退位置"
                },
                "execution_flow": [
                    "select_priority_armored_targets(priority_targets)",
                    "apply_concussive_shells(priority_targets)",
                    "focus_fire_slowed_targets(priority_targets)",
                    "retreat_to_safety_if_needed(retreat_position)"
                ]
            }
        ]
    
    def apply_concussive_shells(self, target) -> Dict[str, Any]:
        """应用震荡弹减速效果
        
        Args:
            target: 目标单位
            
        Returns:
            Dict[str, Any]: 操作结果，包含成功状态、减速效果等信息
        """
        result = {
            "success": False,
            "action": "apply_concussive_shells",
            "slow_applied": False,
            "slow_duration": 0,
            "slow_amount": 0,
            "reason": None
        }
        
        # 检查震荡弹能力是否已研发
        concussive_shells = self.abilities.get("concussive_shells", {})
        if not concussive_shells.get("researched", True):
            result["reason"] = "震荡弹未研发"
            print(f"{self.unique_class_name} 震荡弹未研发")
            return result
        
        # 成功应用减速
        result["success"] = True
        result["slow_applied"] = True
        result["slow_duration"] = concussive_shells.get("slow_duration", 3)
        result["slow_amount"] = concussive_shells.get("slow_amount", 0.5)
        
        print(f"{self.unique_class_name} 对目标应用震荡弹减速，持续 {result['slow_duration']} 秒")
        return result
    
    def use_stimpack_ability(self) -> Dict[str, Any]:
        """使用兴奋剂能力
        
        Returns:
            Dict[str, Any]: 操作结果，包含成功状态、速度提升、生命值消耗等信息
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
    
    def move_to_defensive_position(self, position: Position) -> Dict[str, Any]:
        """移动到防御位置
        
        Args:
            position: 目标防御位置
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        result = {
            "success": True,
            "action": "move_to_defensive_position",
            "position": position
        }
        print(f"{self.unique_class_name} 移动到防御位置: {position}")
        return result
    
    def focus_fire_armored_targets(self, armored_targets) -> Dict[str, Any]:
        """集火装甲目标
        
        Args:
            armored_targets: 装甲目标列表
            
        Returns:
            Dict[str, Any]: 操作结果，包含目标数量
        """
        result = {
            "success": True,
            "action": "focus_fire_armored_targets",
            "target_count": len(armored_targets) if armored_targets else 0
        }
        print(f"{self.unique_class_name} 集火 {result['target_count']} 个装甲目标")
        return result
    
    def apply_concussive_shells_to_enemies(self, enemies) -> Dict[str, Any]:
        """对多个敌人应用震荡弹
        
        Args:
            enemies: 敌人列表
            
        Returns:
            Dict[str, Any]: 操作结果，包含敌人数量和被减速的数量
        """
        result = {
            "success": True,
            "action": "apply_concussive_shells_to_enemies",
            "enemy_count": len(enemies) if enemies else 0,
            "slowed_count": 0
        }
        
        if enemies:
            for enemy in enemies:
                # 简单检查是否为装甲单位
                if isinstance(enemy, dict) and "attributes" in enemy and "Armored" in enemy["attributes"]:
                    result["slowed_count"] += 1
            
        print(f"{self.unique_class_name} 对 {result['enemy_count']} 个敌人应用震荡弹，其中 {result['slowed_count']} 个被减速")
        return result
    
    def form_combined_forces(self, position: Position) -> Dict[str, Any]:
        """组成混合部队
        
        Args:
            position: 集合位置
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        result = {
            "success": True,
            "action": "form_combined_forces",
            "position": position
        }
        print(f"{self.unique_class_name} 与陆战队员组成混合部队，位于位置: {position}")
        return result
    
    def charge_enemy_lines(self, enemy_composition) -> Dict[str, Any]:
        """冲锋敌人防线
        
        Args:
            enemy_composition: 敌人组成
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        result = {
            "success": True,
            "action": "charge_enemy_lines",
            "enemy_composition": enemy_composition
        }
        print(f"{self.unique_class_name} 冲锋敌人防线")
        return result
    
    def maintain_front_line_position(self) -> Dict[str, Any]:
        """保持前线位置
        
        Returns:
            Dict[str, Any]: 操作结果
        """
        result = {
            "success": True,
            "action": "maintain_front_line_position"
        }
        print(f"{self.unique_class_name} 保持前线位置")
        return result
    
    def select_priority_armored_targets(self, targets) -> Dict[str, Any]:
        """选择优先装甲目标
        
        Args:
            targets: 目标列表
            
        Returns:
            Dict[str, Any]: 操作结果，包含目标数量
        """
        result = {
            "success": True,
            "action": "select_priority_armored_targets",
            "target_count": len(targets) if targets else 0
        }
        print(f"{self.unique_class_name} 选择 {result['target_count']} 个优先装甲目标")
        return result
    
    def focus_fire_slowed_targets(self, targets) -> Dict[str, Any]:
        """集火已减速目标
        
        Args:
            targets: 目标列表
            
        Returns:
            Dict[str, Any]: 操作结果，包含目标数量
        """
        result = {
            "success": True,
            "action": "focus_fire_slowed_targets",
            "target_count": len(targets) if targets else 0
        }
        print(f"{self.unique_class_name} 集火 {result['target_count']} 个已减速目标")
        return result
    
    def retreat_to_safety_if_needed(self, retreat_position: Position) -> Dict[str, Any]:
        """必要时撤退到安全位置
        
        Args:
            retreat_position: 撤退位置
            
        Returns:
            Dict[str, Any]: 操作结果，包含撤退状态
        """
        
        result = {
            "success": True,
            "action": "retreat_to_safety_if_needed",
            "retreat_position": retreat_position,
            "retreated": False
        }
        
        # 检查是否需要撤退（生命值过低）
        current_health = getattr(self, 'current_health', self.unit_stats['health'])
        max_health = self.unit_stats['health']
        
        if current_health < max_health * 0.3:
            result["retreated"] = True
            print(f"{self.unique_class_name} 生命值过低，撤退到位置: {retreat_position}")
        else:
            print(f"{self.unique_class_name} 继续战斗")
        
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
            "can_stimpack": self.can_stimpack,
            "requires_tech_lab": self.requires_tech_lab
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