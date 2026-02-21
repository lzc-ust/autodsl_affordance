from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import json

@dataclass
class Position:
    """位置坐标"""
    x: float
    y: float
    z: float = 0.0

@dataclass  
class Cost:
    """资源成本"""
    mineral: int
    vespene: int
    supply: float
    time: float

class Unit:
    """所有单位的基类 - 森林的根节点"""
    
    def __init__(self):
        # 核心标识属性
        self.unique_class_name: str = self.__class__.__name__
        self.unit_type: str = "Abstract Unit"
        self.description: str = "所有单位的基础抽象类"
        
        # 游戏状态属性
        self.game_id: str = ""
        self.owner: str = "Neutral"
        self.position: Position = Position(0, 0, 0)
        self.is_alive: bool = True
        self.selection_priority: int = 1
        
        # VLM集成属性
        self.llm_interface: Dict[str, Any] = {}
        self.visual_recognition: Dict[str, Any] = {}
        self.tactical_context: Dict[str, Any] = {}
        
        # 继承关系追踪
        self._inheritance_chain: List[str] = self._build_inheritance_chain()
    
    def _build_inheritance_chain(self) -> List[str]:
        """构建继承链用于森林结构验证"""
        chain = []
        cls = self.__class__
        while cls != object:
            chain.append(cls.__name__)
            cls = cls.__bases__[0] if cls.__bases__ else object
        return list(reversed(chain))
    
    @property
    def inheritance_chain(self) -> List[str]:
        """获取完整的继承链"""
        return self._inheritance_chain
    
    @property
    def parent_class(self) -> Optional[str]:
        """获取直接父类名"""
        return self._inheritance_chain[-2] if len(self._inheritance_chain) > 1 else None
    
    def to_forest_node(self) -> Dict[str, Any]:
        """转换为森林节点格式"""
        return {
            "unique_class_name": self.unique_class_name,
            "parent_class": self.parent_class,
            "inheritance_depth": len(self._inheritance_chain),
            "inheritance_chain": self._inheritance_chain,
            "race": getattr(self, 'race', 'Unknown'),
            "unit_type": self.unit_type
        }
    
    # 基础方法 - 所有单位共享
    def move_to(self, target_position: Position) -> bool:
        """移动到目标位置"""
        print(f"{self.unique_class_name} 移动到位置 {target_position}")
        self.position = target_position
        return True
    
    def get_destroyed(self) -> None:
        """单位被摧毁"""
        print(f"{self.unique_class_name} 被摧毁")
        self.is_alive = False
    
    def get_selected(self) -> None:
        """单位被选中"""
        print(f"{self.unique_class_name} 被选中")
    
    def __repr__(self) -> str:
        return f"{self.unique_class_name}(position={self.position}, alive={self.is_alive})"