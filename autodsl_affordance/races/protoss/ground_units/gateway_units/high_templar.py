from autodsl_affordance.races.protoss import ProtossGatewayUnit
from autodsl_affordance.core.base_units.unit import Cost, Position
from autodsl_affordance.utils.json_loader import UnitJsonLoader
from typing import Dict, Any, List, Optional, TypeVar

# 前向声明
Unit = TypeVar('Unit')

class ProtossHighTemplar(ProtossGatewayUnit):
    """高阶圣堂武士 - 神族强大法术单位，擅长使用灵能风暴和反馈等高级灵能能力。"""
    
    def __init__(self, development_mode: bool = False):
        super().__init__()
        self.unique_class_name = "Protoss_HighTemplar"
        self.development_mode = development_mode
        
        # 核心属性初始化
        self.description = ""
        self.cost = None
        self.attack = {}
        self.unit_stats = {}
        self.abilities = {}  # type: Dict[str, Dict[str, Any]]
        self.tactical_info = {}
        
        # 状态属性
        self.current_energy = 50
        self.has_reserved = False
        
        # 加载单位数据
        self._load_data()
        # 设置默认值
        self._set_default_values()
        # VLM接口增强
        self._enhance_vlm_interface()
    
    def _load_data(self):
        """从JSON文件加载单位数据"""
        try:
            loader = UnitJsonLoader()
            data = loader.load_unit_data(self.unique_class_name)
            
            if data:
                self.description = data.get("Description", "") or data.get("description", "")
                
                # 处理成本数据
                cost_data = data.get("Cost", {})
                if cost_data:
                    self.cost = Cost(
                        mineral=cost_data.get("mineral", 0),
                        vespene=cost_data.get("vespene", 0),
                        supply=cost_data.get("supply", 0),
                        time=cost_data.get("game_time", 0)
                    )
                
                # 处理攻击数据
                attack_data = data.get("Attack", {})
                if attack_data:
                    self.attack = {
                        "damage": attack_data.get("Damage", 4), 
                        "damage_upgrade": attack_data.get("Damage Upgrade", 1), 
                        "range": attack_data.get("Range", 4),
                        "dps": attack_data.get("DPS", 2.8), 
                        "is_primary": False
                    }
                
                # 处理单位统计
                unit_stats_data = data.get("Unit stats", {})
                if unit_stats_data:
                    self.unit_stats = {
                        "health": 40, "shield": 40, "armor": 0, "armor_upgrade": 1,
                        "attributes": ["Biological", "Light", "Psionic"],
                        "sight": 10, "speed": 2.82, "cargo_size": 2,
                        "energy": {"max": 200, "start": 50, "regen_rate": 0.5625}
                    }
                
                # 处理能力数据
                ability_data = data.get("Ability", {})
                if ability_data:
                    self.abilities = {
                        "psionic_storm": {"energy_cost": 75, "researched": False, "damage": 80},
                        "feedback": {"energy_cost": 50, "damage_multiplier": 1.0}
                    }
                
                # 处理战术信息
                self.tactical_info = {
                    "strong_against": data.get("Strong against", []),
                    "weak_against": data.get("Weak against", []),
                    "synergies": ["Archon", "Sentry", "Warp Prism"]
                }
        except Exception as e:
            if self.development_mode:
                raise e
            print(f"警告: 无法加载{self.unique_class_name}的数据: {e}")
    
    def _set_default_values(self):
        """设置默认值，确保属性完整性"""
        if not self.description:
            if self.development_mode:
                raise ValueError("单位描述不能为空")
            self.description = "神族强大法术单位，具备灵能风暴和反馈能力"
        
        if not self.cost:
            self.cost = Cost(mineral=50, vespene=150, supply=2, time=39)
        
        if not self.attack:
            self.attack = {
                "damage": 4, "damage_upgrade": 1, "range": 4,
                "dps": 2.8, "is_primary": False
            }
        
        if not self.unit_stats:
            self.unit_stats = {
                "health": 40, "shield": 40, "armor": 0, "armor_upgrade": 1,
                "attributes": ["Biological", "Light", "Psionic"],
                "sight": 10, "speed": 2.82, "cargo_size": 2,
                "energy": {"max": 200, "start": 50, "regen_rate": 0.5625}
            }
        
        if not self.abilities:
            self.abilities = {
                "psionic_storm": {"energy_cost": 75, "researched": False, "damage": 80},
                "feedback": {"energy_cost": 50, "damage_multiplier": 1.0}
            }
        
        if not self.tactical_info:
            self.tactical_info = {
                "strong_against": ["Marine", "Marauder", "Hydralisk", "Roach", "Zealot", "Dark Templar"],
                "weak_against": ["Zergling", "Stalker", "Phoenix", "Medivac", "Baneling"],
                "synergies": ["Archon", "Sentry", "Warp Prism"]
            }
        
        # 更新当前能量值
        self.current_energy = self.unit_stats.get("energy", {}).get("start", 50)
    
    def _enhance_vlm_interface(self):
        """增强VLM接口，优化视觉和语言模型交互"""
        self.llm_interface.update({
            "natural_language_aliases": ["电兵", "HT", "高阶圣堂武士", "high templar", "圣堂"],
            "role_description": "高阶圣堂武士 - 神族强大法术单位，擅长使用灵能风暴和反馈等高级灵能能力",
            "tactical_keywords": ["灵能风暴", "反馈", "范围伤害", "反法术", "能量控制"],
            "primary_role": ["范围伤害", "反法术", "能量控制"],
            "common_tactics": ["风暴集群", "反馈关键单位", "合体执政官", "保护后排"]
        })
        
        self.visual_recognition.update({
            "identifying_features": ["长袍形态", "蓝色能量光环", "手持法杖", "灵能风暴特效"],
            "minimap_characteristics": "小型蓝色单位",
            "unique_visual_queues": ["风暴电闪特效", "反馈能量吸取特效"],
            "llm_vision_prompt": "识别画面中的高阶圣堂武士 - 长袍形态，拥有蓝色能量光环，可能正在施放灵能风暴或反馈"
        })
        
        self.tactical_context.update({
            "early_game": [],
            "mid_game": ["范围伤害", "反法术", "控制战场"],
            "late_game": ["主力输出", "能量压制", "合体执政官"],
            "counters": self.tactical_info.get("weak_against", []),
            "countered_by": self.tactical_info.get("strong_against", []),
            "synergies": [f"与{s}配合" for s in self.tactical_info.get("synergies", [])]
        })
    
    def cast_psionic_storm(self, target_area: Position) -> Dict[str, Any]:
        """施放灵能风暴"""
        result = {
            "success": False,
            "storm_cast": False,
            "energy_remaining": self.current_energy,
            "notes": []
        }
        
        storm = self.abilities.get("psionic_storm", {})
        energy_cost = storm.get("energy_cost", 75)
        
        # 检查是否已研发并拥有足够能量
        if storm.get("researched", True) and self.current_energy >= energy_cost:
            # 消耗能量
            self.current_energy -= energy_cost
            
            print(f"{self.unique_class_name} 在 {target_area} 施放灵能风暴")
            result["success"] = True
            result["storm_cast"] = True
            result["energy_remaining"] = self.current_energy
            result["notes"].append(f"灵能风暴已施放，造成{storm.get('damage', 80)}点伤害")
        else:
            if not storm.get("researched", True):
                result["notes"].append("灵能风暴尚未研发")
            else:
                result["notes"].append(f"能量不足，需要{energy_cost}点能量")
        
        return result
    
    def cast_feedback(self, target_unit: 'Unit') -> Dict[str, Any]:
        """施放反馈"""
        result = {
            "success": False,
            "feedback_applied": False,
            "damage_dealt": 0,
            "energy_remaining": self.current_energy,
            "notes": []
        }
        
        feedback = self.abilities.get("feedback", {})
        energy_cost = feedback.get("energy_cost", 50)
        multiplier = feedback.get("damage_multiplier", 1.0)
        
        # 检查是否拥有足够能量
        if self.current_energy >= energy_cost:
            # 假设target_unit有energy属性
            if hasattr(target_unit, 'current_energy'):
                damage = int(target_unit.current_energy * multiplier)
                
                # 消耗能量
                self.current_energy -= energy_cost
                
                print(f"{self.unique_class_name} 对 {target_unit.unique_class_name} 施放反馈，造成{damage}点伤害")
                result["success"] = True
                result["feedback_applied"] = True
                result["damage_dealt"] = damage
                result["energy_remaining"] = self.current_energy
                result["notes"].append(f"反馈已施放，造成{damage}点伤害")
            else:
                result["notes"].append("目标单位没有能量，无法施放反馈")
        else:
            result["notes"].append(f"能量不足，需要{energy_cost}点能量")
        
        return result
    
    def merge_to_archon(self, other_templar: 'ProtossHighTemplar') -> Dict[str, Any]:
        """合体为执政官"""
        result = {
            "success": False,
            "archon_merged": False,
            "notes": []
        }
        
        # 检查是否为两个高阶圣堂武士
        if isinstance(other_templar, ProtossHighTemplar):
            print(f"{self.unique_class_name} 与 {other_templar.unique_class_name} 合体为执政官")
            result["success"] = True
            result["archon_merged"] = True
            result["notes"].append("两个高阶圣堂武士成功合体为执政官")
        else:
            result["notes"].append("只能与另一个高阶圣堂武士合体")
        
        return result
    
    def reserve_energy(self, amount: int) -> bool:
        """预留能量用于特定技能"""
        max_energy = self.unit_stats.get("energy", {}).get("max", 200)
        if self.current_energy + amount <= max_energy:
            self.has_reserved = True
            print(f"{self.unique_class_name} 预留{amount}点能量")
            return True
        return False
    
    def regen_energy(self, time_passed: float) -> float:
        """能量恢复"""
        regen_rate = self.unit_stats.get("energy", {}).get("regen_rate", 0.5625)
        max_energy = self.unit_stats.get("energy", {}).get("max", 200)
        
        # 计算恢复的能量
        energy_gained = regen_rate * time_passed
        new_energy = min(self.current_energy + energy_gained, max_energy)
        
        self.current_energy = new_energy
        return self.current_energy
    
    def _calculate_distance(self, pos1: Position, pos2: Position) -> float:
        """计算两点之间的距离"""
        return ((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2) ** 0.5
    
    @property
    def prefab_function_candidates(self):
        """预置函数候选"""
        return [
            {
                "function_name": "灵能风暴施放",
                "trigger_condition": "发现敌方单位集群",
                "required_units": ["Protoss_HighTemplar"],
                "llm_trigger_words": ["风暴", "电兵", "灵能", "范围", "集群"],
                "execution_flow": ["cast_psionic_storm"]
            },
            {
                "function_name": "反馈能量吸取",
                "trigger_condition": "发现敌方能量单位",
                "required_units": ["Protoss_HighTemplar"],
                "llm_trigger_words": ["反馈", "能量", "吸取", "反隐", "反法师"],
                "execution_flow": ["cast_feedback"]
            },
            {
                "function_name": "执政官合体",
                "trigger_condition": "需要加强前排",
                "required_units": ["Protoss_HighTemplar", "Protoss_HighTemplar"],
                "llm_trigger_words": ["合体", "执政官", "archon", "前排", "坦克"],
                "execution_flow": ["merge_to_archon"]
            }
        ]