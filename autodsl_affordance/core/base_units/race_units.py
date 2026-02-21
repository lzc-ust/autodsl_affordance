from .standard_unit import StandardUnit
from .unit import Position, Cost

class ProtossUnit(StandardUnit):
    """神族单位基类 - 第一层子树"""
    
    def __init__(self, development_mode: bool = False, **kwargs):
        super().__init__(race="Protoss", development_mode=development_mode, **kwargs)
        self.unit_type: str = "Protoss Unit"
        
        # 神族特有属性
        self.shield: int = 0
        self.shield_max: int = 0
        self.shield_upgrade: int = 1
        self.attributes: List[str] = []
        
        # 神族机制
        self.warp_in_time: float = 0
        self.requires_pylon_power: bool = False
        
        # VLM优化
        self.llm_interface.update({
            "race_keywords": ["神族", "Protoss", "高科技", "护盾"],
            "visual_characteristics": ["能量护盾", "蓝色调", "几何外形"]
        })
    
    def regenerate_shields(self) -> bool:
        """神族护盾再生"""
        if self.is_alive and self.shield < self.shield_max:
            self.shield = min(self.shield + 1, self.shield_max)
            print(f"{self.unique_class_name} 护盾再生: {self.shield}/{self.shield_max}")
            return True
        return False
    
    def warp_in(self, warp_location: Position) -> bool:
        """神族折跃机制"""
        if self.requires_pylon_power:
            print(f"{self.unique_class_name} 需要在能量场中折跃")
            return False
        
        print(f"{self.unique_class_name} 正在折跃到 {warp_location}")
        self.position = warp_location
        self.shield = 0  # 刚折跃时护盾为空
        return True

class TerranUnit(StandardUnit):
    """人族单位基类 - 第一层子树"""
    
    def __init__(self, development_mode: bool = False, **kwargs):
        super().__init__(race="Terran", development_mode=development_mode, **kwargs)
        self.unit_type: str = "Terran Unit"
        
        # 人族特有属性
        self.attributes: List[str] = []
        self.can_be_repaired: bool = False
        self.construction_time: float = 0
        self.add_on_compatible: bool = False
        
        # VLM优化
        self.llm_interface.update({
            "race_keywords": ["人族", "Terran", "机械化", "工程"],
            "visual_characteristics": ["金属装甲", "工业设计", "实用主义"]
        })
    
    def be_repaired(self, scv_unit: 'Unit') -> bool:
        """人族维修机制"""
        if self.is_alive and self.can_be_repaired:
            print(f"{self.unique_class_name} 正在被SCV维修")
            return True
        return False
    
    def lift_off(self) -> bool:
        """人族建筑起飞"""
        if hasattr(self, 'is_building') and getattr(self, 'is_building', False):
            print(f"{self.unique_class_name} 正在起飞")
            return True
        return False

class ZergUnit(StandardUnit):
    """虫族单位基类 - 第一层子树"""
    
    def __init__(self, development_mode: bool = False, **kwargs):
        super().__init__(race="Zerg", development_mode=development_mode, **kwargs)
        self.unit_type: str = "Zerg Unit"
        
        # 虫族特有属性
        self.attributes: List[str] = []
        self.requires_creep: bool = False
        self.morphs_from: Optional[str] = None
        self.morphs_into: Optional[str] = None
        self.regeneration_rate: float = 0
        
        # VLM优化
        self.llm_interface.update({
            "race_keywords": ["虫族", "Zerg", "生物", "进化"],
            "visual_characteristics": ["有机体", "虫族组织", "生物质感"]
        })
    
    def regenerate_health(self) -> bool:
        """虫族生命再生"""
        if self.is_alive:
            print(f"{self.unique_class_name} 正在再生生命")
            return True
        return False
    
    def morph_into(self, target_unit_type: str) -> bool:
        """虫族变形机制"""
        if self.morphs_into and target_unit_type in self.morphs_into:
            print(f"{self.unique_class_name} 正在变形为 {target_unit_type}")
            return True
        return False