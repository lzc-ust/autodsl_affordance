from autodsl_affordance.races.protoss import ProtossGatewayUnit
from autodsl_affordance.core.base_units.unit import Cost, Position
from typing import Dict, Any, List

class ProtossZealot(ProtossGatewayUnit):
    """狂热者 - 神族基础近战单位，拥有冲锋能力，适合近战战斗和快速接敌。"""
    
    def __init__(self, development_mode: bool = False):
        super().__init__()
        self.unique_class_name = "Protoss_Zealot"
        self.development_mode = development_mode
        
        # 核心属性初始化
        self.description = ""
        self.cost = None
        self.attack = {}
        self.unit_stats = {}
        self.abilities = {}  # type: Dict[str, Dict[str, Any]]
        self.tactical_info = {}
        
        # 加载单位数据
        self._load_data()
        # 设置默认值
        self._set_default_values()
        # VLM接口增强
        self._enhance_vlm_interface()
    
    def _load_data(self):
        """从JSON文件加载单位数据"""
        try:
            # 尝试直接加载JSON文件
            import os
            import json
            # 正确的JSON路径计算
            json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                   'sc2_unit_info', f'{self.unique_class_name}.json')
            
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.description = data.get("Description", "")
                    
                    # 处理成本数据
                    cost_data = data.get("Cost", {})
                    self.cost = Cost(
                        mineral=cost_data.get("mineral", 100),
                        vespene=cost_data.get("vespene", 0),
                        supply=cost_data.get("supply", 2),
                        time=cost_data.get("game_time", 27)
                    )
                    
                    # 处理攻击数据
                    if 'Attack' in data:
                        attack_data = data['Attack']
                        # 提取伤害信息
                        damage_str = attack_data.get('Damage', '8 (+1) × 2 attacks')
                        base_damage = 8  # 默认值，实际应该从字符串中解析
                        
                        self.attack = {
                            "targets": [attack_data.get('Targets', 'Ground')],
                            "damage": base_damage,
                            "damage_upgrade": 1,
                            "attacks": 2,
                            "total_damage": base_damage * 2,
                            "dps": float(attack_data.get('DPS', '11.4').split(' ')[0]),
                            "cooldown": float(attack_data.get('Cooldown', '1.4')),
                            "bonus_damage": {"value": 0, "vs": "None"},
                            "range": float(attack_data.get('Range', '0.1').split(' ')[0]),
                            "melee": True
                        }
                    
                    # 处理单位统计
                    if 'Unit stats' in data:
                        stats_data = data['Unit stats']
                        defense_parts = stats_data.get('Defense', '100 50 1 (+1)').split()
                        
                        # 解析速度数据
                        speed_str = stats_data.get('Speed', '3.15 (4.72 with Charge)')
                        base_speed = float(speed_str.split(' ')[0])
                        charge_speed = 4.72  # 默认值
                        if '(' in speed_str and 'with Charge' in speed_str:
                            charge_speed_part = speed_str.split('(')[1].split(' ')[0]
                            charge_speed = float(charge_speed_part)
                        
                        self.unit_stats = {
                            "health": int(defense_parts[0]),
                            "shield": int(defense_parts[1]),
                            "armor": int(defense_parts[2].split('(')[0]),
                            "armor_upgrade": 1,
                            "attributes": stats_data.get('Attributes', 'Light, Biological').split(', '),
                            "sight": int(stats_data.get('Sight', '9')),
                            "speed": {
                                "base": base_speed,
                                "with_charge": charge_speed
                            },
                            "cargo_size": int(stats_data.get('Cargo size', '2'))
                        }
                    
                    # 处理能力数据
                    if 'Ability' in data:
                        ability_data = data['Ability']
                        self.abilities = {
                            "charge": {
                                "name": ability_data.get('Name', 'Charge'),
                                "researched": False,
                                "cooldown": 7,  # 默认值
                                "range": 7.5,  # 默认值
                                "description": ability_data.get('Description', ''),
                                "hotkey": ability_data.get('Hotkey', 'C')
                            }
                        }
                    
                    # 处理克制关系
                    self.strong_against = data.get('Strong against', [])
                    self.weak_against = data.get('Weak against', [])
                    
                    # 处理升级信息
                    if 'Upgrade' in data:
                        upgrade_data = data['Upgrade']
                        self.upgrades = {
                            "charge_research": {
                                "name": upgrade_data.get('Name', 'Charge Research'),
                                "mineral_cost": upgrade_data.get('Mineral Cost', 100),
                                "vespene_cost": upgrade_data.get('Vespene Cost', 100),
                                "research_time": upgrade_data.get('Research Time', 121),
                                "researched_from": upgrade_data.get('Researched From', 'Twilight Council'),
                                "effect": upgrade_data.get('Effect', '')
                            }
                        }
                    
                    # 处理战术信息
                    if 'Competitive Usage' in data:
                        self.tactical_info = data.get('Competitive Usage', {})
                        # 添加协同单位信息
                        self.tactical_info['synergies'] = ["Immortal", "Stalker", "Archon", "Colossus"]
            else:
                # JSON文件不存在，使用硬编码数据
                self._set_hardcoded_data()
                print(f"警告: JSON文件不存在，使用硬编码数据: {json_path}")
        except Exception as e:
            if self.development_mode:
                raise e
            print(f"警告: 无法加载{self.unique_class_name}的数据: {e}，使用硬编码数据")
            self._set_hardcoded_data()
    
    def _set_hardcoded_data(self):
        """设置硬编码的单位数据作为后备"""
        # 设置默认单位数据，类似于_set_default_values方法但更完整
        self.description = "神族基础近战单位，高生命值，冲锋后能快速接近敌人"
        self.cost = Cost(mineral=100, vespene=0, supply=2, time=27)
        self.attack = {
            "targets": ["Ground"],
            "damage": 8,
            "damage_upgrade": 1,
            "attacks": 2,
            "total_damage": 16,
            "dps": 11.4,
            "cooldown": 1.4,
            "bonus_damage": {"value": 0, "vs": "None"},
            "range": 0.1,
            "melee": True
        }
        self.unit_stats = {
            "health": 100,
            "shield": 50,
            "armor": 1,
            "armor_upgrade": 1,
            "attributes": ["Light", "Biological"],
            "sight": 9,
            "speed": {
                "base": 3.15,
                "with_charge": 4.72
            },
            "cargo_size": 2
        }
        self.abilities = {
            "charge": {
                "name": "Charge",
                "researched": False,
                "cooldown": 7,
                "range": 7.5,
                "description": "允许狂热者快速冲向敌人",
                "hotkey": "C"
            }
        }
        self.strong_against = ["Marine", "Zergling"]
        self.weak_against = ["Marauder", "Baneling", "Siege Tank"]
        self.upgrades = {
            "charge_research": {
                "name": "Charge Research",
                "mineral_cost": 100,
                "vespene_cost": 100,
                "research_time": 121,
                "researched_from": "Twilight Council",
                "effect": "狂热者获得冲锋能力"
            }
        }
        self.tactical_info = {
            "strong_against": ["Marine", "Zergling"],
            "weak_against": ["Marauder", "Baneling", "Siege Tank"],
            "synergies": ["Immortal", "Stalker", "Archon", "Colossus"]
        }
    
    def _set_default_values(self):
        """设置默认值，确保属性完整性"""
        if not self.description:
            if self.development_mode:
                raise ValueError("单位描述不能为空")
            self.description = "神族基础近战单位，高生命值，冲锋后能快速接近敌人"
        
        if not self.cost:
            self.cost = Cost(mineral=100, vespene=0, supply=2, time=27)
        
        if not self.attack:
            self.attack = {
                "damage": 8, "damage_upgrade": 1, "attacks": 2, "total_damage": 16,
                "dps": 11.4, "cooldown": 1.4, "range": 0.1, "melee": True
            }
        
        if not self.unit_stats:
            self.unit_stats = {
                "health": 100, "shield": 50, "armor": 1, "armor_upgrade": 1,
                "attributes": ["Light", "Biological"],
                "sight": 9, "speed": {"base": 3.15, "with_charge": 4.72},
                "cargo_size": 2
            }
        
        if not self.abilities:
            self.abilities = {
                "charge": {"researched": False, "cooldown": 7, "range": 7.5}
            }
        
        # 战术信息
        if not self.tactical_info:
            self.tactical_info = {
                "strong_against": ["Marine", "Zergling"],
                "weak_against": ["Marauder", "Baneling", "Siege Tank"],
                "synergies": ["Immortal", "Stalker"]
            }
    
    def _enhance_vlm_interface(self):
        """增强VLM接口，优化视觉和语言模型交互"""
        # 初始化接口字典（如果不存在）
        if not hasattr(self, 'llm_interface'):
            self.llm_interface = {}
        if not hasattr(self, 'visual_recognition'):
            self.visual_recognition = {}
        if not hasattr(self, 'tactical_context'):
            self.tactical_context = {}
        
        # 动态获取战术信息
        general_tactics = self.tactical_info.get('General', '') if hasattr(self, 'tactical_info') else ''
        
        self.llm_interface.update({
            "natural_language_aliases": ["狂热者", "zealot", "叉子兵", "冲锋叉", "双光刃战士"],
            "role_description": self.description,
            "tactical_keywords": ["前线坦克", "包围敌人", "冲锋接敌", "多线骚扰", "肉盾", "突击", "包抄", "压制"],
            "primary_role": ["前线", "包围", "骚扰", "肉盾", "突击"],
            "common_tactics": ["冲锋接敌", "保护后排", "多线骚扰", "包围战术", "分矿防守", "棱镜空投", "诱捕拉扯"],
            "special_abilities": ["冲锋（Charge）"],
            "micro_techniques": ["冲锋包围", "分散站位", "追击残血", "分割包围", "保护输出"],
            "visual_recognition_features": ["蓝色装甲", "双光刃", "冲锋时拖影效果"],
            "competitive_insights": general_tactics
        })
        
        self.visual_recognition.update({
            "identifying_features": ["蓝色装甲", "双光刃", "冲锋时拖影效果"],
            "minimap_characteristics": "蓝色中等点",
            "unique_visual_queues": ["双光刃攻击动画", "冲锋拖影"],
            "llm_vision_prompt": "识别画面中的狂热者 - 蓝色人形单位，手持双光刃"
        })
        
        self.tactical_context.update({
            "early_game": ["前线压制", "防御骚扰", "快速接敌", "分矿防守"],
            "mid_game": ["主力前排", "包围战术", "棱镜空投", "多线骚扰"],
            "late_game": ["辅助输出", "清理残血", "保护主力", "包围敌方"],
            "counters": self.weak_against if hasattr(self, 'weak_against') else [],
            "countered_by": self.strong_against if hasattr(self, 'strong_against') else [],
            "synergies": [f"与{s}配合" for s in self.tactical_info.get("synergies", [])] if hasattr(self, 'tactical_info') else [],
            "vs_protoss": self.tactical_info.get('Vs. Protoss', '') if hasattr(self, 'tactical_info') else '',
            "vs_terran": self.tactical_info.get('Vs. Terran', '') if hasattr(self, 'tactical_info') else '',
            "vs_zerg": self.tactical_info.get('Vs. Zerg', '') if hasattr(self, 'tactical_info') else ''
        })
        
        # 预置函数候选
        self.prefab_function_candidates = [
            {
                "function_name": "zealot_charge_surround",
                "description": "狂热者使用冲锋能力接近并包围敌人",
                "parameters": {
                    "enemy_positions": "敌人位置列表",
                    "target_position": "冲锋目标位置"
                },
                "execution_flow": [
                    "use_charge(target_position)",
                    "surround_enemy(enemy_positions)",
                    "engage_in_melee()"
                ]
            },
            {
                "function_name": "zealot_protect_backline",
                "description": "狂热者保护后排单位免受攻击",
                "parameters": {
                    "backline_units": "后排单位列表",
                    "threat_positions": "威胁位置列表"
                },
                "execution_flow": [
                    "use_charge(threat_positions[0])",
                    "surround_enemy([threat_positions[0]])",
                    "maintain_frontline()"
                ]
            },
            {
                "function_name": "zealot_multi_prong_harass",
                "description": "狂热者多线骚扰",
                "parameters": {
                    "harass_positions": "骚扰位置列表",
                    "enemy_base_locations": "敌方基地位置列表"
                },
                "execution_flow": [
                    "warp_in_at_position(harass_positions[0])",
                    "use_charge(enemy_base_locations[0])",
                    "engage_in_melee()",
                    "retreat_if_vulnerable()"
                ]
            },
            {
                "function_name": "zealot_counter_melee",
                "description": "狂热者对抗敌方近战单位",
                "parameters": {
                    "enemy_melee_units": "敌方近战单位列表",
                    "engagement_position": "交战位置"
                },
                "execution_flow": [
                    "use_charge(engagement_position)",
                    "engage_in_melee()",
                    "split_to_avoid_splash()"
                ]
            }
        ]
    
    def use_charge(self, target_position: Position) -> Dict[str, Any]:
        """使用冲锋能力快速接近目标"""
        result = {
            "success": False,
            "action": "use_charge",
            "charged": False,
            "position_changed": False,
            "new_position": None,
            "reason": None
        }
        
        charge = self.abilities.get("charge", {})
        
        # 检查是否已研发
        if not charge.get("researched", False):
            result["reason"] = "冲锋技能尚未研究"
            return result
        
        # 检查冷却
        if charge.get("cooldown_remaining", 0) > 0:
            result["reason"] = f"冲锋技能正在冷却中，剩余时间: {charge['cooldown_remaining']}秒"
            return result
        
        # 获取位置信息
        charge_range = charge.get("range", 7.5)
        current_position = getattr(self, "position", Position(0, 0))
        
        # 计算距离
        distance = self._calculate_distance(current_position, target_position)
        
        if distance > charge_range:
            result["reason"] = f"目标位置超出冲锋范围，距离: {distance:.2f}，最大范围: {charge_range}"
            return result
        
        # 执行冲锋
        print(f"{self.unique_class_name} 向 {target_position} 发起冲锋!")
        self.position = target_position
        # 重置冲锋冷却
        if "cooldown" in charge:
            charge["cooldown_remaining"] = charge["cooldown"]
        
        result["success"] = True
        result["charged"] = True
        result["position_changed"] = True
        result["new_position"] = target_position
        result["previous_position"] = current_position
        result["distance_traveled"] = distance
        result["cooldown_applied"] = charge.get("cooldown", 7)
        
        # 更新移动速度
        if hasattr(self, 'unit_stats') and 'speed' in self.unit_stats:
            current_speed = self.unit_stats['speed'].get('with_charge', 4.72)
            result["current_speed"] = current_speed
        
        return result
    
    def maintain_frontline(self) -> Dict[str, Any]:
        """保持前线位置，保护后排单位"""
        result = {
            "success": True,
            "action": "maintain_frontline",
            "tactical_purpose": "保护后排单位免受敌方攻击"
        }
        
        print(f"{self.unique_class_name} 维持前线位置，保护后排单位")
        
        return result
    
    def retreat_if_vulnerable(self) -> Dict[str, Any]:
        """当狂热者处于脆弱状态时撤退"""
        result = {
            "success": True,
            "action": "retreat_if_vulnerable",
            "retreat_recommended": False,
            "vulnerability_factors": [],
            "tactical_purpose": "保护狂热者免受集火"
        }
        
        print(f"{self.unique_class_name} 评估自身脆弱性，判断是否需要撤退")
        
        return result
    
    def split_to_avoid_splash(self) -> Dict[str, Any]:
        """分散站位以避免范围伤害"""
        result = {
            "success": True,
            "action": "split_to_avoid_splash",
            "tactical_purpose": "避免受到范围伤害技能的影响"
        }
        
        print(f"{self.unique_class_name} 分散站位以避免范围伤害")
        
        return result
    
    def research_charge(self) -> Dict[str, Any]:
        """研究冲锋能力"""
        result = {
            "success": True,
            "action": "research_charge",
            "researched": False,
            "research_cost": {
                "mineral": 100,
                "vespene": 100,
                "time": 121
            }
        }
        
        if "charge" not in self.abilities:
            self.abilities["charge"] = {"cooldown": 7, "range": 7.5}
        
        # 设置为已研究
        self.abilities["charge"]["researched"] = True
        self.abilities["charge"]["cooldown_remaining"] = 0
        
        # 从升级数据中获取研究成本
        if hasattr(self, 'upgrades') and 'charge_research' in self.upgrades:
            upgrade_data = self.upgrades['charge_research']
            result["research_cost"] = {
                "mineral": upgrade_data.get('mineral_cost', 100),
                "vespene": upgrade_data.get('vespene_cost', 100),
                "time": upgrade_data.get('research_time', 121)
            }
            result["researched_from"] = upgrade_data.get('researched_from', 'Twilight Council')
        
        print(f"{self.unique_class_name} 已研究冲锋能力")
        result["researched"] = True
        
        # 更新速度为冲锋速度
        if hasattr(self, 'unit_stats') and 'speed' in self.unit_stats:
            self.unit_stats['speed']['current'] = self.unit_stats['speed'].get('with_charge', 4.72)
        
        return result
    
    def warp_in_at_position(self, position: Position) -> Dict[str, Any]:
        """在指定位置折跃狂热者"""
        result = {
            "success": True,
            "action": "warp_in_at_position",
            "warp_in_position": position,
            "tactical_purpose": "快速部署单位到指定位置"
        }
        
        print(f"{self.unique_class_name} 在位置 {position} 折跃完成")
        self.position = position
        
        return result
    
    def engage_in_melee(self, target_unit: str = None) -> Dict[str, Any]:
        """近战攻击目标单位"""
        result = {
            "success": True,
            "action": "engage_in_melee",
            "target_unit": target_unit,
            "damage_dealt": {},
            "effectiveness_rating": "medium"
        }
        
        # 从攻击数据获取伤害值
        damage_per_attack = self.attack.get("damage", 8)
        attacks = self.attack.get("attacks", 2)
        total_damage = damage_per_attack * attacks
        
        if target_unit:
            # 检查目标是否为被克制单位
            target_lower = target_unit.lower()
            
            # 检查是否为优势目标
            is_strong_against = False
            if hasattr(self, 'strong_against'):
                is_strong_against = any(unit.lower() in target_lower for unit in self.strong_against)
            
            # 检查是否为劣势目标
            is_weak_against = False
            if hasattr(self, 'weak_against'):
                is_weak_against = any(unit.lower() in target_lower for unit in self.weak_against)
            
            if is_strong_against:
                damage_bonus = 0.2  # 20% 加成
                result["effectiveness_rating"] = "excellent"
            elif is_weak_against:
                damage_bonus = -0.1  # 10% 减益
                result["effectiveness_rating"] = "poor"
            else:
                damage_bonus = 0
                result["effectiveness_rating"] = "medium"
            
            # 应用伤害加成/减益
            final_damage = total_damage * (1 + damage_bonus)
            
            result["damage_dealt"] = {
                "base_damage": damage_per_attack,
                "attacks": attacks,
                "total_damage": total_damage,
                "final_damage": final_damage,
                "bonus_applied": damage_bonus * 100,  # 百分比
                "target_evaluation": "strong_against" if is_strong_against else "weak_against" if is_weak_against else "neutral"
            }
            
            print(f"{self.unique_class_name} 对{target_unit}造成{final_damage:.2f}点伤害")
        else:
            # 没有特定目标，返回基础伤害信息
            result["damage_dealt"] = {
                "base_damage": damage_per_attack,
                "attacks": attacks,
                "total_damage": total_damage
            }
            
            print(f"{self.unique_class_name} 进行近战攻击，基础伤害: {total_damage}")
        
        return result
    
    def surround_enemy(self, enemy_positions: List[Position]) -> Dict[str, Any]:
        """包围敌人单位"""
        result = {
            "success": True,
            "action": "surround_enemy",
            "total_enemies": len(enemy_positions),
            "surround_completed": False,
            "surround_effectiveness": "poor"
        }
        
        if not enemy_positions:
            result["reason"] = "没有敌人位置需要包围"
            return result
        
        # 简单的包围逻辑实现
        print(f"{self.unique_class_name} 尝试包围 {len(enemy_positions)} 个敌人单位")
        
        # 根据敌人数量评估包围效果
        enemy_count = len(enemy_positions)
        if enemy_count <= 2:
            result["surround_completed"] = True
            result["surround_effectiveness"] = "excellent"
        elif enemy_count <= 5:
            result["surround_completed"] = True
            result["surround_effectiveness"] = "good"
        elif enemy_count <= 10:
            result["surround_completed"] = False
            result["surround_effectiveness"] = "medium"
        else:
            result["surround_completed"] = False
            result["surround_effectiveness"] = "poor"
        
        return result
    
    def _calculate_distance(self, pos1: Position, pos2: Position) -> float:
        """计算两点之间的距离"""
        return ((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2) ** 0.5
    
    # 预置函数候选已在_enhance_vlm_interface中定义