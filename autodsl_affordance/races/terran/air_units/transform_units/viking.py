# races/terran/air_units/transform_units/viking.py

from autodsl_affordance.races.terran import TerranTransformUnit
from autodsl_affordance.core.base_units.unit import Position

class TerranViking(TerranTransformUnit):
    """维京 - 人族空地对地变形单位"""
    
    def __init__(self, development_mode: bool = False, **kwargs):
        # 设置单位唯一标识
        self.unique_class_name = "Terran_Viking"
        
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
        self.current_mode = "Air"  # Air or Ground
        self.requires_tech_lab = True
        # 变形单位特有攻击属性
        self.air_attack = {"targets": [], "damage": 0, "range": 0}
        self.ground_attack = {"targets": [], "damage": 0, "range": 0}
    
    def _enhance_vlm_interface(self):
        """增强VLM接口"""
        self.llm_interface.update({
            "natural_language_aliases": ["维京", "viking", "变形战机", "空对空"],
            "role_description": self.description,
            "tactical_keywords": ["变形", "对空", "对地", "多功能"],
            "primary_role": ["防空", "对地支援", "模式切换"],
            "common_tactics": ["对抗空军", "模式切换", "配合机械化部队"]
        })
    
    def air_attack_mode(self) -> dict:
        """获取空中攻击模式属性"""
        return self.air_attack
    
    def ground_attack_mode(self) -> dict:
        """获取地面攻击模式属性"""
        return self.ground_attack
    
    def transform_to_air_mode(self) -> bool:
        """变形为空中模式"""
        result = super().transform_to_air_mode()
        if result:
            self.current_mode = "Air"
        return result
    
    def transform_to_ground_mode(self) -> bool:
        """变形为地面模式"""
        result = super().transform_to_ground_mode()
        if result:
            self.current_mode = "Ground"
        return result