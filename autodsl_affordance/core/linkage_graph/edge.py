from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

class LinkageType(Enum):
    """链接类型枚举"""
    # 无向边类型
    INTERACTION = "interaction"      # 交互关系
    COMBINATION = "combination"      # 组合关系
    ASSOCIATION = "association"      # 关联关系
    
    # 有向边类型
    INVOCATION = "invocation"        # 调用关系
    DEPENDENCY = "dependency"        # 依赖关系

class EdgeDirection(Enum):
    """边方向枚举"""
    DIRECTED = "directed"            # 有向边
    UNDIRECTED = "undirected"        # 无向边

@dataclass
class EdgeMetadata:
    """边的元数据"""
    weight: float = 1.0              # 边的权重
    confidence: float = 1.0          # 边的置信度
    source: str = "auto_detected"    # 边的来源（自动检测或手动添加）
    discovered_in_round: int = 0     # 在哪一轮遍历中发现
    evidence: List[str] = None       # 支持此边的证据
    context_info: Dict[str, Any] = None  # 上下文信息
    
    def __post_init__(self):
        if self.evidence is None:
            self.evidence = []
        if self.context_info is None:
            self.context_info = {}

class GraphEdge:
    """程序链接图的边类"""
    
    def __init__(self, source_node_id: str, target_node_id: str, 
                 linkage_type: LinkageType, direction: EdgeDirection = None, **kwargs):
        # 节点标识
        self.source_node_id: str = source_node_id
        self.target_node_id: str = target_node_id
        
        # 链接类型和方向
        self.linkage_type: LinkageType = linkage_type
        
        # 根据链接类型自动确定方向
        if direction is None:
            if linkage_type in [LinkageType.INTERACTION, LinkageType.COMBINATION, LinkageType.ASSOCIATION]:
                self.direction: EdgeDirection = EdgeDirection.UNDIRECTED
            else:  # INVOCATION, DEPENDENCY
                self.direction: EdgeDirection = EdgeDirection.DIRECTED
        else:
            self.direction: EdgeDirection = direction
        
        # 边ID - 无向边使用规范化排序的ID
        if self.direction == EdgeDirection.UNDIRECTED:
            node_ids = sorted([source_node_id, target_node_id])
            self.edge_id: str = f"{node_ids[0]}__{self.linkage_type.value}__{node_ids[1]}"
        else:
            self.edge_id: str = f"{source_node_id}__{self.linkage_type.value}__{target_node_id}"
        
        # 描述信息
        self.description: str = kwargs.get('description', '')
        
        # 相关方法（对于调用关系特别有用）
        self.source_method: Optional[str] = kwargs.get('source_method', None)
        self.target_method: Optional[str] = kwargs.get('target_method', None)
        
        # 元数据
        self.metadata: EdgeMetadata = kwargs.get('metadata', EdgeMetadata())
        
        # 初始化元数据
        if 'weight' in kwargs:
            self.metadata.weight = kwargs['weight']
        if 'confidence' in kwargs:
            self.metadata.confidence = kwargs['confidence']
        if 'source' in kwargs:
            self.metadata.source = kwargs['source']
        if 'discovered_in_round' in kwargs:
            self.metadata.discovered_in_round = kwargs['discovered_in_round']
        if 'evidence' in kwargs:
            self.metadata.evidence = kwargs['evidence']
        if 'context_info' in kwargs:
            self.metadata.context_info = kwargs['context_info']
    
    def is_undirected(self) -> bool:
        """检查边是否为无向边"""
        return self.direction == EdgeDirection.UNDIRECTED
    
    def is_directed(self) -> bool:
        """检查边是否为有向边"""
        return self.direction == EdgeDirection.DIRECTED
    
    def get_related_nodes(self) -> Tuple[str, str]:
        """获取相关的两个节点ID，对于无向边返回排序后的结果"""
        if self.is_undirected():
            return tuple(sorted([self.source_node_id, self.target_node_id]))
        else:
            return (self.source_node_id, self.target_node_id)
    
    def has_node(self, node_id: str) -> bool:
        """检查边是否包含指定的节点"""
        return node_id == self.source_node_id or node_id == self.target_node_id
    
    def get_other_node(self, node_id: str) -> Optional[str]:
        """获取边中与指定节点相连的另一个节点ID"""
        if node_id == self.source_node_id:
            return self.target_node_id
        elif node_id == self.target_node_id:
            return self.source_node_id
        return None
    
    def add_evidence(self, evidence: str) -> None:
        """添加支持此边的证据"""
        if evidence not in self.metadata.evidence:
            self.metadata.evidence.append(evidence)
    
    def update_metadata(self, **kwargs) -> None:
        """更新元数据"""
        for key, value in kwargs.items():
            if hasattr(self.metadata, key):
                setattr(self.metadata, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "edge_id": self.edge_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "linkage_type": self.linkage_type.value,
            "direction": self.direction.value,
            "description": self.description,
            "source_method": self.source_method,
            "target_method": self.target_method,
            "metadata": {
                "weight": self.metadata.weight,
                "confidence": self.metadata.confidence,
                "source": self.metadata.source,
                "discovered_in_round": self.metadata.discovered_in_round,
                "evidence": self.metadata.evidence,
                "context_info": self.metadata.context_info
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GraphEdge':
        """从字典创建边"""
        # 解析链接类型和方向
        linkage_type = LinkageType(data["linkage_type"])
        direction = EdgeDirection(data["direction"])
        
        # 重新构建元数据
        metadata = EdgeMetadata(
            weight=data["metadata"].get("weight", 1.0),
            confidence=data["metadata"].get("confidence", 1.0),
            source=data["metadata"].get("source", "auto_detected"),
            discovered_in_round=data["metadata"].get("discovered_in_round", 0),
            evidence=data["metadata"].get("evidence", []),
            context_info=data["metadata"].get("context_info", {})
        )
        
        # 创建边实例
        return cls(
            source_node_id=data["source_node_id"],
            target_node_id=data["target_node_id"],
            linkage_type=linkage_type,
            direction=direction,
            description=data.get("description", ""),
            source_method=data.get("source_method"),
            target_method=data.get("target_method"),
            metadata=metadata
        )
    
    def __eq__(self, other) -> bool:
        """边的相等性检查"""
        if not isinstance(other, GraphEdge):
            return False
        
        # 对于无向边，节点顺序不重要
        if self.is_undirected() and other.is_undirected():
            return (self.linkage_type == other.linkage_type and
                    set(self.get_related_nodes()) == set(other.get_related_nodes()))
        
        # 对于有向边，节点顺序重要
        return (self.linkage_type == other.linkage_type and
                self.direction == other.direction and
                self.source_node_id == other.source_node_id and
                self.target_node_id == other.target_node_id)
    
    def __hash__(self) -> int:
        """边的哈希值计算"""
        if self.is_undirected():
            # 对于无向边，使用排序后的节点ID计算哈希
            node_ids = tuple(sorted([self.source_node_id, self.target_node_id]))
            return hash((self.linkage_type, node_ids))
        else:
            return hash((self.linkage_type, self.direction, 
                        self.source_node_id, self.target_node_id))
    
    def __repr__(self) -> str:
        """边的字符串表示"""
        if self.is_undirected():
            return f"GraphEdge[{self.linkage_type.value}]: {self.source_node_id} <-> {self.target_node_id}"
        else:
            return f"GraphEdge[{self.linkage_type.value}]: {self.source_node_id} -> {self.target_node_id}"