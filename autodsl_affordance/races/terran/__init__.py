# races/terran/__init__.py

from autodsl_affordance.core.base_units.race_units import TerranUnit
from autodsl_affordance.core.base_units.mobility_units import TerranGroundUnit, TerranAirUnit

class TerranInfantryUnit(TerranGroundUnit):
    """人族步兵单位基类 - 第三层子树"""
    
    def __init__(self):
        super().__init__()
        self.production_building: str = "Barracks"
        self.requires_tech_lab: bool = False
        self.requires_reactor: bool = False
        self.can_stimpack: bool = False
        self.can_use_combat_shields: bool = False
        
        # VLM优化
        self.llm_interface.update({
            "production_keywords": ["步兵单位", "兵营单位"],
            "tactical_role": ["基础作战", "多功能"]
        })
    
    def use_stimpack(self) -> bool:
        """使用兴奋剂"""
        if self.can_stimpack:
            print(f"{self.unique_class_name} 使用兴奋剂")
            return True
        return False
    
    def use_combat_shields(self) -> bool:
        """使用战斗护盾"""
        if self.can_use_combat_shields:
            print(f"{self.unique_class_name} 激活战斗护盾")
            return True
        return False

class TerranVehicleUnit(TerranGroundUnit):
    """人族车辆单位基类 - 第三层子树"""
    
    def __init__(self):
        super().__init__()
        self.production_building: str = "Factory"
        self.requires_tech_lab: bool = False
        self.requires_reactor: bool = False
        self.can_transform: bool = False
        self.can_siege_mode: bool = False
        
        # VLM优化
        self.llm_interface.update({
            "production_keywords": ["车辆单位", "重工厂单位"],
            "tactical_role": ["重火力", "机械化"]
        })
    
    def transform_mode(self) -> bool:
        """变形模式"""
        if self.can_transform:
            print(f"{self.unique_class_name} 切换模式")
            return True
        return False
    
    def repair_vehicle(self, scv_unit: 'Unit') -> bool:
        """维修车辆"""
        print(f"{self.unique_class_name} 正在被SCV维修")
        return True

class TerranStarportUnit(TerranAirUnit):
    """人族星港单位基类 - 第三层子树"""
    
    def __init__(self):
        super().__init__()
        self.production_building: str = "Starport"
        self.requires_tech_lab: bool = False
        self.requires_reactor: bool = False
        self.can_transform_air_ground: bool = False
        
        # VLM优化
        self.llm_interface.update({
            "production_keywords": ["星港单位", "空中单位"],
            "tactical_role": ["空中优势", "支援"]
        })
    
    def land_for_repair(self) -> bool:
        """降落维修"""
        print(f"{self.unique_class_name} 降落进行维修")
        return True

class TerranTransformUnit(TerranAirUnit):
    """人族变形单位基类 - 第三层子树"""
    
    def __init__(self):
        super().__init__()
        self.production_building: str = "Starport"
        self.can_transform_between_modes: bool = True
        self.current_mode: str = "Air"  # Air or Ground
        
        # VLM优化
        self.llm_interface.update({
            "production_keywords": ["变形单位", "多模式单位"],
            "tactical_role": ["多功能", "适应性强"]
        })
    
    def transform_to_air_mode(self) -> bool:
        """变形为空中模式"""
        if self.can_transform_between_modes:
            self.current_mode = "Air"
            print(f"{self.unique_class_name} 变形为空中模式")
            return True
        return False
    
    def transform_to_ground_mode(self) -> bool:
        """变形为地面模式"""
        if self.can_transform_between_modes:
            self.current_mode = "Ground"
            print(f"{self.unique_class_name} 变形为地面模式")
            return True
        return False