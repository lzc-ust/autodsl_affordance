from typing import Dict, List, Any, Optional
import inspect
from dataclasses import dataclass
from typing import Type

@dataclass
class NodeAttribute:
    """节点属性类"""
    name: str
    data_type: str
    default_value: Any = None
    description: str = ""
    is_required: bool = False

@dataclass
class NodeMethod:
    """节点方法类"""
    name: str
    return_type: str
    parameters: List[Dict[str, str]]
    description: str = ""
    is_overridden: bool = False

class GraphNode:
    """程序链接图的节点类"""
    
    def __init__(self, class_obj=None, **kwargs):
        # 基本标识信息
        self.node_id: str = kwargs.get('node_id', '')
        self.class_name: str = kwargs.get('class_name', '')
        self.unique_class_name: str = kwargs.get('unique_class_name', '')
        
        # 类层次关系
        self.inheritance_chain: List[str] = kwargs.get('inheritance_chain', [])
        self.parent_class: Optional[str] = kwargs.get('parent_class', None)
        self.inheritance_depth: int = kwargs.get('inheritance_depth', 0)
        
        # 属性映射
        self.attributes: List[NodeAttribute] = kwargs.get('attributes', [])
        
        # 方法映射
        self.methods: List[NodeMethod] = kwargs.get('methods', [])
        
        # VLM接口信息
        self.llm_interface: Dict[str, Any] = kwargs.get('llm_interface', {})
        self.visual_recognition: Dict[str, Any] = kwargs.get('visual_recognition', {})
        self.tactical_context: Dict[str, Any] = kwargs.get('tactical_context', {})
        
        # 额外元数据
        self.description: str = kwargs.get('description', '')
        self.race: str = kwargs.get('race', 'Unknown')
        self.unit_type: str = kwargs.get('unit_type', 'Abstract')
        
        # 如果提供了类对象，自动从类对象构建节点
        if class_obj:
            self._build_from_class(class_obj)
            
    @staticmethod
    def from_class(cls: Type) -> 'GraphNode':
        """从类对象创建GraphNode实例
        
        Args:
            cls: 类对象
            
        Returns:
            GraphNode: 表示该类的节点
        """
        # 创建节点
        node = GraphNode()
        
        # 设置基本信息
        node.class_name = cls.__name__
        node.unique_class_name = getattr(cls, 'unique_class_name', cls.__name__)
        node.node_id = node.unique_class_name
        node.description = inspect.getdoc(cls) or ""
        
        # 解析基类信息
        for base in cls.__bases__:
            if base is not object:
                node.parent_class = base.__name__
                
        # 解析继承链
        chain = []
        current_cls = cls
        
        while current_cls is not object and current_cls is not None:
            chain.append(current_cls.__name__)
            bases = current_cls.__bases__
            if bases and bases[0] is not object:
                current_cls = bases[0]
            else:
                break
        
        node.inheritance_chain = list(reversed(chain))
        node.inheritance_depth = len(node.inheritance_chain)
        
        # 尝试实例化（如果可能）来提取属性
        try:
            instance = cls()
            node._extract_attributes(instance)
            
            # 收集VLM相关信息
            if hasattr(instance, 'llm_interface'):
                node.llm_interface = instance.llm_interface
            if hasattr(instance, 'visual_recognition'):
                node.visual_recognition = instance.visual_recognition
            if hasattr(instance, 'tactical_context'):
                node.tactical_context = instance.tactical_context
            
            # 收集关键战术属性
            if hasattr(instance, 'strong_against'):
                node.strong_against = instance.strong_against
            if hasattr(instance, 'weak_against'):
                node.weak_against = instance.weak_against
            if hasattr(instance, 'abilities'):
                node.abilities = instance.abilities
            if hasattr(instance, 'upgrades'):
                node.upgrades = instance.upgrades
            if hasattr(instance, 'tactical_info'):
                node.tactical_info = instance.tactical_info
            
            # 收集其他元数据
            if hasattr(instance, 'description'):
                node.description = instance.description
            if hasattr(instance, 'race'):
                node.race = instance.race
            if hasattr(instance, 'unit_type'):
                node.unit_type = instance.unit_type
        except Exception as e:
            # 实例化失败时，尝试从类中提取静态属性
            print(f"警告: 无法实例化类 {cls.__name__}，错误: {e}")
            
            # 尝试从类属性中提取关键信息
            if hasattr(cls, 'strong_against'):
                node.strong_against = cls.strong_against
            if hasattr(cls, 'weak_against'):
                node.weak_against = cls.weak_against
        
        # 提取类方法
        node._extract_methods(cls)
        
        # 尝试提取单位特定的属性
        node._extract_unit_specific_attributes(cls)
        
        return node
        
    def _extract_unit_specific_attributes(self, cls: Type):
        """提取单位特定的属性"""
        # 尝试从类中提取种族信息
        if hasattr(cls, '__module__'):
            if 'terran' in cls.__module__.lower():
                self.race = 'Terran'
            elif 'protoss' in cls.__module__.lower():
                self.race = 'Protoss'
            elif 'zerg' in cls.__module__.lower():
                self.race = 'Zerg'
            
            # 尝试提取单位类型
            if 'infantry' in cls.__module__.lower():
                self.unit_type = 'Infantry'
            elif 'ground' in cls.__module__.lower():
                self.unit_type = 'Ground'
            elif 'air' in cls.__module__.lower():
                self.unit_type = 'Air'
    
    def _build_from_class(self, class_obj) -> None:
        """从类对象构建节点信息"""
        # 设置基本信息
        self.class_name = class_obj.__name__
        self.unique_class_name = getattr(class_obj, 'unique_class_name', class_obj.__name__)
        self.node_id = self.unique_class_name
        
        # 构建继承链
        inheritance_chain = []
        cls = class_obj
        while cls != object:
            inheritance_chain.append(cls.__name__)
            cls = cls.__bases__[0] if cls.__bases__ else object
        inheritance_chain = list(reversed(inheritance_chain))
        
        self.inheritance_chain = inheritance_chain
        self.inheritance_depth = len(inheritance_chain)
        self.parent_class = inheritance_chain[-2] if len(inheritance_chain) > 1 else None
        
        # 收集属性
        instance = class_obj()
        self._extract_attributes(instance)
        
        # 收集方法
        self._extract_methods(class_obj)
        
        # 收集VLM相关信息
        if hasattr(instance, 'llm_interface'):
            self.llm_interface = instance.llm_interface
        if hasattr(instance, 'visual_recognition'):
            self.visual_recognition = instance.visual_recognition
        if hasattr(instance, 'tactical_context'):
            self.tactical_context = instance.tactical_context
        
        # 收集其他元数据
        if hasattr(instance, 'description'):
            self.description = instance.description
        if hasattr(instance, 'race'):
            self.race = instance.race
        if hasattr(instance, 'unit_type'):
            self.unit_type = instance.unit_type
    
    def _extract_attributes(self, instance) -> None:
        """从实例中提取属性信息"""
        attributes = []
        
        # 获取实例的所有非私有属性
        for attr_name, attr_value in instance.__dict__.items():
            if not attr_name.startswith('_'):
                attr_type = type(attr_value).__name__ if attr_value is not None else "Any"
                attributes.append(NodeAttribute(
                    name=attr_name,
                    data_type=attr_type,
                    default_value=attr_value,
                    description=""
                ))
        
        self.attributes = attributes
        
        # 提取关键战术属性
        if hasattr(instance, 'strong_against') and hasattr(instance, 'weak_against'):
            self.counter_relations = {
                'strong_against': instance.strong_against,
                'weak_against': instance.weak_against
            }
        
        # 提取prefab_function_candidates
        if hasattr(instance, 'prefab_function_candidates'):
            self.prefab_function_candidates = instance.prefab_function_candidates
        
        # 提取建造需求（如果有）
        if hasattr(instance, 'build_requirements'):
            self.build_requirements = instance.build_requirements
    
    def _extract_methods(self, class_obj) -> None:
        """从类中提取方法信息"""
        methods = []
        
        # 获取类的所有非私有方法
        for method_name, method in inspect.getmembers(class_obj, predicate=inspect.isfunction):
            if not method_name.startswith('_'):
                sig = inspect.signature(method)
                
                # 提取参数信息
                params = []
                for param_name, param in list(sig.parameters.items())[1:]:  # 跳过self参数
                    param_type = "Any"
                    if param.annotation != inspect.Parameter.empty:
                        param_type = param.annotation.__name__ if hasattr(param.annotation, '__name__') else str(param.annotation)
                    
                    params.append({
                        "name": param_name,
                        "type": param_type
                    })
                
                # 获取返回类型
                return_type = "None"
                if sig.return_annotation != inspect.Parameter.empty:
                    return_type = sig.return_annotation.__name__ if hasattr(sig.return_annotation, '__name__') else str(sig.return_annotation)
                
                # 检查是否是重写的方法
                is_overridden = False
                for base in class_obj.__bases__:
                    if base != object and hasattr(base, method_name):
                        is_overridden = True
                        break
                
                methods.append(NodeMethod(
                    name=method_name,
                    return_type=return_type,
                    parameters=params,
                    description=inspect.getdoc(method) or "",
                    is_overridden=is_overridden
                ))
        
        self.methods = methods
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "node_id": self.node_id,
            "class_name": self.class_name,
            "unique_class_name": self.unique_class_name,
            "inheritance_chain": self.inheritance_chain,
            "parent_class": self.parent_class,
            "inheritance_depth": self.inheritance_depth,
            "attributes": [
                {
                    "name": attr.name,
                    "data_type": attr.data_type,
                    "default_value": attr.default_value,
                    "description": attr.description,
                    "is_required": attr.is_required
                }
                for attr in self.attributes
            ],
            "methods": [
                {
                    "name": method.name,
                    "return_type": method.return_type,
                    "parameters": method.parameters,
                    "description": method.description,
                    "is_overridden": method.is_overridden
                }
                for method in self.methods
            ],
            "llm_interface": self.llm_interface,
            "visual_recognition": self.visual_recognition,
            "tactical_context": self.tactical_context,
            "description": self.description,
            "race": self.race,
            "unit_type": self.unit_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GraphNode':
        """从字典创建节点"""
        # 重新构建属性对象
        attributes = [
            NodeAttribute(
                name=attr["name"],
                data_type=attr["data_type"],
                default_value=attr["default_value"],
                description=attr["description"],
                is_required=attr["is_required"]
            )
            for attr in data.get("attributes", [])
        ]
        
        # 重新构建方法对象
        methods = [
            NodeMethod(
                name=method["name"],
                return_type=method["return_type"],
                parameters=method["parameters"],
                description=method["description"],
                is_overridden=method["is_overridden"]
            )
            for method in data.get("methods", [])
        ]
        
        # 创建节点实例
        return cls(
            node_id=data.get("node_id", ""),
            class_name=data.get("class_name", ""),
            unique_class_name=data.get("unique_class_name", ""),
            inheritance_chain=data.get("inheritance_chain", []),
            parent_class=data.get("parent_class"),
            inheritance_depth=data.get("inheritance_depth", 0),
            attributes=attributes,
            methods=methods,
            llm_interface=data.get("llm_interface", {}),
            visual_recognition=data.get("visual_recognition", {}),
            tactical_context=data.get("tactical_context", {}),
            description=data.get("description", ""),
            race=data.get("race", "Unknown"),
            unit_type=data.get("unit_type", "Abstract")
        )