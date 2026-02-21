# races/terran/air_units/starport_units/banshee.py

from autodsl_affordance.races.terran import TerranStarportUnit
from autodsl_affordance.core.base_units.unit import Position

class TerranBanshee(TerranStarportUnit):
    """女妖 - 人族隐形对地攻击机"""
    
    def __init__(self, development_mode: bool = False, **kwargs):
        # 设置单位唯一标识
        self.unique_class_name = "Terran_Banshee"
        
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
        self.requires_tech_lab = True
        self.energy = 0
        self.energy_max = 0
    
    def _enhance_vlm_interface(self):
        """增强VLM接口"""
        self.llm_interface.update({
            "natural_language_aliases": ["女妖", "banshee", "隐形战机", "对地攻击机"],
            "role_description": self.description,
            "tactical_keywords": ["隐形", "骚扰", "对地攻击", "快速移动"],
            "primary_role": ["骚扰", "对地输出", "隐形打击"],
            "common_tactics": ["骚扰经济", "偷袭后排", "配合主力"]
        })
    
    def toggle_cloak(self) -> bool:
        """切换隐形状态"""
        print(f"{self.unique_class_name} 切换隐形状态")
        return True
    
    def harass_attack(self, target_position: Position) -> bool:
        """骚扰攻击"""
        print(f"{self.unique_class_name} 对位置 {target_position} 进行骚扰攻击")
        return True