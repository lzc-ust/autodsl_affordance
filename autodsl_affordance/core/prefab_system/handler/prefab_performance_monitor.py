import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class PrefabPerformanceMonitor:
    """
    预制函数性能监控器，用于记录预制函数的使用效果和决策质量数据
    """
    def __init__(self):
        self.function_usage_history = []  # 记录函数使用历史
        self.decision_quality_data = []    # 记录决策质量数据
        self.prefab_relevance_history = []  # 记录预制函数与游戏状态的相关性历史
        self.decision_impact_history = []   # 记录决策对游戏状态的影响
        self.action_effectiveness = {}      # 记录动作效果

    def record_function_usage(self, func_id: str, func_name: str, step: int, selected: bool, confidence: float = 0.0, relevance: float = 0.0):
        """
        记录预制函数使用情况
        
        Args:
            func_id: 函数ID
            func_name: 函数名称
            step: 当前步骤
            selected: 是否被选中
            confidence: 函数置信度
            relevance: 函数与游戏状态的相关性
        """
        usage_record = {
            'func_id': func_id,
            'func_name': func_name,
            'step': step,
            'selected': selected,
            'confidence': confidence,
            'relevance': relevance,
            'timestamp': logging.Formatter('%(asctime)s').formatTime(logging.LogRecord('name', 0, '', 0, '', '', '', 0, ''))
        }
        self.function_usage_history.append(usage_record)

    def record_decision_quality(self, step: int, decision_type: str, functions_used: List[str], outcome: Dict[str, Any], game_state: Dict[str, Any] = None):
        """
        记录决策质量数据
        
        Args:
            step: 当前步骤
            decision_type: 决策类型
            functions_used: 使用的函数列表
            outcome: 决策结果
            game_state: 当前游戏状态
        """
        quality_record = {
            'step': step,
            'decision_type': decision_type,
            'functions_used': functions_used,
            'outcome': outcome,
            'game_state': game_state,
            'timestamp': logging.Formatter('%(asctime)s').formatTime(logging.LogRecord('name', 0, '', 0, '', '', '', 0, ''))
        }
        self.decision_quality_data.append(quality_record)

    def record_prefab_relevance(self, func_id: str, func_name: str, step: int, relevance: float, game_state: Dict[str, Any]):
        """
        记录预制函数与游戏状态的相关性
        
        Args:
            func_id: 函数ID
            func_name: 函数名称
            step: 当前步骤
            relevance: 相关性得分
            game_state: 当前游戏状态
        """
        relevance_record = {
            'func_id': func_id,
            'func_name': func_name,
            'step': step,
            'relevance': relevance,
            'game_state': game_state,
            'timestamp': logging.Formatter('%(asctime)s').formatTime(logging.LogRecord('name', 0, '', 0, '', '', '', 0, ''))
        }
        self.prefab_relevance_history.append(relevance_record)

    def record_decision_impact(self, step: int, pre_game_state: Dict[str, Any], post_game_state: Dict[str, Any], actions: Dict[str, Any]):
        """
        记录决策对游戏状态的影响
        
        Args:
            step: 当前步骤
            pre_game_state: 决策前的游戏状态
            post_game_state: 决策后的游戏状态
            actions: 执行的动作
        """
        # 计算状态变化
        state_change = {
            'friendly_count_change': post_game_state.get('friendly_count', 0) - pre_game_state.get('friendly_count', 0),
            'enemy_count_change': post_game_state.get('enemy_count', 0) - pre_game_state.get('enemy_count', 0),
            'low_health_units_change': (1 if post_game_state.get('has_low_health_units', False) else 0) - \
                                      (1 if pre_game_state.get('has_low_health_units', False) else 0),
            'action_count': len(actions.get('attack', [])) + len(actions.get('move', [])) + len(actions.get('ability', []))
        }
        
        impact_record = {
            'step': step,
            'pre_game_state': pre_game_state,
            'post_game_state': post_game_state,
            'actions': actions,
            'state_change': state_change,
            'timestamp': logging.Formatter('%(asctime)s').formatTime(logging.LogRecord('name', 0, '', 0, '', '', '', 0, ''))
        }
        self.decision_impact_history.append(impact_record)

    def get_performance_summary(self):
        """
        获取性能总结
        
        Returns:
            Dict[str, Any]: 性能总结数据
        """
        # 计算各函数的使用频率、选中率和平均相关性
        function_stats = {}
        for record in self.function_usage_history:
            func_id = record['func_id']
            if func_id not in function_stats:
                function_stats[func_id] = {
                    'name': record['func_name'],
                    'total_count': 0,
                    'selected_count': 0,
                    'total_relevance': 0.0,
                    'total_confidence': 0.0
                }
            function_stats[func_id]['total_count'] += 1
            function_stats[func_id]['total_relevance'] += record.get('relevance', 0.0)
            function_stats[func_id]['total_confidence'] += record.get('confidence', 0.0)
            if record['selected']:
                function_stats[func_id]['selected_count'] += 1
        
        # 计算平均相关性和置信度
        for func_id, stats in function_stats.items():
            stats['avg_relevance'] = stats['total_relevance'] / stats['total_count'] if stats['total_count'] > 0 else 0.0
            stats['avg_confidence'] = stats['total_confidence'] / stats['total_count'] if stats['total_count'] > 0 else 0.0
            stats['selected_rate'] = stats['selected_count'] / stats['total_count'] if stats['total_count'] > 0 else 0.0
        
        # 计算决策质量统计
        total_decisions = len(self.decision_quality_data)
        
        # 计算平均动作数量和类型分布
        avg_actions = {
            'attack': 0.0,
            'move': 0.0,
            'ability': 0.0
        }
        if total_decisions > 0:
            for record in self.decision_quality_data:
                outcome = record['outcome']
                avg_actions['attack'] += outcome.get('attack_count', 0)
                avg_actions['move'] += outcome.get('move_count', 0)
                avg_actions['ability'] += outcome.get('ability_count', 0)
            
            avg_actions['attack'] /= total_decisions
            avg_actions['move'] /= total_decisions
            avg_actions['ability'] /= total_decisions
        
        # 计算相关性趋势
        relevance_trend = []
        if self.prefab_relevance_history:
            # 按步骤分组计算平均相关性
            step_relevance = {}
            for record in self.prefab_relevance_history:
                step = record['step']
                if step not in step_relevance:
                    step_relevance[step] = []
                step_relevance[step].append(record['relevance'])
            
            # 计算每个步骤的平均相关性
            for step in sorted(step_relevance.keys()):
                avg_relevance = sum(step_relevance[step]) / len(step_relevance[step])
                relevance_trend.append({
                    'step': step,
                    'avg_relevance': avg_relevance
                })
        
        return {
            'function_stats': function_stats,
            'total_decisions': total_decisions,
            'avg_actions': avg_actions,
            'relevance_trend': relevance_trend,
            'usage_history': self.function_usage_history,
            'quality_history': self.decision_quality_data,
            'relevance_history': self.prefab_relevance_history,
            'decision_impact_history': self.decision_impact_history
        }
