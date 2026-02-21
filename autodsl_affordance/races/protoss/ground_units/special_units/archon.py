from autodsl_affordance.races.protoss import ProtossSpecialUnit
from autodsl_affordance.core.base_units.unit import Cost, Position

class ProtossArchon(ProtossSpecialUnit):
    """执政官 - 神族灵能融合单位"""
    
    def __init__(self):
        super().__init__()
        self.unique_class_name = "Protoss_Archon"
        self.description = "神族灵能融合单位，由两个圣堂武士融合而成，具备强大范围攻击"
        
        # 游戏属性
        self.cost = Cost(mineral=0, vespene=0, supply=4, time=9)  # 融合时间
        self.attack = {
            "targets": ["Ground", "Air"],
            "damage": 25, "damage_upgrade": 2,
            "dps": {"base": 20.8, "vs_biological": 41.6},
            "cooldown": 1.2,
            "bonus_damage": {"value": 10, "upgrade": 1, "vs": "Biological"},
            "range": 3,
            "splash": {"radius": 1, "falloff": 0.5}
        }
        self.unit_stats = {
            "health": 10, "shield": 350, "armor": 0, "armor_upgrade": 1,
            "attributes": ["Massive", "Psionic"],
            "sight": 9, "speed": 3.15, "cargo_size": 4
        }
        
        # 能力配置
        self.abilities = {
            "fusion": {"required_units": 2, "unit_types": ["HighTemplar", "DarkTemplar"]},
            "feedback": {"damage_multiplier": 1, "range": 9}
        }
        
        # VLM优化
        self._enhance_vlm_interface()
    
    def _enhance_vlm_interface(self):
        """增强VLM接口"""
        self.llm_interface.update({
            "natural_language_aliases": ["执政官", "archon", "白球", "灵能融合体"],
            "role_description": "神族灵能融合单位，由两个圣堂武士融合而成，具备强大范围攻击",
            "tactical_keywords": ["范围伤害", "反生物", "对空对地", "灵能爆发"],
            "primary_role": ["反生物", "范围输出", "紧急应对"],
            "common_tactics": ["清理生物单位", "对空防御", "残血圣堂武士融合"]
        })
    
    def fuse_templars(self, high_templar, dark_templar) -> bool:
        """融合圣堂武士"""
        print(f"{self.unique_class_name} 融合圣堂武士形成执政官")
        return True
    
    def feedback(self, target) -> bool:
        """反馈技能 - 对灵能单位造成伤害"""
        print(f"{self.unique_class_name} 对目标使用反馈")
        return True