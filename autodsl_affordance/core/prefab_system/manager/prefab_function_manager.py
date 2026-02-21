import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from autodsl_affordance.core.prefab_system.loader.prefab_loader import PrefabLoader
from autodsl_affordance.core.prefab_system.handler.prefab_function_handler import PrefabFunctionHandler
from autodsl_affordance.core.prefab_system.handler.prefab_performance_monitor import PrefabPerformanceMonitor

logger = logging.getLogger(__name__)

class PrefabFunctionManager:
    """
    预制函数管理器，作为顶层协调者
    负责：
    1. 初始化和管理所有处理器
    2. 提供统一的预制函数访问接口
    3. 协调预制函数的处理流程
    4. 管理配置和资源
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化预制函数管理器
        
        Args:
            config: 配置字典
        """
        # 加载配置
        self.config = config or {
            'top_k': 3,
            'cache_size': 100,
            'enable_performance_monitor': True
        }
        
        # 初始化加载器
        self.loader = PrefabLoader()
        
        # 加载预制函数
        self.functions = self.loader.load_functions()
        
        # 初始化处理器
        self.function_handler = PrefabFunctionHandler()
        
        # 初始化性能监控器
        self.performance_monitor = PrefabPerformanceMonitor() if self.config.get('enable_performance_monitor') else None
        
        # 初始化缓存和历史记录
        self.cache = {}
        self.execution_history = []
        
        logger.info("PrefabFunctionManager 初始化完成")
    
    def get_optimal_functions(self, observation: Dict[str, Any], top_k: int = None, race: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取最优预制函数
        
        Args:
            observation: 游戏观察数据
            top_k: 返回前k个最优函数
            race: 当前种族
        
        Returns:
            List[Dict]: 最优函数列表
        """
        # 使用配置中的默认值
        if top_k is None:
            top_k = self.config.get('top_k', 3)
        
        # 生成缓存键
        cache_key = self._generate_cache_key(observation, race)
        
        # 检查缓存
        if cache_key in self.cache:
            logger.info("从缓存中获取最优函数")
            return self.cache[cache_key]
        
        # 分析游戏状态
        game_state = self._analyze_game_state(observation)
        
        # 检测种族
        if not race:
            race = self._detect_race(observation)
        
        # 检索相关函数
        relevant_functions = self._retrieve_relevant_functions(game_state, race)
        
        # 评分和选择
        scored_functions = self.function_handler.score_functions(relevant_functions, observation)
        optimal_functions = self.function_handler.select_optimal_functions(scored_functions, top_k, game_state)
        
        # 记录性能
        if self.performance_monitor:
            for i, func in enumerate(optimal_functions):
                self.performance_monitor.record_function_usage(
                    func_id=func.get('function_id', 'unknown'),
                    func_name=func.get('name', 'unknown'),
                    step=-1,  # 步骤号将在调用处更新
                    selected=True,
                    confidence=func.get('confidence', 0.0),
                    relevance=0.0  # 简化处理
                )
        
        # 缓存结果
        self._cache_result(cache_key, optimal_functions)
        
        return optimal_functions
    
    def execute_function(self, function: Dict[str, Any], observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行预制函数
        
        Args:
            function: 要执行的函数
            observation: 当前游戏状态
        
        Returns:
            Dict: 执行结果
        """
        # 记录执行前状态
        game_state_before = self._analyze_game_state(observation)
        
        # 执行函数
        result = self.function_handler.execute_functions([function], observation, 0)
        
        # 记录执行后状态
        game_state_after = self._analyze_game_state(observation)
        
        # 构建执行结果
        execution_result = {
            "function_id": function['function_id'],
            "success": True,  # 简化处理
            "actions": result,
            "metrics": self._calculate_metrics(game_state_before, game_state_after),
            "timestamp": datetime.now().isoformat(),
            "game_state_before": game_state_before,
            "game_state_after": game_state_after
        }
        
        # 记录执行结果
        self.execution_history.append(execution_result)
        
        # 记录性能
        if self.performance_monitor:
            # 记录决策质量
            self.performance_monitor.record_decision_quality(
                step=-1,  # 步骤号将在调用处更新
                decision_type='prefab_execution',
                functions_used=[execution_result['function_id']],
                outcome=execution_result,
                game_state=execution_result['game_state_after']
            )
            
            # 记录决策影响
            self.performance_monitor.record_decision_impact(
                step=-1,  # 步骤号将在调用处更新
                pre_game_state=execution_result['game_state_before'],
                post_game_state=execution_result['game_state_after'],
                actions=execution_result['actions']
            )
        
        # 更新函数评分
        self._update_function_score(function['function_id'], execution_result)
        
        return execution_result
    
    def get_function_details(self, function_id: str) -> Optional[Dict[str, Any]]:
        """
        获取函数详情
        
        Args:
            function_id: 函数ID
        
        Returns:
            Dict: 函数详细信息，如果未找到返回None
        """
        return self.loader.get_function_by_id(function_id, self.functions)
    
    def update_function_score(self, function_id: str, success: bool, metrics: Dict[str, Any]) -> None:
        """
        更新函数评分
        
        Args:
            function_id: 函数ID
            success: 执行是否成功
            metrics: 执行效果指标
        """
        # 查找函数
        function = self.get_function_details(function_id)
        if not function:
            logger.warning(f"未找到函数: {function_id}")
            return
        
        # 更新使用次数和成功率
        function['usage_count'] = function.get('usage_count', 0) + 1
        
        # 更新成功率
        if 'success_rate' in function:
            old_success_rate = function['success_rate']
            old_count = function['usage_count'] - 1
            new_success_rate = (old_success_rate * old_count + (1 if success else 0)) / function['usage_count']
            function['success_rate'] = new_success_rate
        else:
            function['success_rate'] = 1 if success else 0
        
        # 更新置信度
        if 'confidence' in function:
            # 基于执行结果调整置信度
            confidence_adjustment = 0.05 if success else -0.05
            new_confidence = max(0.1, min(1.0, function['confidence'] + confidence_adjustment))
            function['confidence'] = new_confidence
    
    def _analyze_game_state(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析游戏状态
        
        Args:
            observation: 游戏观察数据
        
        Returns:
            Dict: 分析后的游戏状态
        """
        # 获取单位信息
        unit_info = observation.get('unit_info', [])
        
        # 分离友方和敌方单位
        friendly_units = [unit for unit in unit_info if unit['alliance'] == 1]
        enemy_units = [unit for unit in unit_info if unit['alliance'] != 1]
        
        # 分析单位类型
        friendly_unit_types = {}
        enemy_unit_types = {}
        
        for unit in friendly_units:
            unit_type = unit['unit_name'].split('_')[0]
            friendly_unit_types[unit_type] = friendly_unit_types.get(unit_type, 0) + 1
        
        for unit in enemy_units:
            unit_type = unit['unit_name'].split('_')[0]
            enemy_unit_types[unit_type] = enemy_unit_types.get(unit_type, 0) + 1
        
        # 分析健康状况
        has_low_health_units = any(unit['health'] < unit['max_health'] * 0.5 for unit in friendly_units)
        has_medivac = any('Medivac' in unit['unit_name'] for unit in friendly_units)
        
        return {
            'friendly_count': len(friendly_units),
            'enemy_count': len(enemy_units),
            'friendly_unit_types': friendly_unit_types,
            'enemy_unit_types': enemy_unit_types,
            'has_low_health_units': has_low_health_units,
            'has_medivac': has_medivac,
            'text_observation': observation.get('text', ''),
            'timestamp': datetime.now().isoformat()
        }
    
    def _detect_race(self, observation: Dict[str, Any]) -> str:
        """
        检测种族
        
        Args:
            observation: 游戏观察数据
        
        Returns:
            str: 种族名称
        """
        unit_info = observation.get('unit_info', [])
        friendly_units = [unit for unit in unit_info if unit['alliance'] == 1]
        
        if not friendly_units:
            return 'unknown'
        
        # 检测种族
        for unit in friendly_units:
            unit_name = unit['unit_name'].lower()
            
            # 检测神族单位
            if any(keyword in unit_name for keyword in ['zealot', 'stalker', 'phoenix', 'immortal', 'archon']):
                return 'protoss'
            
            # 检测人族单位
            if any(keyword in unit_name for keyword in ['marine', 'marauder', 'medivac', 'siegetank', 'battlecruiser']):
                return 'terran'
            
            # 检测虫族单位
            if any(keyword in unit_name for keyword in ['zergling', 'baneling', 'roach', 'hydralisk', 'ultralisk']):
                return 'zerg'
        
        return 'unknown'
    
    def _retrieve_relevant_functions(self, game_state: Dict[str, Any], race: str) -> List[Dict[str, Any]]:
        """
        检索相关函数
        
        Args:
            game_state: 游戏状态
            race: 种族
        
        Returns:
            List[Dict]: 相关函数列表
        """
        # 使用PrefabLoader的搜索功能
        relevant_functions = self.loader.search_functions(self.functions, race=race)
        
        # 进一步过滤
        filtered_functions = []
        for func in relevant_functions:
            if self._is_function_relevant(func, game_state):
                filtered_functions.append(func)
        
        return filtered_functions
    
    def _is_function_relevant(self, func: Dict[str, Any], game_state: Dict[str, Any]) -> bool:
        """
        检查函数是否与游戏状态相关
        
        Args:
            func: 函数信息
            game_state: 游戏状态
        
        Returns:
            bool: 是否相关
        """
        # 检查所需单位
        if 'required_units' in func:
            for required_unit in func['required_units']:
                unit_type = required_unit.split('_')[-1].lower()
                if not any(unit_type in unit.lower() for unit in game_state['friendly_unit_types']):
                    return False
        
        # 检查战术类别
        if 'tactic_category' in func:
            category = func['tactic_category']
            if category == 'defense' and game_state['friendly_count'] > game_state['enemy_count']:
                return False
            if category == 'offense' and game_state['friendly_count'] < game_state['enemy_count']:
                return False
        
        return True
    
    def _calculate_metrics(self, game_state_before: Dict[str, Any], game_state_after: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算执行效果指标
        
        Args:
            game_state_before: 执行前游戏状态
            game_state_after: 执行后游戏状态
        
        Returns:
            Dict: 执行效果指标
        """
        return {
            'friendly_count_change': game_state_after.get('friendly_count', 0) - game_state_before.get('friendly_count', 0),
            'enemy_count_change': game_state_after.get('enemy_count', 0) - game_state_before.get('enemy_count', 0),
            'health_change': 0,  # 需要根据实际情况计算
            'resource_change': 0   # 需要根据实际情况计算
        }
    
    def _generate_cache_key(self, observation: Dict[str, Any], race: Optional[str]) -> str:
        """
        生成缓存键
        
        Args:
            observation: 游戏观察数据
            race: 种族
        
        Returns:
            str: 缓存键
        """
        # 简化的缓存键生成
        unit_info = observation.get('unit_info', [])
        friendly_count = len([unit for unit in unit_info if unit['alliance'] == 1])
        enemy_count = len([unit for unit in unit_info if unit['alliance'] != 1])
        
        key_parts = [str(friendly_count), str(enemy_count), race or 'unknown']
        return '_'.join(key_parts)
    
    def _cache_result(self, key: str, result: List[Dict[str, Any]]):
        """
        缓存结果
        
        Args:
            key: 缓存键
            result: 要缓存的结果
        """
        # 检查缓存大小
        if len(self.cache) >= self.config.get('cache_size', 100):
            # 移除最早的缓存项
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = result
    
    def _update_function_score(self, function_id: str, execution_result: Dict[str, Any]):
        """
        更新函数评分
        
        Args:
            function_id: 函数ID
            execution_result: 执行结果
        """
        self.update_function_score(
            function_id,
            execution_result['success'],
            execution_result['metrics']
        )
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """
        获取执行历史
        
        Returns:
            List[Dict]: 执行历史记录
        """
        return self.execution_history
    
    def clear_cache(self):
        """
        清除缓存
        """
        self.cache.clear()
        logger.info("缓存已清除")
    
    def clear_history(self):
        """
        清除执行历史
        """
        self.execution_history.clear()
        logger.info("执行历史已清除")
