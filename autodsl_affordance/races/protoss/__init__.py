from autodsl_affordance.core.base_units.race_units import ProtossUnit
from autodsl_affordance.core.base_units.mobility_units import ProtossGroundUnit, ProtossAirUnit

class ProtossGatewayUnit(ProtossGroundUnit):
    """神族Gateway单位基类 - 第三层子树"""
    
    def __init__(self):
        super().__init__()
        self.production_building: str = "Gateway"
        self.requires_cybernetics_core: bool = False
        self.requires_templar_archives: bool = False
        
        # VLM优化
        self.llm_interface.update({
            "production_keywords": ["网关单位", "基础兵种"],
            "tactical_role": ["前线", "多功能"]
        })
    
    def warp_in_at_pylon(self, pylon: 'Unit') -> bool:
        """在能量场中折跃"""
        print(f"{self.unique_class_name} 在能量场中折跃")
        return True

class ProtossRoboticsUnit(ProtossGroundUnit):
    """神族Robotics单位基类 - 第三层子树"""
    
    def __init__(self):
        super().__init__()
        self.production_building: str = "Robotics Facility"
        self.requires_robotics_bay: bool = False
        self.assembly_time: float = 30.0
        
        # VLM优化
        self.llm_interface.update({
            "production_keywords": ["机械台单位", "重甲单位"],
            "tactical_role": ["重火力", "特殊功能"]
        })
    
    def be_assembled(self) -> bool:
        """机械单位组装"""
        print(f"{self.unique_class_name} 正在组装")
        return True

class ProtossStargateUnit(ProtossAirUnit):
    """神族Stargate单位基类 - 第三层子树"""
    
    def __init__(self):
        super().__init__()
        self.production_building: str = "Stargate"
        self.requires_fleet_beacon: bool = False
        
        # VLM优化
        self.llm_interface.update({
            "production_keywords": ["星门单位", "空中单位"],
            "tactical_role": ["空中优势", "特殊能力"]
        })
    
    def deploy_from_stargate(self, stargate: 'Unit') -> bool:
        """从星门部署"""
        print(f"{self.unique_class_name} 从星门部署")
        return True

class ProtossSpecialUnit(ProtossGroundUnit):
    """神族特殊单位基类 - 第三层子树"""
    
    def __init__(self):
        super().__init__()
        self.production_building: str = "Special"
        self.is_special_creation: bool = True
        
        # VLM优化
        self.llm_interface.update({
            "production_keywords": ["特殊单位", "融合单位"],
            "tactical_role": ["特殊功能", "紧急应对"]
        })
    
    def special_creation(self) -> bool:
        """特殊单位创建"""
        print(f"{self.unique_class_name} 通过特殊方式创建")
        return True

class ProtossAirSpecialUnit(ProtossAirUnit):
    """神族空中特殊单位基类 - 第三层子树"""
    
    def __init__(self):
        super().__init__()
        self.production_building: str = "Special"
        self.is_special_creation: bool = True
        
        # VLM优化
        self.llm_interface.update({
            "production_keywords": ["空中特殊单位", "侦察单位"],
            "tactical_role": ["侦察", "视野控制"]
        })
    
    def special_creation(self) -> bool:
        """特殊单位创建"""
        print(f"{self.unique_class_name} 通过特殊方式创建")
        return True