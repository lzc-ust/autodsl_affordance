import os
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class PrefabLoader:
    """
    预制函数加载器，负责加载和解析预制函数文件
    """
    
    def __init__(self, prefab_dir=None):
        """
        初始化预制函数加载器
        
        Args:
            prefab_dir: 预制函数文件目录，如果为None则使用默认目录
        """
        self.prefab_dir = prefab_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'linkage_graph', 'prefab_functions'
        )
        logger.info(f"预制函数加载器初始化，使用目录: {self.prefab_dir}")
    
    def load_functions(self, race=None) -> Dict[str, Any]:
        """
        加载预制函数
        
        Args:
            race: 种族名称，如'terran', 'protoss', 'zerg'，如果为None则加载所有种族
        
        Returns:
            Dict: 加载的预制函数，按种族和类型组织
        """
        functions = {
            'all': [],
            'by_race': {},
            'by_type': {}
        }
        
        # 获取预制函数文件
        prefab_files = self._get_prefab_files(race)
        
        # 加载每个文件
        for file_path in prefab_files:
            try:
                file_functions = self._load_file(file_path)
                
                # 提取种族信息
                file_race = self._extract_race_from_filename(file_path)
                
                # 提取函数类型
                file_type = self._extract_type_from_filename(file_path)
                
                # 添加到总列表
                functions['all'].extend(file_functions)
                
                # 按种族组织
                if file_race not in functions['by_race']:
                    functions['by_race'][file_race] = []
                functions['by_race'][file_race].extend(file_functions)
                
                # 按类型组织
                if file_type not in functions['by_type']:
                    functions['by_type'][file_type] = []
                functions['by_type'][file_type].extend(file_functions)
                
                logger.info(f"成功加载文件: {os.path.basename(file_path)}，包含 {len(file_functions)} 个函数")
                
            except Exception as e:
                logger.error(f"加载文件 {os.path.basename(file_path)} 失败: {str(e)}")
        
        logger.info(f"总共加载 {len(functions['all'])} 个预制函数")
        return functions
    
    def _get_prefab_files(self, race=None) -> List[str]:
        """
        获取预制函数文件列表
        
        Args:
            race: 种族名称，如果为None则获取所有文件
        
        Returns:
            List[str]: 文件路径列表
        """
        files = []
        
        if not os.path.exists(self.prefab_dir):
            logger.warning(f"预制函数目录不存在: {self.prefab_dir}")
            return files
        
        for filename in os.listdir(self.prefab_dir):
            if filename.endswith('.json'):
                # 如果指定了种族，只加载对应种族的文件
                if race and race.lower() not in filename.lower():
                    continue
                files.append(os.path.join(self.prefab_dir, filename))
        
        return files
    
    def _load_file(self, file_path) -> List[Dict[str, Any]]:
        """
        加载单个预制函数文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            List[Dict]: 函数列表
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 处理不同格式的数据
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'functions' in data:
            return data['functions']
        elif isinstance(data, dict):
            # 如果是字典形式，转换为列表
            return [data]
        else:
            logger.warning(f"文件 {os.path.basename(file_path)} 格式不正确")
            return []
    
    def _extract_race_from_filename(self, file_path) -> str:
        """
        从文件名中提取种族信息
        
        Args:
            file_path: 文件路径
        
        Returns:
            str: 种族名称
        """
        filename = os.path.basename(file_path).lower()
        
        if 'terran' in filename:
            return 'terran'
        elif 'protoss' in filename:
            return 'protoss'
        elif 'zerg' in filename:
            return 'zerg'
        else:
            return 'unknown'
    
    def _extract_type_from_filename(self, file_path) -> str:
        """
        从文件名中提取函数类型
        
        Args:
            file_path: 文件路径
        
        Returns:
            str: 函数类型
        """
        filename = os.path.basename(file_path).lower()
        
        if 'synergy' in filename:
            return 'synergy'
        elif 'heterogeneous' in filename:
            return 'heterogeneous'
        elif 'without_move' in filename:
            return 'without_move'
        else:
            return 'standard'
    
    def get_function_by_id(self, function_id: str, functions: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据函数ID获取函数
        
        Args:
            function_id: 函数ID
            functions: 加载的函数集合
        
        Returns:
            Dict: 函数信息，如果未找到返回None
        """
        for func in functions['all']:
            if func.get('function_id') == function_id:
                return func
        return None
    
    def search_functions(self, functions: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        """
        搜索函数
        
        Args:
            functions: 加载的函数集合
            **kwargs: 搜索条件，如unit, race, type等
        
        Returns:
            List[Dict]: 匹配的函数列表
        """
        results = []
        
        for func in functions['all']:
            match = True
            
            # 检查单位匹配
            if 'unit' in kwargs:
                unit = kwargs['unit'].lower()
                if not self._unit_matches(func, unit):
                    match = False
            
            # 检查种族匹配
            if 'race' in kwargs:
                race = kwargs['race'].lower()
                if not self._race_matches(func, race):
                    match = False
            
            # 检查类型匹配
            if 'type' in kwargs:
                func_type = kwargs['type'].lower()
                if not self._type_matches(func, func_type):
                    match = False
            
            if match:
                results.append(func)
        
        return results
    
    def _unit_matches(self, func: Dict[str, Any], unit: str) -> bool:
        """
        检查函数是否与单位匹配
        
        Args:
            func: 函数信息
            unit: 单位名称
        
        Returns:
            bool: 是否匹配
        """
        # 检查source_unit
        if 'source_unit' in func:
            source_unit = func['source_unit'].lower()
            if unit in source_unit:
                return True
        
        # 检查prerequisites.required_units
        if 'prerequisites' in func and 'required_units' in func['prerequisites']:
            for req_unit in func['prerequisites']['required_units']:
                if unit in req_unit.lower():
                    return True
        
        # 检查required_units（兼容旧格式）
        if 'required_units' in func:
            for req_unit in func['required_units']:
                if unit in req_unit.lower():
                    return True
        
        # 检查participating_units
        if 'participating_units' in func:
            for part_unit in func['participating_units']:
                if unit in part_unit.lower():
                    return True
        
        # 检查units
        if 'units' in func:
            for part_unit in func['units']:
                if unit in part_unit.lower():
                    return True
        
        return False
    
    def _race_matches(self, func: Dict[str, Any], race: str) -> bool:
        """
        检查函数是否与种族匹配
        
        Args:
            func: 函数信息
            race: 种族名称
        
        Returns:
            bool: 是否匹配
        """
        # 检查函数ID中的种族信息
        func_id = func.get('function_id', '').lower()
        if race in func_id:
            return True
        
        # 检查函数名称中的种族信息
        func_name = func.get('name', '').lower()
        if race in func_name:
            return True
        
        return False
    
    def _type_matches(self, func: Dict[str, Any], func_type: str) -> bool:
        """
        检查函数是否与类型匹配
        
        Args:
            func: 函数信息
            func_type: 函数类型
        
        Returns:
            bool: 是否匹配
        """
        # 检查function_type
        if func.get('function_type', '').lower() == func_type:
            return True
        
        # 检查synergy_type
        if func_type == 'synergy' and 'synergy_type' in func:
            return True
        
        return False
