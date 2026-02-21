# races/zerg/__init__.py

from autodsl_affordance.core.base_units.race_units import ZergUnit
from autodsl_affordance.core.base_units.mobility_units import ZergGroundUnit

class ZergCombatUnit(ZergGroundUnit):
    """虫族战斗单位基类 - 第三层子树"""
    
    def __init__(self):
        super().__init__()
        self.production_building: str = "Hatchery"
        self.requires_spawning_pool: bool = False
        self.requires_evolution_chamber: bool = False
        self.can_burrow: bool = False
        self.can_tunnel: bool = False
        
        # VLM优化
        self.llm_interface.update({
            "production_keywords": ["虫族战斗单位", "孵化场单位"],
            "tactical_role": ["基础作战", "虫海战术"]
        })
    
    def burrow_move(self) -> bool:
        """潜地移动"""
        if self.can_burrow:
            print(f"{self.unique_class_name} 潜地移动")
            return True
        return False
    
    def tunnel_attack(self) -> bool:
        """地道攻击"""
        if self.can_tunnel:
            print(f"{self.unique_class_name} 使用地道攻击")
            return True
        return False

class ZergSuicideUnit(ZergGroundUnit):
    """虫族自杀单位基类 - 第三层子树"""
    
    def __init__(self):
        super().__init__()
        self.production_building: str = "Baneling Nest"
        self.is_suicide_unit: bool = True
        self.explosion_damage: int = 0
        self.explosion_radius: float = 0
        
        # VLM优化
        self.llm_interface.update({
            "production_keywords": ["自杀单位", "爆炸单位"],
            "tactical_role": ["自杀攻击", "范围伤害"]
        })
    
    def suicide_attack(self, target_position) -> bool:
        """自杀攻击"""
        if self.is_suicide_unit:
            print(f"{self.unique_class_name} 进行自杀攻击")
            self.get_destroyed()
            return True
        return False