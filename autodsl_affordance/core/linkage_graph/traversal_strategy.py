from typing import List, Dict, Any, Optional, Set
from enum import Enum
from .edge import LinkageType, GraphEdge
from .node import GraphNode
import inspect
import importlib
import os
import re

class TraversalPhase(Enum):
    """遍历阶段枚举"""
    PHASE_1_INTERACTION = 1     # 阶段1：识别交互关系
    PHASE_2_COMBINATION = 2     # 阶段2：识别组合关系
    PHASE_3_ASSOCIATION = 3     # 阶段3：识别关联关系
    PHASE_4_DEPENDENCY = 4      # 阶段4：识别依赖关系
    PHASE_5_INVOCATION = 5      # 阶段5：识别调用关系

class TraversalStrategy:
    """多轮图遍历策略类"""
    
    def __init__(self):
        # 遍历阶段顺序
        self.traversal_order = [
            TraversalPhase.PHASE_1_INTERACTION,
            TraversalPhase.PHASE_2_COMBINATION,
            TraversalPhase.PHASE_3_ASSOCIATION,
            TraversalPhase.PHASE_4_DEPENDENCY,
            TraversalPhase.PHASE_5_INVOCATION
        ]
        
        # 每阶段的链接类型映射
        self.phase_to_linkage_types = {
            TraversalPhase.PHASE_1_INTERACTION: [LinkageType.INTERACTION],
            TraversalPhase.PHASE_2_COMBINATION: [LinkageType.COMBINATION],
            TraversalPhase.PHASE_3_ASSOCIATION: [LinkageType.ASSOCIATION],
            TraversalPhase.PHASE_4_DEPENDENCY: [LinkageType.DEPENDENCY],
            TraversalPhase.PHASE_5_INVOCATION: [LinkageType.INVOCATION]
        }
    
    def get_next_phase(self, current_phase: Optional[TraversalPhase]) -> Optional[TraversalPhase]:
        """获取下一个遍历阶段"""
        if current_phase is None:
            return self.traversal_order[0]
        
        current_index = self.traversal_order.index(current_phase)
        if current_index < len(self.traversal_order) - 1:
            return self.traversal_order[current_index + 1]
        return None
    
    def get_linkage_types_for_phase(self, phase: TraversalPhase) -> List[LinkageType]:
        """获取指定阶段的链接类型"""
        return self.phase_to_linkage_types.get(phase, [])
    
    def identify_interaction_links(self, nodes: Dict[str, GraphNode], 
                                  existing_edges: Set[GraphEdge]) -> List[GraphEdge]:
        """阶段1：识别交互关系
        
        交互关系定义为：两个单位类之间存在逻辑上的交互，通常基于游戏内的克制关系、协同效应等
        """
        new_edges = []
        
        for node_id, node in nodes.items():
            # 1. 基于克制关系的交互（从strong_against和weak_against属性直接提取）
            if hasattr(node, 'strong_against'):
                for strong_target in node.strong_against:
                    for target_node_id, target_node in nodes.items():
                        if node_id != target_node_id and \
                           strong_target.lower() in target_node.class_name.lower():
                            
                            edge = GraphEdge(
                                source_node_id=node_id,
                                target_node_id=target_node_id,
                                linkage_type=LinkageType.INTERACTION,
                                description=f"{node.class_name} 强势对抗 {target_node.class_name}",
                                confidence=0.85,
                                evidence=[f"克制关系数据显示 {node.class_name} 强势对抗 {strong_target}"]
                            )
                            
                            if edge not in existing_edges:
                                new_edges.append(edge)
            
            if hasattr(node, 'weak_against'):
                for weak_target in node.weak_against:
                    for target_node_id, target_node in nodes.items():
                        if node_id != target_node_id and \
                           weak_target.lower() in target_node.class_name.lower():
                            
                            edge = GraphEdge(
                                source_node_id=node_id,
                                target_node_id=target_node_id,
                                linkage_type=LinkageType.INTERACTION,
                                description=f"{node.class_name} 弱势对抗 {target_node.class_name}",
                                confidence=0.85,
                                evidence=[f"克制关系数据显示 {node.class_name} 弱势对抗 {weak_target}"]
                            )
                            
                            if edge not in existing_edges:
                                new_edges.append(edge)
            
            # 2. 基于战术上下文的交互
            if node.tactical_context:
                # 从tactical_context中提取协同单位
                synergies = node.tactical_context.get('synergies', [])
                for synergy in synergies:
                    for target_node_id, target_node in nodes.items():
                        if node_id != target_node_id and \
                           (target_node.class_name.lower() in synergy.lower() or \
                            target_node.description.lower() in synergy.lower()):
                            
                            edge = GraphEdge(
                                source_node_id=node_id,
                                target_node_id=target_node_id,
                                linkage_type=LinkageType.INTERACTION,
                                description=f"{node.class_name} 与 {target_node.class_name} 具有战术协同",
                                confidence=0.8,
                                evidence=[f"战术上下文显示协同: {synergy}"]
                            )
                            
                            if edge not in existing_edges:
                                new_edges.append(edge)
            
            # 3. 基于LLM接口中的共同战术
            if node.llm_interface:
                common_tactics = node.llm_interface.get('common_tactics', [])
                for tactic in common_tactics:
                    for target_node_id, target_node in nodes.items():
                        if node_id != target_node_id and \
                           (target_node.class_name.lower() in tactic.lower() or \
                            target_node.description.lower() in tactic.lower()):
                            
                            edge = GraphEdge(
                                source_node_id=node_id,
                                target_node_id=target_node_id,
                                linkage_type=LinkageType.INTERACTION,
                                description=f"{node.class_name} 与 {target_node.class_name} 在战术 '{tactic}' 中协同使用",
                                confidence=0.75,
                                evidence=[f"LLM接口共同战术: {tactic}"]
                            )
                            
                            if edge not in existing_edges:
                                new_edges.append(edge)
        
        return new_edges
    
    def identify_combination_links(self, nodes: Dict[str, GraphNode], 
                                   existing_edges: Set[GraphEdge],
                                   interaction_edges: List[GraphEdge]) -> List[GraphEdge]:
        """阶段2：识别组合关系
        
        组合关系定义为：两个或多个单位类在战术上经常组合使用，形成协同效应
        """
        new_edges = []
        
        # 1. 基于战术上下文的阵型偏好和协同关系
        for node_id, node in nodes.items():
            if node.tactical_context:
                # 从tactical_context中提取协同单位
                synergies = node.tactical_context.get('synergies', [])
                for synergy in synergies:
                    for target_node_id, target_node in nodes.items():
                        if node_id != target_node_id and \
                           (target_node.class_name.lower() in synergy.lower() or \
                            target_node.description.lower() in synergy.lower()):
                            
                            edge = GraphEdge(
                                source_node_id=node_id,
                                target_node_id=target_node_id,
                                linkage_type=LinkageType.COMBINATION,
                                description=f"{node.class_name} 与 {target_node.class_name} 形成战术组合",
                                confidence=0.85,
                                evidence=[f"战术协同: {synergy}"]
                            )
                            
                            if edge not in existing_edges:
                                new_edges.append(edge)
        
        # 2. 基于预置函数候选中的组合使用模式
        for node_id, node in nodes.items():
            prefab_candidates = getattr(node, 'prefab_function_candidates', [])
            for candidate in prefab_candidates:
                # 检查执行流程中是否涉及其他单位
                execution_flow = candidate.get('execution_flow', [])
                for step in execution_flow:
                    for target_node_id, target_node in nodes.items():
                        if node_id != target_node_id and \
                           (target_node.class_name.lower() in step.lower() or \
                            target_node.description.lower() in step.lower()):
                            
                            edge = GraphEdge(
                                source_node_id=node_id,
                                target_node_id=target_node_id,
                                linkage_type=LinkageType.COMBINATION,
                                description=f"{node.class_name} 与 {target_node.class_name} 在战术 '{candidate.get('function_name', '')}' 中组合使用",
                                confidence=0.9,
                                evidence=[f"预置函数执行流程: {step}"]
                            )
                            
                            if edge not in existing_edges:
                                new_edges.append(edge)
        
        # 3. 基于战术角色互补的组合
        for node_id, node in nodes.items():
            if node.llm_interface:
                primary_roles = node.llm_interface.get('primary_role', [])
                
                for target_node_id, target_node in nodes.items():
                    if node_id != target_node_id and target_node.llm_interface:
                        target_roles = target_node.llm_interface.get('primary_role', [])
                        
                        # 检查角色互补性（前线+后排，肉盾+输出等）
                        if ('前线' in primary_roles or '肉盾' in primary_roles) and \
                           ('后排' in target_roles or '输出' in target_roles):
                            
                            edge = GraphEdge(
                                source_node_id=node_id,
                                target_node_id=target_node_id,
                                linkage_type=LinkageType.COMBINATION,
                                description=f"{node.class_name} (前线/肉盾) 与 {target_node.class_name} (后排/输出) 形成互补组合",
                                confidence=0.85,
                                evidence=[f"角色互补: {primary_roles[0]} + {target_roles[0]}"]
                            )
                            
                            if edge not in existing_edges:
                                new_edges.append(edge)
        
        # 4. 基于相同战术关键词的组合
        for node_id, node in nodes.items():
            if node.llm_interface:
                tactical_keywords = node.llm_interface.get('tactical_keywords', [])
                
                for target_node_id, target_node in nodes.items():
                    if node_id != target_node_id and target_node.llm_interface:
                        target_keywords = target_node.llm_interface.get('tactical_keywords', [])
                        
                        # 计算共同关键词数量
                        common_keywords = set(tactical_keywords) & set(target_keywords)
                        if len(common_keywords) >= 2:
                            
                            edge = GraphEdge(
                                source_node_id=node_id,
                                target_node_id=target_node_id,
                                linkage_type=LinkageType.COMBINATION,
                                description=f"{node.class_name} 与 {target_node.class_name} 具有共同战术关键词",
                                confidence=0.75,
                                evidence=[f"共同战术关键词: {', '.join(common_keywords)}"]
                            )
                            
                            if edge not in existing_edges:
                                new_edges.append(edge)
        
        return new_edges
    
    def identify_association_links(self, nodes: Dict[str, GraphNode],
                                   existing_edges: Set[GraphEdge],
                                   interaction_edges: List[GraphEdge],
                                   combination_edges: List[GraphEdge]) -> List[GraphEdge]:
        """阶段3：识别关联关系
        
        关联关系定义为：两个单位类之间存在某种松散的关联，但不如组合关系紧密
        优化策略：减少同种族/同类型的全连接，只保留有实际战术关联的单位
        """
        new_edges = []
        
        # 1. 基于战术协同关系的关联（从tactical_context中提取）
        for node_id, node in nodes.items():
            if node.tactical_context:
                synergies = node.tactical_context.get('synergies', [])
                for synergy in synergies:
                    # 查找提到的其他单位
                    for target_node_id, target_node in nodes.items():
                        if node_id != target_node_id and \
                           (target_node.class_name.lower() in synergy.lower() or \
                            target_node.description.lower() in synergy.lower()):
                            
                            edge = GraphEdge(
                                source_node_id=node_id,
                                target_node_id=target_node_id,
                                linkage_type=LinkageType.ASSOCIATION,
                                description=f"{node.class_name} 与 {target_node.class_name} 具有战术协同关系",
                                confidence=0.8,
                                evidence=[f"战术协同: {synergy}"]
                            )
                            
                            if edge not in existing_edges:
                                new_edges.append(edge)
        
        # 2. 基于相同建造设施的关联
        facility_groups = {}
        for node_id, node in nodes.items():
            # 从类名或描述中提取建造设施信息
            if 'Gateway' in node.class_name or 'Gateway' in node.description:
                facility = 'Gateway'
            elif 'Stargate' in node.class_name or 'Stargate' in node.description:
                facility = 'Stargate'
            elif 'Robotics' in node.class_name or 'Robotics' in node.description:
                facility = 'Robotics Facility'
            else:
                continue
            
            if facility not in facility_groups:
                facility_groups[facility] = []
            facility_groups[facility].append(node_id)
        
        # 为相同建造设施的单位创建关联关系
        for facility, node_ids in facility_groups.items():
            for i in range(len(node_ids)):
                for j in range(i + 1, len(node_ids)):
                    edge = GraphEdge(
                        source_node_id=node_ids[i],
                        target_node_id=node_ids[j],
                        linkage_type=LinkageType.ASSOCIATION,
                        description=f"同由{facility}建造的单位",
                        confidence=0.85,
                        evidence=[f"相同建造设施: {facility}"]
                    )
                    
                    if edge not in existing_edges:
                        new_edges.append(edge)
        
        # 3. 基于战术角色的关联（只保留核心关联）
        role_groups = {}
        for node_id, node in nodes.items():
            if node.llm_interface:
                primary_roles = node.llm_interface.get('primary_role', [])
                for role in primary_roles:
                    if role not in role_groups:
                        role_groups[role] = []
                    role_groups[role].append(node_id)
        
        # 为相同战术角色的单位创建关联关系（限制数量）
        for role, node_ids in role_groups.items():
            # 只保留前5个单位的关联，避免数量膨胀
            for i in range(min(5, len(node_ids))):
                for j in range(i + 1, min(5, len(node_ids))):
                    edge = GraphEdge(
                        source_node_id=node_ids[i],
                        target_node_id=node_ids[j],
                        linkage_type=LinkageType.ASSOCIATION,
                        description=f"具有相同战术角色 '{role}' 的单位",
                        confidence=0.75,
                        evidence=[f"相同战术角色: {role}"]
                    )
                    
                    if edge not in existing_edges:
                        new_edges.append(edge)
        
        return new_edges
    
    def identify_dependency_links(self, nodes: Dict[str, GraphNode],
                                 existing_edges: Set[GraphEdge],
                                 interaction_edges: List[GraphEdge],
                                 combination_edges: List[GraphEdge],
                                 association_edges: List[GraphEdge]) -> List[GraphEdge]:
        """阶段4：识别依赖关系
        
        依赖关系定义为：一个单位类依赖于另一个单位类才能发挥最大效用
        """
        new_edges = []
        
        # 1. 基于战术协同的依赖关系（从tactical_info中提取）
        for node_id, node in nodes.items():
            if hasattr(node, 'tactical_info') and node.tactical_info:
                synergies = node.tactical_info.get('synergies', [])
                for synergy_unit in synergies:
                    for target_node_id, target_node in nodes.items():
                        if node_id != target_node_id and \
                           synergy_unit.lower() in target_node.class_name.lower():
                            
                            edge = GraphEdge(
                                source_node_id=node_id,
                                target_node_id=target_node_id,
                                linkage_type=LinkageType.DEPENDENCY,
                                description=f"{node.class_name} 在战术上依赖于 {target_node.class_name} 形成协同",
                                confidence=0.85,
                                evidence=[f"战术协同: {synergy_unit}"]
                            )
                            
                            if edge not in existing_edges:
                                new_edges.append(edge)
        
        # 2. 基于建造设施的依赖关系
        for node_id, node in nodes.items():
            # 根据单位类型推断建造设施
            unit_type = node.unit_type.lower()
            class_name = node.class_name.lower()
            
            # 推断建造设施
            facility = None
            if 'gateway' in class_name or 'adept' in class_name or 'zealot' in class_name or 'stalker' in class_name or 'sentry' in class_name or 'high templar' in class_name:
                facility = 'Gateway'
            elif 'stargate' in class_name or 'phoenix' in class_name or 'oracle' in class_name:
                facility = 'Stargate'
            elif 'robotics' in class_name or 'immortal' in class_name or 'colossus' in class_name or 'disruptor' in class_name or 'observer' in class_name:
                facility = 'Robotics Facility'
            
            if facility:
                # 查找建造设施对应的节点
                for target_node_id, target_node in nodes.items():
                    if node_id != target_node_id and \
                       facility.lower() in target_node.class_name.lower():
                        
                        edge = GraphEdge(
                            source_node_id=node_id,
                            target_node_id=target_node_id,
                            linkage_type=LinkageType.DEPENDENCY,
                            description=f"{node.class_name} 依赖于 {target_node.class_name} 建造",
                            confidence=0.95,
                            evidence=[f"建造设施: {facility}"]
                        )
                        
                        if edge not in existing_edges:
                            new_edges.append(edge)
        
        # 3. 基于升级需求的依赖关系
        for node_id, node in nodes.items():
            if hasattr(node, 'upgrades') and node.upgrades:
                for upgrade_name, upgrade_data in node.upgrades.items():
                    researched_from = upgrade_data.get('researched_from', '')
                    if researched_from:
                        # 查找研究设施对应的节点
                        for target_node_id, target_node in nodes.items():
                            if node_id != target_node_id and \
                               (target_node.class_name.lower() in researched_from.lower() or \
                                'twilight' in researched_from.lower() or \
                                'forge' in researched_from.lower() or \
                                'cybernetics' in researched_from.lower()):
                                
                                edge = GraphEdge(
                                    source_node_id=node_id,
                                    target_node_id=target_node_id,
                                    linkage_type=LinkageType.DEPENDENCY,
                                    description=f"{node.class_name} 的 {upgrade_name} 升级依赖于研究设施",
                                    confidence=0.9,
                                    evidence=[f"升级需求: {researched_from}"]
                                )
                                
                                if edge not in existing_edges:
                                    new_edges.append(edge)
        
        # 4. 基于能力协同的依赖关系
        for node_id, node in nodes.items():
            if hasattr(node, 'abilities') and node.abilities:
                for ability_name, ability_data in node.abilities.items():
                    # 检查能力是否需要其他单位支持
                    if 'charge' in ability_name.lower() or 'blink' in ability_name.lower() or 'force field' in ability_name.lower():
                        # 这些能力通常需要特定的升级或支持
                        for target_node_id, target_node in nodes.items():
                            if node_id != target_node_id and \
                               (target_node.class_name.lower() in ['twilight council', 'cybernetics core', 'forge']):
                                
                                edge = GraphEdge(
                                    source_node_id=node_id,
                                    target_node_id=target_node_id,
                                    linkage_type=LinkageType.DEPENDENCY,
                                    description=f"{node.class_name} 的 {ability_name} 能力依赖于研究设施",
                                    confidence=0.85,
                                    evidence=[f"能力需求: {ability_name}"]
                                )
                                
                                if edge not in existing_edges:
                                    new_edges.append(edge)
        
        return new_edges
    
    def identify_invocation_links(self, nodes: Dict[str, GraphNode],
                                 existing_edges: Set[GraphEdge],
                                 interaction_edges: List[GraphEdge],
                                 combination_edges: List[GraphEdge],
                                 association_edges: List[GraphEdge],
                                 dependency_edges: List[GraphEdge]) -> List[GraphEdge]:
        """阶段5：识别调用关系
        
        调用关系定义为：一个单位类的方法明确调用了另一个单位类的方法
        """
        new_edges = []
        
        # 1. 基于方法参数类型的调用关系
        for node_id, node in nodes.items():
            for method in node.methods:
                for param in method.parameters:
                    param_type = param.get('type', '')
                    
                    # 查找对应的目标节点
                    for target_node_id, target_node in nodes.items():
                        if node_id != target_node_id and \
                           param_type.lower() in target_node.class_name.lower():
                            
                            edge = GraphEdge(
                                source_node_id=node_id,
                                target_node_id=target_node_id,
                                linkage_type=LinkageType.INVOCATION,
                                source_method=method.name,
                                description=f"{node.class_name}.{method.name} 方法通过参数引用了 {target_node.class_name}",
                                confidence=0.85,
                                evidence=[f"方法参数类型: {param_type}"]
                            )
                            
                            if edge not in existing_edges:
                                new_edges.append(edge)
        
        # 2. 基于方法返回类型的调用关系
        for node_id, node in nodes.items():
            for method in node.methods:
                return_type = method.return_type
                
                # 查找对应的目标节点
                for target_node_id, target_node in nodes.items():
                    if node_id != target_node_id and \
                       return_type.lower() in target_node.class_name.lower():
                        
                        edge = GraphEdge(
                            source_node_id=node_id,
                            target_node_id=target_node_id,
                            linkage_type=LinkageType.INVOCATION,
                            source_method=method.name,
                            description=f"{node.class_name}.{method.name} 方法返回 {target_node.class_name} 类型",
                            confidence=0.8,
                            evidence=[f"方法返回类型: {return_type}"]
                        )
                        
                        if edge not in existing_edges:
                            new_edges.append(edge)
        
        # 3. 基于预置函数中的单位引用
        for node_id, node in nodes.items():
            prefab_candidates = getattr(node, 'prefab_function_candidates', [])
            for candidate in prefab_candidates:
                function_name = candidate.get('function_name', '')
                if function_name:
                    # 查找函数名中提到的其他单位
                    for target_node_id, target_node in nodes.items():
                        if node_id != target_node_id and \
                           target_node.class_name.lower() in function_name.lower():
                            
                            edge = GraphEdge(
                                source_node_id=node_id,
                                target_node_id=target_node_id,
                                linkage_type=LinkageType.INVOCATION,
                                source_method=function_name,
                                description=f"{node.class_name} 的预置函数 {function_name} 引用了 {target_node.class_name}",
                                confidence=0.85,
                                evidence=[f"预置函数: {function_name}"]
                            )
                            
                            if edge not in existing_edges:
                                new_edges.append(edge)
        
        return new_edges
    
    def execute_phase(self, phase: TraversalPhase, nodes: Dict[str, GraphNode],
                     existing_edges: Set[GraphEdge], edge_history: Dict[TraversalPhase, List[GraphEdge]]) -> List[GraphEdge]:
        """执行指定的遍历阶段"""
        linkage_types = self.get_linkage_types_for_phase(phase)
        
        # 获取历史边数据
        interaction_edges = edge_history.get(TraversalPhase.PHASE_1_INTERACTION, [])
        combination_edges = edge_history.get(TraversalPhase.PHASE_2_COMBINATION, [])
        association_edges = edge_history.get(TraversalPhase.PHASE_3_ASSOCIATION, [])
        dependency_edges = edge_history.get(TraversalPhase.PHASE_4_DEPENDENCY, [])
        
        # 根据阶段执行相应的识别逻辑
        if phase == TraversalPhase.PHASE_1_INTERACTION:
            new_edges = self.identify_interaction_links(nodes, existing_edges)
        elif phase == TraversalPhase.PHASE_2_COMBINATION:
            new_edges = self.identify_combination_links(nodes, existing_edges, interaction_edges)
        elif phase == TraversalPhase.PHASE_3_ASSOCIATION:
            new_edges = self.identify_association_links(nodes, existing_edges, 
                                                       interaction_edges, combination_edges)
        elif phase == TraversalPhase.PHASE_4_DEPENDENCY:
            new_edges = self.identify_dependency_links(nodes, existing_edges,
                                                      interaction_edges, combination_edges,
                                                      association_edges)
        elif phase == TraversalPhase.PHASE_5_INVOCATION:
            new_edges = self.identify_invocation_links(nodes, existing_edges,
                                                      interaction_edges, combination_edges,
                                                      association_edges, dependency_edges)
        else:
            new_edges = []
        
        # 设置发现轮次
        for edge in new_edges:
            edge.metadata.discovered_in_round = phase.value
        
        return new_edges