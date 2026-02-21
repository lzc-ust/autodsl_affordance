from autodsl_affordance.races.protoss import ProtossGatewayUnit
from autodsl_affordance.core.base_units.unit import Cost, Position
from typing import Dict, Any, List, Optional

class ProtossSentry(ProtossGatewayUnit):
    """哨兵 - 神族支援单位，拥有力场和能量盾等支援能力"""
    
    def __init__(self, development_mode: bool = False):
        super().__init__()
        self.unique_class_name = "Protoss_Sentry"
        self.development_mode = development_mode
        
        # 核心属性初始化
        self.description = ""
        self.cost = None
        self.attack = {}
        self.unit_stats = {}
        self.abilities = {}  # type: Dict[str, Dict[str, Any]]
        self.tactical_info = {}
        self.position = Position(0, 0)  # 默认位置
        self.energy = 50  # 默认能量值
        self.max_energy = 100  # 最大能量值
        
        # 加载单位数据
        self._load_data()
        # 设置默认值
        self._set_default_values()
        # VLM接口增强
        self._enhance_vlm_interface()
    
    def _load_data(self):
        """从JSON文件加载单位数据，如果不存在则使用硬编码数据"""
        try:
            # 尝试直接加载JSON文件
            import os
            import json
            json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 
                                   'sc2_unit_info', f'{self.unique_class_name}.json')
            
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._parse_json_data(data)
            else:
                # JSON文件不存在，使用硬编码数据
                self._set_hardcoded_data()
                print(f"警告: JSON文件不存在，使用硬编码数据: {json_path}")
        except Exception as e:
            if self.development_mode:
                raise e
            print(f"警告: 无法加载{self.unique_class_name}的数据: {e}，使用硬编码数据")
            self._set_hardcoded_data()
    
    def _parse_json_data(self, data: Dict[str, Any]):
        """解析JSON数据"""
        self.description = data.get("Description", "哨兵 - 神族支援单位，拥有力场和能量盾等支援能力")
        
        # 处理成本数据
        cost_data = data.get("Cost", {})
        self.cost = Cost(
            mineral=cost_data.get("mineral", 50),
            vespene=cost_data.get("vespene", 100),
            supply=cost_data.get("supply", 2),
            time=cost_data.get("game_time", 33)
        )
        
        # 处理攻击数据
        if 'Attack' in data:
            attack_data = data['Attack']
            self.attack = {
                "targets": [attack_data.get('Targets', 'Ground, Air')],
                "damage": float(attack_data.get('Damage', '4').split()[0]),
                "damage_upgrade": 1,
                "dps": float(attack_data.get('DPS', '5.7').split(' ')[0]),
                "cooldown": float(attack_data.get('Cooldown', '0.7')),
                "range": float(attack_data.get('Range', '5').split(' ')[0]),
                "bonus_damage": {"value": 0, "vs": "None"}
            }
        
        # 处理单位统计
        if 'Unit stats' in data:
            stats_data = data['Unit stats']
            defense_parts = stats_data.get('Defense', '40 40 1 (+1)').split()
            
            self.unit_stats = {
                "health": int(defense_parts[0]),
                "shield": int(defense_parts[1]),
                "armor": int(defense_parts[2].split('(')[0]),
                "armor_upgrade": 1,
                "attributes": stats_data.get('Attributes', 'Light, Biological').split(', '),
                "sight": int(stats_data.get('Sight', '8')),
                "speed": float(stats_data.get('Speed', '2.8').split(' ')[0]),
                "cargo_size": int(stats_data.get('Cargo size', '2'))
            }
        
        # 处理能力数据
        if 'Ability' in data:
            ability_data = data['Ability']
            # 假设Ability是一个列表或字典
            if isinstance(ability_data, list):
                for ability in ability_data:
                    self._process_ability(ability)
            elif isinstance(ability_data, dict):
                self._process_ability(ability_data)
        
        # 处理克制关系
        self.strong_against = data.get('Strong against', ["Marine", "Zergling", "Probe", "SCV", "Drone"])
        self.weak_against = data.get('Weak against', ["Roach", "Marauder", "Stalker", "Queen", "All air units"])
        
        # 处理战术信息
        if 'Competitive Usage' in data:
            self.tactical_info = data.get('Competitive Usage', {})
            # 添加协同单位信息
            self.tactical_info['synergies'] = ["Immortal", "Stalker", "Colossus", "High Templar"]
    
    def _process_ability(self, ability: Dict[str, Any]):
        """处理单个能力数据"""
        ability_name = ability.get('Name', '').lower()
        if 'force' in ability_name or '力场' in ability_name:
            self.abilities['force_field'] = {
                "name": ability.get('Name', 'Force Field'),
                "energy_cost": ability.get('Energy Cost', 25),
                "cooldown": ability.get('Cooldown', 10),
                "range": ability.get('Range', 7),
                "duration": ability.get('Duration', 15),
                "description": ability.get('Description', ''),
                "hotkey": ability.get('Hotkey', 'F'),
                "cooldown_remaining": 0
            }
        elif 'shield' in ability_name or '能量盾' in ability_name:
            self.abilities['guardian_shield'] = {
                "name": ability.get('Name', 'Guardian Shield'),
                "energy_cost": ability.get('Energy Cost', 25),
                "cooldown": ability.get('Cooldown', 45),
                "duration": ability.get('Duration', 30),
                "range": ability.get('Range', 0),  # 光环效果
                "description": ability.get('Description', ''),
                "hotkey": ability.get('Hotkey', 'G'),
                "cooldown_remaining": 0,
                "active": False,
                "damage_reduction": 2
            }
        elif 'hallucination' in ability_name or '幻象' in ability_name:
            self.abilities['hallucination'] = {
                "name": ability.get('Name', 'Hallucination'),
                "energy_cost": ability.get('Energy Cost', 100),
                "cooldown": ability.get('Cooldown', 30),
                "description": ability.get('Description', ''),
                "hotkey": ability.get('Hotkey', 'H'),
                "cooldown_remaining": 0
            }
    
    def _set_hardcoded_data(self):
        """设置硬编码数据"""
        self.description = "哨兵 - 神族支援单位，拥有力场和能量盾等支援能力"
        
        # 成本数据
        self.cost = Cost(mineral=50, vespene=100, supply=2, time=33)
        
        # 攻击数据
        self.attack = {
            "targets": ["Ground", "Air"],
            "damage": 4,
            "damage_upgrade": 1,
            "dps": 5.7,
            "cooldown": 0.7,
            "range": 5,
            "bonus_damage": {"value": 0, "vs": "None"}
        }
        
        # 单位统计
        self.unit_stats = {
            "health": 40,
            "shield": 40,
            "armor": 1,
            "armor_upgrade": 1,
            "attributes": ["Light", "Biological"],
            "sight": 8,
            "speed": 2.8,
            "cargo_size": 2
        }
        
        # 能力数据
        self.abilities = {
            "force_field": {
                "name": "Force Field",
                "energy_cost": 25,
                "cooldown": 10,
                "range": 7,
                "duration": 15,
                "description": "在指定位置创建一个力场，阻挡敌方单位通行",
                "hotkey": "F",
                "cooldown_remaining": 0
            },
            "guardian_shield": {
                "name": "Guardian Shield",
                "energy_cost": 25,
                "cooldown": 45,
                "duration": 30,
                "range": 0,  # 光环效果
                "description": "在哨兵周围创造一个能量盾，减少友方单位受到的远程伤害",
                "hotkey": "G",
                "cooldown_remaining": 0,
                "active": False,
                "damage_reduction": 2
            },
            "hallucination": {
                "name": "Hallucination",
                "energy_cost": 100,
                "cooldown": 30,
                "description": "制造一个幻象单位",
                "hotkey": "H",
                "cooldown_remaining": 0
            }
        }
        
        # 克制关系
        self.strong_against = ["Marine", "Zergling", "Probe", "SCV", "Drone"]
        self.weak_against = ["Roach", "Marauder", "Stalker", "Queen", "All air units"]
        
        # 战术信息
        self.tactical_info = {
            "General": "哨兵是Protoss的重要支援单位，能够创造力场阻挡敌人移动，使用能量盾保护友方单位。",
            "Vs. Protoss": "力场可以有效阻挡地面推进，能量盾对追猎者有显著保护效果。",
            "Vs. Terran": "力场可以分割人族陆战队员和掠夺者，能量盾可以减少远程伤害。",
            "Vs. Zerg": "力场在防守时尤其有效，可以阻挡大量虫族单位的推进。",
            "synergies": ["Immortal", "Stalker", "Colossus", "High Templar"]
        }
    
    def _set_default_values(self):
        """设置默认值，确保所有必要属性都有值"""
        # 确保核心属性都有值
        if not self.description:
            self.description = "哨兵 - 神族支援单位，拥有力场和能量盾等支援能力"
        
        if not self.cost:
            self.cost = Cost(mineral=50, vespene=100, supply=2, time=33)
        
        if not self.attack:
            self.attack = {
                "targets": ["Ground", "Air"],
                "damage": 4,
                "damage_upgrade": 1,
                "dps": 5.7,
                "cooldown": 0.7,
                "range": 5
            }
        
        if not self.unit_stats:
            self.unit_stats = {
                "health": 40,
                "shield": 40,
                "armor": 1,
                "armor_upgrade": 1,
                "attributes": ["Light", "Biological"],
                "sight": 8,
                "speed": 2.8,
                "cargo_size": 2
            }
        
        if not self.abilities:
            self.abilities = {
                "force_field": {"cooldown": 10, "energy_cost": 25, "range": 7},
                "guardian_shield": {"cooldown": 45, "energy_cost": 25, "active": False}
            }
        
        if not self.tactical_info:
            self.tactical_info = {
                "strong_against": ["Marine", "Zergling"],
                "weak_against": ["Roach", "Marauder"],
                "synergies": ["Immortal", "Stalker"]
            }
    
    def _enhance_vlm_interface(self):
        """增强VLM接口，优化视觉和语言模型交互"""
        # 初始化接口字典
        if not hasattr(self, 'llm_interface'):
            self.llm_interface = {}
        if not hasattr(self, 'visual_recognition'):
            self.visual_recognition = {}
        if not hasattr(self, 'tactical_context'):
            self.tactical_context = {}
        
        # 动态获取战术信息
        general_tactics = self.tactical_info.get('General', '')
        
        self.llm_interface.update({
            "natural_language_aliases": ["哨兵", "sentry", "支援者"],
            "role_description": self.description,
            "tactical_keywords": ["力场", "能量盾", "分割战场", "支援", "防守", "战术控制", "幻象"],
            "primary_role": ["支援", "防守", "战术控制"],
            "common_tactics": ["力场分割", "能量盾保护", "幻象侦查", "阻挡敌人", "创造通道"],
            "special_abilities": ["力场 (Force Field)", "能量盾 (Guardian Shield)", "幻象 (Hallucination)"],
            "micro_techniques": ["力场位置控制", "能量管理", "幻象单位选择", "能量盾时机"],
            "visual_recognition_features": ["蓝色装甲", "球形装置", "力场特效", "能量盾光环"],
            "competitive_insights": general_tactics
        })
        
        self.visual_recognition.update({
            "identifying_features": ["蓝色装甲", "球形装置", "力场特效", "能量盾光环"],
            "minimap_characteristics": "蓝色中等点",
            "unique_visual_queues": ["力场释放动画", "能量盾光环效果"],
            "llm_vision_prompt": "识别画面中的哨兵 - 蓝色人形单位，手持球形装置"
        })
        
        self.tactical_context.update({
            "early_game": ["防守骚扰", "力场阻挡", "能量盾保护"],
            "mid_game": ["战术控制", "分割战场", "支援进攻"],
            "late_game": ["能量管理", "保护后排", "创造战术空间"],
            "counters": self.weak_against if hasattr(self, 'weak_against') else [],
            "countered_by": self.strong_against if hasattr(self, 'strong_against') else [],
            "synergies": [f"与{s}配合" for s in self.tactical_info.get("synergies", [])],
            "vs_protoss": self.tactical_info.get('Vs. Protoss', ''),
            "vs_terran": self.tactical_info.get('Vs. Terran', ''),
            "vs_zerg": self.tactical_info.get('Vs. Zerg', '')
        })
        
        # 预置函数候选
        self.prefab_function_candidates = [
            {
                "function_name": "sentry_force_field_split",
                "description": "哨兵使用力场分割敌方阵型",
                "parameters": {
                    "enemy_positions": "敌人位置列表",
                    "split_position": "力场放置位置"
                },
                "execution_flow": [
                    "create_force_field(split_position)",
                    "evaluate_field_effectiveness(enemy_positions)",
                    "maintain_position()"
                ]
            },
            {
                "function_name": "sentry_guardian_shield",
                "description": "哨兵使用能量盾保护友方单位",
                "parameters": {
                    "friendly_units": "友方单位列表",
                    "engagement_position": "交战位置"
                },
                "execution_flow": [
                    "move_to_position(engagement_position)",
                    "activate_guardian_shield()",
                    "monitor_energy_level()",
                    "retreat_when_low_energy()"
                ]
            },
            {
                "function_name": "sentry_hallucination_scout",
                "description": "哨兵使用幻象进行侦查",
                "parameters": {
                    "target_areas": "目标侦查区域列表",
                    "hallucination_unit": "幻象单位类型"
                },
                "execution_flow": [
                    "create_hallucination(hallucination_unit)",
                    "send_hallucination_to_area(target_areas[0])",
                    "observe_enemy_activities()",
                    "report_findings()"
                ]
            },
            {
                "function_name": "sentry_defensive_field",
                "description": "哨兵创造防守力场",
                "parameters": {
                    "defense_location": "防守位置",
                    "enemy_approach_path": "敌方接近路径"
                },
                "execution_flow": [
                    "create_force_field(enemy_approach_path)",
                    "create_force_field(enemy_approach_path)",
                    "activate_guardian_shield()",
                    "maintain_defensive_position()"
                ]
            }
        ]
    
    def create_force_field(self, position: Position) -> Dict[str, Any]:
        """在指定位置创建力场"""
        result = {
            "success": False,
            "action": "create_force_field",
            "field_created": False,
            "position": position,
            "reason": None
        }
        
        # 检查能力是否存在
        force_field = self.abilities.get("force_field", {})
        if not force_field:
            result["reason"] = "力场能力不存在"
            return result
        
        # 检查能量
        energy_cost = force_field.get("energy_cost", 25)
        if self.energy < energy_cost:
            result["reason"] = f"能量不足，需要{energy_cost}，当前{self.energy}"
            return result
        
        # 检查冷却
        if force_field.get("cooldown_remaining", 0) > 0:
            result["reason"] = f"力场技能正在冷却中，剩余时间: {force_field['cooldown_remaining']}秒"
            return result
        
        # 检查范围
        range_limit = force_field.get("range", 7)
        distance = self._calculate_distance(self.position, position)
        if distance > range_limit:
            result["reason"] = f"目标位置超出力场范围，距离: {distance:.2f}，最大范围: {range_limit}"
            return result
        
        # 执行力场创建
        print(f"{self.unique_class_name} 在位置 {position} 创建力场!")
        
        # 扣除能量
        self.energy -= energy_cost
        
        # 设置冷却
        force_field["cooldown_remaining"] = force_field.get("cooldown", 10)
        
        # 设置结果
        result["success"] = True
        result["field_created"] = True
        result["energy_consumed"] = energy_cost
        result["cooldown_applied"] = force_field.get("cooldown", 10)
        result["field_duration"] = force_field.get("duration", 15)
        
        return result
    
    def activate_guardian_shield(self) -> Dict[str, Any]:
        """激活能量盾保护周围友方单位"""
        result = {
            "success": False,
            "action": "activate_guardian_shield",
            "shield_activated": False,
            "reason": None
        }
        
        # 检查能力是否存在
        guardian_shield = self.abilities.get("guardian_shield", {})
        if not guardian_shield:
            result["reason"] = "能量盾能力不存在"
            return result
        
        # 检查是否已经激活
        if guardian_shield.get("active", False):
            result["reason"] = "能量盾已经处于激活状态"
            return result
        
        # 检查能量
        energy_cost = guardian_shield.get("energy_cost", 25)
        if self.energy < energy_cost:
            result["reason"] = f"能量不足，需要{energy_cost}，当前{self.energy}"
            return result
        
        # 检查冷却
        if guardian_shield.get("cooldown_remaining", 0) > 0:
            result["reason"] = f"能量盾技能正在冷却中，剩余时间: {guardian_shield['cooldown_remaining']}秒"
            return result
        
        # 执行能量盾激活
        print(f"{self.unique_class_name} 激活能量盾!")
        
        # 扣除能量
        self.energy -= energy_cost
        
        # 设置冷却
        guardian_shield["cooldown_remaining"] = guardian_shield.get("cooldown", 45)
        
        # 激活状态
        guardian_shield["active"] = True
        guardian_shield["activation_time"] = 0  # 游戏时间，需要根据游戏循环更新
        
        # 设置结果
        result["success"] = True
        result["shield_activated"] = True
        result["energy_consumed"] = energy_cost
        result["cooldown_applied"] = guardian_shield.get("cooldown", 45)
        result["shield_duration"] = guardian_shield.get("duration", 30)
        result["damage_reduction"] = guardian_shield.get("damage_reduction", 2)
        
        return result
    
    def create_hallucination(self, unit_type: str) -> Dict[str, Any]:
        """创造一个幻象单位"""
        result = {
            "success": False,
            "action": "create_hallucination",
            "hallucination_created": False,
            "unit_type": unit_type,
            "reason": None
        }
        
        # 检查能力是否存在
        hallucination = self.abilities.get("hallucination", {})
        if not hallucination:
            result["reason"] = "幻象能力不存在"
            return result
        
        # 检查能量
        energy_cost = hallucination.get("energy_cost", 100)
        if self.energy < energy_cost:
            result["reason"] = f"能量不足，需要{energy_cost}，当前{self.energy}"
            return result
        
        # 检查冷却
        if hallucination.get("cooldown_remaining", 0) > 0:
            result["reason"] = f"幻象技能正在冷却中，剩余时间: {hallucination['cooldown_remaining']}秒"
            return result
        
        # 执行幻象创造
        print(f"{self.unique_class_name} 创造了一个{unit_type}的幻象!")
        
        # 扣除能量
        self.energy -= energy_cost
        
        # 设置冷却
        hallucination["cooldown_remaining"] = hallucination.get("cooldown", 30)
        
        # 设置结果
        result["success"] = True
        result["hallucination_created"] = True
        result["energy_consumed"] = energy_cost
        result["cooldown_applied"] = hallucination.get("cooldown", 30)
        
        return result
    
    def maintain_position(self) -> Dict[str, Any]:
        """保持当前位置"""
        result = {
            "success": True,
            "action": "maintain_position",
            "current_position": self.position,
            "tactical_purpose": "保持战术位置"
        }
        
        print(f"{self.unique_class_name} 保持位置 {self.position}")
        
        return result
    
    def move_to_position(self, position: Position) -> Dict[str, Any]:
        """移动到指定位置"""
        result = {
            "success": True,
            "action": "move_to_position",
            "from_position": self.position,
            "to_position": position,
            "distance": self._calculate_distance(self.position, position)
        }
        
        print(f"{self.unique_class_name} 移动到位置 {position}")
        self.position = position
        
        return result
    
    def monitor_energy_level(self) -> Dict[str, Any]:
        """监控能量水平"""
        result = {
            "success": True,
            "action": "monitor_energy_level",
            "current_energy": self.energy,
            "max_energy": self.max_energy,
            "energy_percentage": (self.energy / self.max_energy) * 100
        }
        
        print(f"{self.unique_class_name} 能量水平: {self.energy}/{self.max_energy} ({(self.energy / self.max_energy) * 100:.1f}%)")
        
        return result
    
    def retreat_when_low_energy(self, threshold: float = 25.0) -> Dict[str, Any]:
        """当能量低于阈值时撤退"""
        energy_percentage = (self.energy / self.max_energy) * 100
        
        result = {
            "success": True,
            "action": "retreat_when_low_energy",
            "current_energy": self.energy,
            "energy_percentage": energy_percentage,
            "threshold": threshold,
            "retreat_recommended": energy_percentage < threshold,
            "tactical_purpose": "保留能量以备后续技能使用"
        }
        
        if energy_percentage < threshold:
            print(f"{self.unique_class_name} 能量不足，建议撤退")
        else:
            print(f"{self.unique_class_name} 能量充足，继续战斗")
        
        return result
    
    def evaluate_field_effectiveness(self, enemy_positions: List[Position]) -> Dict[str, Any]:
        """评估力场效果"""
        result = {
            "success": True,
            "action": "evaluate_field_effectiveness",
            "enemy_count": len(enemy_positions),
            "effectiveness_rating": "unknown"
        }
        
        # 简单的力场效果评估逻辑
        if len(enemy_positions) == 0:
            result["effectiveness_rating"] = "poor"
            result["reason"] = "没有敌人被力场影响"
        elif len(enemy_positions) <= 5:
            result["effectiveness_rating"] = "good"
            result["reason"] = "少量敌人被力场阻挡"
        else:
            result["effectiveness_rating"] = "excellent"
            result["reason"] = "大量敌人被力场阻挡"
        
        print(f"{self.unique_class_name} 评估力场效果: {result['effectiveness_rating']}")
        
        return result
    
    def maintain_defensive_position(self) -> Dict[str, Any]:
        """保持防守位置"""
        result = {
            "success": True,
            "action": "maintain_defensive_position",
            "defensive_position": self.position,
            "tactical_purpose": "维持防守阵型"
        }
        
        print(f"{self.unique_class_name} 维持防守位置 {self.position}")
        
        return result
    
    def send_hallucination_to_area(self, target_area: Position) -> Dict[str, Any]:
        """派遣幻象到目标区域"""
        result = {
            "success": True,
            "action": "send_hallucination_to_area",
            "target_area": target_area,
            "tactical_purpose": "侦查目标区域"
        }
        
        print(f"{self.unique_class_name} 派遣幻象到区域 {target_area}")
        
        return result
    
    def observe_enemy_activities(self) -> Dict[str, Any]:
        """观察敌人活动"""
        result = {
            "success": True,
            "action": "observe_enemy_activities",
            "tactical_purpose": "收集敌人情报"
        }
        
        print(f"{self.unique_class_name} 通过幻象观察敌人活动")
        
        return result
    
    def report_findings(self) -> Dict[str, Any]:
        """报告侦查发现"""
        result = {
            "success": True,
            "action": "report_findings",
            "tactical_purpose": "分享侦察情报"
        }
        
        print(f"{self.unique_class_name} 报告侦察发现")
        
        return result
    
    def _calculate_distance(self, pos1: Position, pos2: Position) -> float:
        """计算两个位置之间的距离"""
        return ((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2) ** 0.5