import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from autodsl_affordance.core.prefab_system.handler.prefab_performance_monitor import PrefabPerformanceMonitor

class SynergyType(Enum):
    """协同类型枚举"""
    AIR_GROUND_COORDINATION = "air_ground_coordination"
    LONG_SHORT_RANGE_COORDINATION = "long_short_range_coordination" 
    ABILITY_UNIT_SYNERGY = "ability_unit_synergy"
    ARMOR_TYPE_COORDINATION = "armor_type_coordination"
    SUPPORT_DPS_COORDINATION = "support_dps_coordination"

@dataclass
class SynergyScore:
    """协同评分"""
    function_id: str
    name: str
    synergy_type: str
    synergy_score: float
    unit_availability_score: float
    tactical_fitness_score: float
    total_score: float
    relevance: float

# Common unit ID mappings for integer to string conversion
COMMON_UNIT_IDS = {
    # Protoss units
    105: 'Zealot',
    106: 'Stalker',
    107: 'Sentry',
    108: 'Adept',
    109: 'HighTemplar',
    110: 'DarkTemplar',
    111: 'Archon',
    113: 'Phoenix',
    114: 'VoidRay',
    115: 'Oracle',
    116: 'Tempest',
    117: 'Carrier',
    118: 'Interceptor',
    119: 'WarpPrism',
    120: 'Observer',
    121: 'Immortal',
    122: 'Colossus',
    123: 'Disruptor',
    
    # Terran units
    48: 'SCV',
    49: 'Marine',
    50: 'Marauder',
    51: 'Reaper',
    52: 'Ghost',
    53: 'Hellion',
    54: 'Hellbat',
    55: 'SiegeTank',
    56: 'Thor',
    57: 'Medivac',
    58: 'Viking',
    59: 'Banshee',
    60: 'Raven',
    61: 'Battlecruiser',
    62: 'Liberator',
    
    # Zerg units
    104: 'Drone',
    11: 'Zergling',
    12: 'Baneling',
    13: 'Roach',
    14: 'Ravager',
    15: 'Hydralisk',
    16: 'Lurker',
    17: 'Mutalisk',
    18: 'Corruptor',
    19: 'Viper',
    20: 'SwarmHost',
    21: 'Ultralisk',
    22: 'Infestor',
    23: 'Queen',
    24: 'Overlord'
}

# Import get_unit_name to convert integer unit types to string names
try:
    from vlm_attention.env.config import get_unit_name
except ImportError:
    # Fallback if the function is not available
    def get_unit_name(unit_type: int) -> str:
        """Fallback function to convert integer unit IDs to string names"""
        return COMMON_UNIT_IDS.get(unit_type, str(unit_type))

@dataclass
class UnitInfo:
    """单位信息"""
    unit_type: str
    tag: int
    position: Tuple[int, int]
    health: float
    shield: float
    is_alive: bool = True

logger = logging.getLogger(__name__)

