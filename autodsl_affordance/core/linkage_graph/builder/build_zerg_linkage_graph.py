import os
import sys
import logging

# 添加项目根目录到Python路径
current_file_dir = os.path.dirname(os.path.abspath(__file__))
print(f"当前文件目录: {current_file_dir}")

# 计算项目根目录 - 从builder目录需要向上4级到达VLM-Play-StarCraft2目录
project_root = os.path.abspath(os.path.join(current_file_dir, '../../../../'))
sys.path.append(project_root)
print(f"添加项目根目录到Python路径: {project_root}")

# 打印Python路径中包含VLM-Play-StarCraft2的目录，验证是否正确添加
print("\nPython路径中包含VLM-Play-StarCraft2的目录:")
for path in sys.path:
    if 'VLM-Play-StarCraft2' in path:
        print(f"  - {path}")

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入实际的图构建类
from autodsl_affordance.core.linkage_graph.graph_builder import ProgramLinkageGraph

# 导入实际的Zerg单位类
from autodsl_affordance.races.zerg.ground_units.combat_units.zergling import ZergZergling
from autodsl_affordance.races.zerg.ground_units.combat_units.roach import ZergRoach
from autodsl_affordance.races.zerg.ground_units.suicide_units.baneling import ZergBaneling

def build_zerg_linkage_graph():
    """
    构建Zerg单位的联动图
    使用ProgramLinkageGraph类，从实际的Zerg单位类构建
    """
    logger.info("开始构建Zerg单位联动图")
    
    # 创建图实例 - 使用autodsl_affordance.core.linkage_graph.graph_builder中的ProgramLinkageGraph
    graph = ProgramLinkageGraph()
    
    # 收集所有实际的Zerg单位类
    zerg_unit_classes = [
        ZergZergling,
        ZergRoach,
        ZergBaneling
    ]
    
    logger.info(f"准备导入 {len(zerg_unit_classes)} 个实际Zerg单位类")
    
    # 严格按照ProgramLinkageGraph接口使用
    try:
        # 1. 从类对象构建节点
        node_count = graph.build_from_classes(zerg_unit_classes)
        logger.info(f"成功从类对象构建了 {node_count} 个节点")
        
        # 2. 执行多轮遍历构建关系（按照用户提供的示例方式）
        traversal_round = 0
        logger.info("开始执行多轮遍历构建关系")
        
        while not graph.traversal_complete:
            traversal_round += 1
            logger.info(f"执行遍历轮次: {traversal_round}")
            new_edges = graph.execute_single_traversal_phase()
            logger.info(f"本轮遍历发现 {len(new_edges)} 条新边")
            
            # 避免无限循环，设置最大遍历轮数
            if traversal_round > 10:
                logger.warning("达到最大遍历轮数，终止遍历")
                break
    except Exception as e:
        logger.error(f"构建联动图时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    
    logger.info("联动图构建完成")
    return graph

def analyze_graph_relationships(graph):
    """
    分析图中的关系
    
    Args:
        graph: 构建好的联动图实例
    """
    if not graph:
        logger.error("无效的图实例，无法分析")
        return
    
    logger.info("开始分析图关系")
    
    # 统计节点和边
    node_count = len(graph.nodes)
    edge_count = len(graph.edges)
    logger.info(f"图统计: {node_count} 个节点, {edge_count} 条边")
    
    # 统计边类型
    edge_type_counts = {}
    for edge in graph.edges.values():
        edge_type = edge.linkage_type.value
        edge_type_counts[edge_type] = edge_type_counts.get(edge_type, 0) + 1
    
    logger.info("边类型分布:")
    for edge_type, count in edge_type_counts.items():
        logger.info(f"  {edge_type}: {count} 条边")
    
    # 统计每个节点的连接数
    logger.info("节点连接数统计:")
    for node_id, node in graph.nodes.items():
        connected_edges = graph.node_id_to_edges.get(node_id, [])
        logger.info(f"  节点 {node_id}: {len(connected_edges)} 条连接")

if __name__ == "__main__":
    # 构建图
    graph = build_zerg_linkage_graph()
    
    if graph:
        # 分析图关系
        analyze_graph_relationships(graph)
        
        # 保存图到JSON文件
        output_dir = os.path.join(current_file_dir, '../graph')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'zerg_linkage_graph.json')
        
        try:
            success = graph.export_to_json(output_path)
            if success:
                logger.info(f"成功保存Zerg联动图到 {output_path}")
            else:
                logger.error(f"保存Zerg联动图失败")
        except Exception as e:
            logger.error(f"保存联动图时出错: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        logger.error("构建Zerg联动图失败")
