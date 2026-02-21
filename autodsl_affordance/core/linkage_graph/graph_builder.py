import json
import logging
from typing import Dict, List, Set, Optional, Any, Generator, Tuple
from .node import GraphNode
from .edge import GraphEdge, LinkageType
from .traversal_strategy import TraversalStrategy, TraversalPhase
import uuid

# 自定义JSON编码器，用于处理Position等自定义类型
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # 处理Position类型对象
        if hasattr(obj, 'x') and hasattr(obj, 'y'):
            return {"__type__": "Position", "x": obj.x, "y": obj.y}
        # 处理Cost类型对象
        elif hasattr(obj, 'minerals') and hasattr(obj, 'gas') and hasattr(obj, 'supply'):
            return {"__type__": "Cost", "minerals": obj.minerals, "gas": obj.gas, "supply": obj.supply}
        # 处理其他复杂类型
        elif hasattr(obj, '__dict__'):
            return {"__type__": type(obj).__name__, "data": obj.__dict__}
        # 默认处理
        return super().default(obj)
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProgramLinkageGraph:
    """程序联动图核心类
    
    负责构建和管理包含节点和边的完整图结构，提供多轮遍历功能
    """
    
    def __init__(self):
        # 图的唯一标识符
        self.graph_id = str(uuid.uuid4())
        
        # 节点集合 {node_id: GraphNode}
        self.nodes: Dict[str, GraphNode] = {}
        
        # 边集合 {edge_id: GraphEdge}
        self.edges: Dict[str, GraphEdge] = {}
        
        # 遍历策略
        self.traversal_strategy = TraversalStrategy()
        
        # 遍历历史，记录每轮发现的边
        self.traversal_history: Dict[TraversalPhase, List[GraphEdge]] = {}
        
        # 遍历状态
        self.current_phase: Optional[TraversalPhase] = None
        self.traversal_complete = False
        
        # 索引结构，优化查询性能
        self.node_id_to_edges: Dict[str, List[str]] = {}
        self.edge_type_index: Dict[LinkageType, List[str]] = {}
    
    def add_node(self, node: GraphNode) -> bool:
        """添加一个节点到图中
        
        Args:
            node: 要添加的节点对象
            
        Returns:
            bool: 如果节点添加成功则返回True，否则返回False
        """
        if node.node_id in self.nodes:
            logger.warning(f"节点 {node.node_id} 已存在，无法添加")
            return False
        
        self.nodes[node.node_id] = node
        self.node_id_to_edges[node.node_id] = []
        logger.info(f"成功添加节点: {node.node_id} ({node.class_name})")
        return True
    
    def add_edge(self, edge: GraphEdge) -> bool:
        """添加一条边到图中
        
        Args:
            edge: 要添加的边对象
            
        Returns:
            bool: 如果边添加成功则返回True，否则返回False
        """
        # 检查源节点和目标节点是否存在
        if edge.source_node_id not in self.nodes:
            logger.warning(f"源节点 {edge.source_node_id} 不存在，无法添加边")
            return False
        
        if edge.target_node_id not in self.nodes:
            logger.warning(f"目标节点 {edge.target_node_id} 不存在，无法添加边")
            return False
        
        # 检查边是否已存在
        if edge.edge_id in self.edges:
            logger.warning(f"边 {edge.edge_id} 已存在，无法添加")
            return False
        
        # 检查是否是重复的边（相同的源节点、目标节点和链接类型）
        for existing_edge in self.edges.values():
            if (existing_edge.source_node_id == edge.source_node_id and
                existing_edge.target_node_id == edge.target_node_id and
                existing_edge.linkage_type == edge.linkage_type):
                logger.warning(f"相同的边已存在: {existing_edge.edge_id}")
                return False
        
        # 添加边到图中
        self.edges[edge.edge_id] = edge
        
        # 更新索引
        self.node_id_to_edges[edge.source_node_id].append(edge.edge_id)
        self.node_id_to_edges[edge.target_node_id].append(edge.edge_id)
        
        if edge.linkage_type not in self.edge_type_index:
            self.edge_type_index[edge.linkage_type] = []
        self.edge_type_index[edge.linkage_type].append(edge.edge_id)
        
        logger.info(f"成功添加边: {edge.edge_id} ({edge.linkage_type.value})")
        return True
    
    def remove_node(self, node_id: str) -> bool:
        """从图中移除一个节点
        
        Args:
            node_id: 要移除的节点ID
            
        Returns:
            bool: 如果节点移除成功则返回True，否则返回False
        """
        if node_id not in self.nodes:
            logger.warning(f"节点 {node_id} 不存在，无法移除")
            return False
        
        # 先移除所有与该节点相关的边
        edges_to_remove = self.node_id_to_edges.get(node_id, []).copy()
        for edge_id in edges_to_remove:
            self.remove_edge(edge_id)
        
        # 移除节点
        del self.nodes[node_id]
        del self.node_id_to_edges[node_id]
        
        logger.info(f"成功移除节点: {node_id}")
        return True
    
    def remove_edge(self, edge_id: str) -> bool:
        """从图中移除一条边
        
        Args:
            edge_id: 要移除的边ID
            
        Returns:
            bool: 如果边移除成功则返回True，否则返回False
        """
        if edge_id not in self.edges:
            logger.warning(f"边 {edge_id} 不存在，无法移除")
            return False
        
        edge = self.edges[edge_id]
        
        # 从索引中移除
        self.node_id_to_edges[edge.source_node_id].remove(edge_id)
        self.node_id_to_edges[edge.target_node_id].remove(edge_id)
        self.edge_type_index[edge.linkage_type].remove(edge_id)
        
        # 移除边
        del self.edges[edge_id]
        
        logger.info(f"成功移除边: {edge_id}")
        return True
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """获取节点
        
        Args:
            node_id: 节点ID
            
        Returns:
            GraphNode: 如果节点存在则返回节点对象，否则返回None
        """
        return self.nodes.get(node_id)
    
    def get_edge(self, edge_id: str) -> Optional[GraphEdge]:
        """获取边
        
        Args:
            edge_id: 边ID
            
        Returns:
            GraphEdge: 如果边存在则返回边对象，否则返回None
        """
        return self.edges.get(edge_id)
    
    def get_edges_for_node(self, node_id: str) -> List[GraphEdge]:
        """获取与指定节点相连的所有边
        
        Args:
            node_id: 节点ID
            
        Returns:
            List[GraphEdge]: 与节点相连的边列表
        """
        if node_id not in self.node_id_to_edges:
            return []
        
        return [self.edges[edge_id] for edge_id in self.node_id_to_edges[node_id]]
    
    def get_edges_by_type(self, linkage_type: LinkageType) -> List[GraphEdge]:
        """获取指定类型的所有边
        
        Args:
            linkage_type: 链接类型
            
        Returns:
            List[GraphEdge]: 指定类型的边列表
        """
        if linkage_type not in self.edge_type_index:
            return []
        
        return [self.edges[edge_id] for edge_id in self.edge_type_index[linkage_type]]
    
    def get_neighbors(self, node_id: str) -> List[GraphNode]:
        """获取指定节点的所有邻居节点
        
        Args:
            node_id: 节点ID
            
        Returns:
            List[GraphNode]: 邻居节点列表
        """
        neighbors = []
        edges = self.get_edges_for_node(node_id)
        
        for edge in edges:
            if edge.source_node_id == node_id:
                neighbor_id = edge.target_node_id
            else:
                neighbor_id = edge.source_node_id
            
            if neighbor_id in self.nodes:
                neighbors.append(self.nodes[neighbor_id])
        
        return neighbors
    
    def get_node_degree(self, node_id: str) -> int:
        """获取节点的度（连接数）
        
        Args:
            node_id: 节点ID
            
        Returns:
            int: 节点的度
        """
        if node_id not in self.node_id_to_edges:
            return 0
        
        return len(self.node_id_to_edges[node_id])
    
    def build_from_classes(self, class_objects: List[type]) -> int:
        """从类对象列表构建图
        
        Args:
            class_objects: 类对象列表
            
        Returns:
            int: 添加的节点数量
        """
        count = 0
        for cls in class_objects:
            # 从类对象创建节点
            node = GraphNode.from_class(cls)
            if self.add_node(node):
                count += 1
        
        logger.info(f"从 {len(class_objects)} 个类对象中成功构建了 {count} 个节点")
        return count
    
    def execute_single_traversal_phase(self) -> List[GraphEdge]:
        """执行单个遍历阶段
        
        Returns:
            List[GraphEdge]: 当前阶段发现的新边列表
        """
        # 获取下一个遍历阶段
        next_phase = self.traversal_strategy.get_next_phase(self.current_phase)
        
        if next_phase is None:
            logger.info("所有遍历阶段已完成")
            self.traversal_complete = True
            return []
        
        logger.info(f"开始执行遍历阶段: {next_phase.name}")
        
        # 执行当前阶段
        new_edges = self.traversal_strategy.execute_phase(
            next_phase,
            self.nodes,
            set(self.edges.values()),
            self.traversal_history
        )
        
        # 添加新发现的边到图中
        added_count = 0
        for edge in new_edges:
            if self.add_edge(edge):
                added_count += 1
        
        # 更新遍历历史
        self.traversal_history[next_phase] = new_edges
        self.current_phase = next_phase
        
        logger.info(f"阶段 {next_phase.name} 完成: 发现 {len(new_edges)} 条边，成功添加 {added_count} 条边")
        return new_edges
    
    def execute_full_traversal(self) -> Dict[TraversalPhase, List[GraphEdge]]:
        """执行完整的多轮遍历
        
        Returns:
            Dict[TraversalPhase, List[GraphEdge]]: 每个阶段发现的边
        """
        logger.info("开始执行完整的多轮遍历")
        
        # 重置遍历状态
        self.current_phase = None
        self.traversal_complete = False
        self.traversal_history = {}
        
        # 执行所有阶段
        while not self.traversal_complete:
            self.execute_single_traversal_phase()
        
        logger.info(f"完整遍历完成: 总共发现 {sum(len(edges) for edges in self.traversal_history.values())} 条边")
        return self.traversal_history
    
    def find_path(self, start_node_id: str, end_node_id: str, 
                  max_depth: int = 10) -> Optional[List[GraphEdge]]:
        """查找从起始节点到目标节点的路径
        
        Args:
            start_node_id: 起始节点ID
            end_node_id: 目标节点ID
            max_depth: 最大搜索深度
            
        Returns:
            List[GraphEdge]: 如果找到路径则返回边列表，否则返回None
        """
        # 边界检查
        if start_node_id not in self.nodes or end_node_id not in self.nodes:
            return None
        
        # 如果起始节点就是目标节点
        if start_node_id == end_node_id:
            return []
        
        # 使用BFS查找路径
        visited = set()
        # 存储(当前节点ID, 路径边列表)
        queue = [(start_node_id, [])]
        
        while queue:
            current_id, path = queue.pop(0)
            
            # 检查是否超过最大深度
            if len(path) >= max_depth:
                continue
            
            # 标记为已访问
            if current_id in visited:
                continue
            visited.add(current_id)
            
            # 获取所有相连的边
            edges = self.get_edges_for_node(current_id)
            
            for edge in edges:
                # 确定邻居节点ID
                if edge.source_node_id == current_id:
                    neighbor_id = edge.target_node_id
                else:
                    neighbor_id = edge.source_node_id
                
                # 如果到达目标节点
                if neighbor_id == end_node_id:
                    return path + [edge]
                
                # 将邻居节点加入队列
                if neighbor_id not in visited:
                    new_path = path + [edge]
                    queue.append((neighbor_id, new_path))
        
        # 没有找到路径
        return None
    
    def get_linkage_summary(self) -> Dict[LinkageType, int]:
        """获取链接类型统计摘要
        
        Returns:
            Dict[LinkageType, int]: 每种链接类型的数量
        """
        summary = {}
        for linkage_type in LinkageType:
            count = len(self.get_edges_by_type(linkage_type))
            summary[linkage_type] = count
        
        return summary
    
    def export_to_json(self, filepath: str) -> bool:
        """将图导出为JSON文件
        
        Args:
            filepath: 导出文件路径
            
        Returns:
            bool: 如果导出成功则返回True，否则返回False
        """
        try:
            graph_data = {
                "graph_id": self.graph_id,
                "nodes": {},
                "edges": {}
            }
            
            # 导出节点数据，处理复杂属性
            for node_id, node in self.nodes.items():
                node_dict = node.to_dict()
                # 处理节点属性中的复杂对象
                if 'attributes' in node_dict:
                    for attr in node_dict['attributes']:
                        if 'value' in attr and attr['value'] is not None and not isinstance(attr['value'], (str, int, float, bool, list, dict, type(None))):
                            # 使用自定义编码器处理复杂值
                            encoder = CustomJSONEncoder()
                            attr['value'] = json.loads(encoder.encode(attr['value']))
                graph_data["nodes"][node_id] = node_dict
            
            # 导出边数据
            for edge_id, edge in self.edges.items():
                graph_data["edges"][edge_id] = edge.to_dict()
            
            # 导出遍历历史
            graph_data["traversal_history"] = {}
            for phase, edges in self.traversal_history.items():
                phase_name = phase.name
                graph_data["traversal_history"][phase_name] = [
                    edge.to_dict() for edge in edges
                ]
            
            # 写入文件，使用自定义编码器
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)
            
            logger.info(f"图数据成功导出到: {filepath}")
            return True
        except Exception as e:
            logger.error(f"导出图数据失败: {str(e)}")
            return False
    
    def load_from_json(self, filepath: str) -> bool:
        """从JSON文件加载图
        
        Args:
            filepath: 导入文件路径
            
        Returns:
            bool: 如果加载成功则返回True，否则返回False
        """
        try:
            # 读取文件
            with open(filepath, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
            
            # 重置图
            self.nodes = {}
            self.edges = {}
            self.node_id_to_edges = {}
            self.edge_type_index = {}
            self.traversal_history = {}
            
            # 导入节点数据
            for node_id, node_data in graph_data.get("nodes", {}).items():
                node = GraphNode.from_dict(node_data)
                self.add_node(node)
            
            # 导入边数据
            for edge_id, edge_data in graph_data.get("edges", {}).items():
                edge = GraphEdge.from_dict(edge_data)
                self.add_edge(edge)
            
            # 导入遍历历史
            history_data = graph_data.get("traversal_history", {})
            for phase_name, edges_data in history_data.items():
                # 从阶段名称获取TraversalPhase枚举
                phase = None
                for p in TraversalPhase:
                    if p.name == phase_name:
                        phase = p
                        break
                
                if phase:
                    edges = [GraphEdge.from_dict(edge_data) for edge_data in edges_data]
                    self.traversal_history[phase] = edges
            
            # 更新图ID
            self.graph_id = graph_data.get("graph_id", str(uuid.uuid4()))
            
            logger.info(f"图数据成功从: {filepath} 加载")
            return True
        except Exception as e:
            logger.error(f"加载图数据失败: {str(e)}")
            return False
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """获取图的统计信息
        
        Returns:
            Dict[str, Any]: 图的统计信息
        """
        stats = {
            "graph_id": self.graph_id,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "linkage_summary": {},
            "avg_node_degree": 0,
            "is_traversal_complete": self.traversal_complete,
            "current_phase": self.current_phase.name if self.current_phase else None
        }
        
        # 计算链接类型统计
        for linkage_type, count in self.get_linkage_summary().items():
            stats["linkage_summary"][linkage_type.value] = count
        
        # 计算平均节点度
        if self.nodes:
            total_degree = sum(self.get_node_degree(node_id) for node_id in self.nodes)
            stats["avg_node_degree"] = round(total_degree / len(self.nodes), 2)
        
        # 遍历历史统计
        if self.traversal_history:
            phase_stats = {}
            for phase, edges in self.traversal_history.items():
                phase_stats[phase.name] = len(edges)
            stats["phase_stats"] = phase_stats
        
        return stats
    
    def __str__(self) -> str:
        """返回图的字符串表示"""
        stats = self.get_graph_stats()
        return (
            f"ProgramLinkageGraph(ID: {stats['graph_id']})\n"\
            f"  节点数量: {stats['node_count']}\n"\
            f"  边数量: {stats['edge_count']}\n"\
            f"  平均节点度: {stats['avg_node_degree']}\n"\
            f"  遍历完成: {stats['is_traversal_complete']}\n"\
            f"  当前阶段: {stats['current_phase']}\n"\
            f"  链接类型统计: {stats['linkage_summary']}"
        )