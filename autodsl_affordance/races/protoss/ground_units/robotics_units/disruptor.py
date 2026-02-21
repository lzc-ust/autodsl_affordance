from autodsl_affordance.races.protoss import ProtossRoboticsUnit
from autodsl_affordance.core.base_units.unit import Cost, Position
from autodsl_affordance.utils.json_loader import UnitJsonLoader
from typing import Dict, Any, List, Optional

class ProtossDisruptor(ProtossRoboticsUnit):
    """干扰者 - 神族高伤害范围单位，通过净化新星能力造成巨大范围伤害，需要精确的微操作。"""
    
    def __init__(self, development_mode: bool = False):
        super().__init__()
        self.unique_class_name = "Protoss_Disruptor"
        self.development_mode = development_mode
        
        # 核心属性初始化
        self.description = ""
        self.cost = None
        self.attack = {}
        self.unit_stats = {}
        self.abilities = {}  # type: Dict[str, Dict[str, Any]]
        self.tactical_info = {}
        
        # 状态属性
        self.nova_cooldown = 0
        self.nova_active = False
        self.nova_position = None
        self.nova_timer = 0
        
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
                    mineral=cost_data.get("mineral", 150),
                    vespene=cost_data.get("vespene", 150),
                    supply=cost_data.get("supply", 4),
                    time=cost_data.get("game_time", 36)
                )
                
                # 处理攻击数据（特殊攻击方式）
                if 'Attack' in data:
                    attack_data = data['Attack']
                    # 提取伤害数据
                    damage_str = attack_data.get('Damage', '145 (+25 vs Shields)')
                    base_damage = int(damage_str.split(' ')[0])
                    shield_bonus = 25  # 从描述中提取
                    
                    self.attack = {
                        "targets": ["Ground (via Purification Nova)"],
                        "damage": base_damage,
                        "shield_bonus_damage": shield_bonus,
                        "dps": {"base": 0, "vs_shields": shield_bonus},
                        "cooldown": 21,  # Nova冷却时间
                        "activation_range": 1.5,
                        "nova_control_range": 13
                    }
                
                # 处理单位统计
                if 'Unit stats' in data:
                    stats_data = data['Unit stats']
                    defense_parts = stats_data.get('Defense', '100 100 1 (+1)').split()
                    self.unit_stats = {
                        "health": int(defense_parts[0]),
                        "shield": int(defense_parts[1]),
                        "armor": int(defense_parts[2].split('(')[0]),
                        "armor_upgrade": 1,
                        "attributes": stats_data.get('Attributes', 'Armored, Mechanical').split(', '),
                        "sight": int(stats_data.get('Sight', '9')),
                        "speed": float(stats_data.get('Speed', '3.15')),
                        "cargo_size": int(stats_data.get('Cargo size', '4')),
                        "nova_speed": 4.13  # 从Ability描述中提取
                    }
                
                # 处理能力数据
                if 'Ability' in data:
                    ability_data = data['Ability']
                    self.abilities = {
                        "purification_nova": {
                            "name": "Purification Nova",
                            "hotkey": ability_data.get('Hotkey', 'E'),
                            "damage": 145,
                            "splash_radius": 1.5,
                            "cooldown": 21,
                            "duration": 1.35,
                            "control_range": 13,
                            "shield_bonus_damage": 25,
                            "speed": 4.13,
                            "description": ability_data.get('Description', '')
                        }
                    }
                
                # 处理克制关系
                self.strong_against = data.get('Strong against', [])
                self.weak_against = data.get('Weak against', [])
                
                # 处理战术信息
                if 'Competitive Usage' in data:
                    self.tactical_info = data.get('Competitive Usage', {})
                    # 添加协同单位信息
                    self.tactical_info['synergies'] = ["Warp Prism", "Sentry", "High Templar"]
        except Exception as e:
            if self.development_mode:
                raise e
            print(f"警告: 无法加载{self.unique_class_name}的数据: {e}")
    
    def _set_default_values(self):
        """设置默认值，确保属性完整性"""
        if not self.description:
            if self.development_mode:
                raise ValueError("单位描述不能为空")
            self.description = "神族高伤害范围单位，释放净化新星造成巨大范围伤害"
        
        if not self.cost:
            self.cost = Cost(mineral=150, vespene=150, supply=4, time=36)
        
        if not self.attack:
            self.attack = {
                "targets": ["Ground (via Purification Nova)"],
                "damage": 145, "damage_upgrade": 25,
                "dps": {"base": 0, "vs_shields": 25},
                "cooldown": 21,
                "range": 13
            }
        
        if not self.unit_stats:
            self.unit_stats = {
                "health": 100, "shield": 100, "armor": 1, "armor_upgrade": 1,
                "attributes": ["Armored", "Mechanical"],
                "sight": 9, "speed": 3.15, "cargo_size": 4
            }
        
        if not self.abilities:
            self.abilities = {
                "purification_nova": {
                    "damage": 145, "splash_radius": 1.5,
                    "cooldown": 21, "duration": 1.35,
                    "control_range": 13,
                    "shield_bonus_damage": 25
                }
            }
        
        if not self.tactical_info:
            self.tactical_info = {
                "strong_against": ["Marine", "Marauder", "Hydralisk", "Roach", "Stalker", "Zealot"],
                "weak_against": ["Phoenix", "Marine (with good micro)", "Zergling (with good micro)", "Tempest", "Viper"],
                "synergies": ["Warp Prism", "Sentry", "High Templar"]
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
            "natural_language_aliases": ["干扰者", "disruptor", "自爆球", "净化新星", "能量球"],
            "role_description": self.description,
            "tactical_keywords": ["范围爆发", "高伤害", "战术单位", "阵地破坏", "微操作", "区域封锁"],
            "primary_role": ["范围爆发", "阵地破坏", "单位清除", "区域控制"],
            "common_tactics": ["偷袭后排", "破坏阵型", "配合控制", "区域封锁", "棱镜空投"],
            "special_abilities": ["净化新星（Purification Nova）"],
            "micro_techniques": ["Nova控制", "冷却管理", "位置选择"],
            "visual_recognition_features": ["球形设计", "能量核心", "悬浮效果", "蓝色能量光晕"],
            "competitive_insights": general_tactics
        })
        
        self.visual_recognition.update({
            "identifying_features": ["球形设计", "能量核心", "悬浮效果", "释放净化新星特效"],
            "minimap_characteristics": "小型蓝色单位",
            "unique_visual_queues": ["新星激活动画", "能量球移动轨迹", "爆炸特效"],
            "llm_vision_prompt": "识别画面中的干扰者 - 球形设计，具有能量核心和悬浮效果，可能正在释放或控制净化新星"
        })
        
        self.tactical_context.update({
            "early_game": [],
            "mid_game": ["范围爆发", "破坏阵型", "消灭集群单位"],
            "late_game": ["阵地突破", "配合棱镜空投", "限制敌方移动"],
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
                "function_name": "disruptor_nova_burst",
                "description": "使用净化新星对敌方单位集群造成爆发伤害",
                "parameters": {
                    "target_cluster": "目标集群位置",
                    "priority_targets": "优先目标单位列表"
                },
                "execution_flow": [
                    "launch_purification_nova(target_cluster)",
                    "control_nova(adjusted_position)",
                    "nova_explosion(affected_units)",
                    "retreat_safely()"
                ]
            },
            {
                "function_name": "disruptor_area_denial",
                "description": "使用净化新星进行区域封锁和防守",
                "parameters": {
                    "denial_position": "封锁位置",
                    "enemy_approach_direction": "敌方接近方向"
                },
                "execution_flow": [
                    "launch_purification_nova(denial_position)",
                    "control_nova(enemy_advance_path)",
                    "nova_explosion(approaching_units)",
                    "reposition_disruptor()"
                ]
            },
            {
                "function_name": "disruptor_prism_drop",
                "description": "通过棱镜空投进行干扰者突袭战术",
                "parameters": {
                    "drop_position": "空投位置",
                    "enemy_vulnerable_area": "敌方脆弱区域"
                },
                "execution_flow": [
                    "position_warp_prism(drop_position)",
                    "deploy_disruptor_from_prism()",
                    "launch_purification_nova(enemy_vulnerable_area)",
                    "retreat_to_prism()"
                ]
            },
            {
                "function_name": "disruptor_cooldown_management",
                "description": "管理多个干扰者的净化新星冷却，实现持续输出",
                "parameters": {
                    "disruptor_group": "干扰者群组",
                    "engagement_sequence": "交战顺序"
                },
                "execution_flow": [
                    "identify_ready_disruptors()",
                    "launch_purification_nova(target_area)",
                    "track_cooldown_status()",
                    "rotate_engagement_order()"
                ]
            }
        ]
    
    def launch_purification_nova(self, target_position: Position) -> Dict[str, Any]:
        """发射净化新星"""
        result = {
            "success": False,
            "action": "launch_purification_nova",
            "target_position": target_position,
            "nova_launched": False,
            "current_cooldown": self.nova_cooldown,
            "nova_duration": 1.35,
            "estimated_damage": 145,
            "reason": None
        }
        
        # 检查冷却时间
        if self.nova_cooldown > 0:
            result["reason"] = f"净化新星在冷却中，剩余{self.nova_cooldown}秒"
            return result
        
        # 获取新星能力数据
        nova = self.abilities.get("purification_nova", {})
        
        # 发射新星
        self.nova_active = True
        self.nova_position = target_position
        self.nova_timer = nova.get("duration", 1.35)
        self.nova_cooldown = nova.get("cooldown", 21)
        
        print(f"{self.unique_class_name} 向位置 {target_position} 发射净化新星")
        
        result["success"] = True
        result["nova_launched"] = True
        result["nova_duration"] = nova.get("duration", 1.35)
        result["estimated_damage"] = nova.get("damage", 145)
        result["shield_bonus_damage"] = nova.get("shield_bonus_damage", 25)
        result["splash_radius"] = nova.get("splash_radius", 1.5)
        result["cooldown_applied"] = nova.get("cooldown", 21)
        
        return result
    
    def estimate_nova_effectiveness(self, target_position: Position, enemy_units: List[str]) -> Dict[str, Any]:
        """估算净化新星对目标区域和单位的效果"""
        result = {
            "success": True,
            "action": "estimate_nova_effectiveness",
            "target_position": target_position,
            "potential_targets": [],
            "estimated_damage_per_unit": {},
            "high_value_targets": [],
            "risk_of_friendly_fire": "low"
        }
        
        # 获取新星能力数据
        nova = self.abilities.get("purification_nova", {})
        base_damage = nova.get("damage", 145)
        shield_bonus = nova.get("shield_bonus_damage", 25)
        
        # 分析潜在目标
        for unit in enemy_units:
            unit_lower = unit.lower()
            damage = base_damage
            
            # 判断是否为高价值目标
            is_high_value = any(high in unit_lower for high in ["marine", "marauder", "hydralisk", "roach", "stalker", "zealot"])
            
            # 判断是否有护盾
            has_shield = any(keyword in unit_lower for keyword in ["zealot", "stalker", "sentry", "immortal", "colossus", "protoss"])
            if has_shield:
                damage += shield_bonus
            
            result["potential_targets"].append(unit)
            result["estimated_damage_per_unit"][unit] = damage
            
            if is_high_value:
                result["high_value_targets"].append(unit)
        
        # 检查是否可能伤害到友方单位
        if any("protoss" in unit.lower() for unit in enemy_units):
            result["risk_of_friendly_fire"] = "high"
        
        print(f"净化新星效果估算: 可能影响{len(result['potential_targets'])}个单位，{len(result['high_value_targets'])}个高价值目标")
        
        return result
    
    def control_nova(self, nova_position: Position) -> Dict[str, Any]:
        """控制净化新星移动"""
        result = {
            "success": False,
            "action": "control_nova",
            "nova_redirected": False,
            "previous_position": None,
            "new_position": nova_position,
            "reason": None
        }
        
        # 检查新星是否激活
        if not self.nova_active or self.nova_timer <= 0:
            result["reason"] = "当前没有激活的新星"
            return result
        
        # 获取新星能力数据
        nova = self.abilities.get("purification_nova", {})
        
        # 检查是否有当前位置
        if not self.nova_position:
            result["reason"] = "没有激活的新星可供控制"
            return result
        
        result["previous_position"] = self.nova_position
        
        # 计算当前位置到新位置的距离
        distance = self._calculate_distance(self.nova_position, nova_position)
        
        # 检查是否在控制范围内
        control_range = nova.get("control_range", 13)
        if distance > control_range:
            result["reason"] = f"新位置超出控制范围（{control_range}）"
            result["distance_to_target"] = distance
            return result
        
        # 计算剩余时间内能否到达
        remaining_time = self.nova_timer
        nova_speed = nova.get("speed", 4.13)
        max_reachable_distance = remaining_time * nova_speed
        
        if distance > max_reachable_distance:
            # 计算能到达的最接近位置
            dx = nova_position.x - self.nova_position.x
            dy = nova_position.y - self.nova_position.y
            ratio = max_reachable_distance / distance
            closest_x = self.nova_position.x + dx * ratio
            closest_y = self.nova_position.y + dy * ratio
            closest_pos = Position(closest_x, closest_y)
            
            self.nova_position = closest_pos
            
            result["success"] = True
            result["nova_redirected"] = True
            result["new_position"] = closest_pos
            result["partial_movement"] = True
            result["reason"] = "新位置太远，但已移动到能到达的最近位置"
        else:
            # 重定向新星
            self.nova_position = nova_position
            
            result["success"] = True
            result["nova_redirected"] = True
            result["new_position"] = nova_position
        
        print(f"{self.unique_class_name} 控制净化新星移动到位置 {result['new_position']}")
        
        return result
    
    def reposition_disruptor(self, safe_position: Position) -> Dict[str, Any]:
        """重新定位干扰者到安全位置"""
        result = {
            "success": True,
            "action": "reposition_disruptor",
            "current_position": getattr(self, "position", Position(0, 0)),
            "new_position": safe_position,
            "tactical_purpose": "避免敌人反制"
        }
        
        print(f"{self.unique_class_name} 重新定位到安全位置: {safe_position}")
        self.position = safe_position
        
        return result
    
    def nova_explosion(self, target_units: List[str]) -> Dict[str, Any]:
        """计算净化新星爆炸效果"""
        result = {
            "success": True,
            "action": "nova_explosion",
            "explosion_position": self.nova_position,
            "units_affected": [],
            "damage_dealt": {},
            "friendly_casualties": [],
            "enemy_casualties": [],
            "effectiveness_rating": "medium"
        }
        
        nova = self.abilities.get("purification_nova", {})
        base_damage = nova.get("damage", 145)
        shield_bonus = nova.get("shield_bonus_damage", 25)
        
        for unit in target_units:
            # 检查单位类型和伤害计算
            unit_lower = unit.lower()
            
            # 判断是否为友好单位（这里简化处理，实际应该根据阵营判断）
            is_friendly = any(keyword in unit_lower for keyword in ["protoss", "zealot", "stalker", "sentry"])
            
            # 计算伤害详情
            damage_details = {
                "base_damage": base_damage,
                "shield_bonus": 0,
                "total": base_damage
            }
            
            # 检查是否有护盾
            has_shield = any(keyword in unit_lower for keyword in ["zealot", "stalker", "sentry", "immortal", "colossus", "protoss"])
            if has_shield:
                damage_details["shield_bonus"] = shield_bonus
                damage_details["total"] = base_damage + shield_bonus
            
            result["units_affected"].append(unit)
            result["damage_dealt"][unit] = damage_details
            
            if is_friendly:
                result["friendly_casualties"].append(unit)
            else:
                result["enemy_casualties"].append(unit)
        
        # 重置新星状态
        self.nova_active = False
        self.nova_position = None
        self.nova_timer = 0
        
        # 评估爆炸效果
        enemy_count = len(result["enemy_casualties"])
        friendly_count = len(result["friendly_casualties"])
        
        if enemy_count >= 3 and friendly_count == 0:
            result["effectiveness_rating"] = "excellent"
        elif enemy_count >= 2 and friendly_count <= 1:
            result["effectiveness_rating"] = "good"
        elif enemy_count > 0 and friendly_count == 0:
            result["effectiveness_rating"] = "medium"
        else:
            result["effectiveness_rating"] = "poor"
        
        print(f"{self.unique_class_name} 净化新星爆炸，影响{len(result['units_affected'])}个单位，{enemy_count}个敌方，{friendly_count}个友方")
        
        return result
    
    def retreat_safely(self) -> Dict[str, Any]:
        """安全撤退干扰者"""
        result = {
            "success": True,
            "action": "retreat_safely",
            "current_position": getattr(self, "position", Position(0, 0)),
            "tactical_purpose": "避免敌人反击"
        }
        
        # 计算撤退位置（简化为向后移动）
        retreat_x = result["current_position"].x - 3
        retreat_y = result["current_position"].y
        retreat_position = Position(retreat_x, retreat_y)
        
        print(f"{self.unique_class_name} 安全撤退到位置: {retreat_position}")
        self.position = retreat_position
        
        result["retreat_position"] = retreat_position
        
        return result
    
    def deploy_disruptor_from_prism(self) -> Dict[str, Any]:
        """从棱镜部署干扰者"""
        result = {
            "success": True,
            "action": "deploy_disruptor_from_prism",
            "tactical_advantage": "出其不意的攻击位置"
        }
        
        print(f"{self.unique_class_name} 从棱镜部署到战场")
        
        # 设置部署位置（这里简化处理）
        deploy_position = Position(10, 10)
        self.position = deploy_position
        result["deploy_position"] = deploy_position
        
        return result
    
    def track_cooldown_status(self) -> Dict[str, Any]:
        """跟踪净化新星的冷却状态"""
        result = {
            "success": True,
            "action": "track_cooldown_status",
            "current_cooldown": self.nova_cooldown,
            "status": "ready" if self.nova_cooldown <= 0 else "cooldown",
            "estimated_ready_time": max(0, self.nova_cooldown)
        }
        
        print(f"{self.unique_class_name} 净化新星冷却状态: {result['status']}, 剩余时间: {result['estimated_ready_time']}秒")
        
        return result
    
    def area_denial(self, area_position: Position) -> Dict[str, Any]:
        """区域封锁战术"""
        result = {
            "success": False,
            "action": "area_denial",
            "denial_position": area_position,
            "nova_result": None,
            "tactical_purpose": "阻止敌方单位通过特定区域"
        }
        
        # 发射净化新星进行区域封锁
        nova_result = self.launch_purification_nova(area_position)
        result["nova_result"] = nova_result
        
        if nova_result["success"]:
            print(f"{self.unique_class_name} 在 {area_position} 部署净化新星进行区域封锁")
            result["success"] = True
            result["block_radius"] = nova_result.get("splash_radius", 1.5)
        else:
            print(f"{self.unique_class_name} 无法在冷却期间进行区域封锁")
            result["reason"] = nova_result.get("reason", "未知错误")
        
        return result
    
    def _calculate_distance(self, pos1: Position, pos2: Position) -> float:
        """计算两点之间的距离"""
        return ((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2) ** 0.5
    
    # 预置函数候选已在_enhance_vlm_interface中定义