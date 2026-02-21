from typing import Dict, Any, List, Optional
from autodsl_affordance.core.base_units.unit import Unit, Position, Cost
from autodsl_affordance.utils.json_loader import UnitJsonLoader


class StandardUnit(Unit):
    """
    种族无关的标准单位类模板
    
    所有种族的具体单位类都应遵循此模板，确保代码风格、结构和功能的一致性。
    
    注意：
    1. 每个单位类必须有清晰的中文和英文注释
    2. 严格按照模板结构组织代码
    3. 使用JSON文件加载数据作为首选
    4. 确保所有必要的属性和方法都按照统一格式定义
    """
    
    def __init__(self, race: str = "Unknown", development_mode: bool = False, **kwargs):
        """
        初始化单位
        
        Args:
            race: 单位所属种族
            development_mode: 是否启用开发模式，开发模式下数据缺失会抛出异常
            **kwargs: 可选参数，允许传入自定义配置
        """
        # 调用父类初始化
        super().__init__()
        
        # 设置单位基本信息
        self.race = race
        self.development_mode = development_mode
        self.unique_class_name = self.__class__.__name__  # 默认使用类名作为唯一标识
        
        # 初始化JSON加载器
        self.json_loader = UnitJsonLoader(self, dev_mode=development_mode)
        
        # 设置默认值
        self._set_default_values()
        
        # 加载单位数据
        self._load_unit_data()
        
        # 应用自定义参数
        self._apply_custom_kwargs(kwargs)
        
        # 增强VLM接口
        self._enhance_vlm_interface()
    
    def _set_default_values(self):
        """
        设置所有属性的默认值
        确保所有可能的属性都有初始值，避免None值导致的错误
        """
        # 基本信息
        self.description = ""  # 单位描述
        
        # 游戏属性
        self.cost = Cost(mineral=0, vespene=0, supply=0, time=0)  # 成本对象
        self.attack = {}  # 攻击属性字典
        self.unit_stats = {  # 单位统计信息
            "health": 0,
            "shield": 0,
            "armor": 0,
            "armor_upgrade": 0,
            "attributes": [],
            "sight": 0,
            "speed": 0.0,
            "cargo_size": 0,
            "energy": 0,
            "energy_max": 0
        }
        self.abilities = {}  # 能力配置
        
        # 战术信息
        self.strong_against = []  # 强势对抗的单位
        self.weak_against = []  # 弱势对抗的单位
        self.build_from = "Unknown"  # 建造来源
        self.requirements = ""  # 建造需求
        self.hotkey = ""  # 快捷键
        
        # 单位特有属性 - 子类可以扩展
    
    def _load_unit_data(self):
        """
        从JSON文件加载单位数据
        使用统一的JSON加载器
        """
        try:
            self.json_loader.load_and_apply(self.unique_class_name)
        except Exception as e:
            if self.development_mode:
                raise e
            print(f"[警告] 加载 {self.unique_class_name} 数据失败，使用默认值: {e}")
    
    def _apply_custom_kwargs(self, kwargs: Dict[str, Any]):
        """
        应用从构造函数传入的自定义参数
        
        Args:
            kwargs: 自定义参数字典
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def _enhance_vlm_interface(self):
        """
        增强VLM接口，添加自然语言描述和战术关键词
        用于大语言模型交互
        """
        # 初始化接口字典（如果不存在）
        if not hasattr(self, 'llm_interface'):
            self.llm_interface = {}
        if not hasattr(self, 'visual_recognition'):
            self.visual_recognition = {}
        if not hasattr(self, 'tactical_context'):
            self.tactical_context = {}
        
        # 基础VLM接口
        self.llm_interface.update({
            "natural_language_aliases": [self.__class__.__name__.lower()],
            "role_description": self.description,
            "tactical_keywords": [],
            "primary_role": [],
            "common_tactics": [],
            "special_abilities": list(self.abilities.keys()),
            "visual_recognition_features": [],
        })
        
        # 视觉识别
        self.visual_recognition.update({
            "identifying_features": [],
            "minimap_characteristics": "",
            "unique_visual_queues": [],
            "llm_vision_prompt": f"识别画面中的{self.__class__.__name__}"
        })
        
        # 战术上下文
        self.tactical_context.update({
            "early_game": [],
            "mid_game": [],
            "late_game": [],
            "counters": self.weak_against,
            "countered_by": self.strong_against,
            "synergies": [],
        })
    
    def generate_synergies(self) -> List[Dict[str, Any]]:
        """
        基于单位属性和克制关系动态生成协同关系
        
        Returns:
            List[Dict[str, Any]]: 协同关系列表
        """
        synergies = []
        attributes = self.unit_stats.get("attributes", [])
        
        # 1. 基于单位类型生成协同关系
        unit_type = self.unit_type.split(' ')[-1].lower()
        
        if unit_type == "air":
            synergies.append({
                "type": "combination",
                "target_unit": "GroundUnit",
                "strength": 0.8,
                "condition": "空中单位与地面单位协同作战",
                "description": f"{self.unique_class_name} 与地面单位协同作战，提供空中支援"
            })
        elif unit_type == "ground":
            synergies.append({
                "type": "combination",
                "target_unit": "AirUnit",
                "strength": 0.7,
                "condition": "地面单位与空中单位协同作战",
                "description": f"{self.unique_class_name} 与空中单位协同作战，提供地面支援"
            })
        
        # 2. 基于属性生成协同关系
        if "Detector" in attributes:
            synergies.append({
                "type": "support",
                "target_unit": "StealthUnit",
                "strength": 0.9,
                "condition": "探测单位与隐形单位协同作战",
                "description": f"{self.unique_class_name} 提供反隐支持，配合隐形单位作战"
            })
        
        if "Healer" in attributes or "heal" in self.abilities:
            synergies.append({
                "type": "support",
                "target_unit": "CombatUnit",
                "strength": 0.85,
                "condition": "治疗单位与作战单位协同作战",
                "description": f"{self.unique_class_name} 提供治疗支持，增强作战单位生存能力"
            })
        
        # 3. 基于克制关系生成协同关系
        for unit in self.weak_against:
            synergies.append({
                "type": "dependency",
                "target_unit": unit,
                "strength": 0.9,
                "condition": f"需要克制 {unit} 的单位支援",
                "description": f"{self.unique_class_name} 弱势对抗 {unit}，需要克制单位支援"
            })
        
        for unit in self.strong_against:
            synergies.append({
                "type": "interaction",
                "target_unit": unit,
                "strength": 0.8,
                "condition": f"对抗 {unit} 单位",
                "description": f"{self.unique_class_name} 强势对抗 {unit}，可以主动攻击"
            })
        
        # 4. 基于能力生成协同关系
        for ability_name, ability_info in self.abilities.items():
            if ability_name == "transport":
                synergies.append({
                    "type": "association",
                    "target_unit": "InfantryUnit",
                    "strength": 0.75,
                    "condition": "运输单位与步兵单位协同作战",
                    "description": f"{self.unique_class_name} 可以运输步兵单位，实现快速部署"
                })
        
        return synergies
    
    def generate_graph_edges(self) -> List[Dict[str, Any]]:
        """
        生成Linkage Graph边
        
        Returns:
            List[Dict[str, Any]]: Graph边列表
        """
        edges = []
        synergies = self.generate_synergies()
        
        # 1. 生成协同关系边
        for synergy in synergies:
            edge = {
                "source_node_id": self.unique_class_name,
                "target_node_id": synergy["target_unit"],
                "linkage_type": synergy["type"],
                "metadata": {
                    "strength": synergy["strength"],
                    "condition": synergy["condition"],
                    "description": synergy["description"],
                    "evidence": [f"基于{self.unique_class_name}的单位类型和克制关系"],
                    "confidence": synergy["strength"]
                }
            }
            edges.append(edge)
        
        # 2. 生成能力调用边
        for ability_name, ability_info in self.abilities.items():
            edge = {
                "source_node_id": self.unique_class_name,
                "target_node_id": f"Ability_{ability_name}",
                "linkage_type": "invocation",
                "metadata": {
                    "strength": 1.0,
                    "condition": f"{self.unique_class_name} 可以使用 {ability_name} 能力",
                    "description": f"{self.unique_class_name} 调用 {ability_name} 能力",
                    "evidence": [f"基于{self.unique_class_name}的能力配置"],
                    "confidence": 1.0
                }
            }
            edges.append(edge)
        
        # 3. 生成攻击关系边
        if self.attack.get("damage", 0) > 0:
            for target in self.attack.get("targets", []):
                edge = {
                    "source_node_id": self.unique_class_name,
                    "target_node_id": f"Target_{target}",
                    "linkage_type": "interaction",
                    "metadata": {
                        "strength": self.attack["damage"] / 20,  # 归一化强度
                        "condition": f"{self.unique_class_name} 可以攻击 {target} 目标",
                        "description": f"{self.unique_class_name} 攻击 {target} 目标",
                        "evidence": [f"基于{self.unique_class_name}的攻击属性"],
                        "confidence": 0.9
                    }
                }
                edges.append(edge)
        
        return edges
    
    def generate_prefab_functions(self) -> List[Dict[str, Any]]:
        """
        基于单位属性和协同关系动态生成预制函数
        
        Returns:
            List[Dict[str, Any]]: 预制函数列表
        """
        prefab_functions = []
        synergies = self.generate_synergies()
        graph_edges = self.generate_graph_edges()
        attributes = self.unit_stats.get("attributes", [])
        
        # 1. 基于协同关系生成预制函数
        for i, synergy in enumerate(synergies):
            # 查找对应的graph边
            related_edges = [edge for edge in graph_edges 
                           if edge["source_node_id"] == self.unique_class_name 
                           and edge["target_node_id"] == synergy["target_unit"]
                           and edge["linkage_type"] == synergy["type"]]
            
            function = {
                "function_id": f"{self.unique_class_name}_SYNERGY_{i}",
                "function_type": synergy["type"],
                "name": f"{self.unique_class_name.lower()}_with_{synergy['target_unit'].lower()}",
                "description": synergy["description"],
                "strategy_description": synergy["description"],
                "tactic_category": synergy["type"],
                "source_unit": self.unique_class_name,
                "target_unit": synergy["target_unit"],
                "linkage_type": synergy["type"],
                "execution_type": "concurrent" if synergy["type"] == "combination" else "sequential",
                "related_graph_edges": [edge["source_node_id"] + "_" + edge["target_node_id"] for edge in related_edges],
                "parameters": [
                    {
                        "name": "target_unit_tag",
                        "type": "int",
                        "description": f"目标 {synergy['target_unit']} 的单位标签",
                        "domain": "valid_unit_tags"
                    },
                    {
                        "name": "target_position",
                        "type": "Position",
                        "description": "执行位置",
                        "domain": "valid_map_positions"
                    }
                ],
                "execution_flow": [
                    {
                        "step": 1,
                        "action": f"execute_{self.unique_class_name.lower()}_ability",
                        "parameters": ["target_position"],
                        "condition": "self.energy >= ability_cost"
                    },
                    {
                        "step": 2,
                        "action": f"coordinate_with_{synergy['target_unit'].lower()}",
                        "parameters": ["target_unit_tag", "target_position"],
                        "condition": "target_unit.is_alive()"
                    }
                ],
                "tactical_effect": {
                    "synergy_strength": synergy["strength"],
                    "expected_outcome": self._evaluate_tactical_outcome(synergy),
                    "risk_level": self._evaluate_risk_level(synergy),
                    "resource_cost": {
                        "mineral": 0,
                        "vespene": 0,
                        "supply": 0
                    }
                },
                "evidence": [f"基于{self.unique_class_name}的协同关系分析"],
                "confidence": synergy["strength"]
            }
            prefab_functions.append(function)
        
        # 2. 基于能力生成预制函数
        for i, (ability_name, ability_info) in enumerate(self.abilities.items()):
            function = {
                "function_id": f"{self.unique_class_name}_ABILITY_{i}",
                "function_type": "ability",
                "name": f"{self.unique_class_name.lower()}_use_{ability_name.lower()}",
                "description": f"{self.unique_class_name} 使用 {ability_name} 能力",
                "strategy_description": f"{self.unique_class_name} 使用 {ability_name} 能力执行战术动作",
                "tactic_category": "ability",
                "source_unit": self.unique_class_name,
                "target_unit": None,
                "linkage_type": "invocation",
                "execution_type": "sequential",
                "related_graph_edges": [f"{self.unique_class_name}_Ability_{ability_name}"],
                "parameters": [
                    {
                        "name": "target_position",
                        "type": "Position",
                        "description": "能力执行位置",
                        "domain": "valid_map_positions"
                    }
                ],
                "execution_flow": [
                    {
                        "step": 1,
                        "action": f"use_{ability_name.lower()}",
                        "parameters": ["target_position"],
                        "condition": self._get_ability_condition(ability_name, ability_info)
                    }
                ],
                "tactical_effect": {
                    "synergy_strength": 0.0,
                    "expected_outcome": f"执行 {ability_name} 能力",
                    "risk_level": 0.1,
                    "resource_cost": {
                        "mineral": 0,
                        "vespene": 0,
                        "supply": 0,
                        "energy": ability_info.get("energy_cost", 0)
                    }
                },
                "evidence": [f"基于{self.unique_class_name}的能力配置"],
                "confidence": 1.0
            }
            prefab_functions.append(function)
        
        return prefab_functions
    
    def _evaluate_tactical_outcome(self, synergy: Dict[str, Any]) -> str:
        """
        评估战术效果
        
        Args:
            synergy: 协同关系字典
            
        Returns:
            str: 战术效果评估
        """
        if synergy["type"] == "support":
            return f"增强友方单位 {synergy['target_unit']} 的作战能力"
        elif synergy["type"] == "combination":
            return f"与 {synergy['target_unit']} 协同作战，形成战术组合"
        elif synergy["type"] == "dependency":
            return f"获得 {synergy['target_unit']} 的支援，弥补自身弱点"
        elif synergy["type"] == "interaction":
            return f"攻击敌方 {synergy['target_unit']} 单位，发挥克制优势"
        else:
            return f"与 {synergy['target_unit']} 产生战术协同"
    
    def _evaluate_risk_level(self, synergy: Dict[str, Any]) -> float:
        """
        评估风险等级
        
        Args:
            synergy: 协同关系字典
            
        Returns:
            float: 风险等级 (0.0-1.0)
        """
        if synergy["type"] == "support":
            return 0.2
        elif synergy["type"] == "combination":
            return 0.4
        elif synergy["type"] == "dependency":
            return 0.6
        elif synergy["type"] == "interaction":
            return 0.5
        else:
            return 0.3
    
    def _get_ability_condition(self, ability_name: str, ability_info: Dict[str, Any]) -> str:
        """
        获取能力使用条件
        
        Args:
            ability_name: 能力名称
            ability_info: 能力信息
            
        Returns:
            str: 能力使用条件
        """
        energy_cost = ability_info.get("energy_cost", 0)
        if energy_cost > 0:
            return f"self.energy >= {energy_cost}"
        return "True"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将单位对象转换为字典表示
        
        Returns:
            Dict[str, Any]: 单位数据字典
        """
        return {
            "unique_class_name": self.unique_class_name,
            "race": self.race,
            "description": self.description,
            "cost": {
                "mineral": self.cost.mineral,
                "vespene": self.cost.vespene,
                "supply": self.cost.supply,
                "time": self.cost.time
            },
            "attack": self.attack,
            "unit_stats": self.unit_stats,
            "abilities": self.abilities,
            "tactical_info": {
                "strong_against": self.strong_against,
                "weak_against": self.weak_against,
                "build_from": self.build_from,
                "requirements": self.requirements,
                "hotkey": self.hotkey
            },
            "llm_interface": self.llm_interface,
            "visual_recognition": self.visual_recognition,
            "tactical_context": self.tactical_context,
            "synergies": self.generate_synergies(),
            "graph_edges": self.generate_graph_edges(),
            "prefab_functions": self.generate_prefab_functions()
        }
    
    def execute_ability(self, ability_name: str, **params) -> Dict[str, Any]:
        """
        执行单位能力
        
        Args:
            ability_name: 能力名称
            **params: 能力参数
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        result = {
            "success": False,
            "ability": ability_name,
            "message": f"Ability {ability_name} not found",
            "params": params
        }
        
        if ability_name in self.abilities:
            # 调用能力方法
            ability_method = getattr(self, f"use_{ability_name.lower()}", None)
            if ability_method:
                try:
                    result = ability_method(**params)
                    result["ability"] = ability_name
                    result["params"] = params
                except Exception as e:
                    result["message"] = f"Error executing ability: {e}"
            else:
                result["message"] = f"Ability method use_{ability_name.lower()} not implemented"
        
        return result
    
    # 单位特有方法 - 子类可以扩展
    def use_ability(self, ability_name: str, **params) -> Dict[str, Any]:
        """
        使用单位能力的通用方法
        
        Args:
            ability_name: 能力名称
            **params: 能力参数
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        return self.execute_ability(ability_name, **params)
