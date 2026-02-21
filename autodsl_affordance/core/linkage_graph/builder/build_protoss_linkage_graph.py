import os
import sys
import logging

# 添加项目根目录到Python路径
# 从当前文件路径向上遍历到项目根目录
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

# 导入实际的Protoss单位类
from autodsl_affordance.races.protoss.ground_units.gateway_units.zealot import ProtossZealot
from autodsl_affordance.races.protoss.ground_units.gateway_units.stalker import ProtossStalker
from autodsl_affordance.races.protoss.ground_units.gateway_units.sentry import ProtossSentry
from autodsl_affordance.races.protoss.ground_units.gateway_units.high_templar import ProtossHighTemplar
from autodsl_affordance.races.protoss.ground_units.gateway_units.adept import ProtossAdept
from autodsl_affordance.races.protoss.ground_units.robotics_units.immortal import ProtossImmortal
from autodsl_affordance.races.protoss.ground_units.robotics_units.colossus import ProtossColossus
from autodsl_affordance.races.protoss.ground_units.robotics_units.disruptor import ProtossDisruptor
from autodsl_affordance.races.protoss.ground_units.special_units.archon import ProtossArchon
from autodsl_affordance.races.protoss.air_units.stargate_units.phoenix import ProtossPhoenix
from autodsl_affordance.races.protoss.air_units.stargate_units.oracle import ProtossOracle
from autodsl_affordance.races.protoss.air_units.special_units.observer import ProtossObserver

def build_protoss_linkage_graph():
    """
    构建Protoss单位的联动图
    使用ProgramLinkageGraph类，从实际的Protoss单位类构建
    """
    logger.info("开始构建Protoss单位联动图")
    
    # 创建图实例 - 使用autodsl_affordance.core.linkage_graph.graph_builder中的ProgramLinkageGraph
    graph = ProgramLinkageGraph()
    
    # 收集所有实际的Protoss单位类
    protoss_unit_classes = [
        ProtossZealot,
        ProtossStalker,
        ProtossSentry,
        ProtossHighTemplar,
        ProtossAdept,
        ProtossImmortal,
        ProtossColossus,
        ProtossDisruptor,
        ProtossArchon,
        ProtossPhoenix,
        ProtossOracle,
        ProtossObserver
    ]
    
    logger.info(f"准备导入 {len(protoss_unit_classes)} 个实际Protoss单位类")
    
    # 严格按照ProgramLinkageGraph接口使用
    try:
        # 1. 从类对象构建节点
        node_count = graph.build_from_classes(protoss_unit_classes)
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
    """
    if not graph:
        logger.error("无法分析空图")
        return
    
    logger.info("开始分析图中的关系")
    
    # 获取图的统计信息
    stats = graph.get_graph_stats()
    logger.info(f"图统计信息: {stats}")
    
    # 打印链接类型统计
    logger.info("链接类型统计:")
    for linkage_type, count in stats['linkage_summary'].items():
        logger.info(f"  {linkage_type}: {count}")
    
    # 分析高连接度节点
    logger.info("高连接度节点分析:")
    high_degree_nodes = []
    for node_id in graph.nodes:
        degree = graph.get_node_degree(node_id)
        if degree >= 2:  # 连接数大于等于2的节点
            node = graph.get_node(node_id)
            high_degree_nodes.append((node.class_name, degree))
    
    # 按连接度排序并打印
    high_degree_nodes.sort(key=lambda x: x[1], reverse=True)
    for node_name, degree in high_degree_nodes[:5]:  # 打印前5个
        logger.info(f"  {node_name}: {degree} 个连接")
    
    # 打印一些关键关系示例
    logger.info("关键关系示例:")
    # 尝试获取一些边示例
    if graph.edges:
        edge_count = 0
        for edge_id, edge in graph.edges.items():
            if edge_count >= 5:  # 只打印前5个关系
                break
            source_node = graph.get_node(edge.source_node_id)
            target_node = graph.get_node(edge.target_node_id)
            logger.info(f"  {source_node.class_name} -[{edge.linkage_type.value}]-> {target_node.class_name}")
            edge_count += 1

def save_graph_to_json(graph, output_path):
    """
    保存图到JSON文件
    """
    if not graph:
        logger.error("无法保存空图")
        return False
    
    logger.info(f"保存图到文件: {output_path}")
    
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 导出图到JSON
        success = graph.export_to_json(output_path)
        if success:
            logger.info(f"图成功保存到 {output_path}")
            return True
        else:
            logger.error("导出图到JSON失败")
            return False
    except Exception as e:
        logger.error(f"保存图时出错: {str(e)}")
        return False

def main():
    """
    主函数
    """
    try:
        # 构建联动图
        graph = build_protoss_linkage_graph()
        
        if graph:
            # 分析图关系
            analyze_graph_relationships(graph)
            
            # 保存图到JSON
            output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../graph'))
            output_path = os.path.join(output_dir, 'protoss_linkage_graph.json')
            save_graph_to_json(graph, output_path)
            
            # 输出一些基本信息
            print(f"\n联动图构建完成!")
            print(f"节点数量: {len(graph.nodes)}")
            print(f"边数量: {len(graph.edges)}")
            print(f"遍历完成: {graph.traversal_complete}")
            print(f"\n文件已保存到: {output_path}")
    except Exception as e:
        logger.error(f"执行过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()