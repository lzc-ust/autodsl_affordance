# races/terran/air_units/starport_units/medivac.py

from autodsl_affordance.races.terran import TerranStarportUnit
from autodsl_affordance.core.base_units.unit import Position

class TerranMedivac(TerranStarportUnit):
    """医疗艇 - 人族空中医疗运输单位"""
    
    def __init__(self, development_mode: bool = False, **kwargs):
        # 设置单位唯一标识
        self.unique_class_name = "Terran_Medivac"
        
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
        self.requires_tech_lab = False
        self.energy = 0
        self.energy_max = 0
        self.cargo_units = []
    
    def _enhance_vlm_interface(self):
        """增强VLM接口"""
        self.llm_interface.update({
            "natural_language_aliases": ["医疗艇", "medivac", "医疗船", "运输机"],
            "role_description": self.description,
            "tactical_keywords": ["治疗", "运输", "机动性", "支援"],
            "primary_role": ["医疗支援", "单位运输", "机动增援"],
            "common_tactics": ["治疗步兵", "空投战术", "快速撤退"]
        })
    
    def heal_unit(self, target_unit) -> bool:
        """治疗目标单位"""
        if hasattr(self, 'energy') and self.energy >= 1:
            print(f"{self.unique_class_name} 治疗目标单位")
            self.energy -= 1
            return True
        return False
    
    def use_boost(self) -> bool:
        """使用加速能力"""
        if hasattr(self, 'energy') and self.energy >= 50:
            print(f"{self.unique_class_name} 使用加速")
            self.energy -= 50
            return True
        return False
    
    def load_unit(self, unit) -> bool:
        """装载单位"""
        capacity = self.unit_stats.get("cargo_size", 0)
        if len(self.cargo_units) < capacity:
            self.cargo_units.append(unit)
            print(f"{self.unique_class_name} 装载单位 {unit.unique_class_name}")
            return True
        return False
    
    def unload_unit(self, unit) -> bool:
        """卸载单位"""
        if unit in self.cargo_units:
            self.cargo_units.remove(unit)
            print(f"{self.unique_class_name} 卸载单位 {unit.unique_class_name}")
            return True
        return False