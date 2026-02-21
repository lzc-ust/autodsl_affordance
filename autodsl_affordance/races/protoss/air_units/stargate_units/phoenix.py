from autodsl_affordance.races.protoss import ProtossStargateUnit
from autodsl_affordance.core.base_units.unit import Cost, Position
from autodsl_affordance.utils.json_loader import UnitJsonLoader
from typing import Dict, Any, List, Optional

class ProtossPhoenix(ProtossStargateUnit):
    """凤凰 - 神族空对空战斗机，具备悬浮攻击和引力光束能力，适合空中优势和战术干扰。"""
    
    def __init__(self, development_mode: bool = False):
        super().__init__()
        self.unique_class_name = "Protoss_Phoenix"
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
            # 尝试直接加载JSON文件（备用方案）
            json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 
                                   'sc2_unit_info', f'{self.unique_class_name}.json')
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                self.description = data.get("Description", "")
                
                # 处理成本数据
                cost_data = data.get("Cost", {})
                self.cost = Cost(
                    mineral=cost_data.get("mineral", 150),
                    vespene=cost_data.get("vespene", 100),
                    supply=cost_data.get("supply", 2),
                    time=cost_data.get("game_time", 25)
                )
                
                # 处理攻击数据
                if 'Attack' in data:
                    attack_data = data['Attack']
                    self.attack = {
                        "targets": ["Air"],
                        "damage": 10,  # 5 × 2 beams
                        "damage_upgrade": 2,  # +1 × 2 beams
                        "dps": {"base": 15.4, "vs_light": 28.1},
                        "cooldown": 0.65,
                        "bonus_damage": {"value": 10, "upgrade": 2, "vs": "Light"},  # +5 × 2 beams
                        "range": 5,
                        "upgrade_range": 7
                    }
                
                # 处理单位统计
                if 'Unit stats' in data:
                    stats_data = data['Unit stats']
                    defense_parts = stats_data.get('Defense', '120 60 0 (+1)').split()
                    self.unit_stats = {
                        "health": int(defense_parts[0]),
                        "shield": int(defense_parts[1]),
                        "armor": int(defense_parts[2].split('(')[0]),
                        "armor_upgrade": 1,
                        "attributes": ["Light", "Mechanical"],
                        "sight": 10,
                        "speed": 5.95,
                        "cargo_size": 0
                    }
                
                # 处理能力数据
                if 'Ability' in data and isinstance(data['Ability'], dict):
                    ability_data = data['Ability']
                    self.abilities = {
                        "graviton_beam": {
                            "cooldown": 0,
                            "duration": 8,
                            "energy_cost": 50,
                            "targets": ["Ground"],
                            "range": 5,
                            "description": ability_data.get('Description', ''),
                            "hotkey": ability_data.get('Hotkey', 'G')
                        }
                    }
                
                # 处理升级数据
                if 'Upgrade' in data:
                    self.upgrades = {
                        "anion_pulse_crystals": data.get('Upgrade', {})
                    }
                
                # 处理克制关系
                self.strong_against = data.get('Strong against', [])
                self.weak_against = data.get('Weak against', [])
                
                # 处理战术信息
                if 'Competitive Usage' in data:
                    self.tactical_info = data.get('Competitive Usage', {})
                    # 添加协同单位信息
                    self.tactical_info['synergies'] = ["Void Ray", "Oracle"]
                
        except Exception as e:
            if self.development_mode:
                raise e
            print(f"警告: 无法加载{self.unique_class_name}的数据: {e}")
            # 出错时不中断，将在_set_default_values中设置默认值
    
    def _set_default_values(self):
        """设置默认值，确保属性完整性"""
        if not self.description:
            if self.development_mode:
                raise ValueError("单位描述不能为空")
            self.description = "神族空对空战斗机，具备悬浮攻击和引力光束能力"
        
        if not self.cost:
            self.cost = Cost(mineral=150, vespene=100, supply=2, time=25)
        
        if not self.attack:
            self.attack = {
                "targets": ["Air"],
                "damage": 5, "damage_upgrade": 1,
                "dps": {"base": 15.4, "vs_light": 28.1},  # 从JSON中更新正确的DPS
                "cooldown": 0.65,  # 从JSON中更新正确的冷却时间
                "bonus_damage": {"value": 5, "upgrade": 1, "vs": "Light"},
                "range": 5
            }
        
        if not self.unit_stats:
            self.unit_stats = {
                "health": 120, "shield": 60, "armor": 0, "armor_upgrade": 1,
                "attributes": ["Light", "Mechanical"],
                "sight": 10, "speed": 5.95, "cargo_size": 0
            }
        
        if not self.abilities:
            self.abilities = {
                "graviton_beam": {
                    "cooldown": 0,
                    "duration": 8,
                    "energy_cost": 50,
                    "targets": ["Ground"],
                    "range": 5
                }
            }
        
        if not self.tactical_info:
            self.tactical_info = {
                "strong_against": ["Mutalisk", "Banshee", "Medivac", "Void Ray", "Overlord", "Queen"],
                "weak_against": ["Corruptor", "Viking", "Hydralisk", "Marine", "Archon", "Tempest"],
                "synergies": ["Void Ray", "Oracle"]
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
            "natural_language_aliases": ["凤凰", "phoenix", "空对空战斗机", "引力光束"],
            "role_description": self.description,
            "tactical_keywords": ["制空权", "反轻甲", "单位控制", "悬浮攻击", "移动攻击"],
            "primary_role": ["空对空", "单位控制", "骚扰", "地图控制"],
            "common_tactics": ["对抗飞龙", "控制关键单位", "配合虚空辉光舰", "移动攻击战术"],
            "special_abilities": ["引力光束（Graviton Beam）"],
            "visual_recognition_features": ["菱形外观", "蓝色光芒", "双光束攻击效果", "引力光束悬浮效果"],
            "competitive_insights": general_tactics
        })
        
        self.visual_recognition.update({
            "identifying_features": ["菱形外观", "蓝色光芒", "飞行姿态"],
            "minimap_characteristics": "蓝色小点",
            "unique_visual_queues": ["双光束攻击", "引力光束效果"],
            "llm_vision_prompt": "识别画面中的凤凰战机 - 菱形飞行单位，发射蓝色光束"
        })
        
        self.tactical_context.update({
            "early_game": ["侦察", "对空防御"],
            "mid_game": ["空中压制", "单位控制", "骚扰农民"],
            "late_game": ["空中支援", "关键目标控制"],
            "counters": self.weak_against if hasattr(self, 'weak_against') else [],
            "countered_by": self.strong_against if hasattr(self, 'strong_against') else [],
            "synergies": [f"与{s}配合" for s in self.tactical_info.get("synergies", [])] if hasattr(self, 'tactical_info') else []
        })
        
        # 预置函数候选
        self.prefab_function_candidates = [
            {
                "function_name": "phoenix_air_superiority",
                "description": "使用凤凰执行制空权任务",
                "parameters": {
                    "enemy_air_targets": "敌方空中单位列表",
                    "engagement_range": "交战范围"
                },
                "execution_flow": [
                    "move_to_engagement_area()",
                    "attack_light_air(enemy_air_targets)",
                    "maintain_distance(engagement_range)",
                    "retreat_if_necessary()"
                ]
            },
            {
                "function_name": "phoenix_graviton_control",
                "description": "使用引力光束控制关键地面单位",
                "parameters": {
                    "priority_targets": "优先目标单位列表",
                    "target_positions": "目标位置列表"
                },
                "execution_flow": [
                    "identify_key_targets(priority_targets)",
                    "use_graviton_beam(targets[0], positions[0])",
                    "maintain_distance()",
                    "reposition_for_next_target()"
                ]
            },
            {
                "function_name": "phoenix_worker_harassment",
                "description": "使用凤凰骚扰敌方农民",
                "parameters": {
                    "target_base": "目标基地位置",
                    "retreat_threshold": "撤退阈值"
                },
                "execution_flow": [
                    "approach_base(target_base)",
                    "attack_workers()",
                    "move_while_attacking()",
                    "check_health(retreat_threshold)",
                    "retreat_safely()"
                ]
            },
            {
                "function_name": "phoenix_fleet_maneuver",
                "description": "凤凰舰队机动战术",
                "parameters": {
                    "formation": "舰队阵型",
                    "waypoints": "路径点列表"
                },
                "execution_flow": [
                    "form_up(formation)",
                    "move_to_waypoint(waypoints[0])",
                    "scout_area()",
                    "advance_to_next_waypoint(waypoints[1])",
                    "maintain_air_superiority()"
                ]
            }
        ]
    
    def use_graviton_beam(self, target_unit: str, target_position: Position) -> Dict[str, Any]:
        """使用引力光束抬起地面单位"""
        result = {
            "success": False,
            "action": "use_graviton_beam",
            "target_unit": target_unit,
            "target_position": target_position,
            "lifted": False,
            "duration": 0,
            "remaining_energy": 0,
            "reason": None
        }
        
        graviton_beam = self.abilities.get("graviton_beam", {})
        energy_cost = graviton_beam.get("energy_cost", 50)
        
        # 检查能量
        current_energy = getattr(self, "energy", 50)
        if current_energy < energy_cost:
            result["reason"] = f"能量不足，需要 {energy_cost} 能量，当前 {current_energy}"
            return result
        
        # 检查距离
        current_position = getattr(self, "position", Position(0, 0))
        distance = self._calculate_distance(current_position, target_position)
        range_limit = graviton_beam.get("range", 5)
        
        if distance > range_limit:
            result["reason"] = f"目标超出范围，当前距离 {distance:.2f}，最大范围 {range_limit}"
            return result
        
        # 检查是否为地面单位
        if not any(target.lower() in target_unit.lower() for target in ["tank", "immortal", "roach", "queen", "colossus"]):
            result["reason"] = f"{target_unit} 不是有效的地面目标"
            return result
        
        # 扣除能量
        self.energy = current_energy - energy_cost
        
        # 执行引力光束
        duration = graviton_beam.get("duration", 8)
        print(f"{self.unique_class_name} 对 {target_unit} 使用引力光束，持续 {duration} 秒")
        
        result["success"] = True
        result["lifted"] = True
        result["duration"] = duration
        result["remaining_energy"] = self.energy
        
        # 记录被抬起的单位
        if not hasattr(self, 'lifted_units'):
            self.lifted_units = []
        
        self.lifted_units.append({
            "unit": target_unit,
            "position": target_position,
            "lift_time": 0,  # 应该记录实际游戏时间
            "duration": duration
        })
        
        return result
    
    def research_anion_pulse_crystals(self) -> Dict[str, Any]:
        """研究阴离子脉冲水晶升级，增加凤凰的攻击范围"""
        result = {
            "success": False,
            "action": "research_anion_pulse_crystals",
            "status": "not_researched",
            "message": None
        }
        
        # 检查是否有升级信息
        upgrade_info = self.upgrades.get("anion_pulse_crystals", {}) if hasattr(self, 'upgrades') else {}
        
        # 设置默认升级信息（如果不存在）
        if not upgrade_info:
            upgrade_info = {
                "Mineral Cost": 150,
                "Vespene Cost": 150,
                "Research Time": 57
            }
        
        print(f"开始研究阴离子脉冲水晶升级 - 消耗: {upgrade_info.get('Mineral Cost', 150)} 矿, {upgrade_info.get('Vespene Cost', 150)} 气, 时间: {upgrade_info.get('Research Time', 57)} 秒")
        
        # 标记升级状态
        if not hasattr(self, 'upgrades_researched'):
            self.upgrades_researched = {}
        
        self.upgrades_researched["anion_pulse_crystals"] = {
            "researched": True,
            "effect": "攻击范围从5增加到7"
        }
        
        # 更新攻击范围
        if hasattr(self, 'attack'):
            self.attack["range"] = 7
            self.attack["has_upgraded_range"] = True
        
        result["success"] = True
        result["status"] = "researched"
        result["message"] = "阴离子脉冲水晶升级研究完成"
        result["upgrade_effect"] = "攻击范围从5增加到7"
        
        return result
    
    def attack_air_while_moving(self, targets: List[str], path: List[Position]) -> Dict[str, Any]:
        """执行移动攻击战术，边移动边攻击敌方空中单位"""
        result = {
            "success": True,
            "action": "attack_air_while_moving",
            "targets_attacked": [],
            "path_completed": False,
            "tactical_effect": "hit_and_run"
        }
        
        print(f"{self.unique_class_name} 开始执行移动攻击战术")
        
        # 模拟沿路径移动并攻击
        for i, waypoint in enumerate(path):
            print(f"  移动到路径点 {i+1}: {waypoint}")
            
            # 攻击附近的目标
            for target in targets:
                if "mutalisk" in target.lower() or "banshee" in target.lower() or "medivac" in target.lower():
                    print(f"  攻击目标: {target}")
                    result["targets_attacked"].append(target)
        
        result["path_completed"] = True
        print(f"移动攻击战术执行完成，攻击了 {len(result['targets_attacked'])} 个目标")
        
        return result
    
    def attack_light_air(self, air_targets: List[str]) -> Dict[str, Any]:
        """攻击轻甲空中单位"""
        result = {
            "success": True,
            "targets_attacked": [],
            "damage_per_target": 0,
            "notes": []
        }
        
        # 基础伤害
        base_damage = 5 * 2  # 双光束
        bonus_damage = 5 * 2  # 对轻甲额外伤害
        
        for target in air_targets:
            # 检查是否为轻甲空中单位
            if any(unit.lower() in target.lower() for unit in ["mutalisk", "banshee", "medivac", "phoenix", "overlord"]):
                result["targets_attacked"].append(target)
                result["notes"].append(f"对{target}造成额外伤害")
        
        result["damage_per_target"] = base_damage + bonus_damage
        return result
    
    def harassment_run(self, target_area: Position, target_type: str = "worker") -> bool:
        """执行骚扰任务"""
        current_position = getattr(self, "position", Position(0, 0))
        
        print(f"{self.unique_class_name} 执行骚扰任务，目标区域: {target_area}，目标类型: {target_type}")
        # 模拟移动到目标区域
        self.position = target_area
        
        return True
    
    def _calculate_distance(self, pos1: Position, pos2: Position) -> float:
        """计算两点之间的距离"""
        return ((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2) ** 0.5
    
    @property
    def prefab_function_candidates(self):
        """预置函数候选"""
        return [
            {
                "function_name": "凤凰引力光束控制",
                "trigger_condition": "敌方有关键地面单位",
                "required_units": ["Protoss_Phoenix"],
                "llm_trigger_words": ["控制", "抬起", "引力光束", "坦克", "不朽者"],
                "execution_flow": ["use_graviton_beam"]
            },
            {
                "function_name": "凤凰对空压制",
                "trigger_condition": "敌方有轻甲空中单位",
                "required_units": ["Protoss_Phoenix"],
                "llm_trigger_words": ["制空", "飞龙", "维京", "空中优势"],
                "execution_flow": ["attack_light_air"]
            }
        ]