class PrefabFunctionHandler:
    """
    预制函数处理器，封装所有预制函数相关逻辑
    包括：函数检索、评分、选择、执行和结果反馈
    """
    
    def __init__(self, prefab_function_manager, default_race: str = None):
        """
        初始化预制函数处理器
        
        Args:
            prefab_function_manager: 预制函数管理器实例
            default_race: 默认种族值，当种族检测失败时使用
        """
        self.prefab_function_manager = prefab_function_manager
        self.default_race = default_race
        
        # 执行历史记录
        self.prefab_function_history = []
        # 冷却时间管理
        self.prefab_function_cooldowns = {}
        # 执行结果记录
        self.prefab_execution_results = []
        
        # 单位池管理
        self.unit_pool = {
            'friendly': [],
            'enemy': []
        }
        
        # 向后兼容标志
        self._legacy_mode = False
        
        # 添加性能监控器
        self.performance_monitor = PrefabPerformanceMonitor()
        
        # 初始化游戏日志记录器（暂时注释，后续集成新的日志系统）
        # from vlm_attention.utils.game_logger import GameLogger
        # self.game_logger = GameLogger('prefab_function_logger')
    
    def retrieve_relevant_functions(self, observation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        基于当前游戏状态检索相关预制函数
        
        Args:
            observation: 游戏观察数据
            
        Returns:
            List[Dict[str, Any]]: 相关预制函数列表
        """
        prefab_functions = []
        
        # 获取当前友方单位和敌方单位
        friendly_units = [unit for unit in observation['unit_info'] if unit['alliance'] == 1]
        
        # 提取友方单位类型集合
        friendly_unit_types = set()
        for unit in friendly_units:
            unit_name = unit['unit_name']
            # 提取基础单位类型（去掉数字后缀）
            base_unit_type = unit_name.split('_')[0]
            friendly_unit_types.add(base_unit_type)
        
        # 1. 根据当前单位检索预制函数
        for unit in friendly_units:
            unit_name = unit['unit_name']
            # 提取基础单位类型（去掉数字后缀）
            base_unit_type = unit_name.split('_')[0]
            
            # 搜索与该单位相关的预制函数，尝试多种匹配方式
            unit_functions = []
            
            # 1.1 尝试精确匹配（带完整单位名）
            unit_functions.extend(self.prefab_function_manager.search_functions(unit=unit_name))
            
            # 1.2 尝试匹配基础单位类型
            unit_functions.extend(self.prefab_function_manager.search_functions(unit=base_unit_type))
            
            # 1.3 尝试带种族前缀的匹配（例如 Marine -> TerranMarine）
            race_prefixed_unit = f"{unit_name.split('_')[0].capitalize()}{base_unit_type}"
            unit_functions.extend(self.prefab_function_manager.search_functions(unit=race_prefixed_unit))
            
            prefab_functions.extend(unit_functions)
        
        # 2. 额外搜索所有异构协同函数
        # 获取所有预制函数并筛选出异构协同函数
        all_functions = self.prefab_function_manager.get_all_functions()
        for func in all_functions:
            # 检查是否为异构协同函数
            tactic_category = func.get('tactic_category', '')
            if tactic_category == 'heterogeneous_coordination':
                # 检查是否满足单位要求
                if 'prerequisites' in func and 'required_units' in func['prerequisites']:
                    required_units = func['prerequisites']['required_units']
                    # 检查所有必需单位是否都在我方单位中
                    if all(req_unit in friendly_unit_types for req_unit in required_units):
                        prefab_functions.append(func)
            # 检查是否为阵型控制协同函数
            elif tactic_category == 'formation_control_coordination':
                # 检查是否满足单位要求
                if 'prerequisites' in func and 'required_units' in func['prerequisites']:
                    required_units = func['prerequisites']['required_units']
                    # 检查所有必需单位是否都在我方单位中
                    if all(req_unit in friendly_unit_types for req_unit in required_units):
                        prefab_functions.append(func)
        
        # 去重
        seen = set()
        unique_prefab_functions = []
        for func in prefab_functions:
            func_id = func['function_id']
            if func_id not in seen:
                seen.add(func_id)
                unique_prefab_functions.append(func)
        
        logger.info(f"检索到 {len(unique_prefab_functions)} 个相关预制函数")
        
        # 记录检索到的预制函数（暂时注释，后续集成新的日志系统）
        # for func in unique_prefab_functions:
        #     self.game_logger.log_prefab_function(
        #         func['function_id'],
        #         func['name'],
        #         0.0,  # 初始评分
        #         0.0,  # 初始相关性
        #         False,  # 初始未选中
        #         event_type="RETRIEVED"
        #     )
        
        return unique_prefab_functions
    
    def _analyze_game_state(self, friendly_units, enemy_units, observation):
        """
        分析当前游戏状态
        
        Args:
            friendly_units: 友方单位列表
            enemy_units: 敌方单位列表
            observation: 游戏观察数据
            
        Returns:
            Dict[str, Any]: 游戏状态分析结果
        """
        # 计算单位数量
        friendly_count = len(friendly_units)
        enemy_count = len(enemy_units)
        
        # 分析单位类型
        friendly_unit_types = {}
        enemy_unit_types = {}
        
        # 详细单位类型映射
        friendly_detailed_types = {}
        enemy_detailed_types = {}
        
        for unit in friendly_units:
            unit_type = unit['unit_name'].split('_')[0]  # 提取基础单位类型
            friendly_unit_types[unit_type] = friendly_unit_types.get(unit_type, 0) + 1
            
            # 添加详细单位类型
            detailed_type = unit['unit_name']
            friendly_detailed_types[detailed_type] = friendly_detailed_types.get(detailed_type, 0) + 1
        
        for unit in enemy_units:
            unit_type = unit['unit_name'].split('_')[0]  # 提取基础单位类型
            enemy_unit_types[unit_type] = enemy_unit_types.get(unit_type, 0) + 1
            
            # 添加详细单位类型
            detailed_type = unit['unit_name']
            enemy_detailed_types[detailed_type] = enemy_detailed_types.get(detailed_type, 0) + 1
        
        # 分析单位健康状况
        has_medivac = any('Medivac' in unit['unit_name'] for unit in friendly_units)
        has_low_health_units = any(unit['health'] < unit['max_health'] * 0.5 for unit in friendly_units)
        
        # 分析单位能量状况
        has_energy_units = any(unit['energy'] > 0 for unit in friendly_units)
        high_energy_units = any(unit['energy'] > 50 for unit in friendly_units)
        
        # 分析单位类型比例
        unit_type_diversity = len(friendly_unit_types) / friendly_count if friendly_count > 0 else 0
        
        return {
            'friendly_count': friendly_count,
            'enemy_count': enemy_count,
            'friendly_unit_types': friendly_unit_types,
            'enemy_unit_types': enemy_unit_types,
            'friendly_detailed_types': friendly_detailed_types,
            'enemy_detailed_types': enemy_detailed_types,
            'has_medivac': has_medivac,
            'has_low_health_units': has_low_health_units,
            'has_energy_units': has_energy_units,
            'high_energy_units': high_energy_units,
            'unit_type_diversity': unit_type_diversity,
            'text_observation': observation.get('text', '')
        }
    
    def score_functions(self, prefab_functions: List[Dict[str, Any]], observation: Dict[str, Any]) -> List[Tuple[Dict[str, Any], float]]:
        """
        为预制函数评分
        
        Args:
            prefab_functions: 预制函数列表
            observation: 游戏观察数据
            
        Returns:
            List[Tuple[Dict[str, Any], float]]: 带评分的预制函数列表
        """
        # 分析游戏状态
        friendly_units = [unit for unit in observation['unit_info'] if unit['alliance'] == 1]
        enemy_units = [unit for unit in observation['unit_info'] if unit['alliance'] != 1]
        game_state = self._analyze_game_state(friendly_units, enemy_units, observation)
        
        # 检测当前种族
        current_race = self._detect_race(friendly_units)
        
        logger.info(f"当前检测到的种族: {current_race}")
        
        # 为每个预制函数评分
        scored_functions = []
        for func in prefab_functions:
            func_id = func['function_id']
            func_name = func['name']
            score = 0.0
            
            # 检查函数是否适合WithoutMove模式
            # 过滤掉明确要求move的函数，但保留与move相关但可以适配的战术性移动函数
            is_pure_move = False
            
            func_name_lower = func_name.lower()
            
            # 特殊处理医疗机相关函数，它们不是纯移动函数
            if 'medivac' in func_name_lower or 'heal_' in func_name_lower:
                # 医疗机相关函数不是纯移动函数，直接通过
                pass
            else:
                # 检查函数名称中是否包含纯移动相关词汇
                pure_move_keywords = ['move', 'move_to_position', 'position_move', 'navigate']
                allowed_move_keywords = ['push', 'retreat', 'advance', 'withdraw', 'flank', 'mm_push']
                
                has_pure_move = any(keyword in func_name_lower for keyword in pure_move_keywords)
                has_allowed_move = any(keyword in func_name_lower for keyword in allowed_move_keywords)
                
                # 检查执行流程中是否包含纯移动指令
                execution_flow = str(func.get('execution_flow', '')).lower()
                has_move_execution = 'move_to_position' in execution_flow or 'move(' in execution_flow
                has_allowed_execution = 'mm_push' in func_name_lower
                
                # 综合判断是否为纯移动函数
                if has_pure_move and not has_allowed_move:
                    is_pure_move = True
                elif has_move_execution and not has_allowed_execution:
                    is_pure_move = True
                
                if is_pure_move:
                    # 跳过纯移动函数，保留战术性移动函数
                    continue
            
            # 种族匹配检查：如果当前种族已检测，跳过不匹配的预制函数
            if current_race:
                # 检测预制函数的种族
                func_race = ""
                
                # 从函数ID中提取种族
                func_id_upper = func_id.upper()
                if 'TERRAN' in func_id_upper:
                    func_race = "terran"
                elif 'PROTOSS' in func_id_upper:
                    func_race = "protoss"
                elif 'ZERG' in func_id_upper:
                    func_race = "zerg"
                
                # 从函数名称中提取种族
                if not func_race:
                    if any(race in func_name_lower for race in ['terran', 'protoss', 'zerg']):
                        func_race = next(race for race in ['terran', 'protoss', 'zerg'] if race in func_name_lower)
                
                # 从源单位中提取种族
                if not func_race and 'source_unit' in func:
                    source_unit_lower = func['source_unit'].lower()
                    if any(race in source_unit_lower for race in ['terran', 'protoss', 'zerg']):
                        func_race = next(race for race in ['terran', 'protoss', 'zerg'] if race in source_unit_lower)
                
                # 从目标单位中提取种族
                if not func_race and 'target_unit' in func:
                    target_unit_lower = func['target_unit'].lower()
                    if any(race in target_unit_lower for race in ['terran', 'protoss', 'zerg']):
                        func_race = next(race for race in ['terran', 'protoss', 'zerg'] if race in target_unit_lower)
                
                # 从执行流程中提取种族
                if not func_race:
                    execution_flow_lower = str(func.get('execution_flow', '')).lower()
                    if any(race in execution_flow_lower for race in ['terran', 'protoss', 'zerg']):
                        func_race = next(race for race in ['terran', 'protoss', 'zerg'] if race in execution_flow_lower)
                
                # 如果预制函数明确指定了种族，且与当前种族不匹配，跳过
                if func_race and func_race != current_race.lower():
                    # logger.info(f"跳过预制函数 {func_id} ({func_name}): 种族不匹配，函数种族为{func_race}，当前种族为{current_race}")
                    continue
                elif func_race:
                    logger.info(f"预制函数 {func_id} ({func_name}) 种族匹配，函数种族为{func_race}，当前种族为{current_race}")
            
            # 检查源单位是否为我方单位
            if 'source_unit' in func:
                source_unit = func['source_unit']
                # 特殊处理通用单位类型
                if source_unit in ['all_friendly', 'all_ground_friendly', 'friendly_infantry', 'all_mechanical', 'all_infantry']:
                    # 通用单位类型直接通过检查
                    has_source = True
                else:
                    # 提取基础单位类型，支持从TerranMarine中提取Marine
                    # 方法：如果单位名称包含'_',则取最后一部分；否则，尝试匹配全名或提取种族后的部分
                    if '_' in source_unit:
                        source_base = source_unit.split('_')[-1]
                    else:
                        # 尝试直接匹配全名
                        source_base = source_unit
                    
                    # 检查源单位是否是我方拥有的单位
                    has_source = any(source_base.lower() in u['unit_name'].lower() for u in friendly_units)
                    
                    # 如果直接匹配失败，尝试提取种族前缀后的部分（如TerranMarine -> Marine）
                    if not has_source and len(source_base) > 5:  # 排除太短的单位名称
                        # 尝试去掉种族前缀（Terran, Protoss, Zerg）
                        for race_prefix in ['Terran', 'Protoss', 'Zerg']:
                            if source_base.startswith(race_prefix):
                                race_removed = source_base[len(race_prefix):]
                                has_source = any(race_removed.lower() in u['unit_name'].lower() for u in friendly_units)
                                if has_source:
                                    break
                    
                    # 尝试更灵活的匹配：检查源单位的小写形式是否包含在单位名称的小写形式中
                    if not has_source:
                        source_lower = source_unit.lower()
                        has_source = any(source_lower in u['unit_name'].lower() for u in friendly_units)
                    
                    if not has_source:
                        # 源单位不是我方单位，跳过该函数
                        # logger.info(f"跳过预制函数 {func_id} ({func_name}): 源单位 {source_unit} 不是我方单位")
                        continue
            
            # 检查目标单位是否为敌方单位
            if 'target_unit' in func:
                target_unit = func['target_unit']
                # 如果是通用目标类型，允许
                if target_unit not in ['high_value_enemy_unit', 'high_value_terran_unit', 'nearest_enemy', 'nearest_enemy_unit', 'highest_threat_enemy', 'lowest_health_enemy', 'armored_enemy', 'light_enemy', 'lowest_health_friendly', 'all_enemy', 'closest_enemy']:
                    # 提取基础单位类型，支持从ProtossColossus中提取Colossus
                    if '_' in target_unit:
                        target_base = target_unit.split('_')[-1]
                    else:
                        target_base = target_unit
                    
                    # 检查目标单位是否是敌方单位类型
                    has_enemy_target = any(target_base.lower() in unit['unit_name'].lower() for unit in enemy_units)
                    
                    # 如果直接匹配失败，尝试提取种族前缀后的部分（如ProtossColossus -> Colossus）
                    if not has_enemy_target and len(target_base) > 5:  # 排除太短的单位名称
                        # 尝试去掉种族前缀（Terran, Protoss, Zerg）
                        for race_prefix in ['Terran', 'Protoss', 'Zerg']:
                            if target_base.startswith(race_prefix):
                                race_removed = target_base[len(race_prefix):]
                                has_enemy_target = any(race_removed.lower() in unit['unit_name'].lower() for unit in enemy_units)
                                if has_enemy_target:
                                    break
                    
                    if not has_enemy_target:
                        # 目标单位不是敌方单位，跳过该函数
                        # logger.info(f"跳过预制函数 {func_id} ({func_name}): 目标单位 {target_unit} 不是敌方单位")
                        continue
            
            # 1. 基于函数置信度评分
            if 'confidence' in func:
                score += func['confidence'] * 5.0
            
            # 2. 基于函数名称和游戏状态评分（按种族优化）
            if 'target_' in func_name:
                # 目标设置函数：检查源单位和目标单位是否存在
                if 'source_unit' in func and 'target_unit' in func:
                    source_unit = func['source_unit']
                    target_unit = func['target_unit']
                    
                    # 提取基础单位类型（去掉种族前缀）
                    source_base = source_unit.split('_')[-1] if '_' in source_unit else source_unit
                    target_base = target_unit.split('_')[-1] if '_' in target_unit else target_unit
                    
                    # 检查是否有匹配的友方和敌方单位
                    has_source = any(source_base in unit['unit_name'] for unit in friendly_units)
                    has_target = any(target_base in unit['unit_name'] for unit in enemy_units)
                    
                    if has_source and has_target:
                        score += 8.0
                    elif has_source:
                        score += 4.0
            
            # 人族特有函数评分
            elif current_race == 'terran':
                if 'mm_push' in func_name:
                    # MM推进函数：检查是否有足够的Marine和Marauder
                    marine_count = game_state['friendly_unit_types'].get('Marine', 0)
                    marauder_count = game_state['friendly_unit_types'].get('Marauder', 0)
                    
                    if marine_count >= 3 and marauder_count >= 1:
                        score += 10.0
                    elif marine_count >= 2 and marauder_count >= 1:
                        score += 6.0
                    elif marine_count >= 2:
                        score += 3.0
                elif 'LoadMedivac' in func_name or 'UnloadMedivac' in func_name:
                    # 如果有医疗运输机和受伤单位，加载/卸载函数评分高
                    if game_state['has_medivac']:
                        score += 5.0
                        if game_state['has_low_health_units']:
                            score += 3.0
                elif 'heal_' in func_name or 'medivac' in func_name.lower():
                    # 治疗函数和医疗机相关函数：检查是否有医疗运输机
                    if game_state['has_medivac']:
                        # 为医疗机相关预制函数增加额外评分
                        if 'follow' in func_name.lower() or 'stay' in func_name.lower():
                            # 跟随类医疗机函数获得更高评分
                            score += 12.0
                        elif game_state['has_low_health_units']:
                            # 治疗函数，有受伤单位时评分更高
                            score += 10.0
                        else:
                            # 一般医疗机函数
                            score += 7.0
                elif 'Stim' in func_name:
                    # 如果有大量陆战队或掠夺者，兴奋剂函数评分高
                    if game_state['friendly_unit_types'].get('Marine', 0) > 3 or game_state['friendly_unit_types'].get('Marauder', 0) > 2:
                        score += 7.0
                elif 'Siege' in func_name or 'Unsiege' in func_name:
                    # 如果有攻城坦克，攻城/解除攻城函数评分高
                    if game_state['friendly_unit_types'].get('SiegeTank', 0) > 0:
                        score += 8.0
            
            # 神族特有函数评分
            elif current_race == 'protoss':
                if 'Warp' in func_name or 'WarpIn' in func_name:
                    # 如果有 warp prism 或相关单位， warp 相关函数评分高
                    if game_state['friendly_unit_types'].get('WarpPrism', 0) > 0:
                        score += 8.0
                elif 'Shield' in func_name or 'GuardianShield' in func_name:
                    # 如果有 sentry，护盾相关函数评分高
                    if game_state['friendly_unit_types'].get('Sentry', 0) > 0:
                        score += 7.0
                elif 'Psionic' in func_name or 'Storm' in func_name:
                    # 如果有 high templar，灵能相关函数评分高
                    if game_state['friendly_unit_types'].get('HighTemplar', 0) > 0:
                        score += 9.0
            
            # 虫族特有函数评分
            elif current_race == 'zerg':
                if 'Creep' in func_name or 'SpreadCreep' in func_name:
                    # 如果有 queen，蔓延菌毯函数评分高
                    if game_state['friendly_unit_types'].get('Queen', 0) > 0:
                        score += 7.0
                elif 'Inject' in func_name or 'Larva' in func_name:
                    # 如果有 queen，注卵相关函数评分高
                    if game_state['friendly_unit_types'].get('Queen', 0) > 0:
                        score += 8.0
                elif 'Swarm' in func_name or 'Spawn' in func_name:
                    # 如果有足够的单位，虫群相关函数评分高
                    if game_state['friendly_count'] > 5:
                        score += 6.0
            
            # 通用函数评分
            elif 'Attack' in func_name or 'FocusFire' in func_name:
                # 如果敌方单位数量多，攻击函数评分高
                if game_state['enemy_count'] > game_state['friendly_count']:
                    score += 6.0
            elif 'Move' in func_name or 'Retreat' in func_name:
                # 如果友方单位数量少，移动/撤退函数评分高
                if game_state['friendly_count'] < game_state['enemy_count']:
                    score += 6.0
            
            # 3. 基于战术类别评分
            tactic_category = func.get('tactic_category', '')
            if tactic_category == 'targeting':
                score += 3.0
            elif tactic_category == 'offense' and game_state['friendly_count'] > game_state['enemy_count']:
                score += 4.0
            elif tactic_category == 'defense' and game_state['friendly_count'] < game_state['enemy_count']:
                score += 4.0
            elif tactic_category == 'support' and game_state['has_low_health_units']:
                score += 5.0
            elif tactic_category == 'heterogeneous_coordination':
                # 为异构协同函数添加额外评分加成
                score += 8.0
                # 如果包含多种不同类型的单位，再添加额外加成
                if len(game_state['friendly_unit_types']) >= 4:
                    score += 2.0
            elif tactic_category == 'formation_control_coordination':
                # 为阵型控制协同函数添加额外评分加成
                score += 6.0
            
            # 4. 基于函数类型评分和单位检查
            function_type = func.get('function_type', '')
            linkage_type = func.get('linkage_type', '')
            
            # 检查是否为组合类型（考虑function_type或linkage_type）
            is_combination = function_type == 'combination' or linkage_type == 'combination'
            
            # 检查所有需要的单位是否都是我方单位
            all_units_valid = True
            required_units = []
            
            # 从prerequisites.required_units获取单位
            if 'prerequisites' in func and 'required_units' in func['prerequisites']:
                required_units.extend(func['prerequisites']['required_units'])
            
            # 从units获取单位（兼容旧格式）
            if 'units' in func:
                required_units.extend(func['units'])
            
            # 检查所有需要的单位
            for unit in required_units:
                # 特殊处理通用单位类型
                if unit in ['all_friendly', 'all_ground_friendly', 'friendly_infantry', 'all_mechanical', 'all_infantry']:
                    continue
                
                # 提取基础单位类型，支持从TerranMarine中提取Marine
                if '_' in unit:
                    unit_base = unit.split('_')[-1]
                else:
                    unit_base = unit
                
                # 1. 直接匹配：检查单位是否是我方拥有的单位
                has_unit = any(unit_base.lower() in u['unit_name'].lower() for u in friendly_units)
                
                # 2. 提取种族前缀后的部分（如TerranMarine -> Marine）
                if not has_unit and len(unit_base) > 5:  # 排除太短的单位名称
                    # 尝试去掉种族前缀（Terran, Protoss, Zerg）
                    for race_prefix in ['Terran', 'Protoss', 'Zerg']:
                        if unit_base.startswith(race_prefix):
                            race_removed = unit_base[len(race_prefix):]
                            has_unit = any(race_removed.lower() in u['unit_name'].lower() for u in friendly_units)
                            if has_unit:
                                break
                
                # 3. 更灵活的匹配：检查单位的小写形式是否包含在单位名称的小写形式中
                if not has_unit:
                    unit_lower = unit.lower()
                    has_unit = any(unit_lower in u['unit_name'].lower() for u in friendly_units)
                
                # 4. 检查基础单位类型是否匹配（去掉数字后缀）
                if not has_unit:
                    base_unit_type = unit_base.split('_')[0] if '_' in unit_base else unit_base
                    has_unit = any(base_unit_type.lower() == u['unit_name'].split('_')[0].lower() for u in friendly_units)
                
                if not has_unit:
                    all_units_valid = False
                    break
            
            if is_combination:
                if all_units_valid:
                    # 组合函数评分更高
                    score += 3.0
                else:
                    # 组合函数中包含我方没有的单位，跳过
                    # logger.info(f"跳过预制函数 {func_id} ({func_name}): 组合函数中包含我方没有的单位")
                    continue
            elif required_units and not all_units_valid:
                # 非组合函数但包含我方没有的单位，跳过
                # logger.info(f"跳过预制函数 {func_id} ({func_name}): 包含我方没有的单位")
                continue
            elif function_type == 'interaction':
                score += 2.0
            
            # 5. 多样性约束：避免重复执行相同函数，但降低惩罚力度
            recent_history = self.prefab_function_history[-5:]  # 最近5步的历史
            func_usage_count = recent_history.count(func_id)
            if func_usage_count > 0:
                # 降低多样性惩罚，从0.8调整为0.95，允许更频繁使用有效的函数
                score *= (0.95 ** func_usage_count)
            
            # 6. 冷却时间约束：如果函数在冷却中，降低评分，但降低惩罚力度
            if func_id in self.prefab_function_cooldowns:
                cooldown = self.prefab_function_cooldowns[func_id]
                if cooldown > 0:
                    # 根据剩余冷却时间调整评分，降低惩罚力度
                    score *= (0.8 + (cooldown / 10.0))  # 冷却惩罚从0.2降低到0.1 per step
            
            # 7. 执行结果反馈：根据历史执行结果调整评分
            if func_id in [result['func_id'] for result in self.prefab_execution_results]:
                # 查找最近5次执行结果
                recent_results = [r for r in self.prefab_execution_results if r['func_id'] == func_id][-5:]
                if recent_results:
                    # 计算平均成功率
                    success_rate = sum(1 for r in recent_results if r['success']) / len(recent_results)
                    # 根据成功率调整评分
                    score *= (0.5 + success_rate * 0.5)  # 成功率越高，评分加成越高
            
            scored_functions.append((func, score))
            logger.info(f"预制函数评分: ID={func_id}, Name={func_name}, Score={score}")
        
        # 按分数排序
        scored_functions.sort(key=lambda x: x[1], reverse=True)
        return scored_functions
    
    def select_optimal_functions(self, scored_functions: List[Tuple[Dict[str, Any], float]], top_k: int = 3, game_state: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        选择最优预制函数
        
        Args:
            scored_functions: 带评分的预制函数列表
            top_k: 选择前k个最优函数
            game_state: 当前游戏状态，用于相关性计算和性能监控
            
        Returns:
            List[Dict[str, Any]]: 最优预制函数列表
        """
        # 按分数排序
        scored_functions.sort(key=lambda x: x[1], reverse=True)
        
        # 选择前top_k个函数
        optimal_functions = [func for func, score in scored_functions[:top_k] if score > 0]
        
        # 记录函数选择情况到性能监控器
        for func, score in scored_functions:
            is_selected = func in optimal_functions
            relevance = 0.0
            if game_state:
                relevance = self._calculate_function_relevance(func, game_state)
                # 记录预制函数与游戏状态的相关性
                self.performance_monitor.record_prefab_relevance(
                    func_id=func['function_id'],
                    func_name=func['name'],
                    step=-1,  # 步骤号将在调用处更新
                    relevance=relevance,
                    game_state=game_state
                )
            
            self.performance_monitor.record_function_usage(
                func_id=func['function_id'],
                func_name=func['name'],
                step=-1,  # 步骤号将在调用处更新
                selected=is_selected,
                confidence=func.get('confidence', 0.0),
                relevance=relevance
            )
        
        logger.info(f"最终选择了 {len(optimal_functions)} 个最优预制函数:")
        for i, func in enumerate(optimal_functions, 1):
            score = next(s for f, s in scored_functions if f == func)
            relevance = self._calculate_function_relevance(func, game_state) if game_state else 0.0
            logger.info(f"  {i}. ID={func['function_id']}, Name={func['name']}, Score={score}, Relevance={relevance}")
        
        # 记录最终选择的预制函数（暂时注释，后续集成新的日志系统）
        # for func in optimal_functions:
        #     score = next(s for f, s in scored_functions if f == func)
        #     relevance = self._calculate_function_relevance(func, game_state) if game_state else 0.0
        #     self.game_logger.log_prefab_function(
        #         func['function_id'],
        #         func['name'],
        #         score,
        #         relevance,
        #         True,
        #         event_type="SELECTED",
        #         game_state=game_state
        #     )
        
        # 更新实时监控器
        return optimal_functions
    
    def execute_functions(self, optimal_prefab_functions: List[Dict[str, Any]], observation: Dict[str, Any], step_count: int) -> Dict[str, List[Any]]:
        """
        简化版执行方法，仅返回空动作，不进行具体执行
        
        Args:
            optimal_prefab_functions: 最优预制函数列表
            observation: 游戏观察数据
            step_count: 当前步骤计数
            
        Returns:
            Dict[str, List[Any]]: 空动作字典
        """
        logger.info(f"简化模式：预制函数仅提供战术信息，不直接执行动作")
        return {}
    
    def update_unit_pool(self, friendly_units: List[UnitInfo], enemy_units: List[UnitInfo] = None):
        """更新单位池"""
        self.unit_pool = {
            'friendly': friendly_units,
            'enemy': enemy_units or []
        }
    
    def _normalize_unit_name(self, unit_name: str) -> str:
        """标准化单位名称，用于匹配"""
        if not unit_name:
            return ""
        
        # 去除空格和下划线，转为小写
        normalized = unit_name.replace(" ", "").replace("_", "").lower()
        
        # 处理种族前缀
        prefixes = ["protoss", "terran", "zerg"]
        for prefix in prefixes:
            if normalized.startswith(prefix):
                # 去除种族前缀，保留基础名称
                base_name = normalized[len(prefix):]
                # 去除数字后缀
                base_name = ''.join([c for c in base_name if not c.isdigit()])
                return base_name
        
        # 去除数字后缀
        normalized = ''.join([c for c in normalized if not c.isdigit()])
        return normalized
    
    def _is_unit_match(self, required_unit: str, available_unit: str) -> bool:
        """检查单位是否匹配，仅支持精确匹配"""
        if not required_unit or not available_unit:
            return False
        
        # 标准化名称
        required_normalized = self._normalize_unit_name(required_unit)
        available_normalized = self._normalize_unit_name(available_unit)
        
        # 仅精确匹配
        if required_normalized == available_normalized:
            return True
        
        return False
    
    def _analyze_terrain(self, friendly_units: List[UnitInfo], enemy_units: List[UnitInfo]) -> Dict[str, Any]:
        """分析地形特征： choke points, high ground, cover"""
        terrain_analysis = {
            'has_choke_point': False,
            'friendly_on_high_ground': False,
            'enemy_on_high_ground': False,
            'friendly_has_cover': False,
            'enemy_has_cover': False,
            'terrain_complexity': 0.0
        }
        
        # 简化的地形分析（基于单位位置分布）
        if not friendly_units:
            return terrain_analysis
        
        # 计算单位位置分布的紧凑度来检测可能的瓶颈
        friendly_positions = [unit.position for unit in friendly_units]
        enemy_positions = [unit.position for unit in enemy_units]
        
        # 检测瓶颈：如果单位分布非常集中
        if len(friendly_positions) >= 3:
            # 计算位置方差
            avg_x = sum(pos[0] for pos in friendly_positions) / len(friendly_positions)
            avg_y = sum(pos[1] for pos in friendly_positions) / len(friendly_positions)
            variance_x = sum((pos[0] - avg_x)**2 for pos in friendly_positions) / len(friendly_positions)
            variance_y = sum((pos[1] - avg_y)**2 for pos in friendly_positions) / len(friendly_positions)
            
            # 如果方差很小，可能处于瓶颈
            if variance_x < 1000 and variance_y < 1000:
                terrain_analysis['has_choke_point'] = True
        
        # 简化的高地检测（基于y坐标，假设y值越高位置越高）
        avg_friendly_y = sum(pos[1] for pos in friendly_positions) / len(friendly_positions) if friendly_positions else 0
        avg_enemy_y = sum(pos[1] for pos in enemy_positions) / len(enemy_positions) if enemy_positions else 0
        
        # 高地优势判断
        if avg_friendly_y > avg_enemy_y + 20:
            terrain_analysis['friendly_on_high_ground'] = True
        elif avg_enemy_y > avg_friendly_y + 20:
            terrain_analysis['enemy_on_high_ground'] = True
        
        # 简化的掩体检测（基于单位间距）
        if len(friendly_positions) >= 2:
            # 计算单位间平均距离
            distances = []
            for i in range(len(friendly_positions)):
                for j in range(i+1, len(friendly_positions)):
                    dist = ((friendly_positions[i][0] - friendly_positions[j][0])**2 + 
                            (friendly_positions[i][1] - friendly_positions[j][1])**2)**0.5
                    distances.append(dist)
            
            avg_distance = sum(distances) / len(distances) if distances else 0
            
            # 如果单位间距离适中，可能有良好的掩体分布
            if 10 < avg_distance < 30:
                terrain_analysis['friendly_has_cover'] = True
        
        # 地形复杂度评估（基于位置多样性）
        x_values = set(pos[0] for pos in friendly_positions)
        y_values = set(pos[1] for pos in friendly_positions)
        terrain_analysis['terrain_complexity'] = min(1.0, (len(x_values) + len(y_values)) / 20.0)
        
        return terrain_analysis
    
    def _detect_race(self, units: List[Any]) -> str:
        """检测单位所属种族"""
        try:
            for unit in units:
                # 处理不同格式的单位信息
                if isinstance(unit, dict):
                    unit_type_str = unit.get('unit_name', '').lower()
                else:
                    unit_type_str = str(unit.unit_type).lower()
                
                # 检测种族关键字
                if any(protoss in unit_type_str for protoss in ['zealot', 'stalker', 'phoenix', 'immortal', 'archon', 'sentry', 'hightemplar', 'darktemplar', 'colossus', 'observer', 'warp prism', 'carrier', 'tempest', 'void ray', 'protoss']):
                    return 'protoss'
                elif any(terran in unit_type_str for terran in ['marine', 'marauder', 'reaper', 'ghost', 'hellbat', 'siegetank', 'thor', 'medivac', 'viking', 'banshee', 'raven', 'battlecruiser', 'liberator', 'terran']):
                    return 'terran'
                elif any(zerg in unit_type_str for zerg in ['zergling', 'baneling', 'roach', 'ravager', 'hydralisk', 'lurker', 'mutalisk', 'corruptor', 'viper', 'ultralisk', 'infestor', 'swarm host', 'brood lord', 'queen', 'drone', 'overlord', 'zerg']):
                    return 'zerg'
            
            # 检测失败，检查是否有默认种族
            if self.default_race:
                logger.info(f"种族检测失败，使用默认种族: {self.default_race}")
                return self.default_race
            else:
                logger.info("种族检测失败，且无默认种族设置，返回unknown")
                return 'unknown'
        except Exception as e:
            logger.error(f"种族检测过程中出现异常: {e}")
            # 异常情况下，使用默认种族
            if self.default_race:
                logger.info(f"种族检测异常，使用默认种族: {self.default_race}")
                return self.default_race
            else:
                logger.info("种族检测异常，且无默认种族设置，返回unknown")
                return 'unknown'
    
    def _evaluate_positioning(self, friendly_units: List[UnitInfo], enemy_units: List[UnitInfo]) -> Dict[str, float]:
        """评估单位定位和阵型： frontline, support positioning, flanking potential"""
        positioning_scores = {
            'frontline_cohesion': 0.0,
            'support_behind_frontline': 0.0,
            'flanking_potential': 0.0,
            'enemy_encirclement': 0.0,
            'overall_positioning': 0.0
        }
        
        if not friendly_units or not enemy_units:
            return positioning_scores
        
        # 简化的单位分类：假设某些单位类型是前线，某些是支援
        frontline_units = {
            'ProtossZealot', 'ProtossImmortal', 'ProtossArchon',
            'TerranMarine', 'TerranMarauder', 'TerranSiegeTank', 'TerranThor',
            'ZergZergling', 'ZergRoach', 'ZergUltralisk'
        }
        
        support_units = {
            'ProtossHighTemplar', 'ProtossSentry', 'ProtossObserver',
            'TerranMedivac', 'TerranRaven', 'TerranGhost',
            'ZergQueen', 'ZergInfestor', 'ZergViper'
        }
        
        # 提取前线和支援单位
        friendly_frontline = [unit for unit in friendly_units if unit.unit_type in frontline_units]
        friendly_support = [unit for unit in friendly_units if unit.unit_type in support_units]
        
        # 1. 前线凝聚力：前线单位之间的距离
        if friendly_frontline:
            frontline_positions = [unit.position for unit in friendly_frontline]
            avg_x = sum(pos[0] for pos in frontline_positions) / len(frontline_positions)
            
            # 计算前线单位与平均x坐标的偏差
            cohesion_deviation = sum(abs(pos[0] - avg_x) for pos in frontline_positions) / len(frontline_positions)
            # 标准化到0-1范围，偏差越小越好
            positioning_scores['frontline_cohesion'] = max(0.0, min(1.0, 1.0 - cohesion_deviation / 50.0))
        
        # 2. 支援单位位于前线后方：比较y坐标（假设y值越高越靠后）
        if friendly_frontline and friendly_support:
            avg_frontline_y = sum(unit.position[1] for unit in friendly_frontline) / len(friendly_frontline)
            avg_support_y = sum(unit.position[1] for unit in friendly_support) / len(friendly_support)
            
            # 如果支援单位平均y坐标高于前线，说明在后方
            if avg_support_y > avg_frontline_y:
                positioning_scores['support_behind_frontline'] = 1.0
            else:
                # 计算支援单位在后方面积的比例
                support_behind = sum(1 for unit in friendly_support if unit.position[1] > avg_frontline_y)
                positioning_scores['support_behind_frontline'] = support_behind / len(friendly_support)
        
        # 3. 侧翼潜力：检查是否有单位位于敌人侧翼
        if friendly_units and enemy_units:
            enemy_positions = [unit.position for unit in enemy_units]
            avg_enemy_x = sum(pos[0] for pos in enemy_positions) / len(enemy_positions)
            avg_enemy_y = sum(pos[1] for pos in enemy_positions) / len(enemy_positions)
            
            # 计算敌人的左右边界
            enemy_left = min(pos[0] for pos in enemy_positions)
            enemy_right = max(pos[0] for pos in enemy_positions)
            
            # 检测侧翼单位：位于敌人左右两侧超过一定距离
            flank_distance = (enemy_right - enemy_left) * 0.5
            flanking_units = [unit for unit in friendly_units 
                            if (unit.position[0] < enemy_left - flank_distance or 
                                unit.position[0] > enemy_right + flank_distance) and 
                                abs(unit.position[1] - avg_enemy_y) < flank_distance]
            
            positioning_scores['flanking_potential'] = min(1.0, len(flanking_units) / len(friendly_units) * 2.0)
        
        # 4. 计算整体定位评分
        positioning_scores['overall_positioning'] = (
            positioning_scores['frontline_cohesion'] * 0.3 +
            positioning_scores['support_behind_frontline'] * 0.3 +
            positioning_scores['flanking_potential'] * 0.4
        )
        
        return positioning_scores
    
    def update_history(self, func_id: str, func_name: str, actions: Dict[str, List[Any]], step_count: int, success: bool = True) -> None:
        """
        更新预制函数执行历史
        
        Args:
            func_id: 函数ID
            func_name: 函数名称
            actions: 执行生成的动作
            step_count: 当前步骤计数
            success: 执行是否成功
        """
        # 记录执行的函数ID
        self.prefab_function_history.append(func_id)
        
        # 设置冷却时间（根据函数类型设置不同冷却时间）
        if 'mm_push' in func_name:
            self.prefab_function_cooldowns[func_id] = 3  # mm_push冷却3步
        elif 'Stim' in func_name:
            self.prefab_function_cooldowns[func_id] = 2  # Stim冷却2步
        elif 'Siege' in func_name:
            self.prefab_function_cooldowns[func_id] = 4  # Siege冷却4步
        else:
            self.prefab_function_cooldowns[func_id] = 1  # 其他函数冷却1步
        
        # 记录执行结果
        self.prefab_execution_results.append({
            'func_id': func_id,
            'func_name': func_name,
            'step': step_count,
            'success': success,
            'actions': actions
        })
    
    def decrement_cooldowns(self) -> None:
        """
        递减所有预制函数的冷却时间
        """
        for func_id in list(self.prefab_function_cooldowns.keys()):
            self.prefab_function_cooldowns[func_id] -= 1
            if self.prefab_function_cooldowns[func_id] <= 0:
                del self.prefab_function_cooldowns[func_id]
    
    def record_execution_result(self, func_id: str, success: bool, game_state_before: Dict[str, Any], game_state_after: Dict[str, Any], actions: Dict[str, List[Any]] = None):
        """
        记录预制函数执行结果，增强反馈机制
        
        Args:
            func_id: 预制函数ID
            success: 执行是否成功
            game_state_before: 执行前的游戏状态
            game_state_after: 执行后的游戏状态
            actions: 执行的具体动作
        """
        from datetime import datetime
        
        # 计算执行效果指标
        effect_metrics = {
            'friendly_count_change': game_state_after.get('friendly_count', 0) - game_state_before.get('friendly_count', 0),
            'enemy_count_change': game_state_after.get('enemy_count', 0) - game_state_before.get('enemy_count', 0),
            'low_health_units_change': (1 if game_state_after.get('has_low_health_units', False) else 0) - 
                                     (1 if game_state_before.get('has_low_health_units', False) else 0),
            'friendly_health_change': game_state_after.get('friendly_health', 0) - game_state_before.get('friendly_health', 0),
            'enemy_health_change': game_state_after.get('enemy_health', 0) - game_state_before.get('enemy_health', 0),
            'resource_change': game_state_after.get('resources', 0) - game_state_before.get('resources', 0)
        }
        
        # 评估执行质量（多维度评估）
        execution_quality = self._evaluate_execution_quality(success, effect_metrics)
        
        execution_result = {
            'func_id': func_id,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'game_state_before': game_state_before,
            'game_state_after': game_state_after,
            'actions': actions or {},
            'effect_metrics': effect_metrics,
            'execution_quality': execution_quality
        }
        
        self.prefab_execution_results.append(execution_result)
        logger.info(f"记录预制函数执行结果: ID={func_id}, 成功={success}")
        
        # 记录决策影响
        self.performance_monitor.record_decision_impact(
            step=game_state_after.get('step', 0),
            pre_game_state=game_state_before,
            post_game_state=game_state_after,
            actions=actions or {}
        )
        
        # 更新预制函数的置信度
        self._update_function_confidence(func_id, success, execution_quality)
        
        # 生成优化建议
        optimization_suggestion = self._generate_optimization_suggestion(func_id, execution_result)
        if optimization_suggestion:
            logger.info(f"预制函数优化建议: ID={func_id}, 建议={optimization_suggestion}")
    
    def _evaluate_execution_quality(self, success: bool, effect_metrics: Dict[str, Any]) -> float:
        """
        多维度评估预制函数执行质量
        
        Args:
            success: 执行是否成功
            effect_metrics: 执行效果指标
            
        Returns:
            float: 执行质量评分 (0-1)
        """
        # 基础分数
        base_score = 0.5
        
        # 成功/失败权重
        success_weight = 0.3
        if success:
            base_score += success_weight
        else:
            base_score -= success_weight
        
        # 单位数量变化权重
        unit_count_weight = 0.2
        friendly_change = effect_metrics.get('friendly_count_change', 0)
        enemy_change = effect_metrics.get('enemy_count_change', 0)
        unit_score = (enemy_change * -0.5 + friendly_change * 0.5) / 10  # 归一化到[-0.5, 0.5]
        base_score += unit_count_weight * unit_score
        
        # 生命值变化权重
        health_weight = 0.2
        friendly_health_change = effect_metrics.get('friendly_health_change', 0)
        enemy_health_change = effect_metrics.get('enemy_health_change', 0)
        health_score = (friendly_health_change * 0.3 + enemy_health_change * -0.7) / 100  # 归一化
        base_score += health_weight * health_score
        
        # 受伤单位变化权重
        low_health_weight = 0.15
        low_health_change = effect_metrics.get('low_health_units_change', 0)
        base_score += low_health_weight * (-low_health_change * 0.5)  # 受伤单位减少加分
        
        # 资源变化权重
        resource_weight = 0.15
        resource_change = effect_metrics.get('resource_change', 0)
        resource_score = min(resource_change / 1000, 1.0)  # 归一化，最多加0.15
        base_score += resource_weight * resource_score
        
        # 确保分数在0-1之间
        return max(0.0, min(1.0, base_score))
    
    def _generate_optimization_suggestion(self, func_id: str, execution_result: Dict[str, Any]) -> str:
        """
        根据执行结果生成优化建议
        
        Args:
            func_id: 预制函数ID
            execution_result: 执行结果
            
        Returns:
            str: 优化建议
        """
        func = self.prefab_function_manager.get_function_by_id(func_id)
        if not func:
            return ""
    
    def calculate_synergy_score(self, synergy_function: Dict, current_units: List[UnitInfo]) -> SynergyScore:
        """计算协同预制函数评分"""
        function_id = synergy_function.get('function_id', '')
        name = synergy_function.get('name', '')
        synergy_type = synergy_function.get('synergy_type', 'unknown')
        unit_composition = synergy_function.get('unit_composition', {})
        
        # 1. 单位可用性评分 (0-10分)
        availability_score = self._evaluate_unit_availability(unit_composition, current_units)
        
        # 2. 协同适配性评分 (0-10分) 
        tactical_score = self._evaluate_tactical_fitness(synergy_function, current_units)
        
        # 3. 基础协同评分 (基于函数类型和复杂度) (0-10分)
        synergy_base_score = self._calculate_synergy_base_score(synergy_function)
        
        # 综合评分计算
        total_score = (availability_score * 0.4 + tactical_score * 0.4 + synergy_base_score * 0.2)
        
        # 相关性评分 (基于函数适配度)
        relevance = min(1.0, total_score / 10.0)
        
        return SynergyScore(
            function_id=function_id,
            name=name,
            synergy_type=synergy_type,
            synergy_score=synergy_base_score,
            unit_availability_score=availability_score,
            tactical_fitness_score=tactical_score,
            total_score=total_score,
            relevance=relevance
        )
    
    def _evaluate_unit_availability(self, unit_composition: Dict, current_units: List[UnitInfo]) -> float:
        """评估单位可用性"""
        primary_units = unit_composition.get('primary', [])
        secondary_units = unit_composition.get('secondary', [])
        support_units = unit_composition.get('support', [])
        
        available_units = {unit.unit_type for unit in current_units if unit.is_alive}
        
        primary_match = sum(1 for unit_type in primary_units if unit_type in available_units)
        secondary_match = sum(1 for unit_type in secondary_units if unit_type in available_units)
        support_match = sum(1 for unit_type in support_units if unit_type in available_units)
        
        total_required = len(primary_units) + len(secondary_units) + len(support_units)
        total_matched = primary_match + secondary_match + support_match
        
        if total_required == 0:
            return 10.0
        
        # 主要单位权重更高
        weighted_score = (primary_match * 2.0 + secondary_match * 1.5 + support_match * 1.0)
        max_weighted = (len(primary_units) * 2.0 + len(secondary_units) * 1.5 + len(support_units) * 1.0)
        
        return min(10.0, (weighted_score / max_weighted) * 10.0) if max_weighted > 0 else 0.0
    
    def _evaluate_tactical_fitness(self, synergy_function: Dict, current_units: List[UnitInfo]) -> float:
        """评估战术适配性"""
        synergy_type = synergy_function.get('synergy_type', '')
        applicable_scenarios = synergy_function.get('applicable_scenarios', [])
        
        enemy_units = self.unit_pool.get('enemy', [])
        friendly_units = self.unit_pool.get('friendly', [])
        
        fitness_score = 0.0
        scenario_count = len(applicable_scenarios)
        
        # 基于当前战场情况评估适配性
        if synergy_type == SynergyType.AIR_GROUND_COORDINATION.value:
            fitness_score = self._evaluate_air_ground_fitness(friendly_units, enemy_units)
        elif synergy_type == SynergyType.LONG_SHORT_RANGE_COORDINATION.value:
            fitness_score = self._evaluate_long_short_range_fitness(friendly_units, enemy_units)
        elif synergy_type == SynergyType.ABILITY_UNIT_SYNERGY.value:
            fitness_score = self._evaluate_ability_synergy_fitness(friendly_units, enemy_units)
        elif synergy_type == SynergyType.ARMOR_TYPE_COORDINATION.value:
            fitness_score = self._evaluate_armor_coordination_fitness(friendly_units, enemy_units)
        elif synergy_type == SynergyType.SUPPORT_DPS_COORDINATION.value:
            fitness_score = self._evaluate_support_dps_fitness(friendly_units, enemy_units)
        
        return min(10.0, fitness_score)
    
    def _evaluate_air_ground_fitness(self, friendly_units: List[UnitInfo], enemy_units: List[UnitInfo]) -> float:
        """评估地空协同适配性"""
        has_air_units = any(unit.unit_type in ['ProtossPhoenix', 'ProtossCorsair', 'ProtossCarrier', 'TerranViking', 'TerranBanshee', 'TerranBattlecruiser', 'ZergMutalisk', 'ZergCorruptor'] for unit in friendly_units)
        has_ground_units = any(unit.unit_type in ['ProtossZealot', 'ProtossStalker', 'ProtossSentry', 'TerranMarine', 'TerranMarauder', 'TerranSiegeTank', 'ZergZergling', 'ZergRoach', 'ZergUltralisk'] for unit in friendly_units)
        has_high_value_targets = any(unit.unit_type in ['TerranSiegeTank', 'TerranThor', 'ZergUltralisk', 'ProtossColossus'] for unit in enemy_units)
        
        score = 0.0
        if has_air_units:
            score += 4.0
        if has_ground_units:
            score += 4.0
        if has_high_value_targets:
            score += 2.0
            
        return score
    
    def _evaluate_long_short_range_fitness(self, friendly_units: List[UnitInfo], enemy_units: List[UnitInfo]) -> float:
        """评估远近程协同适配性"""
        has_melee_units = any(unit.unit_type in ['ProtossZealot', 'ProtossDarkTemplar', 'TerranMarine', 'ZergZergling', 'ZergBaneling'] for unit in friendly_units)
        has_ranged_units = any(unit.unit_type in ['ProtossStalker', 'ProtossImmortal', 'TerranMarauder', 'TerranSiegeTank', 'ZergHydralisk', 'ZergLurker'] for unit in friendly_units)
        
        # 敌人距离多样化
        enemy_distances = []
        for enemy in enemy_units[:3]:  # 只考虑前3个敌人
            for friendly in friendly_units:
                distance = ((enemy.position[0] - friendly.position[0])**2 + (enemy.position[1] - friendly.position[1])**2)**0.5
                enemy_distances.append(distance)
        
        distance_variance = len(set([int(d/10) for d in enemy_distances])) if enemy_distances else 0
        
        score = 0.0
        if has_melee_units:
            score += 3.0
        if has_ranged_units:
            score += 3.0
        if distance_variance >= 2:
            score += 2.0
        if len(enemy_units) >= 3:
            score += 2.0
            
        return score
    
    def _evaluate_ability_synergy_fitness(self, friendly_units: List[UnitInfo], enemy_units: List[UnitInfo]) -> float:
        """评估技能协同适配性"""
        has_ability_units = any(unit.unit_type in ['ProtossHighTemplar', 'ProtossSentry', 'TerranGhost', 'TerranMedivac', 'ZergInfestor', 'ZergQueen'] for unit in friendly_units)
        has_support_units = any(unit.unit_type in ['ProtossSentry', 'ProtossZealot', 'TerranMedivac', 'ZergQueen'] for unit in friendly_units)
        
        # 敌人聚集度
        if len(enemy_units) >= 3:
            positions = [unit.position for unit in enemy_units]
            avg_x = sum(pos[0] for pos in positions) / len(positions)
            avg_y = sum(pos[1] for pos in positions) / len(positions)
            variance = sum((pos[0] - avg_x)**2 + (pos[1] - avg_y)**2 for pos in positions) / len(positions)
            cluster_factor = 1.0 if variance < 1000 else 0.5
        else:
            cluster_factor = 0.0
        
        score = 0.0
        if has_ability_units:
            score += 4.0
        if has_support_units:
            score += 3.0
        score += cluster_factor * 3.0
            
        return score
    
    def _evaluate_armor_coordination_fitness(self, friendly_units: List[UnitInfo], enemy_units: List[UnitInfo]) -> float:
        """评估装甲协同适配性"""
        has_specialized_units = any(unit.unit_type in ['ProtossImmortal', 'ProtossColossus', 'TerranSiegeTank', 'TerranThor', 'ZergUltralisk'] for unit in friendly_units)
        has_diverse_units = len(set(unit.unit_type for unit in friendly_units)) >= 3
        
        score = 0.0
        if has_specialized_units:
            score += 5.0
        if has_diverse_units:
            score += 3.0
        if len(enemy_units) >= 2:
            score += 2.0
            
        return score
    
    def _evaluate_support_dps_fitness(self, friendly_units: List[UnitInfo], enemy_units: List[UnitInfo]) -> float:
        """评估支援输出协同适配性"""
        has_support_units = any(unit.unit_type in ['ProtossSentry', 'ProtossHighTemplar', 'ProtossObserver', 'TerranMedivac', 'TerranRaven', 'ZergQueen', 'ZergInfestor'] for unit in friendly_units)
        has_dps_units = any(unit.unit_type in ['ProtossZealot', 'ProtossStalker', 'ProtossDarkTemplar', 'TerranMarine', 'TerranMarauder', 'ZergZergling', 'ZergHydralisk'] for unit in friendly_units)
        
        # 敌人威胁度
        threat_level = 0
        for enemy in enemy_units:
            if enemy.unit_type in ['TerranGhost', 'TerranRaven', 'ZergViper', 'ProtossHighTemplar']:
                threat_level += 2
            elif enemy.unit_type in ['TerranBattlecruiser', 'ZergUltralisk', 'ProtossColossus']:
                threat_level += 1
        
        score = 0.0
        if has_support_units:
            score += 4.0
        if has_dps_units:
            score += 4.0
        score += min(2.0, threat_level * 0.5)
            
        return score
    
    def _calculate_synergy_base_score(self, synergy_function: Dict) -> float:
        """计算基础协同评分"""
        difficulty = synergy_function.get('difficulty_level', 'medium')
        confidence = synergy_function.get('confidence', 0.8)
        
        difficulty_score = {
            'easy': 8.0,
            'medium': 6.0,
            'hard': 4.0
        }.get(difficulty, 6.0)
        
        return difficulty_score * confidence
    
    def select_optimal_synergy_functions(self, current_units: List[UnitInfo], k: int = 3) -> List[SynergyScore]:
        """选择最优协同函数"""
        if not self.prefab_function_manager or not current_units:
            return []
        
        # 获取所有预制函数
        all_functions = []
        for func_id, func in self.prefab_function_manager.prefab_functions.items():
            all_functions.append(func)
        
        synergy_scores = []
        for function in all_functions:
            # 检查是否为协同函数
            if function.get('synergy_type'):
                score = self.calculate_synergy_score(function, current_units)
                if score.total_score > 0:  # 只考虑有意义的评分
                    synergy_scores.append(score)
        
        # 按总分排序
        synergy_scores.sort(key=lambda x: x.total_score, reverse=True)
        
        # 返回前k个最优函数
        return synergy_scores[:k]
    
    def get_synergy_function_details(self, function_id: str) -> Optional[Dict]:
        """获取协同函数详细信息"""
        if not self.prefab_function_manager:
            return None
        
        return self.prefab_function_manager.get_function_by_id(function_id)
    
    def explain_synergy_benefits(self, function_id: str) -> Optional[str]:
        """解释协同函数的优势"""
        function_details = self.get_synergy_function_details(function_id)
        if not function_details:
            return None
        
        tactical_benefits = function_details.get('tactical_benefits', [])
        if tactical_benefits:
            return "主要优势：\n" + "\n".join(f"• {benefit}" for benefit in tactical_benefits)
        return None
    
    def get_execution_history(self, func_id: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取执行历史记录
        
        Args:
            func_id: 可选，指定函数ID，否则返回所有
            limit: 返回记录数量限制
            
        Returns:
            List[Dict[str, Any]]: 执行历史记录
        """
        if func_id:
            history = [r for r in self.prefab_execution_results if r['func_id'] == func_id]
        else:
            history = self.prefab_execution_results.copy()
        
        # 返回最近的记录
        return history[-limit:]
    
    def _update_function_confidence(self, func_id: str, success: bool, execution_quality: float):
        """
        根据执行结果和质量更新预制函数的置信度
        
        Args:
            func_id: 预制函数ID
            success: 执行是否成功
            execution_quality: 执行质量评分 (0-1)
        """
        # 获取预制函数
        func = self.prefab_function_manager.get_function_by_id(func_id)
        if func:
            current_confidence = func.get('confidence', 0.5)
            
            # 根据执行结果和质量调整置信度
            # 基础调整量
            base_adjustment = 0.03
            
            # 质量加权调整
            quality_factor = execution_quality
            if success:
                # 成功时，根据质量增加置信度
                adjustment = base_adjustment + (quality_factor * 0.07)  # 总增加0.03-0.1
                new_confidence = min(1.0, current_confidence + adjustment)
            else:
                # 失败时，根据质量减少置信度，质量越低减少越多
                adjustment = base_adjustment + ((1 - quality_factor) * 0.07)  # 总减少0.03-0.1
                new_confidence = max(0.1, current_confidence - adjustment)
            
            # 更新预制函数的置信度
            func['confidence'] = new_confidence
            logger.info(f"更新预制函数置信度: ID={func_id}, 之前={current_confidence:.3f}, 之后={new_confidence:.3f}, 执行结果={'成功' if success else '失败'}, 质量={execution_quality:.3f}")
        else:
            logger.warning(f"无法更新预制函数置信度: 未找到ID为{func_id}的预制函数")
    
    def _calculate_function_relevance(self, func: Dict[str, Any], game_state: Dict[str, Any]) -> float:
        """
        计算预制函数与当前游戏状态的相关性
        
        Args:
            func: 预制函数字典
            game_state: 当前游戏状态
            
        Returns:
            float: 相关性得分，范围0-1
        """
        relevance = func.get('confidence', 0.5)  # 基础相关性为置信度
        
        func_name = func['name']
        
        # 1. 单位匹配度检查（强化版）
        friendly_types = game_state.get('friendly_unit_types', {})
        enemy_types = game_state.get('enemy_unit_types', {})
        
        # 检查函数中指定的源单位是否存在于我方单位中
        if 'source_unit' in func:
            source_unit = func['source_unit']
            source_base = source_unit.split('_')[-1] if '_' in source_unit else source_unit
            if any(source_base.lower() in unit.lower() for unit in friendly_types.keys()):
                relevance += 0.2  # 源单位存在，增加相关性
            else:
                relevance -= 0.5  # 源单位不存在，大幅降低相关性
        
        # 检查函数中指定的目标单位是否存在于敌方单位中
        if 'target_unit' in func:
            target_unit = func['target_unit']
            # 如果是通用目标类型，允许
            if target_unit not in ['high_value_enemy_unit', 'high_value_terran_unit', 'nearest_enemy', 'nearest_enemy_unit', 'highest_threat_enemy', 'lowest_health_enemy', 'armored_enemy', 'light_enemy', 'lowest_health_friendly', 'all_enemy', 'closest_enemy']:
                target_base = target_unit.split('_')[-1] if '_' in target_unit else target_unit
                if any(target_base.lower() in unit.lower() for unit in enemy_types.keys()):
                    relevance += 0.2  # 目标单位存在，增加相关性
                else:
                    relevance -= 0.5  # 目标单位不存在，大幅降低相关性
        
        # 2. 基于函数类型和游戏状态的详细相关性评估
        if 'mm_push' in func_name.lower():
            # MM推进函数：检查是否有足够的Marine和Marauder
            marine_count = friendly_types.get('Marine', 0)
            marauder_count = friendly_types.get('Marauder', 0)
            total_mm = marine_count + marauder_count
            
            if marine_count >= 3 and marauder_count >= 1:
                relevance += 0.3  # 单位充足，增加相关性
            elif total_mm >= 4:
                relevance += 0.2  # 有一定数量的MM单位
            
            # 考虑敌方单位数量
            if game_state.get('enemy_count', 0) <= total_mm:
                relevance += 0.1  # 敌方数量适中，适合推进
        
        elif 'heal' in func_name.lower() or 'medivac' in func_name.lower():
            # 治疗函数：检查是否有医疗运输机和受伤单位
            if game_state.get('has_medivac', False):
                relevance += 0.2  # 有医疗运输机
            if game_state.get('has_low_health_units', False):
                relevance += 0.3  # 有受伤单位需要治疗
            
            # 检查医疗运输机能量
            if game_state.get('high_energy_units', False):
                relevance += 0.1  # 医疗运输机能量充足
        
        elif 'stim' in func_name.lower():
            # 兴奋剂函数：检查是否有大量陆战队或掠夺者
            marine_count = friendly_types.get('Marine', 0)
            marauder_count = friendly_types.get('Marauder', 0)
            stim_units = marine_count + marauder_count
            
            if stim_units >= 5:
                relevance += 0.3  # 大量可使用兴奋剂的单位
            elif stim_units >= 3:
                relevance += 0.2  # 一定数量的可使用兴奋剂的单位
            
            # 考虑战斗状态
            if game_state.get('enemy_count', 0) > 0:
                relevance += 0.1  # 处于战斗状态，适合使用兴奋剂
        
        elif 'siege' in func_name.lower():
            # 攻城/解除攻城函数：检查是否有攻城坦克
            siege_tank_count = friendly_types.get('SiegeTank', 0)
            if siege_tank_count > 0:
                relevance += 0.3  # 有攻城坦克
                
                # 考虑当前战斗状态
                if game_state.get('friendly_count', 0) >= game_state.get('enemy_count', 0):
                    relevance += 0.1  # 我方数量占优，适合攻城推进
        
        elif 'attack' in func_name.lower() or 'focusfire' in func_name.lower():
            # 攻击/集火函数：检查敌方单位数量和我方攻击能力
            enemy_count = game_state.get('enemy_count', 0)
            friendly_count = game_state.get('friendly_count', 0)
            
            if enemy_count > 0:
                relevance += 0.2  # 有敌方单位可以攻击
            if friendly_count > enemy_count:
                relevance += 0.2  # 我方数量占优，适合主动攻击
        
        elif 'move' in func_name.lower() or 'retreat' in func_name.lower():
            # 移动/撤退函数：根据单位数量和位置调整
            friendly_count = game_state.get('friendly_count', 0)
            enemy_count = game_state.get('enemy_count', 0)
            
            if friendly_count < enemy_count:
                relevance += 0.2  # 我方数量劣势，适合移动或撤退
        
        # 3. 根据战术类别调整相关性
        tactic_category = func.get('tactic_category', '')
        friendly_count = game_state.get('friendly_count', 0)
        enemy_count = game_state.get('enemy_count', 0)
        
        if tactic_category == 'offense':
            if friendly_count > enemy_count:
                relevance += 0.2  # 进攻策略在我方数量占优时更相关
            elif friendly_count == enemy_count and game_state.get('has_energy_units', False):
                relevance += 0.1  # 数量相等但有能量单位，适合进攻
        
        elif tactic_category == 'defense':
            if friendly_count < enemy_count:
                relevance += 0.2  # 防御策略在我方数量劣势时更相关
            elif game_state.get('has_low_health_units', False):
                relevance += 0.1  # 有受伤单位，需要防御
        
        elif tactic_category == 'support':
            if game_state.get('has_low_health_units', False):
                relevance += 0.2  # 支持策略在有受伤单位时更相关
            elif game_state.get('has_energy_units', False) and friendly_count > 0:
                relevance += 0.1  # 有能量单位可以提供支持
        
        elif tactic_category == 'targeting':
            if enemy_count > 0:
                relevance += 0.2  # 目标策略在有敌方单位时更相关
        
        # 4. 基于单位类型多样性的调整
        if game_state.get('unit_type_diversity', 0) > 0.5 and tactic_category == 'combination':
            relevance += 0.1  # 单位类型多样，适合组合战术
        
        # 5. 基于游戏阶段的调整（如果有游戏阶段信息）
        if 'game_stage' in game_state:
            game_stage = game_state['game_stage']
            if game_stage == 'early' and 'early' in func_name.lower():
                relevance += 0.1  # 早期游戏，适合早期战术
            elif game_stage == 'mid' and 'mid' in func_name.lower():
                relevance += 0.1  # 中期游戏，适合中期战术
            elif game_stage == 'late' and 'late' in func_name.lower():
                relevance += 0.1  # 后期游戏，适合后期战术
        
        # 确保相关性在0-1范围内
        return max(0.0, min(1.0, relevance))
    
    def get_prefab_info_for_prompt(self, optimal_prefab_functions: List[Dict[str, Any]], game_state: Dict[str, Any] = None) -> str:
        """
        获取预制函数信息，用于整合到VLM提示中作为RAG上下文
        
        Args:
            optimal_prefab_functions: 最优预制函数列表
            game_state: 当前游戏状态，用于增强预制函数与游戏状态的关联性
            
        Returns:
            str: 格式化的预制函数信息，适合作为RAG上下文
        """
        if not optimal_prefab_functions:
            return ""
        
        prefab_functions_info = "\n## 🔍 战术策略建议 (RAG辅助):\n"
        prefab_functions_info += "以下是根据当前战场状态智能推荐的战术策略，您可以直接参考这些策略生成具体的单位动作：\n\n"
        
        for i, func in enumerate(optimal_prefab_functions[:5]):  # 只显示前5个预制函数
            prefab_functions_info += f"### [{i+1}] 🎯 {func['name']}\n"
            
            # 策略概述
            prefab_functions_info += f"**核心策略**: {func.get('strategy_description', func.get('description', ''))}\n"
            
            # 战术分类
            prefab_functions_info += f"**战术类型**: {func.get('tactic_category', 'unknown')}\n"
            
            # 执行类型
            prefab_functions_info += f"**执行方式**: {func.get('execution_type', 'unknown')}\n"
            
            # 置信度
            confidence = func.get('confidence', 0.0)
            prefab_functions_info += f"**推荐指数**: {'⭐' * int(confidence * 5)} ({confidence})\n"
            
            # 游戏状态关联性
            if game_state:
                relevance = self._calculate_function_relevance(func, game_state)
                prefab_functions_info += f"**当前状态匹配度**: {'✅' * int(relevance * 5)} ({relevance})\n"
                
                # 添加具体的关联性分析
                relevance_reasons = []
                func_name = func['name']
                
                if 'mm_push' in func_name:
                    marine_count = game_state.get('friendly_unit_types', {}).get('Marine', 0)
                    marauder_count = game_state.get('friendly_unit_types', {}).get('Marauder', 0)
                    if marine_count >= 3 and marauder_count >= 1:
                        relevance_reasons.append(f"拥有充足的Marine({marine_count})和Marauder({marauder_count})")
                elif 'heal_' in func_name:
                    if game_state.get('has_medivac', False):
                        relevance_reasons.append("拥有医疗运输机")
                    if game_state.get('has_low_health_units', False):
                        relevance_reasons.append("存在低生命值单位需要治疗")
                elif 'Stim' in func_name:
                    marine_count = game_state.get('friendly_unit_types', {}).get('Marine', 0)
                    marauder_count = game_state.get('friendly_unit_types', {}).get('Marauder', 0)
                    if marine_count > 3 or marauder_count > 2:
                        relevance_reasons.append(f"拥有大量可使用兴奋剂的单位")
                elif 'Siege' in func_name or 'Unsiege' in func_name:
                    if game_state.get('friendly_unit_types', {}).get('SiegeTank', 0) > 0:
                        relevance_reasons.append("拥有攻城坦克")
                
                if relevance_reasons:
                    prefab_functions_info += f"**匹配理由**: {'; '.join(relevance_reasons)}\n"
            
            # 简明执行步骤
            if 'execution_flow' in func and func['execution_flow']:
                flow_str = "\n".join([f"  {i+1}. {step}" for i, step in enumerate(func['execution_flow'])])
                prefab_functions_info += f"**执行步骤**:\n{flow_str}\n"
            
            # 战术理由
            if 'evidence' in func and func['evidence']:
                evidence_str = "\n".join([f"  - {ev}" for ev in func['evidence']])
                prefab_functions_info += f"**战术优势**:\n{evidence_str}\n"
            
            # 适用场景
            if 'applicable_scenarios' in func and func['applicable_scenarios']:
                scenarios_str = "\n".join([f"  - {scenario}" for scenario in func['applicable_scenarios']])
                prefab_functions_info += f"**适用场景**:\n{scenarios_str}\n"
            
            prefab_functions_info += "\n"
        
        # 提示大模型如何使用这些信息
        prefab_functions_info += "📋 **使用指南**:\n"
        prefab_functions_info += "1. 严格按照推荐的战术策略生成单位动作，确保动作与策略完全匹配\n"
        prefab_functions_info += "2. 直接参考执行步骤生成对应的单位动作序列\n"
        prefab_functions_info += "3. 确保所有单位动作都基于当前战场态势，避免无意义的移动\n"
        prefab_functions_info += "4. 保持单位协同，所有单位应向同一方向移动，避免分散行动\n"
        prefab_functions_info += "5. 积极推进战线，单位应向敌方方向移动，避免向地图边缘移动\n"
        prefab_functions_info += "6. 战术类型建议：\n"
        prefab_functions_info += "   - 进攻型策略：当我方单位数量占优时使用，所有单位协同推进\n"
        prefab_functions_info += "   - 防御型策略：当我方单位数量劣势时使用，保持单位紧凑阵型\n"
        prefab_functions_info += "   - 支援型策略：当存在受伤单位或需要技能支持时使用，优先治疗关键单位\n"
        prefab_functions_info += "7. 单位协同建议：\n"
        prefab_functions_info += "   - 医疗运输机(Medivac)：必须始终跟随地面部队，保持在地面部队后方或侧方1-2格距离\n"
        prefab_functions_info += "   - 医疗运输机应严格根据地面部队的移动动态调整位置，不得停留在固定位置\n"
        prefab_functions_info += "   - 医疗运输机应优先治疗低生命值的关键单位，如Marauder或Siege Tank\n"
        prefab_functions_info += "   - 医疗运输机在没有需要治疗的单位时，应保持在安全位置并随时准备支援\n"
        prefab_functions_info += "8. 医疗运输机特定指令：\n"
        prefab_functions_info += "   - 当地面部队推进时，医疗运输机必须移动到地面部队附近(1-2格范围内)\n"
        prefab_functions_info += "   - 当地面部队攻击时，医疗运输机必须悬停在攻击位置附近，确保能立即治疗受伤单位\n"
        prefab_functions_info += "   - 严禁医疗运输机单独行动或远离地面部队\n"
        prefab_functions_info += "   - 医疗运输机的移动指令必须与地面部队的移动方向保持完全一致\n"
        prefab_functions_info += "   - 医疗运输机绝对不能移动到地图边缘或与地面部队分离的位置\n"
        prefab_functions_info += "9. 动作执行要求：\n"
        prefab_functions_info += "   - 所有单位的移动位置必须基于当前战场态势，不得使用硬编码的固定位置\n"
        prefab_functions_info += "   - 单位的移动方向必须与战术策略一致\n"
        prefab_functions_info += "   - 攻击目标必须明确，优先攻击高价值敌方单位\n"
        prefab_functions_info += "   - 技能使用必须合理，根据单位能量和战场需求决定\n"
        
        return prefab_functions_info
    
    def load_prefab_functions(self, file_path: str):
        """
        加载预制函数，同时支持从文件加载和通过管理器加载
        
        Args:
            file_path: 预制函数文件路径
        """
        # 通过管理器加载（向后兼容）
        if self.prefab_function_manager:
            self.prefab_function_manager.load_prefab_functions(file_path, merge=True)
