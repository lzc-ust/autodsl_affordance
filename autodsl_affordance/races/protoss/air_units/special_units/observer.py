from autodsl_affordance.races.protoss import ProtossAirSpecialUnit
from autodsl_affordance.core.base_units.unit import Position

class ProtossObserver(ProtossAirSpecialUnit):
    """观察者 - 神族隐形侦察单位"""
    
    def __init__(self, development_mode: bool = False, **kwargs):
        # 设置单位唯一标识
        self.unique_class_name = "Protoss_Observer"
        
        # 调用父类初始化（不传递development_mode参数）
        super().__init__(**kwargs)
        
        # 初始化JSON加载器
        from autodsl_affordance.utils.json_loader import UnitJsonLoader
        self.json_loader = UnitJsonLoader(self, dev_mode=development_mode)
        
        # 重新加载单位数据
        self._load_unit_data()
    
    def _set_default_values(self):
        """设置所有属性的默认值"""
        super()._set_default_values()
        # 单位特有属性
        self.unit_stats["shield"] = 0  # 神族单位特有护盾
    
    def _enhance_vlm_interface(self):
        """增强VLM接口"""
        self.llm_interface.update({
            "natural_language_aliases": ["观察者", "observer", "OB", "侦察机", "眼虫克星"],
            "role_description": self.description,
            "tactical_keywords": ["侦查", "反隐", "视野控制", "隐形"],
            "primary_role": ["侦察", "反隐", "视野提供"],
            "common_tactics": ["地图控制", "侦查敌军", "保护重要单位"]
        })
    
    def detect_units(self) -> list:
        """检测隐形单位"""
        print(f"{self.unique_class_name} 检测隐形单位")
        return []
    
    def provide_vision(self, position: Position) -> bool:
        """提供视野"""
        print(f"{self.unique_class_name} 在位置 {position} 提供视野")
        return True