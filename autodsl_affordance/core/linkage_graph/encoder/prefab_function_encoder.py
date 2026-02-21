import os
import sys
import logging
import json
from typing import Dict, List, Tuple, Set, Any
from collections import defaultdict
from itertools import combinations

# 添加项目根目录到Python路径
current_file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_file_dir, '../../../../'))
sys.path.append(project_root)

from autodsl_affordance.core.linkage_graph.graph_builder import ProgramLinkageGraph
from autodsl_affordance.core.linkage_graph.edge import LinkageType

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PrefabFunctionEncoder:
    """基于Program Linkage Graph自动检测和封装组合技能的编码器"""
    
    def __init__(self, graph: ProgramLinkageGraph):
        """
        初始化编码器
        
        Args:
            graph: ProgramLinkageGraph实例
        """
        self.graph = graph
        self.prefab_functions = []
        self.function_counter = 0
    
    def encode_prefab_functions(self) -> List[Dict[str, Any]]:
        """
        编码所有预制函数
        
        Returns:
            List[Dict[str, Any]]: 预制函数列表
        """
        logger.info("开始编码预制函数")
        
        # 1. 编码一阶INTERACTION链接
        self._encode_interaction_functions()
        
        # 2. 编码COMBINATION链接的连通组件和最大团
        self._encode_combination_functions()
        
        # 3. 编码ASSOCIATION链接的连通组件和最大团
        self._encode_association_functions()
        
        # 4. 编码INVOCATION链接的连通组件和最大团
        self._encode_invocation_functions()
        
        # 5. 编码DEPENDENCY链接的连通组件和最大团
        self._encode_dependency_functions()
        
        logger.info(f"成功编码 {len(self.prefab_functions)} 个预制函数")
        return self.prefab_functions
    
    def _encode_interaction_functions(self):
        """
        编码一阶INTERACTION链接为预制函数
        """
        logger.info("编码INTERACTION链接为预制函数")
        
        # 获取所有INTERACTION边
        interaction_edges = self.graph.get_edges_by_type(LinkageType.INTERACTION)
        
        for edge in interaction_edges:
            source_node = self.graph.get_node(edge.source_node_id)
            target_node = self.graph.get_node(edge.target_node_id)
            
            # 生成战术描述
            tactic_category = "targeting"
            strategy_description = f"使用 {source_node.class_name} 针对 {target_node.class_name} 进行精确打击，利用单位克制关系获取优势"
            
            # 封装为目标设置函数
            function = {
                "function_id": f"INTERACTION_{self.function_counter}",
                "function_type": "interaction",
                "name": f"target_{source_node.class_name}_on_{target_node.class_name}",
                "description": f"设置 {source_node.class_name} 的目标为 {target_node.class_name}",
                "strategy_description": strategy_description,
                "tactic_category": tactic_category,
                "source_unit": source_node.class_name,
                "target_unit": target_node.class_name,
                "linkage_type": "interaction",
                "execution_type": "target_setting",
                "parameters": [
                    {
                        "name": "target_unit_tag",
                        "type": "int",
                        "description": f"{target_node.class_name} 的单位标签",
                        "domain": "valid_enemy_tags"
                    }
                ],
                "execution_flow": [
                    f"set_target({source_node.class_name}, target_unit_tag)"
                ],
                "evidence": edge.metadata.evidence,
                "confidence": edge.metadata.confidence
            }
            
            self.prefab_functions.append(function)
            self.function_counter += 1
    
    def _encode_combination_functions(self):
        """
        编码COMBINATION链接的连通组件和最大团为预制函数
        """
        logger.info("编码COMBINATION链接为预制函数")
        
        # 获取所有COMBINATION边
        combination_edges = self.graph.get_edges_by_type(LinkageType.COMBINATION)
        
        # 构建COMBINATION子图
        combination_subgraph = self._build_subgraph(combination_edges)
        
        # 检测连通组件
        connected_components = self._find_connected_components(combination_subgraph)
        
        for component in connected_components:
            if len(component) < 2:
                continue
            
            # 检测最大团
            max_cliques = self._find_max_cliques(combination_subgraph, component)
            
            for clique in max_cliques:
                if len(clique) < 2:
                    continue
                
                # 生成战术描述
                tactic_category = "scouting"
                unit_names = [node.class_name for node in clique]
                strategy_description = f"使用 {'、'.join(unit_names)} 进行协同侦察，实现高效的战场情报收集，各单位并行执行任务，发挥组合优势"
                
                # 构建执行流程
                execute_calls = [f"{node.class_name}.execute()" for node in clique]
                execution_flow_str = f"concurrent_execute([{', '.join(execute_calls)}])"
                
                # 封装为并发操作函数
                function = {
                    "function_id": f"COMBINATION_{self.function_counter}",
                    "function_type": "combination",
                    "name": f"coordinated_scouting_{'_'.join(sorted(unit_names))}",
                    "description": f"执行 {'、'.join(unit_names)} 的并发组合侦察操作",
                    "strategy_description": strategy_description,
                    "tactic_category": tactic_category,
                    "units": unit_names,
                    "linkage_type": "combination",
                    "execution_type": "concurrent",
                    "parameters": [
                        {
                            "name": "target_area",
                            "type": "str",
                            "description": "侦察目标区域",
                            "domain": ["enemy_base", "expansion", "middle", "flank"]
                        }
                    ],
                    "execution_flow": [execution_flow_str],
                    "evidence": ["基于COMBINATION链接的最大团检测"],
                    "confidence": 0.85
                }
                
                self.prefab_functions.append(function)
                self.function_counter += 1
    
    def _encode_association_functions(self):
        """
        编码ASSOCIATION链接的连通组件和最大团为预制函数
        """
        logger.info("编码ASSOCIATION链接为预制函数")
        
        # 获取所有ASSOCIATION边
        association_edges = self.graph.get_edges_by_type(LinkageType.ASSOCIATION)
        
        # 构建ASSOCIATION子图
        association_subgraph = self._build_subgraph(association_edges)
        
        # 检测连通组件
        connected_components = self._find_connected_components(association_subgraph)
        
        for component in connected_components:
            if len(component) < 2:
                continue
            
            # 检测最大团
            max_cliques = self._find_max_cliques(association_subgraph, component)
            
            for clique in max_cliques:
                if len(clique) < 2:
                    continue
                
                # 生成战术描述
                tactic_category = "frontline_combat"
                unit_names = [node.class_name for node in clique]
                strategy_description = f"使用 {'、'.join(unit_names)} 组成前线战斗群，根据战术需求执行移动、攻击或防御操作，实现多单位协同作战，发挥1+1>2的组合优势"
                
                # 构建执行流程
                execute_calls = [f"{node.class_name}.{{operation_type}}()" for node in clique]
                execution_flow_str = f"parallel_execute([{', '.join(execute_calls)}])"
                
                # 封装为并行操作函数
                function = {
                    "function_id": f"ASSOCIATION_{self.function_counter}",
                    "function_type": "association",
                    "name": f"frontline_combat_group_{'_'.join(sorted(unit_names))}",
                    "description": f"执行 {'、'.join(unit_names)} 的并行关联操作",
                    "strategy_description": strategy_description,
                    "tactic_category": tactic_category,
                    "units": unit_names,
                    "linkage_type": "association",
                    "execution_type": "parallel",
                    "parameters": [
                        {
                            "name": "operation_type",
                            "type": "str",
                            "description": "操作类型",
                            "domain": ["move", "attack", "defend"]
                        }
                    ],
                    "execution_flow": [execution_flow_str],
                    "evidence": ["基于ASSOCIATION链接的最大团检测"],
                    "confidence": 0.8
                }
                
                self.prefab_functions.append(function)
                self.function_counter += 1
    
    def _encode_invocation_functions(self):
        """
        编码INVOCATION链接的连通组件和最大团为预制函数
        """
        logger.info("编码INVOCATION链接为预制函数")
        
        # 获取所有INVOCATION边
        invocation_edges = self.graph.get_edges_by_type(LinkageType.INVOCATION)
        
        # 构建INVOCATION子图
        invocation_subgraph = self._build_subgraph(invocation_edges)
        
        # 检测连通组件
        connected_components = self._find_connected_components(invocation_subgraph)
        
        for component in connected_components:
            if len(component) < 2:
                continue
            
            # 检测最大团
            max_cliques = self._find_max_cliques(invocation_subgraph, component)
            
            for clique in max_cliques:
                if len(clique) < 2:
                    continue
                
                # 生成战术描述
                tactic_category = "tactical_sequence"
                unit_names = [node.class_name for node in clique]
                strategy_description = f"使用 {'、'.join(unit_names)} 执行顺序战术操作，针对特定目标单位类型进行精准打击，实现战术流程的有序执行"
                
                # 构建执行流程
                execute_calls = [f"{node.class_name}.invoke({{target_unit}})" for node in clique]
                execution_flow_str = f"sequential_execute([{', '.join(execute_calls)}])"
                
                # 封装为顺序操作函数
                function = {
                    "function_id": f"INVOCATION_{self.function_counter}",
                    "function_type": "invocation",
                    "name": f"tactical_sequence_{'_'.join(sorted(unit_names))}",
                    "description": f"执行 {'、'.join(unit_names)} 的顺序调用操作",
                    "strategy_description": strategy_description,
                    "tactic_category": tactic_category,
                    "units": unit_names,
                    "linkage_type": "invocation",
                    "execution_type": "sequential",
                    "parameters": [
                        {
                            "name": "target_unit",
                            "type": "str",
                            "description": "目标单位类型",
                            "domain": "valid_unit_types"
                        }
                    ],
                    "execution_flow": [execution_flow_str],
                    "evidence": ["基于INVOCATION链接的最大团检测"],
                    "confidence": 0.9
                }
                
                self.prefab_functions.append(function)
                self.function_counter += 1
    
    def _encode_dependency_functions(self):
        """
        编码DEPENDENCY链接的连通组件和最大团为预制函数
        """
        logger.info("编码DEPENDENCY链接为预制函数")
        
        # 获取所有DEPENDENCY边
        dependency_edges = self.graph.get_edges_by_type(LinkageType.DEPENDENCY)
        
        # 构建DEPENDENCY子图
        dependency_subgraph = self._build_subgraph(dependency_edges)
        
        # 检测连通组件
        connected_components = self._find_connected_components(dependency_subgraph)
        
        for component in connected_components:
            if len(component) < 2:
                continue
            
            # 检测最大团
            max_cliques = self._find_max_cliques(dependency_subgraph, component)
            
            for clique in max_cliques:
                if len(clique) < 2:
                    continue
                
                # 生成战术描述
                tactic_category = "strategic_deployment"
                unit_names = [node.class_name for node in clique]
                strategy_description = f"使用 {'、'.join(unit_names)} 进行战略性部署，按照单位依赖关系顺序执行操作，合理分配资源，实现高效的战术执行"
                
                # 构建执行流程
                execute_calls = [f"{node.class_name}.execute({{resource_allocation}})" for node in clique]
                execution_flow_str = f"sequential_execute([{', '.join(execute_calls)}])"
                
                # 封装为顺序操作函数
                function = {
                    "function_id": f"DEPENDENCY_{self.function_counter}",
                    "function_type": "dependency",
                    "name": f"strategic_deployment_{'_'.join(sorted(unit_names))}",
                    "description": f"执行 {'、'.join(unit_names)} 的依赖顺序操作",
                    "strategy_description": strategy_description,
                    "tactic_category": tactic_category,
                    "units": unit_names,
                    "linkage_type": "dependency",
                    "execution_type": "sequential",
                    "parameters": [
                        {
                            "name": "resource_allocation",
                            "type": "Dict[str, int]",
                            "description": "资源分配",
                            "domain": "valid_resource_ranges"
                        }
                    ],
                    "execution_flow": [execution_flow_str],
                    "evidence": ["基于DEPENDENCY链接的最大团检测"],
                    "confidence": 0.95
                }
                
                self.prefab_functions.append(function)
                self.function_counter += 1
    
    def _build_subgraph(self, edges: List) -> Dict[str, List[str]]:
        """
        构建子图
        
        Args:
            edges: 边列表
            
        Returns:
            Dict[str, List[str]]: 子图邻接表
        """
        subgraph = defaultdict(list)
        
        for edge in edges:
            source_id = edge.source_node_id
            target_id = edge.target_node_id
            
            subgraph[source_id].append(target_id)
            subgraph[target_id].append(source_id)
        
        return subgraph
    
    def _find_connected_components(self, subgraph: Dict[str, List[str]]) -> List[List[Any]]:
        """
        查找连通组件
        
        Args:
            subgraph: 子图邻接表
            
        Returns:
            List[List[Any]]: 连通组件列表
        """
        visited = set()
        components = []
        
        for node_id in subgraph:
            if node_id not in visited:
                # BFS查找连通组件
                queue = [node_id]
                visited.add(node_id)
                component = []
                
                while queue:
                    current = queue.pop(0)
                    component.append(self.graph.get_node(current))
                    
                    for neighbor in subgraph[current]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                
                components.append(component)
        
        return components
    
    def _find_max_cliques(self, subgraph: Dict[str, List[str]], component: List) -> List[List[Any]]:
        """
        查找最大团
        
        Args:
            subgraph: 子图邻接表
            component: 连通组件
            
        Returns:
            List[List[Any]]: 最大团列表
        """
        max_cliques = []
        node_ids = [node.node_id for node in component]
        
        # 尝试所有可能的团大小，从最大的开始
        for size in range(len(node_ids), 1, -1):
            for combo in combinations(node_ids, size):
                # 检查是否是团
                is_clique = True
                for i in range(size):
                    for j in range(i + 1, size):
                        if combo[j] not in subgraph[combo[i]]:
                            is_clique = False
                            break
                    if not is_clique:
                        break
                
                if is_clique:
                    # 检查是否是最大团
                    is_maximal = True
                    for node_id in node_ids:
                        if node_id not in combo:
                            # 检查添加该节点后是否仍然是团
                            new_combo = list(combo) + [node_id]
                            new_is_clique = True
                            for i in range(len(new_combo)):
                                for j in range(i + 1, len(new_combo)):
                                    if new_combo[j] not in subgraph[new_combo[i]]:
                                        new_is_clique = False
                                        break
                                if not new_is_clique:
                                    break
                            if new_is_clique:
                                is_maximal = False
                                break
                    
                    if is_maximal:
                        # 转换为节点对象
                        clique_nodes = [self.graph.get_node(node_id) for node_id in combo]
                        max_cliques.append(clique_nodes)
        
        return max_cliques
    
    def save_prefab_functions(self, output_path: str):
        """
        保存预制函数到JSON文件
        
        Args:
            output_path: 输出文件路径
        """
        logger.info(f"保存预制函数到 {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.prefab_functions, f, ensure_ascii=False, indent=2)
        
        logger.info(f"成功保存 {len(self.prefab_functions)} 个预制函数")

# 测试代码
if __name__ == "__main__":
    # 从JSON加载图
    from autodsl_affordance.core.linkage_graph.graph_builder import ProgramLinkageGraph
    
    # 构建图
    graph = ProgramLinkageGraph()
    graph.load_from_json("../graph/protoss_linkage_graph.json")
    
    # 编码预制函数
    encoder = PrefabFunctionEncoder(graph)
    prefab_functions = encoder.encode_prefab_functions()
    
    # 保存预制函数
    encoder.save_prefab_functions("../prefab_functions/protoss_prefab_functions.json")
    
    print(f"成功编码 {len(prefab_functions)} 个预制函数")
    for func in prefab_functions[:5]:
        print(f"\n函数ID: {func['function_id']}")
        print(f"名称: {func['name']}")
        print(f"描述: {func['description']}")
        print(f"执行类型: {func['execution_type']}")
