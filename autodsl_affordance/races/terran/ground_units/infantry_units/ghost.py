# races/terran/ground_units/infantry_units/ghost.py

from typing import Dict, Any
from autodsl_affordance.races.terran import TerranInfantryUnit
from autodsl_affordance.core.base_units.unit import Cost, Position

class TerranGhost(TerranInfantryUnit):
    """幽灵 - 人族隐形特种单位
    
    人族的隐形特种作战单位，配备狙击步枪和EMP冲击弹，能够呼叫核弹打击。
    具备反重甲、反灵能和战术打击能力，需要科技实验室支持。
    """
    
    def __init__(self, **kwargs):
        """
        初始化幽灵单位
        
        Args:
            **kwargs: 可选参数，允许传入自定义配置
        """
        super().__init__(**kwargs)
        self.unique_class_name = "Terran_Ghost"
        
        # 设置默认值
        self._set_default_values()
        
        # 尝试从JSON文件加载数据，失败则使用硬编码数据
        self._load_unit_data()
        
        # 应用自定义参数
        self._apply_custom_kwargs(kwargs)
        
        # VLM优化
        self._enhance_vlm_interface()
        
    def _set_default_values(self):
        """
        设置所有属性的默认值
        确保所有可能的属性都有初始值，避免None值导致的错误
        """
        self.description = ""
        self.cost = None
        self.attack = {}
        self.unit_stats = {}
        self.abilities = {}
        self.llm_interface = {}
        self.requires_tech_lab = False
        self.energy = 0
        self.energy_max = 0
        self.counter_relations = {}
        self.upgrades = {}
        self.tactical_info = {}
    
    def _load_unit_data(self):
        """
        从JSON文件加载单位数据
        如果JSON文件不存在或加载失败，则使用硬编码数据
        """
        # 计算JSON文件路径
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "..", "..", "unit_data", "terran_ghost.json")
        
        try:
            if os.path.exists(json_path):
                import json
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 加载数据到属性
                    self.description = data.get("description", "")
                    if "cost" in data:
                        self.cost = Cost(**data["cost"])
                    self.attack = data.get("attack", {})
                    self.unit_stats = data.get("unit_stats", {})
                    self.abilities = data.get("abilities", {})
                    self.requires_tech_lab = data.get("requires_tech_lab", True)
                    self.energy = data.get("energy", 75)
                    self.energy_max = data.get("energy_max", 200)
                    self.counter_relations = data.get("counter_relations", {})
                    self.upgrades = data.get("upgrades", {})
                    self.tactical_info = data.get("tactical_info", {})
            else:
                # JSON文件不存在，使用硬编码数据
                self._set_hardcoded_data()
        except Exception as e:
            # 加载出错，使用硬编码数据
            print(f"警告：加载JSON文件失败 {json_path}: {e}")
            self._set_hardcoded_data()
    
    def _set_hardcoded_data(self):
        """
        设置硬编码的单位数据作为后备
        当JSON文件加载失败时使用
        """
        self.description = "人族隐形特种单位，具备狙击、隐形和核弹引导能力"
        
        # 游戏属性
        self.cost = Cost(mineral=150, vespene=125, supply=2, time=29)
        self.attack = {
            "targets": ["Ground", "Air"],
            "damage": 10, "damage_upgrade": 1,
            "dps": {"base": 10.9},
            "cooldown": 1.44,
            "range": 6
        }
        self.unit_stats = {
            "health": 100, "armor": 0, "armor_upgrade": 1,
            "attributes": ["Biological", "Psionic"],
            "sight": 11, "speed": 3.94, "cargo_size": 2
        }
        
        # 能力配置
        self.abilities = {
            "snipe": {
                "cooldown": 0,
                "energy_cost": 25,
                "damage": 170,
                "range": 10
            },
            "cloak": {
                "energy_cost": 25,
                "energy_drain": 0.5625
            },
            "emp_round": {
                "cooldown": 0,
                "energy_cost": 75,
                "range": 10,
                "shield_damage": 100,
                "energy_damage": 100
            },
            "nuke_call": {
                "energy_cost": 50,
                "damage": 300,
                "splash_radius": 7
            }
        }
        
        # 幽灵特有属性
        self.requires_tech_lab = True
        self.energy = 75
        self.energy_max = 200
    
    def _apply_custom_kwargs(self, kwargs):
        """
        应用从构造函数传入的自定义参数
        
        Args:
            kwargs: 自定义参数字典
        """
        # 处理开发模式
        if kwargs.get("development_mode", False):
            # 开发模式特定的设置
            pass
        
        # 应用其他自定义参数
        for key, value in kwargs.items():
            if key != "development_mode" and hasattr(self, key):
                setattr(self, key, value)
        
        # VLM优化
        self._enhance_vlm_interface()
    
    def _enhance_vlm_interface(self):
        """
        增强VLM接口，添加自然语言描述和战术关键词
        用于大语言模型交互
        """
        self.llm_interface.update({
            "natural_language_aliases": ["幽灵", "ghost", "特种兵", "核弹兵"],
            "role_description": "人族隐形特种单位，具备狙击、隐形和核弹引导能力",
            "tactical_keywords": ["狙击", "隐形", "EMP", "核弹", "反灵能"],
            "primary_role": ["反重甲", "反灵能", "战术打击", "侦查"],
            "common_tactics": ["狙击高价值目标", "EMP神族", "核弹打击", "隐形侦查"]
        })
    
    def use_snipe(self, target) -> Dict[str, Any]:
        """
        使用狙击技能，对单个高价值目标造成大量伤害
        
        Args:
            target: 目标单位
            
        Returns:
            Dict[str, Any]: 包含使用结果和相关信息的字典
        """
        result = {
            "success": False,
            "action": "use_snipe",
            "target": str(target),
            "energy_consumed": 25
        }
        
        if self.energy >= 25:
            result["success"] = True
            print(f"{self.unique_class_name} 对目标使用狙击")
            self.energy -= 25
        else:
            result["error"] = "能量不足"
        
        return result
    
    def toggle_cloak(self) -> Dict[str, Any]:
        """
        切换隐形状态，消耗初始能量并持续消耗少量能量
        
        Returns:
            Dict[str, Any]: 包含使用结果和相关信息的字典
        """
        result = {
            "success": True,
            "action": "toggle_cloak",
            "initial_energy_cost": 25,
            "sustained_energy_cost": 0.5625
        }
        
        print(f"{self.unique_class_name} 切换隐形状态")
        return result
    
    def use_emp_round(self, target_position: Position) -> Dict[str, Any]:
        """
        使用EMP冲击弹，对指定位置的敌方单位造成护盾和能量伤害
        
        Args:
            target_position: 目标位置对象
            
        Returns:
            Dict[str, Any]: 包含使用结果和相关信息的字典
        """
        result = {
            "success": False,
            "action": "use_emp_round",
            "target_position": str(target_position),
            "energy_consumed": 75,
            "shield_damage": 100,
            "energy_damage": 100
        }
        
        if self.energy >= 75:
            result["success"] = True
            print(f"{self.unique_class_name} 在位置 {target_position} 使用EMP冲击弹")
            self.energy -= 75
        else:
            result["error"] = "能量不足"
        
        return result
    
    def call_nuke(self, target_position: Position) -> Dict[str, Any]:
        """
        呼叫核弹打击，对指定位置造成大范围高伤害
        
        Args:
            target_position: 目标位置对象
            
        Returns:
            Dict[str, Any]: 包含使用结果和相关信息的字典
        """
        result = {
            "success": False,
            "action": "call_nuke",
            "target_position": str(target_position),
            "energy_consumed": 50,
            "damage": 300,
            "splash_radius": 7
        }
        
        if self.energy >= 50:
            result["success"] = True
            print(f"{self.unique_class_name} 在位置 {target_position} 呼叫核弹打击")
            self.energy -= 50
        else:
            result["error"] = "能量不足"
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将幽灵单位对象转换为字典表示
        
        Returns:
            Dict[str, Any]: 单位数据字典
        """
        result = {
            "unique_class_name": self.unique_class_name,
            "description": self.description,
            "cost": {
                "mineral": self.cost.mineral if self.cost else 0,
                "vespene": self.cost.vespene if self.cost else 0,
                "supply": self.cost.supply if self.cost else 0,
                "time": self.cost.time if self.cost else 0
            },
            "attack": self.attack,
            "unit_stats": self.unit_stats,
            "abilities": self.abilities,
            "llm_interface": self.llm_interface,
            "requires_tech_lab": self.requires_tech_lab,
            "energy": self.energy,
            "energy_max": self.energy_max,
            "counter_relations": getattr(self, 'counter_relations', {}),
            "upgrades": getattr(self, 'upgrades', {}),
            "tactical_info": getattr(self, 'tactical_info', {})
        }
        return result