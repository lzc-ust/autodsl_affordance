from typing import Dict
from .unit import Position
from .race_units import ProtossUnit, TerranUnit, ZergUnit

class GroundUnit:
    """地面单位混入类 - 第二层子树"""
    
    def __init__(self):
        # 地面移动属性
        self.movement_type: str = "Ground"
        self.can_traverse_cliffs: bool = False
        self.pathing_size: str = "Medium"  # Small, Medium, Large
        
        # 地形影响
        self.terrain_speed_multipliers: Dict[str, float] = {
            "normal": 1.0,
            "creep": 1.3,
            "ramp": 0.75, 
            "rough": 0.5
        }
        
        # VLM优化
        if hasattr(self, 'visual_recognition'):
            self.visual_recognition.update({
                "movement_pattern": "地面移动",
                "terrain_interaction": "受地形影响"
            })
    
    def traverse_terrain(self, terrain_type: str) -> float:
        """地面单位地形移动"""
        multiplier = self.terrain_speed_multipliers.get(terrain_type, 1.0)
        print(f"{getattr(self, 'unique_class_name', 'GroundUnit')} 在{terrain_type}地形移动，速度系数: {multiplier}")
        return multiplier
    
    def use_ramp(self, ramp_position: Position) -> bool:
        """使用斜坡"""
        print(f"{getattr(self, 'unique_class_name', 'GroundUnit')} 正在使用斜坡")
        return True

class AirUnit:
    """空中单位混入类 - 第二层子树"""
    
    def __init__(self):
        # 空中移动属性
        self.movement_type: str = "Air"
        self.altitude: str = "Medium"  # Low, Medium, High
        self.can_hover: bool = False
        
        # 地形影响（空中单位通常不受影响）
        self.terrain_speed_multipliers: Dict[str, float] = {
            "normal": 1.0,
            "creep": 1.0,
            "ramp": 1.0,
            "rough": 1.0
        }
        
        # VLM优化
        if hasattr(self, 'visual_recognition'):
            self.visual_recognition.update({
                "movement_pattern": "空中飞行", 
                "terrain_interaction": "不受地形影响"
            })
    
    def change_altitude(self, new_altitude: str) -> bool:
        """改变飞行高度"""
        if self.can_hover:
            self.altitude = new_altitude
            print(f"{getattr(self, 'unique_class_name', 'AirUnit')} 改变高度到 {new_altitude}")
            return True
        return False
    
    def fly_over_terrain(self, terrain_type: str) -> float:
        """空中单位飞越地形"""
        multiplier = self.terrain_speed_multipliers.get(terrain_type, 1.0)
        print(f"{getattr(self, 'unique_class_name', 'AirUnit')} 飞越{terrain_type}地形，速度系数: {multiplier}")
        return multiplier

# 种族特化的移动类型基类
class ProtossGroundUnit(ProtossUnit, GroundUnit):
    """神族地面单位基类"""
    
    def __init__(self, development_mode: bool = False, **kwargs):
        ProtossUnit.__init__(self, development_mode=development_mode, **kwargs)
        GroundUnit.__init__(self)
        self.unit_type = "Protoss Ground Unit"
        
        # 神族地面单位特有属性
        self.warp_in_time = 5.0

class TerranGroundUnit(TerranUnit, GroundUnit):
    """人族地面单位基类"""
    
    def __init__(self, development_mode: bool = False, **kwargs):
        TerranUnit.__init__(self, development_mode=development_mode, **kwargs)
        GroundUnit.__init__(self)
        self.unit_type = "Terran Ground Unit"
        
        # 人族地面单位特有属性
        self.can_be_repaired = True

class ZergGroundUnit(ZergUnit, GroundUnit):
    """虫族地面单位基类"""
    
    def __init__(self, development_mode: bool = False, **kwargs):
        ZergUnit.__init__(self, development_mode=development_mode, **kwargs)
        GroundUnit.__init__(self)
        self.unit_type = "Zerg Ground Unit"
        
        # 虫族地面单位特有属性
        self.regeneration_rate = 0.273
        self.speed_on_creep = 1.3

class ProtossAirUnit(ProtossUnit, AirUnit):
    """神族空中单位基类"""
    
    def __init__(self, development_mode: bool = False, **kwargs):
        ProtossUnit.__init__(self, development_mode=development_mode, **kwargs)
        AirUnit.__init__(self)
        self.unit_type = "Protoss Air Unit"

class TerranAirUnit(TerranUnit, AirUnit):
    """人族空中单位基类"""
    
    def __init__(self, development_mode: bool = False, **kwargs):
        TerranUnit.__init__(self, development_mode=development_mode, **kwargs)
        AirUnit.__init__(self)
        self.unit_type = "Terran Air Unit"

# 注意：虫族主要单位都是地面单位，暂不定义ZergAirUnit