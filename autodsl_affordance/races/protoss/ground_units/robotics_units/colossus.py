from autodsl_affordance.races.protoss import ProtossRoboticsUnit
from autodsl_affordance.core.base_units.unit import Cost, Position
from autodsl_affordance.utils.json_loader import UnitJsonLoader
from typing import Dict, Any, List, Optional

class ProtossColossus(ProtossRoboticsUnit):
    """巨像 - 神族巨型步行机甲，具备强大的范围地面攻击和独特的跨越地形能力，是对集群轻甲单位的致命武器。"""
    
    def __init__(self, development_mode: bool = False):
        super().__init__()
        self.unique_class_name = "Protoss_Colossus"
        self.development_mode = development_mode
        
        # 核心属性初始化
        self.description = ""
        self.cost = None
        self.attack = {}
        self.unit_stats = {}
        self.abilities = {}  # type: Dict[str, Dict[str, Any]]
        self.tactical_info = {}
        self.upgrades = {}
        
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
                    mineral=cost_data.get("mineral", 300),
                    vespene=cost_data.get("vespene", 200),
                    supply=cost_data.get("supply", 6),
                    time=cost_data.get("game_time", 54)
                )
                
                # 处理攻击数据
                if 'Attack' in data:
                    attack_data = data['Attack']
                    self.attack = {
                        "targets": ["Ground"],
                        "damage": 10,  # 每束
                        "damage_upgrade": 1,
                        "dps": {"base": 21.4, "vs_light": 30.7},
                        "cooldown": 0.93,
                        "bonus_damage": {"value": 5, "upgrade": 1, "vs": "Light"},
                        "range": 7,
                        "upgrade_range": 9,
                        "splash": {"radius": 1.5, "falloff": 0.5},
                        "damage_type": "dual_thermal_lances"
                    }
                
                # 处理单位统计
                if 'Unit stats' in data:
                    stats_data = data['Unit stats']
                    defense_parts = stats_data.get('Defense', '200 150 1 (+1)').split()
                    self.unit_stats = {
                        "health": int(defense_parts[0]),
                        "shield": int(defense_parts[1]),
                        "armor": int(defense_parts[2].split('(')[0]),
                        "armor_upgrade": 1,
                        "attributes": ["Armored", "Massive", "Mechanical"],
                        "sight": 10,
                        "speed": 3.15,
                        "cargo_size": 8
                    }
                
                # 处理能力数据
                if 'Ability' in data:
                    ability_data = data['Ability']
                    self.abilities = {
                        "cliff_walk": {
                            "enabled": True,
                            "description": ability_data.get('Description', ''),
                            "hotkey": "",
                            "passive": True
                        }
                    }
                
                # 处理升级数据
                if 'Upgrade' in data:
                    upgrade_data = data['Upgrade']
                    self.upgrades = {
                        "extended_thermal_lance": {
                            "mineral_cost": upgrade_data.get("Mineral Cost", 150),
                            "vespene_cost": upgrade_data.get("Vespene Cost", 150),
                            "research_time": upgrade_data.get("Research Time", 100),
                            "researched_from": upgrade_data.get("Researched From", "Robotics Bay"),
                            "effect": upgrade_data.get("Effect", "Increases attack range from 7 to 9"),
                            "researched": False
                        }
                    }
                
                # 处理克制关系
                self.strong_against = data.get('Strong against', [])
                self.weak_against = data.get('Weak against', [])
                
                # 处理战术信息
                if 'Competitive Usage' in data:
                    self.tactical_info = data.get('Competitive Usage', {})
                    # 添加协同单位信息
                    self.tactical_info['synergies'] = ["Stalker", "Void Ray", "Observer"]
        except Exception as e:
            if self.development_mode:
                raise e
            print(f"警告: 无法加载{self.unique_class_name}的数据: {e}")
    
    def _set_default_values(self):
        """设置默认值，确保属性完整性"""
        if not self.description:
            if self.development_mode:
                raise ValueError("单位描述不能为空")
            self.description = "神族巨型步行机甲，具备范围地面攻击和跨越地形能力"
        
        if not self.cost:
            self.cost = Cost(mineral=300, vespene=200, supply=6, time=54)
        
        if not self.attack:
            self.attack = {
                "targets": ["Ground"],
                "damage": 10, "damage_upgrade": 1,
                "dps": {"base": 21.4, "vs_light": 30.7},
                "cooldown": 0.93,
                "bonus_damage": {"value": 5, "upgrade": 1, "vs": "Light"},
                "range": 7,
                "splash": {"radius": 1.5, "falloff": 0.5}
            }
        
        if not self.unit_stats:
            self.unit_stats = {
                "health": 200, "shield": 150, "armor": 1, "armor_upgrade": 1,
                "attributes": ["Armored", "Massive", "Mechanical"],
                "sight": 10, "speed": 3.15, "cargo_size": 8
            }
        
        if not self.abilities:
            self.abilities = {
                "cliff_walk": {"enabled": True}
            }
        
        if not self.upgrades:
            self.upgrades = {
                "extended_thermal_lance": {
                    "mineral_cost": 150,
                    "vespene_cost": 150,
                    "research_time": 100,
                    "effect": "Increases attack range from 7 to 9",
                    "researched": False
                }
            }
        
        if not self.tactical_info:
            self.tactical_info = {
                "strong_against": ["Marine", "Zergling", "Zealot", "Adept", "Hydralisk"],
                "weak_against": ["Viking", "Corruptor", "Tempest", "Marauder", "Immortal"],
                "synergies": ["Stalker", "Void Ray", "Observer"]
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
            "natural_language_aliases": ["巨像", "colossus", "巨型机甲", "步行机甲", "热能射线"],
            "role_description": self.description,
            "tactical_keywords": ["范围伤害", "反轻甲", "地形跨越", "后排输出", "线性伤害"],
            "primary_role": ["反轻甲", "范围输出", "地形控制", "火力支援"],
            "common_tactics": ["清理小单位集群", "高地压制", "配合前排", "线性区域清理"],
            "special_abilities": ["悬崖行走（Cliff Walk）"],
            "upgrades": ["热能射线升级（Extended Thermal Lance）"],
            "visual_recognition_features": ["四足机甲", "双光束武器", "高大体型", "蓝色光芒"],
            "competitive_insights": general_tactics
        })
        
        self.visual_recognition.update({
            "identifying_features": ["巨型机甲外观", "四足步行", "双光束武器", "高大体型"],
            "minimap_characteristics": "大型蓝色单位",
            "unique_visual_queues": ["光束横扫效果", "跨越悬崖动画"],
            "llm_vision_prompt": "识别画面中的巨像 - 高大的四足机甲，发射横扫光束"
        })
        
        self.tactical_context.update({
            "early_game": [],
            "mid_game": ["范围输出", "高地压制", "清理轻甲集群"],
            "late_game": ["持续火力支援", "地形控制", "配合主力部队"],
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
                "function_name": "colossus_thermal_lance_sweep",
                "description": "使用巨像的热能射线对集群单位进行清扫",
                "parameters": {
                    "target_cluster": "目标集群位置",
                    "priority_targets": "优先目标单位列表"
                },
                "execution_flow": [
                    "position_for_max_effect(target_cluster)",
                    "use_thermal_lance_attack(priority_targets, target_cluster)",
                    "advance_towards_enemy()",
                    "retreat_if_necessary()"
                ]
            },
            {
                "function_name": "colossus_high_ground_siege",
                "description": "利用巨像的悬崖行走能力占据高地进行压制",
                "parameters": {
                    "high_ground_location": "高地位置",
                    "enemy_positions": "敌方单位位置列表"
                },
                "execution_flow": [
                    "climb_cliffs(high_ground_location)",
                    "establish_firing_position()",
                    "use_thermal_lance_attack(identified_enemies, high_ground_location)",
                    "maintain_high_ground_advantage()"
                ]
            },
            {
                "function_name": "colossus_upgrade_thermal_lance",
                "description": "研究热能射线升级以增加巨像攻击范围",
                "parameters": {
                    "research_facility": "研究设施位置"
                },
                "execution_flow": [
                    "research_extended_thermal_lance()",
                    "verify_upgrade_completion()",
                    "adjust_positioning_for_longer_range()"
                ]
            },
            {
                "function_name": "colossus_with_stalker_support",
                "description": "巨像配合追猎者的标准战术组合",
                "parameters": {
                    "enemy_composition": "敌方单位组成",
                    "engagement_position": "交战位置"
                },
                "execution_flow": [
                    "form_stalker_screen()",
                    "position_colossus_behind_screen()",
                    "use_thermal_lance_attack(enemy_infantry, engagement_position)",
                    "retreat_with_stalker_protection()"
                ]
            }
        ]
    
    def climb_cliffs(self, target_position: Position) -> Dict[str, Any]:
        """跨越悬崖到目标位置"""
        result = {
            "success": False,
            "action": "climb_cliffs",
            "current_position": None,
            "target_position": target_position,
            "reached": False,
            "reason": None
        }
        
        # 检查悬崖行走能力是否启用
        if not self.abilities.get("cliff_walk", {}).get("enabled", False):
            result["reason"] = "悬崖行走能力未启用"
            return result
        
        current_position = getattr(self, "position", Position(0, 0))
        result["current_position"] = current_position
        
        # 模拟跨越悬崖
        print(f"{self.unique_class_name} 跨越地形从 {current_position} 到 {target_position}")
        self.position = target_position
        
        result["success"] = True
        result["reached"] = True
        
        return result
    
    def position_for_max_effect(self, target_area: Position) -> Dict[str, Any]:
        """为最大范围效果进行定位"""
        result = {
            "success": True,
            "action": "position_for_max_effect",
            "target_area": target_area,
            "optimal_position": None,
            "tactical_advantage": "线性伤害最大化"
        }
        
        # 计算最佳位置（略微调整目标区域位置以获得最佳线性伤害角度）
        optimal_x = target_area.x + 1  # 略微调整位置以获得更好的角度
        optimal_y = target_area.y + 1
        optimal_pos = Position(optimal_x, optimal_y)
        
        print(f"{self.unique_class_name} 移动到最佳位置 {optimal_pos} 以最大化热能射线效果")
        self.position = optimal_pos
        
        result["optimal_position"] = optimal_pos
        
        return result
    
    def establish_firing_position(self) -> Dict[str, Any]:
        """建立最佳射击位置"""
        result = {
            "success": True,
            "action": "establish_firing_position",
            "current_position": getattr(self, "position", Position(0, 0)),
            "firing_range": self.attack.get("range", 7),
            "has_high_ground_bonus": True
        }
        
        print(f"{self.unique_class_name} 在 {result['current_position']} 建立射击位置")
        
        return result
    
    def use_thermal_lance_attack(self, targets: List[str], target_area: Position) -> Dict[str, Any]:
        """使用热能射线进行范围攻击"""
        result = {
            "success": True,
            "action": "use_thermal_lance_attack",
            "target_area": target_area,
            "targets_hit": [],
            "damage_dealt": {},
            "damage_type": "splash",
            "has_upgrade": False,
            "range_used": 7
        }
        
        # 获取攻击属性
        attack_range = self.attack.get("range", 7)
        base_damage = 10  # 每束
        vs_light_bonus = 5
        
        # 检查是否有升级
        if self.upgrades.get("extended_thermal_lance", {}).get("researched", False):
            attack_range = 9
            result["has_upgrade"] = True
            result["range_used"] = 9
        
        # 计算伤害
        for target in targets:
            damage = base_damage * 2  # 双光束
            
            # 检查是否为轻甲单位
            is_light = any(unit.lower() in target.lower() for unit in ["marine", "zergling", "zealot", "adept", "hydralisk"])
            damage_details = {}
            
            if is_light:
                bonus_damage = vs_light_bonus * 2
                damage += bonus_damage
                damage_details["base"] = base_damage * 2
                damage_details["bonus"] = bonus_damage
                damage_details["reason"] = "对轻甲单位的额外伤害"
            else:
                damage_details["base"] = damage
                damage_details["bonus"] = 0
            
            result["targets_hit"].append(target)
            result["damage_dealt"][target] = damage_details
        
        print(f"{self.unique_class_name} 在 {target_area} 对 {len(targets)} 个目标使用热能射线攻击，射程: {attack_range}")
        
        # 统计总伤害
        total_damage = sum(sum(dmg.values()) for dmg in result["damage_dealt"].values())
        result["total_damage_dealt"] = total_damage
        
        return result
    
    def high_ground_positioning(self, high_ground_position: Position) -> Dict[str, Any]:
        """利用高地形优势进行定位"""
        result = {
            "success": False,
            "action": "high_ground_positioning",
            "high_ground_position": high_ground_position,
            "advantage_gained": False,
            "reason": None
        }
        
        # 先使用悬崖行走到达高地
        climb_result = self.climb_cliffs(high_ground_position)
        
        if climb_result["success"]:
            print(f"{self.unique_class_name} 已成功到达高地位置并获得优势视野")
            
            # 建立射击位置
            firing_result = self.establish_firing_position()
            
            result["success"] = True
            result["advantage_gained"] = True
            result["firing_position"] = firing_result["current_position"]
            result["tactical_advantage"] = "高地视野和射程优势"
        else:
            result["reason"] = "无法到达高地位置"
            print(f"{self.unique_class_name} 无法到达高地位置: {climb_result.get('reason', '未知错误')}")
        
        return result
    
    def research_extended_thermal_lance(self) -> Dict[str, Any]:
        """研究热能射线升级"""
        result = {
            "success": False,
            "action": "research_extended_thermal_lance",
            "status": "not_researched",
            "cost": {},
            "message": None
        }
        
        upgrade = self.upgrades.get("extended_thermal_lance", {})
        
        # 检查是否已经研究过
        if upgrade.get("researched", False):
            result["status"] = "already_researched"
            result["message"] = "热能射线升级已完成"
            return result
        
        # 构建成本信息
        result["cost"] = {
            "mineral": upgrade.get("mineral_cost", 150),
            "vespene": upgrade.get("vespene_cost", 150),
            "time": upgrade.get("research_time", 100),
            "facility": upgrade.get("researched_from", "Robotics Bay")
        }
        
        print(f"开始研究热能射线升级 - 消耗: {result['cost']['mineral']} 矿, {result['cost']['vespene']} 气, 时间: {result['cost']['time']} 秒, 研究设施: {result['cost']['facility']}")
        
        # 模拟研究完成
        upgrade["researched"] = True
        
        # 更新攻击范围
        if hasattr(self, 'attack'):
            self.attack["range"] = 9
            self.attack["has_upgraded_range"] = True
        
        result["success"] = True
        result["status"] = "researched"
        result["message"] = "热能射线升级研究完成"
        result["upgrade_effect"] = "攻击范围从7增加到9"
        
        return result
    
    def form_stalker_screen(self) -> Dict[str, Any]:
        """形成追猎者保护屏障"""
        result = {
            "success": True,
            "action": "form_stalker_screen",
            "formation_type": "半圆形防护",
            "tactical_purpose": "保护巨像免受空中和远程单位攻击"
        }
        
        print(f"{self.unique_class_name} 正在形成追猎者保护屏障")
        
        return result
    
    def position_colossus_behind_screen(self) -> Dict[str, Any]:
        """将巨像定位在保护屏障后方"""
        result = {
            "success": True,
            "action": "position_colossus_behind_screen",
            "current_position": getattr(self, "position", Position(0, 0)),
            "tactical_advantage": "安全输出位置"
        }
        
        # 计算后方位置
        new_x = result["current_position"].x + 2
        new_y = result["current_position"].y
        new_position = Position(new_x, new_y)
        
        print(f"{self.unique_class_name} 移动到保护屏障后方位置: {new_position}")
        self.position = new_position
        
        result["new_position"] = new_position
        
        return result
    
    def _calculate_distance(self, pos1: Position, pos2: Position) -> float:
        """计算两点之间的距离"""
        return ((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2) ** 0.5
    
    # 预置函数候选已在_enhance_vlm_interface中定义