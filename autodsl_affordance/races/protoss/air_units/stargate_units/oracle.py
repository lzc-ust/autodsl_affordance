from autodsl_affordance.races.protoss import ProtossStargateUnit
from autodsl_affordance.core.base_units.unit import Cost, Position
from autodsl_affordance.utils.json_loader import UnitJsonLoader
from typing import Dict, Any, List
import json
import os

class ProtossOracle(ProtossStargateUnit):
    """先知 - 神族侦查骚扰单位"""
    
    def __init__(self):
        super().__init__()
        self.unique_class_name = "Protoss_Oracle"
        
        # 尝试从JSON加载数据，如果失败则使用默认值
        self._load_data()
        
        # 设置默认值（如果JSON加载失败或不完整）
        self._set_default_values()
        
        # VLM优化
        self._enhance_vlm_interface()
    
    def _load_data(self):
        """从JSON文件加载单位数据"""
        json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 
                                'sc2_unit_info', f'{self.unique_class_name}.json')
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 加载描述
                if 'Description' in data:
                    self.description = data['Description']
                
                # 加载成本信息
                if 'Cost' in data:
                    cost_data = data['Cost']
                    self.cost = Cost(
                        mineral=cost_data.get('mineral', 150),
                        vespene=cost_data.get('vespene', 150),
                        supply=cost_data.get('supply', 3),
                        time=cost_data.get('game_time', 37)
                    )
                
                # 加载攻击数据
                if 'Attack' in data:
                    attack_data = data['Attack']
                    self.attack = {
                        "targets": ["Ground"],
                        "damage": 15,
                        "damage_upgrade": 1,
                        "dps": {"base": 22.1, "vs_light": 33.7},
                        "cooldown": 0.45,
                        "bonus_damage": {"value": 7, "upgrade": 1, "vs": "Light"},
                        "range": 4
                    }
                
                # 加载单位统计
                if 'Unit stats' in data:
                    stats_data = data['Unit stats']
                    # 解析防御数据 "100 60 0 (+1)"
                    defense_parts = stats_data.get('Defense', '100 60 0 (+1)').split()
                    self.unit_stats = {
                        "health": int(defense_parts[0]),
                        "shield": int(defense_parts[1]),
                        "armor": int(defense_parts[2].split('(')[0]),
                        "armor_upgrade": 1,
                        "attributes": ["Mechanical", "Armored", "Psionic"],
                        "sight": 10,
                        "speed": 5.6,
                        "cargo_size": 0
                    }
                
                # 加载能力数据
                if 'Ability' in data:
                    abilities_data = data['Ability']
                    self.abilities = {}
                    for ability in abilities_data:
                        ability_name = ability['Name'].lower().replace(' ', '_')
                        if ability_name == "pulsar_beam":
                            self.abilities[ability_name] = {
                                "cooldown": 0,
                                "energy_cost": 25,
                                "energy_per_second": 3,
                                "description": ability.get('Description', '')
                            }
                        elif ability_name == "revelation":
                            self.abilities[ability_name] = {
                                "cooldown": 0,
                                "duration": 30,
                                "energy_cost": 50,
                                "detection_range": 10,
                                "description": ability.get('Description', '')
                            }
                        elif ability_name == "stasis_ward":
                            self.abilities[ability_name] = {
                                "cooldown": 0,
                                "energy_cost": 75,
                                "duration": 30,
                                "activation_delay": 3.5,
                                "stasis_duration": 12,
                                "description": ability.get('Description', '')
                            }
                
                # 加载克制关系
                if 'Strong against' in data:
                    self.strong_against = data['Strong against']
                if 'Weak against' in data:
                    self.weak_against = data['Weak against']
                
                # 加载战术信息
                if 'Competitive Usage' in data:
                    self.tactical_info = data['Competitive Usage']
                    
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Error loading {self.unique_class_name}.json: {e}")
            # 出错时不中断，将在_set_default_values中设置默认值
    
    def _set_default_values(self):
        """设置默认值，确保所有必要属性都有值"""
        # 基础信息
        if not hasattr(self, 'description'):
            self.description = "神族侦查骚扰单位，具备多种战术能力"
        
        # 成本信息
        if not hasattr(self, 'cost'):
            self.cost = Cost(mineral=150, vespene=150, supply=3, time=37)
        
        # 攻击数据
        if not hasattr(self, 'attack'):
            self.attack = {
                "targets": ["Ground"],
                "damage": 15, "damage_upgrade": 1,
                "dps": {"base": 22.1, "vs_light": 33.7},
                "cooldown": 0.45,
                "bonus_damage": {"value": 7, "upgrade": 1, "vs": "Light"},
                "range": 4
            }
        
        # 单位统计
        if not hasattr(self, 'unit_stats'):
            self.unit_stats = {
                "health": 100, "shield": 60, "armor": 0, "armor_upgrade": 1,
                "attributes": ["Mechanical", "Armored", "Psionic"],
                "sight": 10, "speed": 5.6, "cargo_size": 0
            }
        
        # 能力配置
        if not hasattr(self, 'abilities'):
            self.abilities = {
                "revelation": {
                    "cooldown": 0,
                    "duration": 30,
                    "energy_cost": 50,
                    "detection_range": 10
                },
                "pulsar_beam": {
                    "cooldown": 0,
                    "energy_cost": 25,
                    "energy_per_second": 3
                },
                "stasis_ward": {
                    "cooldown": 0,
                    "energy_cost": 75,
                    "duration": 30,
                    "activation_delay": 3.5,
                    "stasis_duration": 12
                }
            }
        
        # 克制关系
        if not hasattr(self, 'strong_against'):
            self.strong_against = ["SCV", "Drone", "Probe", "Zergling", "Marine"]
        if not hasattr(self, 'weak_against'):
            self.weak_against = ["Marine (in numbers)", "Phoenix", "Viking", "Mutalisk", "Hydralisk"]
        
        # 战术信息
        if not hasattr(self, 'tactical_info'):
            self.tactical_info = {
                "General": "The Oracle is primarily used for early-game worker harassment and mid-game scouting/support.",
                "Vs. Protoss": "Effective for early worker harassment and scouting tech choices.",
                "Vs. Terran": "Excellent against Terran mineral lines, but must avoid Marines and Missile Turrets.",
                "Vs. Zerg": "Devastating against drone lines, though Queens and Spore Crawlers pose significant threats."
            }

        # 预设能力冷却和能量
        if hasattr(self, 'energy'):
            self.energy = 50  # 初始能量
        else:
            self.energy = 50
        
        # 预设脉冲光束状态
        self.pulsar_beam_active = False
        self.stasis_wards = []
    
    def _enhance_vlm_interface(self):
        """增强VLM接口"""
        # 动态获取战术信息
        general_tactics = self.tactical_info.get('General', '') if hasattr(self, 'tactical_info') else ''
        
        # 初始化llm_interface（如果不存在）
        if not hasattr(self, 'llm_interface'):
            self.llm_interface = {}
        
        self.llm_interface.update({
            "natural_language_aliases": ["先知", "oracle", "侦查机", "战术单位"],
            "role_description": "神族侦查骚扰单位，具备多种战术能力",
            "tactical_keywords": ["侦查", "骚扰", "视野控制", "能量管理", "静止陷阱", "脉冲光束"],
            "primary_role": ["侦查", "骚扰", "视野控制"],
            "common_tactics": ["侦查敌军", "骚扰农民", "配合主力部队", "放置静止陷阱"],
            "special_abilities": ["启示（Revelation）", "脉冲光束（Pulsar Beam）", "静止陷阱（Stasis Ward）"],
            "visual_recognition_features": ["金黄色飞行单位", "几何翅膀结构", "独特的光束攻击效果", "隐形陷阱部署"],
            "competitive_insights": general_tactics
        })
        
        # 预置函数候选
        self.prefab_function_candidates = [
            {
                "function_name": "oracle_worker_harassment",
                "description": "使用先知骚扰敌方农民",
                "parameters": {
                    "target_base_location": "目标基地位置",
                    "retreat_threshold": "撤退阈值（能量百分比）"
                },
                "execution_flow": [
                    "approach_base(target_base_location)",
                    "activate_pulsar_beam()",
                    "attack_workers()",
                    "check_energy_level(retreat_threshold)",
                    "retreat_if_necessary()"
                ]
            },
            {
                "function_name": "oracle_revelation_scout",
                "description": "使用启示技能进行侦查",
                "parameters": {
                    "target_areas": "目标侦查区域列表"
                },
                "execution_flow": [
                    "move_to_waypoint(target_areas[0])",
                    "cast_revelation(target_areas[0])",
                    "observe_enemy_units()",
                    "report_findings()"
                ]
            },
            {
                "function_name": "oracle_stasis_trap",
                "description": "部署静止陷阱拦截敌军",
                "parameters": {
                    "trap_location": "陷阱部署位置",
                    "retreat_distance": "撤退距离"
                },
                "execution_flow": [
                    "approach_trap_location(trap_location)",
                    "deploy_stasis_ward(trap_location)",
                    "retreat_safely(retreat_distance)",
                    "monitor_trap_activation()"
                ]
            }
        ]
    
    def cast_revelation(self, target_position: Position) -> Dict[str, Any]:
        """施放启示技能提供视野和探测能力"""
        # 检查能量是否足够
        energy_cost = self.abilities.get('revelation', {}).get('energy_cost', 50)
        if self.energy < energy_cost:
            return {
                "success": False,
                "message": f"能量不足，需要 {energy_cost} 能量，当前 {self.energy}",
                "action": "cast_revelation",
                "energy_required": energy_cost,
                "current_energy": self.energy
            }
        
        # 消耗能量
        self.energy -= energy_cost
        duration = self.abilities.get('revelation', {}).get('duration', 30)
        detection_range = self.abilities.get('revelation', {}).get('detection_range', 10)
        
        print(f"{self.unique_class_name} 在位置 {target_position} 施放启示，持续 {duration} 秒，探测范围 {detection_range}")
        
        return {
            "success": True,
            "message": "启示技能施放成功",
            "action": "cast_revelation",
            "target_position": target_position,
            "duration": duration,
            "detection_range": detection_range,
            "remaining_energy": self.energy
        }
    
    def activate_pulsar_beam(self) -> Dict[str, Any]:
        """激活脉冲光束攻击地面单位"""
        # 检查脉冲光束是否已经激活
        if self.pulsar_beam_active:
            return {
                "success": False,
                "message": "脉冲光束已经激活",
                "action": "activate_pulsar_beam",
                "current_state": "active"
            }
        
        # 检查能量是否足够
        energy_cost = self.abilities.get('pulsar_beam', {}).get('energy_cost', 25)
        if self.energy < energy_cost:
            return {
                "success": False,
                "message": f"能量不足，需要 {energy_cost} 能量，当前 {self.energy}",
                "action": "activate_pulsar_beam",
                "energy_required": energy_cost,
                "current_energy": self.energy
            }
        
        # 消耗初始能量并激活光束
        self.energy -= energy_cost
        self.pulsar_beam_active = True
        energy_per_second = self.abilities.get('pulsar_beam', {}).get('energy_per_second', 3)
        
        print(f"{self.unique_class_name} 激活脉冲光束，每秒消耗 {energy_per_second} 能量")
        
        return {
            "success": True,
            "message": "脉冲光束激活成功",
            "action": "activate_pulsar_beam",
            "energy_cost": energy_cost,
            "energy_per_second": energy_per_second,
            "remaining_energy": self.energy
        }
    
    def deactivate_pulsar_beam(self) -> Dict[str, Any]:
        """关闭脉冲光束"""
        if not self.pulsar_beam_active:
            return {
                "success": False,
                "message": "脉冲光束未激活",
                "action": "deactivate_pulsar_beam",
                "current_state": "inactive"
            }
        
        self.pulsar_beam_active = False
        print(f"{self.unique_class_name} 关闭脉冲光束")
        
        return {
            "success": True,
            "message": "脉冲光束关闭成功",
            "action": "deactivate_pulsar_beam",
            "current_state": "inactive"
        }
    
    def deploy_stasis_ward(self, target_position: Position) -> Dict[str, Any]:
        """部署静止陷阱"""
        # 检查能量是否足够
        energy_cost = self.abilities.get('stasis_ward', {}).get('energy_cost', 75)
        if self.energy < energy_cost:
            return {
                "success": False,
                "message": f"能量不足，需要 {energy_cost} 能量，当前 {self.energy}",
                "action": "deploy_stasis_ward",
                "energy_required": energy_cost,
                "current_energy": self.energy
            }
        
        # 消耗能量并部署陷阱
        self.energy -= energy_cost
        duration = self.abilities.get('stasis_ward', {}).get('duration', 30)
        activation_delay = self.abilities.get('stasis_ward', {}).get('activation_delay', 3.5)
        stasis_duration = self.abilities.get('stasis_ward', {}).get('stasis_duration', 12)
        
        # 记录陷阱信息
        ward_info = {
            "position": target_position,
            "deploy_time": 0,  # 这里应该记录实际的游戏时间
            "activation_delay": activation_delay,
            "duration": duration,
            "stasis_duration": stasis_duration
        }
        self.stasis_wards.append(ward_info)
        
        print(f"{self.unique_class_name} 在位置 {target_position} 部署静止陷阱，{activation_delay}秒后激活，持续 {duration} 秒，停滞效果持续 {stasis_duration} 秒")
        
        return {
            "success": True,
            "message": "静止陷阱部署成功",
            "action": "deploy_stasis_ward",
            "target_position": target_position,
            "activation_delay": activation_delay,
            "duration": duration,
            "stasis_duration": stasis_duration,
            "remaining_energy": self.energy,
            "ward_id": len(self.stasis_wards) - 1  # 陷阱ID
        }
    
    def regen_energy(self, amount: float = 1.0) -> Dict[str, Any]:
        """能量恢复（模拟游戏中的能量恢复机制）"""
        max_energy = 100  # 假设最大能量为100
        old_energy = self.energy
        self.energy = min(max_energy, self.energy + amount)
        
        return {
            "success": True,
            "message": f"能量恢复了 {self.energy - old_energy} 点",
            "action": "regen_energy",
            "energy_before": old_energy,
            "energy_after": self.energy,
            "energy_regenerated": self.energy - old_energy
        }
    
    def harass_workers(self, target_base: Position) -> Dict[str, Any]:
        """骚扰敌方农民的战术"""
        # 检查能量是否足够激活脉冲光束
        beam_cost = self.abilities.get('pulsar_beam', {}).get('energy_cost', 25)
        if self.energy < beam_cost:
            return {
                "success": False,
                "message": f"能量不足，无法激活脉冲光束",
                "action": "harass_workers",
                "required_energy": beam_cost,
                "current_energy": self.energy
            }
        
        # 激活脉冲光束并攻击农民
        activate_result = self.activate_pulsar_beam()
        if not activate_result["success"]:
            return activate_result
        
        print(f"{self.unique_class_name} 开始在 {target_base} 骚扰农民")
        
        return {
            "success": True,
            "message": "骚扰农民战术执行成功",
            "action": "harass_workers",
            "target_base": target_base,
            "strategy": "脉冲光束攻击",
            "remaining_energy": self.energy
        }
    
    def scout_enemy_base(self, target_base: Position) -> Dict[str, Any]:
        """侦查敌方基地"""
        # 使用启示技能进行侦查
        revelation_result = self.cast_revelation(target_base)
        if not revelation_result["success"]:
            # 如果启示技能失败，至少提供基础侦查信息
            print(f"{self.unique_class_name} 在 {target_base} 进行基础侦查")
            return {
                "success": True,
                "message": "基础侦查执行成功，但无法使用启示技能",
                "action": "scout_enemy_base",
                "target_base": target_base,
                "scout_type": "basic"
            }
        
        print(f"{self.unique_class_name} 在 {target_base} 使用启示技能进行深度侦查")
        
        return {
            "success": True,
            "message": "启示侦查执行成功",
            "action": "scout_enemy_base",
            "target_base": target_base,
            "scout_type": "advanced",
            "detection_active": True,
            **revelation_result
        }