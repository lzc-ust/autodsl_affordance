import os
import sys
import logging
import json
from typing import Dict, List, Tuple, Set, Any
from collections import defaultdict

# 添加项目根目录到Python路径
current_file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_file_dir, '../../../../'))
sys.path.append(project_root)

# 导入 Schema 验证器
from autodsl_affordance.core.linkage_graph.prefab_functions.utils.schema_validator import PrefabFunctionSchemaValidator

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PrefabFunctionManager:
    """预制函数库管理器，负责函数库的管理、验证和部署"""
    
    def __init__(self):
        """初始化函数库管理器"""
        self.prefab_functions: Dict[str, Dict[str, Any]] = {}
        self.function_type_index: Dict[str, List[str]] = defaultdict(list)
        self.unit_index: Dict[str, List[str]] = defaultdict(list)
        self.execution_type_index: Dict[str, List[str]] = defaultdict(list)
        self.tactic_category_index: Dict[str, List[str]] = defaultdict(list)
        # 初始化 Schema 验证器
        schema_path = os.path.join(current_file_dir, '..', 'prefab_functions', 'schema', 'prefab_function.schema.json')
        self.validator = PrefabFunctionSchemaValidator(schema_path)
    
    def load_prefab_functions(self, file_path: str, race: str = None, map_name: str = None, merge: bool = False) -> bool:
        """
        从JSON文件加载预制函数库，支持按种族和地图过滤
        
        Args:
            file_path: 预制函数库文件路径
            race: 可选，种族过滤（'terran', 'protoss', 'zerg'）
            map_name: 可选，地图名称过滤
            merge: 是否合并到现有库中，否则替换
            
        Returns:
            bool: 加载成功返回True，否则返回False
        """
        logger.info(f"从 {file_path} 加载预制函数库，种族={race}, 地图={map_name}, 合并={merge}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                all_functions = json.load(f)
            
            # 根据种族和地图过滤函数
            filtered_functions = []
            for func in all_functions:
                # 种族过滤
                if race:
                    # 检查函数是否适合该种族
                    is_race_match = False
                    # 1. 从函数ID中提取种族
                    func_id_upper = func['function_id'].upper()
                    if f"{race.upper()}" in func_id_upper:
                        is_race_match = True
                    # 2. 从函数名称中检查种族
                    elif race in func['name'].lower():
                        is_race_match = True
                    # 3. 从源单位/目标单位中检查种族
                    elif 'source_unit' in func and race in func['source_unit'].lower():
                        is_race_match = True
                    elif 'target_unit' in func and race in func['target_unit'].lower():
                        is_race_match = True
                    # 4. 从单位列表中检查种族
                    elif 'units' in func:
                        for unit in func['units']:
                            if race in unit.lower():
                                is_race_match = True
                                break
                    # 5. 从执行流中检查种族
                    elif any(race in step.lower() for step in func.get('execution_flow', [])):
                        is_race_match = True
                    
                    if not is_race_match:
                        continue
                
                # 地图过滤
                if map_name:
                    # 检查函数是否指定了适用地图
                    applicable_maps = func.get('applicable_maps', [])
                    if applicable_maps and map_name not in applicable_maps:
                        continue
                
                # Schema 验证
                if not self.validator.validate_function(func):
                    logger.warning(f"跳过验证失败的预制函数: {func.get('function_id', '未知')}")
                    continue
                
                filtered_functions.append(func)
            
            if not merge:
                # 清空现有库
                self.prefab_functions.clear()
                self.function_type_index.clear()
                self.unit_index.clear()
                self.execution_type_index.clear()
                self.tactic_category_index.clear()
            
            # 加载过滤后的函数并构建索引
            valid_functions = 0
            for func in filtered_functions:
                # 检查必要字段
                if 'function_id' not in func:
                    logger.warning(f"跳过缺少function_id的预制函数")
                    continue
                
                if 'function_type' not in func:
                    logger.warning(f"跳过缺少function_type的预制函数: {func.get('function_id', '未知')}")
                    continue
                
                if 'execution_type' not in func:
                    logger.warning(f"跳过缺少execution_type的预制函数: {func.get('function_id', '未知')}")
                    continue
                
                function_id = func['function_id']
                self.prefab_functions[function_id] = func
                valid_functions += 1
                
                # 构建类型索引
                self.function_type_index[func['function_type']].append(function_id)
                
                # 构建单位索引
                if 'source_unit' in func:
                    self.unit_index[func['source_unit']].append(function_id)
                if 'target_unit' in func:
                    self.unit_index[func['target_unit']].append(function_id)
                if 'units' in func:
                    for unit in func['units']:
                        self.unit_index[unit].append(function_id)
                
                # 构建执行类型索引
                self.execution_type_index[func['execution_type']].append(function_id)
                
                # 构建战术类别索引
                if 'tactic_category' in func:
                    self.tactic_category_index[func['tactic_category']].append(function_id)
            
            logger.info(f"成功加载 {valid_functions} 个有效预制函数（过滤后: {len(filtered_functions)}, 总可用: {len(all_functions)}）")
            return True
        except Exception as e:
            logger.error(f"加载预制函数库失败: {e}")
            return False
    
    def reload_prefab_functions(self, file_path: str, race: str = None, map_name: str = None) -> bool:
        """
        重新加载预制函数库（替换现有）
        
        Args:
            file_path: 预制函数库文件路径
            race: 可选，种族过滤
            map_name: 可选，地图过滤
            
        Returns:
            bool: 加载成功返回True，否则返回False
        """
        return self.load_prefab_functions(file_path, race, map_name, merge=False)
    
    def merge_prefab_functions(self, file_path: str, race: str = None, map_name: str = None) -> bool:
        """
        合并加载预制函数库（不替换现有）
        
        Args:
            file_path: 预制函数库文件路径
            race: 可选，种族过滤
            map_name: 可选，地图过滤
            
        Returns:
            bool: 加载成功返回True，否则返回False
        """
        return self.load_prefab_functions(file_path, race, map_name, merge=True)
    
    def load_race_specific_functions(self, race: str, map_name: str = None) -> bool:
        """
        加载特定种族的预制函数
        
        Args:
            race: 种族名称（'terran', 'protoss', 'zerg'）
            map_name: 可选，地图名称
            
        Returns:
            bool: 加载成功返回True，否则返回False
        """
        import os
        
        # 根据种族构建默认文件路径
        race_lower = race.lower()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # 假设预制函数文件存放在 ../prefab_functions/ 目录
        file_path = os.path.join(base_dir, '..', 'prefab_functions', f'{race_lower}_prefab_functions.json')
        
        if os.path.exists(file_path):
            return self.load_prefab_functions(file_path, race, map_name)
        else:
            logger.error(f"未找到种族 {race} 的预制函数文件: {file_path}")
            return False
    
    def update_function(self, func: Dict[str, Any]) -> bool:
        """
        更新单个预制函数
        
        Args:
            func: 预制函数字典
            
        Returns:
            bool: 更新成功返回True，否则返回False
        """
        return self.add_prefab_function(func)
    
    def remove_function(self, function_id: str) -> bool:
        """
        移除指定ID的预制函数
        
        Args:
            function_id: 预制函数ID
            
        Returns:
            bool: 移除成功返回True，否则返回False
        """
        if function_id not in self.prefab_functions:
            logger.warning(f"预制函数 {function_id} 不存在")
            return False
        
        # 获取要移除的函数
        func = self.prefab_functions.pop(function_id)
        
        # 更新所有索引
        # 1. 函数类型索引
        if func['function_type'] in self.function_type_index:
            self.function_type_index[func['function_type']].remove(function_id)
        
        # 2. 单位索引
        if 'source_unit' in func:
            if func['source_unit'] in self.unit_index:
                self.unit_index[func['source_unit']].remove(function_id)
        if 'target_unit' in func:
            if func['target_unit'] in self.unit_index:
                self.unit_index[func['target_unit']].remove(function_id)
        if 'units' in func:
            for unit in func['units']:
                if unit in self.unit_index:
                    self.unit_index[unit].remove(function_id)
        
        # 3. 执行类型索引
        if func['execution_type'] in self.execution_type_index:
            self.execution_type_index[func['execution_type']].remove(function_id)
        
        # 4. 战术类别索引
        if 'tactic_category' in func:
            if func['tactic_category'] in self.tactic_category_index:
                self.tactic_category_index[func['tactic_category']].remove(function_id)
        
        logger.info(f"成功移除预制函数: {function_id}")
        return True
    
    def get_race_functions(self, race: str) -> List[Dict[str, Any]]:
        """
        获取特定种族的所有预制函数
        
        Args:
            race: 种族名称
            
        Returns:
            List[Dict[str, Any]]: 该种族的预制函数列表
        """
        race_lower = race.lower()
        result = []
        
        for func in self.prefab_functions.values():
            func_id_upper = func['function_id'].upper()
            func_name_lower = func['name'].lower()
            
            # 检查函数是否属于该种族
            if (f"{race.upper()}" in func_id_upper or 
                race_lower in func_name_lower or
                ('source_unit' in func and race_lower in func['source_unit'].lower()) or
                ('target_unit' in func and race_lower in func['target_unit'].lower()) or
                ('units' in func and any(race_lower in unit.lower() for unit in func['units']))):
                result.append(func)
        
        return result
    
    def get_map_specific_functions(self, map_name: str) -> List[Dict[str, Any]]:
        """
        获取特定地图的预制函数
        
        Args:
            map_name: 地图名称
            
        Returns:
            List[Dict[str, Any]]: 该地图适用的预制函数列表
        """
        result = []
        
        for func in self.prefab_functions.values():
            applicable_maps = func.get('applicable_maps', [])
            if not applicable_maps or map_name in applicable_maps:
                result.append(func)
        
        return result
    
    def add_prefab_function(self, func: Dict[str, Any]) -> bool:
        """
        添加单个预制函数到库中
        
        Args:
            func: 预制函数字典
            
        Returns:
            bool: 添加成功返回True，否则返回False
        """
        if 'function_id' not in func:
            logger.error("预制函数缺少function_id")
            return False
        
        # Schema 验证
        if not self.validator.validate_function(func):
            logger.error(f"预制函数验证失败: {func.get('function_id', '未知')}")
            return False
        
        function_id = func['function_id']
        
        if function_id in self.prefab_functions:
            logger.warning(f"预制函数 {function_id} 已存在，将覆盖")
        
        self.prefab_functions[function_id] = func
        
        # 更新索引
        self.function_type_index[func['function_type']].append(function_id)
        
        # 构建单位索引
        if 'source_unit' in func:
            self.unit_index[func['source_unit']].append(function_id)
        if 'target_unit' in func:
            self.unit_index[func['target_unit']].append(function_id)
        if 'units' in func:
            for unit in func['units']:
                self.unit_index[unit].append(function_id)
        
        # 构建执行类型索引
        self.execution_type_index[func['execution_type']].append(function_id)
        
        # 构建战术类别索引
        if 'tactic_category' in func:
            self.tactic_category_index[func['tactic_category']].append(function_id)
        
        logger.info(f"成功添加预制函数: {function_id}")
        return True
    
    def get_function_by_id(self, function_id: str) -> Dict[str, Any]:
        """
        根据function_id获取预制函数
        
        Args:
            function_id: 函数ID
            
        Returns:
            Dict[str, Any]: 预制函数字典，不存在返回None
        """
        return self.prefab_functions.get(function_id)
    
    def get_functions_by_type(self, function_type: str) -> List[Dict[str, Any]]:
        """
        根据function_type获取预制函数列表
        
        Args:
            function_type: 函数类型
            
        Returns:
            List[Dict[str, Any]]: 预制函数列表
        """
        function_ids = self.function_type_index.get(function_type, [])
        return [self.prefab_functions[func_id] for func_id in function_ids]
    
    def get_functions_by_unit(self, unit_name: str) -> List[Dict[str, Any]]:
        """
        根据单位名称获取相关预制函数列表
        
        Args:
            unit_name: 单位名称
            
        Returns:
            List[Dict[str, Any]]: 预制函数列表
        """
        function_ids = self.unit_index.get(unit_name, [])
        return [self.prefab_functions[func_id] for func_id in function_ids]
    
    def get_functions_by_execution_type(self, execution_type: str) -> List[Dict[str, Any]]:
        """
        根据执行类型获取预制函数列表
        
        Args:
            execution_type: 执行类型
            
        Returns:
            List[Dict[str, Any]]: 预制函数列表
        """
        function_ids = self.execution_type_index.get(execution_type, [])
        return [self.prefab_functions[func_id] for func_id in function_ids]
    
    def search_functions(self, **kwargs) -> List[Dict[str, Any]]:
        """
        根据关键字搜索预制函数
        
        Args:
            **kwargs: 搜索条件，如function_type、unit、execution_type等
            
        Returns:
            List[Dict[str, Any]]: 匹配的预制函数列表
        """
        # 获取所有函数ID
        result_ids = set(self.prefab_functions.keys())
        
        # 根据function_type过滤
        if 'function_type' in kwargs:
            type_ids = set(self.function_type_index.get(kwargs['function_type'], []))
            result_ids.intersection_update(type_ids)
        
        # 根据unit过滤
        if 'unit' in kwargs:
            unit_ids = set(self.unit_index.get(kwargs['unit'], []))
            result_ids.intersection_update(unit_ids)
        
        # 根据execution_type过滤
        if 'execution_type' in kwargs:
            exec_ids = set(self.execution_type_index.get(kwargs['execution_type'], []))
            result_ids.intersection_update(exec_ids)
        
        # 根据战术类别过滤
        if 'tactic_category' in kwargs:
            tactic_ids = set(self.tactic_category_index.get(kwargs['tactic_category'], []))
            result_ids.intersection_update(tactic_ids)
        
        # 根据关键字过滤
        if 'keyword' in kwargs:
            keyword = kwargs['keyword'].lower()
            filtered_ids = set()
            for func_id in result_ids:
                func = self.prefab_functions[func_id]
                if keyword in func['name'].lower() or keyword in func['description'].lower():
                    filtered_ids.add(func_id)
            result_ids = filtered_ids
        
        return [self.prefab_functions[func_id] for func_id in result_ids]
    
    def validate_function_consistency(self, func: Dict[str, Any]) -> bool:
        """
        验证预制函数的一致性
        
        Args:
            func: 预制函数字典
            
        Returns:
            bool: 一致返回True，否则返回False
        """
        logger.info(f"验证预制函数 {func.get('function_id')} 的一致性")
        
        # 检查必填字段
        required_fields = ['function_id', 'function_type', 'name', 'description', 
                          'linkage_type', 'execution_type', 'parameters', 'execution_flow']
        
        for field in required_fields:
            if field not in func:
                logger.error(f"缺少必填字段: {field}")
                return False
        
        # 检查参数一致性
        for param in func['parameters']:
            if 'name' not in param or 'type' not in param or 'description' not in param:
                logger.error(f"参数缺少必填字段: {param}")
                return False
        
        # 检查执行流程一致性
        for step in func['execution_flow']:
            # 简单检查：确保执行流程中包含参数名
            for param in func['parameters']:
                param_name = param['name']
                if param_name in step or param_name.upper() in step:
                    break
            else:
                logger.warning(f"执行流程步骤 '{step}' 可能未使用参数")
        
        # 检查置信度范围
        if 'confidence' in func and not (0 <= func['confidence'] <= 1):
            logger.error(f"置信度超出范围 (0-1): {func['confidence']}")
            return False
        
        logger.info(f"预制函数 {func.get('function_id')} 一致性验证通过")
        return True
    
    def validate_all_functions(self) -> List[str]:
        """
        验证所有预制函数的一致性
        
        Returns:
            List[str]: 验证失败的函数ID列表
        """
        logger.info("验证所有预制函数的一致性")
        
        invalid_functions = []
        
        for func_id, func in self.prefab_functions.items():
            if not self.validate_function_consistency(func):
                invalid_functions.append(func_id)
        
        logger.info(f"一致性验证完成，{len(invalid_functions)} 个函数验证失败")
        return invalid_functions
    
    def aggregate_parameters(self, func: Dict[str, Any]) -> Dict[str, Any]:
        """
        聚合函数参数，抽象为具有预定义合理域的函数参数
        
        Args:
            func: 预制函数字典
            
        Returns:
            Dict[str, Any]: 聚合后的预制函数字典
        """
        logger.info(f"聚合预制函数 {func.get('function_id')} 的参数")
        
        # 复制函数字典
        aggregated_func = func.copy()
        
        # 优化参数域
        for param in aggregated_func['parameters']:
            # 根据参数类型和名称优化域
            if param['type'] == 'int' and param['name'] == 'target_unit_tag':
                param['domain'] = 'valid_enemy_tags'
            elif param['type'] == 'List[Tuple[int, int]]' and param['name'] == 'target_positions':
                param['domain'] = 'valid_grid_positions'
            elif param['type'] == 'str' and param['name'] == 'operation_type':
                param['domain'] = ['move', 'attack', 'defend']
            elif param['type'] == 'str' and param['name'] == 'target_unit':
                param['domain'] = 'valid_unit_types'
            elif param['type'] == 'Dict[str, int]' and param['name'] == 'resource_allocation':
                param['domain'] = 'valid_resource_ranges'
        
        return aggregated_func
    
    def aggregate_all_parameters(self) -> None:
        """
        聚合所有预制函数的参数
        """
        logger.info("聚合所有预制函数的参数")
        
        for func_id in self.prefab_functions:
            self.prefab_functions[func_id] = self.aggregate_parameters(self.prefab_functions[func_id])
        
        logger.info("所有预制函数参数聚合完成")
    
    def generate_function_signature(self, func: Dict[str, Any]) -> str:
        """
        生成函数签名
        
        Args:
            func: 预制函数字典
            
        Returns:
            str: 函数签名字符串
        """
        param_str = ', '.join([f"{param['name']}: {param['type']}" for param in func['parameters']])
        return f"{func['name']}({param_str}) -> {func['execution_type']}"
    
    def generate_all_signatures(self) -> Dict[str, str]:
        """
        生成所有函数签名
        
        Returns:
            Dict[str, str]: 函数ID到签名的映射
        """
        signatures = {}
        for func_id, func in self.prefab_functions.items():
            signatures[func_id] = self.generate_function_signature(func)
        return signatures
    
    def save_prefab_functions(self, file_path: str) -> bool:
        """
        保存预制函数库到JSON文件
        
        Args:
            file_path: 输出文件路径
            
        Returns:
            bool: 保存成功返回True，否则返回False
        """
        logger.info(f"保存预制函数库到 {file_path}")
        
        try:
            functions = list(self.prefab_functions.values())
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(functions, f, ensure_ascii=False, indent=2)
            
            logger.info(f"成功保存 {len(functions)} 个预制函数")
            return True
        except Exception as e:
            logger.error(f"保存预制函数库失败: {e}")
            return False
    
    def get_function_count(self) -> int:
        """
        获取预制函数总数
        
        Returns:
            int: 函数总数
        """
        return len(self.prefab_functions)
    
    def get_all_functions(self) -> List[Dict[str, Any]]:
        """
        获取所有预制函数
        
        Returns:
            List[Dict[str, Any]]: 所有预制函数列表
        """
        return list(self.prefab_functions.values())
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取预制函数库统计信息
        
        Returns:
            Dict[str, Any]: 统计信息字典
        """
        stats = {
            "total_functions": len(self.prefab_functions),
            "function_type_distribution": {},
            "execution_type_distribution": {},
            "tactic_category_distribution": {},
            "units_involved": len(self.unit_index),
            "avg_parameters_per_function": 0,
            "avg_confidence": 0
        }
        
        # 计算函数类型分布
        for func_type, func_ids in self.function_type_index.items():
            stats["function_type_distribution"][func_type] = len(func_ids)
        
        # 计算执行类型分布
        for exec_type, func_ids in self.execution_type_index.items():
            stats["execution_type_distribution"][exec_type] = len(func_ids)
        
        # 计算战术类别分布
        for tactic_type, func_ids in self.tactic_category_index.items():
            stats["tactic_category_distribution"][tactic_type] = len(func_ids)
        
        # 计算平均参数数量
        total_params = 0
        total_confidence = 0
        confidence_count = 0
        
        for func in self.prefab_functions.values():
            if 'parameters' in func:
                total_params += len(func['parameters'])
            if 'confidence' in func:
                total_confidence += func['confidence']
                confidence_count += 1
        
        if self.prefab_functions:
            stats["avg_parameters_per_function"] = round(total_params / len(self.prefab_functions), 2)
        
        if confidence_count:
            stats["avg_confidence"] = round(total_confidence / confidence_count, 3)
        
        return stats
    
    def get_optimal_functions(self, observation: Dict[str, Any], game_state: Dict[str, Any], max_functions: int = 5) -> List[Dict[str, Any]]:
        """
        获取当前游戏状态下的最优预制函数
        
        Args:
            observation: 游戏观察
            game_state: 游戏状态信息
            max_functions: 最大返回函数数量
            
        Returns:
            List[Dict[str, Any]]: 最优预制函数列表
        """
        logger.info(f"获取最优预制函数，最大数量: {max_functions}")
        
        # 获取所有预制函数
        all_functions = list(self.prefab_functions.values())
        
        if not all_functions:
            logger.warning("无可用预制函数")
            return []
        
        # 简单实现：根据置信度和游戏状态相关性排序
        # 实际实现应调用PrefabFunctionHandler进行评分
        scored_functions = []
        
        for func in all_functions:
            # 基础分数：置信度
            base_score = func.get('confidence', 0.5)
            
            # 计算相关性分数
            relevance_score = self._calculate_function_relevance(func, game_state)
            
            # 综合分数
            total_score = base_score * 0.7 + relevance_score * 0.3
            
            # 添加分数和相关性到函数中
            func_with_score = func.copy()
            func_with_score['score'] = total_score
            func_with_score['relevance'] = relevance_score
            
            scored_functions.append(func_with_score)
        
        # 按分数排序
        scored_functions.sort(key=lambda x: x['score'], reverse=True)
        
        # 选择前max_functions个函数
        optimal_functions = scored_functions[:max_functions]
        
        # 记录最优函数详细信息
        logger.info(f"最终选择了 {len(optimal_functions)} 个最优预制函数:")
        for i, func in enumerate(optimal_functions, 1):
            logger.info(f"  {i}. ID={func['function_id']}, Name={func['name']}, Score={func['score']:.2f}, Relevance={func['relevance']:.2f}")
            # 记录函数详细内容
            logger.info(f"    描述: {func.get('description', '无')}")
            logger.info(f"    策略描述: {func.get('strategy_description', '无')}")
            logger.info(f"    战术类别: {func.get('tactic_category', '无')}")
            logger.info(f"    执行类型: {func.get('execution_type', '无')}")
            if 'prerequisites' in func:
                logger.info(f"    前置条件: {func['prerequisites']}")
            if 'execution_flow' in func:
                logger.info(f"    执行流程: {func['execution_flow']}")
            logger.info(f"    置信度: {func.get('confidence', '无')}")
        
        return optimal_functions
    
    def _calculate_function_relevance(self, func: Dict[str, Any], game_state: Dict[str, Any]) -> float:
        """
        计算函数与游戏状态的相关性
        
        Args:
            func: 预制函数
            game_state: 游戏状态信息
            
        Returns:
            float: 相关性分数 (0-1)
        """
        relevance = 0.0
        
        # 基于单位类型的相关性
        friendly_unit_types = game_state.get('friendly_unit_types', {})
        enemy_unit_types = game_state.get('enemy_unit_types', {})
        
        # 检查函数是否涉及当前游戏中的单位类型
        func_units = set()
        if 'source_unit' in func:
            func_units.add(func['source_unit'].lower())
        if 'target_unit' in func:
            func_units.add(func['target_unit'].lower())
        if 'units' in func:
            for unit in func['units']:
                func_units.add(unit.lower())
        
        # 检查'all_friendly'或'all_enemy'等特殊值
        if 'all_friendly' in func_units:
            relevance += 0.3
        if 'all_enemy' in func_units:
            relevance += 0.3
        
        # 检查具体单位类型
        for unit_type in friendly_unit_types:
            if unit_type.lower() in func_units:
                relevance += 0.1 * friendly_unit_types[unit_type]
        
        for unit_type in enemy_unit_types:
            if unit_type.lower() in func_units:
                relevance += 0.1 * enemy_unit_types[unit_type]
        
        # 检查前置条件中的必需单位
        if 'prerequisites' in func and 'required_units' in func['prerequisites']:
            required_units = func['prerequisites']['required_units']
            required_unit_count = 0
            for unit in required_units:
                unit_lower = unit.lower()
                if unit_lower in friendly_unit_types:
                    required_unit_count += 1
            # 基于必需单位的匹配程度加分
            if required_unit_count > 0:
                relevance += 0.2 * (required_unit_count / len(required_units))
        
        # 基于执行类型的相关性（扩展版）
        execution_type = func.get('execution_type', '').lower()
        if execution_type:
            if execution_type == 'attack' and game_state.get('enemy_count', 0) > 0:
                relevance += 0.2
            elif execution_type == 'move' and game_state.get('friendly_count', 0) > 0:
                relevance += 0.1
            elif execution_type == 'frontal_assault' and game_state.get('enemy_count', 0) > 0:
                relevance += 0.25
            elif execution_type == 'ambush_attack' and game_state.get('enemy_count', 0) > 0:
                relevance += 0.2
            elif execution_type == 'ability' and game_state.get('friendly_count', 0) > 0:
                relevance += 0.15
            elif execution_type == 'concurrent' and game_state.get('friendly_count', 0) > 1:
                relevance += 0.2
            elif execution_type == 'fortified_position' and game_state.get('friendly_count', 0) > 0:
                relevance += 0.15
            elif execution_type == 'coordinated_advance' and game_state.get('friendly_count', 0) > 1:
                relevance += 0.2
        
        # 归一化相关性分数
        return min(relevance, 1.0)

# 测试代码
if __name__ == "__main__":
    # 创建管理器实例
    manager = PrefabFunctionManager()
    
    # 加载预制函数库
    manager.load_prefab_functions("../prefab_functions/protoss_prefab_functions.json")
    
    # 验证所有函数
    invalid_funcs = manager.validate_all_functions()
    print(f"验证失败的函数: {invalid_funcs}")
    
    # 聚合所有参数
    manager.aggregate_all_parameters()
    
    # 搜索函数
    interaction_funcs = manager.search_functions(function_type="interaction")
    print(f"INTERACTION类型函数数量: {len(interaction_funcs)}")
    
    # 生成统计信息
    stats = manager.get_statistics()
    print(f"统计信息: {stats}")
    
    # 保存更新后的函数库
    manager.save_prefab_functions("../prefab_functions/protoss_prefab_functions_validated.json")
