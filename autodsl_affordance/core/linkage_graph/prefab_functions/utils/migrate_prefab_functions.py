#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据迁移脚本
用于将现有的预制函数转换为新的格式，按链接类型组织并标准化字段
"""

import json
import os
import sys

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../../../'))
sys.path.append(project_root)

# 直接导入 schema_validator 模块
sys.path.append(os.path.dirname(current_dir))
from schema_validator import PrefabFunctionSchemaValidator

class PrefabFunctionMigrator:
    """预制函数迁移器"""
    
    def __init__(self):
        """
        初始化迁移器
        """
        self.validator = PrefabFunctionSchemaValidator()
        self.linkage_types = {
            'interaction': 'INTERACTION',
            'combination': 'COMBINATION',
            'association': 'ASSOCIATION',
            'invocation': 'INVOCATION',
            'dependency': 'DEPENDENCY'
        }
    
    def migrate_file(self, input_path, output_path):
        """
        迁移单个预制函数文件
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            
        Returns:
            bool: 迁移是否成功
        """
        print(f"\n迁移文件: {input_path} -> {output_path}")
        
        try:
            # 读取输入文件
            with open(input_path, 'r', encoding='utf-8') as f:
                original_functions = json.load(f)
            
            print(f"读取了 {len(original_functions)} 个原始预制函数")
            
            # 迁移函数
            migrated_functions = self._migrate_functions(original_functions)
            
            print(f"迁移后得到 {len(migrated_functions)} 个预制函数")
            
            # 验证迁移后的数据
            if not self._validate_functions(migrated_functions):
                print("✗ 迁移后的数据验证失败")
                return False
            
            # 保存输出文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(migrated_functions, f, ensure_ascii=False, indent=2)
            
            print(f"✓ 迁移成功: {output_path}")
            return True
        except Exception as e:
            print(f"✗ 迁移失败: {e}")
            return False
    
    def _migrate_functions(self, functions):
        """
        迁移函数列表
        
        Args:
            functions: 原始函数列表
            
        Returns:
            list: 迁移后的函数列表
        """
        migrated = []
        
        for func in functions:
            try:
                migrated_func = self._migrate_function(func)
                if migrated_func:
                    migrated.append(migrated_func)
            except Exception as e:
                print(f"✗ 迁移函数失败 {func.get('function_id', 'unknown')}: {e}")
        
        return migrated
    
    def _migrate_function(self, func):
        """
        迁移单个函数
        
        Args:
            func: 原始函数
            
        Returns:
            dict: 迁移后的函数
        """
        # 创建迁移后的函数
        migrated_func = func.copy()
        
        # 标准化字段
        self._standardize_fields(migrated_func)
        
        # 按链接类型组织
        self._organize_by_linkage_type(migrated_func)
        
        # 标准化函数 ID
        self._standardize_function_id(migrated_func)
        
        return migrated_func
    
    def _standardize_fields(self, func):
        """
        标准化字段
        
        Args:
            func: 函数字典
        """
        # 移除冗余字段
        if 'synergy_type' in func and 'linkage_type' in func:
            # 保留 link_type，移除 synergy_type
            del func['synergy_type']
        
        # 确保必要字段存在
        required_fields = [
            'function_id', 'function_type', 'name', 'description',
            'strategy_description', 'tactic_category', 'linkage_type',
            'execution_type', 'execution_flow'
        ]
        
        for field in required_fields:
            if field not in func:
                # 为缺失的字段设置默认值
                if field == 'strategy_description':
                    func[field] = func.get('description', '')
                elif field == 'tactic_category':
                    func[field] = 'offense'  # 默认战术类别
                elif field == 'linkage_type':
                    func[field] = func.get('function_type', 'interaction')
                elif field == 'execution_type':
                    func[field] = 'attack'  # 默认执行类型
                elif field == 'execution_flow':
                    func[field] = []  # 默认空执行流程
        
        # 标准化枚举值
        self._standardize_enums(func)
    
    def _standardize_enums(self, func):
        """
        标准化枚举值
        
        Args:
            func: 函数字典
        """
        # 标准化 function_type
        valid_function_types = ['interaction', 'combination', 'association', 'invocation', 'dependency']
        if func.get('function_type') not in valid_function_types:
            func['function_type'] = 'interaction'  # 默认函数类型
        
        # 标准化 tactic_category
        valid_tactic_categories = [
            'offense', 'defense', 'support', 'heterogeneous_coordination',
            'air_ground_coordination', 'long_short_range_coordination',
            'stealth_synergy', 'armor_type_coordination',
            'target_priority_coordination', 'mobility_control_coordination',
            'formation_control_coordination'
        ]
        if func.get('tactic_category') not in valid_tactic_categories:
            func['tactic_category'] = 'offense'  # 默认战术类别
        
        # 标准化 execution_type
        valid_execution_types = [
            'attack', 'ability', 'move', 'coordinated_advance',
            'combined_assault', 'fortified_position', 'ambush_attack',
            'frontal_assault', 'focused_assault', 'mobile_defense',
            'spread_formation', 'hit_and_run', 'concurrent',
            'sequential', 'parallel'
        ]
        if func.get('execution_type') not in valid_execution_types:
            func['execution_type'] = 'attack'  # 默认执行类型
    
    def _organize_by_linkage_type(self, func):
        """
        按链接类型组织
        
        Args:
            func: 函数字典
        """
        # 根据 function_type 设置 linkage_type
        if 'function_type' in func and 'linkage_type' not in func:
            func['linkage_type'] = func['function_type']
    
    def _standardize_function_id(self, func):
        """
        标准化函数 ID
        
        Args:
            func: 函数字典
        """
        function_id = func.get('function_id', '')
        
        # 提取种族信息
        race = 'UNKNOWN'
        if 'TERRAN' in function_id:
            race = 'TERRAN'
        elif 'PROTOSS' in function_id:
            race = 'PROTOSS'
        elif 'ZERG' in function_id:
            race = 'ZERG'
        
        # 提取链接类型
        linkage_type = func.get('linkage_type', 'interaction').upper()
        if linkage_type == 'ADVANCED_SYNERGY':
            linkage_type = 'SYNERGY'
        
        # 生成新的函数 ID
        # 注意：这里简化处理，实际应该根据序号生成
        # 为了保持兼容性，我们保留原始 ID，但确保格式正确
        if not function_id:
            # 如果没有 ID，生成一个
            import uuid
            func['function_id'] = f"{race}_{linkage_type}_{str(uuid.uuid4())[:8].upper()}"
    
    def _validate_functions(self, functions):
        """
        验证函数列表
        
        Args:
            functions: 函数列表
            
        Returns:
            bool: 至少有一个函数验证成功
        """
        success_count = 0
        failure_count = 0
        
        try:
            # 创建一个新的列表，只包含验证成功的函数
            valid_functions = []
            
            for func in functions:
                if self.validator.validate_function(func):
                    valid_functions.append(func)
                    success_count += 1
                else:
                    print(f"✗ 函数验证失败，将被跳过: {func.get('function_id')}")
                    failure_count += 1
            
            # 替换原始函数列表为只包含验证成功的函数
            functions.clear()
            functions.extend(valid_functions)
            
            print(f"\n验证结果: 成功 {success_count}, 失败 {failure_count}")
            print(f"保留了 {len(functions)} 个有效函数")
            
            # 只要有至少一个函数成功，就返回 True
            return len(functions) > 0
        except Exception as e:
            print(f"✗ 验证失败: {e}")
            return False
    
    def _fix_validation_errors(self, func):
        """
        修复验证失败的函数
        
        Args:
            func: 验证失败的函数
            
        Returns:
            dict: 修复后的函数
        """
        fixed_func = func.copy()
        
        # 确保所有必要字段存在
        required_fields = [
            'function_id', 'function_type', 'name', 'description',
            'strategy_description', 'tactic_category', 'linkage_type',
            'execution_type', 'execution_flow'
        ]
        
        for field in required_fields:
            if field not in fixed_func:
                if field == 'function_id':
                    # 生成一个唯一的函数 ID
                    import uuid
                    race = 'UNKNOWN'
                    if 'TERRAN' in str(fixed_func.get('name', '').upper()):
                        race = 'TERRAN'
                    elif 'PROTOSS' in str(fixed_func.get('name', '').upper()):
                        race = 'PROTOSS'
                    elif 'ZERG' in str(fixed_func.get('name', '').upper()):
                        race = 'ZERG'
                    fixed_func['function_id'] = f"{race}_FIXED_{str(uuid.uuid4())[:8].upper()}"
                elif field == 'strategy_description':
                    fixed_func[field] = fixed_func.get('description', '')
                elif field == 'tactic_category':
                    fixed_func[field] = 'offense'
                elif field == 'linkage_type':
                    fixed_func[field] = fixed_func.get('function_type', 'interaction')
                elif field == 'execution_type':
                    fixed_func[field] = 'attack'
                elif field == 'execution_flow':
                    fixed_func[field] = []
        
        # 确保 function_type 是有效的
        valid_function_types = ['interaction', 'combination', 'association', 'invocation', 'dependency']
        if fixed_func.get('function_type') not in valid_function_types:
            fixed_func['function_type'] = 'interaction'
        
        return fixed_func
    
    def migrate_all(self, directory):
        """
        迁移目录中的所有预制函数文件
        
        Args:
            directory: 目录路径
            
        Returns:
            bool: 所有文件是否迁移成功
        """
        print(f"\n迁移目录: {directory}")
        
        success_count = 0
        failure_count = 0
        
        # 迁移每个种族的文件
        for race in ['protoss', 'terran', 'zerg']:
            input_file = os.path.join(directory, f'{race}_prefab_functions.json')
            output_file = os.path.join(directory, f'{race}_prefab_functions.json')  # 覆盖原文件
            
            if os.path.exists(input_file):
                if self.migrate_file(input_file, output_file):
                    success_count += 1
                else:
                    failure_count += 1
            else:
                print(f"✗ 文件不存在: {input_file}")
                failure_count += 1
        
        print(f"\n迁移完成:")
        print(f"  成功: {success_count} 个文件")
        print(f"  失败: {failure_count} 个文件")
        
        return failure_count == 0

def main():
    """主函数"""
    migrator = PrefabFunctionMigrator()
    
    # 迁移默认目录中的预制函数文件
    prefab_functions_dir = os.path.join(current_dir, '..')
    migrator.migrate_all(prefab_functions_dir)

if __name__ == '__main__':
    main()
