from autodsl_affordance.races.protoss import ProtossRoboticsUnit
from autodsl_affordance.core.base_units.unit import Cost, Position
from autodsl_affordance.utils.json_loader import UnitJsonLoader
from typing import Dict, Any, List, Optional

class ProtossImmortal(ProtossRoboticsUnit):
    """不朽者 - 神族重甲杀手，具备强大的屏障能力，可以吸收高伤害攻击，是对抗重甲单位的理想选择。"""
    
    def __init__(self, development_mode: bool = False):
        super().__init__()
        self.unique_class_name = "Protoss_Immortal"
        self.development_mode = development_mode
        
        # 核心属性初始化
        self.description = ""
        self.cost = None
        self.attack = {}
        self.unit_stats = {}
        self.abilities = {}  # type: Dict[str, Dict[str, Any]]
        self.tactical_info = {}
        
        # 状态属性
        self.barrier_active = False
        self.barrier_cooldown = 0
        
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
            json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 
                                   'sc2_unit_info', f'{self.unique_class_name}.json')
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                self.description = data.get("Description", "")
                
                # 处理成本数据
                cost_data = data.get("Cost", {})
                self.cost = Cost(
                    mineral=cost_data.get("mineral", 275),
                    vespene=cost_data.get("vespene", 100),
                    supply=cost_data.get("supply", 4),
                    time=cost_data.get("game_time", 39)
                )
                
                # 处理攻击数据
                if 'Attack' in data:
                    attack_data = data['Attack']
                    # 提取基础伤害和升级数据
                    damage_str = attack_data.get('Damage', '20 (+2)')
                    base_damage = int(damage_str.split(' ')[0])
                    damage_upgrade = int(damage_str.split('(')[1].split(')')[0].replace('+', ''))
                    
                    # 提取额外伤害数据
                    bonus_str = attack_data.get('Bonus', '+30 (+3) vs Armored')
                    bonus_damage = int(bonus_str.split(' ')[0].replace('+', ''))
                    bonus_upgrade = int(bonus_str.split('(')[1].split(')')[0].replace('+', ''))
                    
                    # 提取DPS数据
                    dps_str = attack_data.get('DPS', '15.4 (Base), 44.3 (vs Armored)')
                    dps_parts = dps_str.split(', ')
                    base_dps = float(dps_parts[0].split(' ')[0])
                    vs_armored_dps = float(dps_parts[1].split(' ')[0])
                    
                    self.attack = {
                        "targets": ["Ground"],
                        "damage": base_damage,
                        "damage_upgrade": damage_upgrade,
                        "dps": {"base": base_dps, "vs_armored": vs_armored_dps},
                        "cooldown": float(attack_data.get('Cooldown', '1.3')),
                        "bonus_damage": {
                            "value": bonus_damage,
                            "upgrade": bonus_upgrade,
                            "vs": "Armored"
                        },
                        "range": int(attack_data.get('Range', '6'))
                    }
                
                # 处理单位统计
                if 'Unit stats' in data:
                    stats_data = data['Unit stats']
                    defense_parts = stats_data.get('Defense', '200 100 1 (+1)').split()
                    self.unit_stats = {
                        "health": int(defense_parts[0]),
                        "shield": int(defense_parts[1]),
                        "armor": int(defense_parts[2].split('(')[0]),
                        "armor_upgrade": 1,
                        "attributes": stats_data.get('Attributes', 'Armored, Mechanical').split(', '),
                        "sight": int(stats_data.get('Sight', '9')),
                        "speed": float(stats_data.get('Speed', '3.15')),
                        "cargo_size": int(stats_data.get('Cargo size', '4'))
                    }
                
                # 处理能力数据
                if 'Ability' in data:
                    ability_data = data['Ability']
                    self.abilities = {
                        "barrier": {
                            "name": "Barrier",
                            "cooldown": 31,
                            "shield_amount": 100,
                            "damage_threshold": 10,
                            "description": ability_data.get('Description', ''),
                            "is_passive": True
                        }
                    }
                
                # 处理克制关系
                self.strong_against = data.get('Strong against', [])
                self.weak_against = data.get('Weak against', [])
                
                # 处理战术信息
                if 'Competitive Usage' in data:
                    self.tactical_info = data.get('Competitive Usage', {})
                    # 添加协同单位信息
                    self.tactical_info['synergies'] = ["Sentry", "Stalker", "Warp Prism"]
        except Exception as e:
            if self.development_mode:
                raise e
            print(f"警告: 无法加载{self.unique_class_name}的数据: {e}")
    
    def _set_default_values(self):
        """设置默认值，确保属性完整性"""
        if not self.description:
            if self.development_mode:
                raise ValueError("单位描述不能为空")
            self.description = "神族重甲杀手，具备屏障能力，专门对抗高伤害单位"
        
        if not self.cost:
            self.cost = Cost(mineral=275, vespene=100, supply=4, time=39)
        
        if not self.attack:
            self.attack = {
                "targets": ["Ground"],
                "damage": 20, "damage_upgrade": 2,
                "dps": {"base": 15.4, "vs_armored": 44.3},
                "cooldown": 1.3,
                "bonus_damage": {"value": 30, "upgrade": 3, "vs": "Armored"},
                "range": 6
            }
        
        if not self.unit_stats:
            self.unit_stats = {
                "health": 200, "shield": 100, "armor": 1, "armor_upgrade": 1,
                "attributes": ["Armored", "Mechanical"],
                "sight": 9, "speed": 3.15, "cargo_size": 4
            }
        
        if not self.abilities:
            self.abilities = {
                "barrier": {"cooldown": 31, "shield_amount": 100, "damage_threshold": 10}
            }
        
        if not self.tactical_info:
            self.tactical_info = {
                "strong_against": ["Siege Tank", "Roach", "Stalker", "Marauder", "Thor", "Lurker", "Ultralisk"],
                "weak_against": ["Marine", "Zealot", "Zergling", "Immortal (mirror)", "Viper"],
                "synergies": ["Sentry", "Stalker", "Warp Prism"]
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
            "natural_language_aliases": ["不朽者", "immortal", "重甲杀手", "装甲杀手", "坦克杀手"],
            "role_description": self.description,
            "tactical_keywords": ["反重甲", "屏障", "坦克杀手", "前排", "抗高伤", "地面主力", "装甲克星"],
            "primary_role": ["反重甲", "前排输出", "坦克应对", "抗高伤", "装甲单位摧毁者"],
            "common_tactics": ["集火重甲", "利用屏障", "配合狂热者", "棱镜空投", "高地防守", "坦克线突破"],
            "special_abilities": ["屏障（Barrier）"],
            "micro_techniques": ["屏障管理", "棱镜微操", "集火装甲单位", "规避轻甲单位"],
            "visual_recognition_features": ["双轮机甲", "蓝色能量核心", "大型相位干扰炮", "厚重装甲"],
            "competitive_insights": general_tactics
        })
        
        self.visual_recognition.update({
            "identifying_features": ["双轮机甲", "蓝色能量核心", "大型相位干扰炮", "厚重装甲"],
            "minimap_characteristics": "中型蓝色单位",
            "unique_visual_queues": ["屏障激活特效", "对重甲单位特效"],
            "llm_vision_prompt": "识别画面中的不朽者 - 双轮机甲，拥有蓝色能量核心和相位干扰炮"
        })
        
        self.tactical_context.update({
            "early_game": [],
            "mid_game": ["反重甲", "前排吸收伤害", "坦克应对"],
            "late_game": ["主力输出", "高地防守", "配合棱镜空投"],
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
                "function_name": "immortal_armored_hunter",
                "description": "不朽者针对敌方装甲单位进行高效打击",
                "parameters": {
                    "target_armored_units": "装甲单位列表",
                    "engagement_position": "交战位置"
                },
                "execution_flow": [
                    "activate_barrier()",
                    "counter_armored_units(target_armored_units)",
                    "position_for_max_effect(engagement_position)",
                    "retreat_if_outnumbered()"
                ]
            },
            {
                "function_name": "immortal_tank_line_breaker",
                "description": "不朽者突破敌方坦克防线",
                "parameters": {
                    "tank_line_position": "坦克防线位置",
                    "approach_angle": "接近角度"
                },
                "execution_flow": [
                    "activate_barrier()",
                    "engage_tank_line(tank_line_position)",
                    "focus_fire_highest_threat()",
                    "maintain_formation()"
                ]
            },
            {
                "function_name": "immortal_prism_drop",
                "description": "通过棱镜空投不朽者进行突袭",
                "parameters": {
                    "drop_position": "空投位置",
                    "enemy_vulnerable_area": "敌方脆弱区域"
                },
                "execution_flow": [
                    "position_warp_prism(drop_position)",
                    "deploy_from_prism()",
                    "activate_barrier()",
                    "counter_armored_units(target_units)"
                ]
            },
            {
                "function_name": "immortal_barrier_management",
                "description": "管理不朽者的屏障能力以最大化生存能力",
                "parameters": {
                    "expected_damage": "预期承受伤害",
                    "enemy_composition": "敌方单位组成"
                },
                "execution_flow": [
                    "activate_barrier()",
                    "take_high_damage(expected_damage)",
                    "retreat_if_barrier_down()",
                    "track_cooldown()"
                ]
            }
        ]
    
    def activate_barrier(self) -> Dict[str, Any]:
        """激活屏障能力"""
        result = {
            "success": False,
            "action": "activate_barrier",
            "barrier_activated": False,
            "current_cooldown": self.barrier_cooldown,
            "shield_amount": 100,
            "reason": None
        }
        
        # 检查冷却时间
        if self.barrier_cooldown > 0:
            result["reason"] = f"屏障在冷却中，剩余{self.barrier_cooldown}秒"
            return result
        
        # 获取屏障能力数据
        barrier = self.abilities.get("barrier", {})
        shield_amount = barrier.get("shield_amount", 100)
        
        # 激活屏障
        self.barrier_active = True
        self.barrier_cooldown = barrier.get("cooldown", 31)
        
        print(f"{self.unique_class_name} 激活屏障，获得{shield_amount}点临时护盾")
        
        result["success"] = True
        result["barrier_activated"] = True
        result["shield_amount"] = shield_amount
        result["damage_threshold"] = barrier.get("damage_threshold", 10)
        result["cooldown_applied"] = barrier.get("cooldown", 31)
        
        return result
    
    def track_cooldown(self) -> Dict[str, Any]:
        """跟踪屏障的冷却状态"""
        result = {
            "success": True,
            "action": "track_cooldown",
            "current_cooldown": self.barrier_cooldown,
            "status": "ready" if self.barrier_cooldown <= 0 else "cooldown",
            "estimated_ready_time": max(0, self.barrier_cooldown)
        }
        
        print(f"{self.unique_class_name} 屏障冷却状态: {result['status']}, 剩余时间: {result['estimated_ready_time']}秒")
        
        return result
    
    def position_for_max_effect(self, optimal_position: Position) -> Dict[str, Any]:
        """将不朽者移动到最佳战斗位置"""
        result = {
            "success": True,
            "action": "position_for_max_effect",
            "current_position": getattr(self, "position", Position(0, 0)),
            "optimal_position": optimal_position,
            "tactical_purpose": "最大化输出并最小化受到的伤害"
        }
        
        print(f"{self.unique_class_name} 移动到最佳战斗位置: {optimal_position}")
        self.position = optimal_position
        
        return result
    
    def counter_armored_units(self, armored_units: List[str]) -> Dict[str, Any]:
        """对抗重甲单位"""
        result = {
            "success": True,
            "action": "counter_armored_units",
            "total_targets": len(armored_units),
            "targets_attacked": [],
            "damage_dealt": {},
            "high_value_targets": [],
            "effectiveness_rating": "medium"
        }
        
        # 基础伤害
        base_damage = self.attack.get("damage", 20)
        bonus_damage = self.attack.get("bonus_damage", {}).get("value", 30)
        
        for target in armored_units:
            target_lower = target.lower()
            # 检查是否为装甲单位
            if any(unit.lower() in target_lower for unit in ["siege tank", "roach", "stalker", "marauder", "thor", "lurker", "ultralisk"]):
                total_damage = base_damage + bonus_damage
                result["targets_attacked"].append(target)
                result["damage_dealt"][target] = {
                    "base_damage": base_damage,
                    "bonus_damage": bonus_damage,
                    "total": total_damage,
                    "bonus_type": "vs Armored"
                }
                
                # 判断是否为高价值目标
                if any(high in target_lower for high in ["siege tank", "thor", "ultralisk", "lurker"]):
                    result["high_value_targets"].append(target)
        
        # 评估效果
        armored_count = len(result["targets_attacked"])
        high_value_count = len(result["high_value_targets"])
        
        if armored_count >= 3 or high_value_count >= 2:
            result["effectiveness_rating"] = "excellent"
        elif armored_count >= 2 or high_value_count >= 1:
            result["effectiveness_rating"] = "good"
        elif armored_count >= 1:
            result["effectiveness_rating"] = "medium"
        else:
            result["effectiveness_rating"] = "poor"
        
        print(f"{self.unique_class_name} 对抗 {armored_count} 个装甲单位，其中 {high_value_count} 个高价值目标")
        
        return result
    
    def focus_fire_highest_threat(self) -> Dict[str, Any]:
        """集火最高威胁的敌方单位"""
        result = {
            "success": True,
            "action": "focus_fire_highest_threat",
            "tactical_purpose": "优先消灭最危险的敌方单位"
        }
        
        print(f"{self.unique_class_name} 集火最高威胁的敌方单位")
        
        return result
    
    def maintain_formation(self) -> Dict[str, Any]:
        """保持战斗阵型"""
        result = {
            "success": True,
            "action": "maintain_formation",
            "tactical_purpose": "保持团队协作和防护"
        }
        
        print(f"{self.unique_class_name} 保持战斗阵型")
        
        return result
    
    def take_high_damage(self, damage_amount: int) -> Dict[str, Any]:
        """承受高伤害攻击，触发屏障"""
        result = {
            "success": True,
            "action": "take_high_damage",
            "damage_received": damage_amount,
            "barrier_triggered": False,
            "actual_damage_taken": damage_amount,
            "remaining_shield": 0,
            "barrier_status": "inactive"
        }
        
        barrier = self.abilities.get("barrier", {})
        damage_threshold = barrier.get("damage_threshold", 10)
        shield_amount = barrier.get("shield_amount", 100)
        
        # 检查是否触发屏障
        if damage_amount > damage_threshold and self.barrier_cooldown <= 0:
            # 自动激活屏障
            self.barrier_active = True
            self.barrier_cooldown = barrier.get("cooldown", 31)
            
            # 计算实际受到的伤害
            actual_damage = max(0, damage_amount - shield_amount)
            remaining_shield = max(0, shield_amount - damage_amount)
            
            result["actual_damage_taken"] = actual_damage
            result["barrier_triggered"] = True
            result["remaining_shield"] = remaining_shield
            result["barrier_status"] = "active"
            result["damage_mitigated"] = damage_amount - actual_damage
        
        # 如果屏障已经激活
        elif self.barrier_active:
            result["actual_damage_taken"] = max(0, damage_amount - self._get_current_barrier_shield())
            result["barrier_status"] = "active"
            result["damage_mitigated"] = damage_amount - result["actual_damage_taken"]
        
        print(f"{self.unique_class_name} 受到{damage_amount}点伤害，屏障{'触发' if result['barrier_triggered'] else '未触发'}，实际承受{result['actual_damage_taken']}点伤害")
        
        return result
    
    def _get_current_barrier_shield(self) -> int:
        """获取当前屏障剩余护盾值（简化实现）"""
        return self.abilities.get("barrier", {}).get("shield_amount", 100) if self.barrier_active else 0
    
    def retreat_if_outnumbered(self) -> Dict[str, Any]:
        """当数量处于劣势时撤退"""
        result = {
            "success": True,
            "action": "retreat_if_outnumbered",
            "retreat_recommended": False,
            "tactical_purpose": "避免在不利条件下战斗"
        }
        
        print(f"{self.unique_class_name} 评估战场局势，判断是否需要撤退")
        
        return result
    
    def retreat_if_barrier_down(self) -> Dict[str, Any]:
        """当屏障冷却时撤退以避免高伤害"""
        result = {
            "success": True,
            "action": "retreat_if_barrier_down",
            "barrier_down": self.barrier_cooldown > 0,
            "recommended_action": "retreat" if self.barrier_cooldown > 0 else "continue_fighting",
            "tactical_purpose": "保护不朽者免受高伤害攻击"
        }
        
        print(f"{self.unique_class_name} 屏障状态检查: {'冷却中，建议撤退' if result['barrier_down'] else '可用，继续战斗'}")
        
        return result
    
    def deploy_from_prism(self) -> Dict[str, Any]:
        """从棱镜部署不朽者"""
        result = {
            "success": True,
            "action": "deploy_from_prism",
            "tactical_advantage": "出其不意的攻击位置"
        }
        
        print(f"{self.unique_class_name} 从棱镜部署到战场")
        
        # 设置部署位置（这里简化处理）
        deploy_position = Position(10, 10)
        self.position = deploy_position
        result["deploy_position"] = deploy_position
        
        return result
    
    def engage_tank_line(self, position: Position) -> Dict[str, Any]:
        """对抗坦克防线"""
        result = {
            "success": False,
            "action": "engage_tank_line",
            "engagement_position": position,
            "barrier_result": None,
            "tactical_purpose": "突破敌方坦克防线"
        }
        
        # 激活屏障准备承受坦克伤害
        barrier_result = self.activate_barrier()
        result["barrier_result"] = barrier_result
        
        if barrier_result["success"]:
            print(f"{self.unique_class_name} 在 {position} 激活屏障并向坦克防线推进")
            result["success"] = True
            result["expected_damage_mitigation"] = barrier_result.get("shield_amount", 100)
        else:
            print(f"{self.unique_class_name} 无法在冷却期间对抗坦克防线")
            result["reason"] = barrier_result.get("reason", "未知错误")
        
        return result
    
    def position_warp_prism(self, drop_position: Position) -> Dict[str, Any]:
        """部署棱镜到空投位置（战术配合）"""
        result = {
            "success": True,
            "action": "position_warp_prism",
            "drop_position": drop_position,
            "tactical_purpose": "为不朽者空投做准备"
        }
        
        print(f"指挥棱镜移动到空投位置: {drop_position}")
        
        return result
    
    def _calculate_distance(self, pos1: Position, pos2: Position) -> float:
        """计算两点之间的距离"""
        return ((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2) ** 0.5
    
    # 预置函数候选已在_enhance_vlm_interface中定义