#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON Schema 验证工具
用于验证预制函数的结构是否符合定义的 Schema
"""

import json
import os
import sys
from jsonschema import validate, ValidationError

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../../../'))
sys.path.append(project_root)

class PrefabFunctionSchemaValidator:
    """预制函数 Schema 验证器"""
    
    def __init__(self, schema_path=None):
        """
        初始化验证器
        
        Args:
            schema_path: Schema 文件路径，如果为 None 则使用默认路径
        """
        if schema_path is None:
            # 使用默认 Schema 路径
            schema_path = os.path.join(
                current_dir, 
                '../schema/prefab_function.schema.json'
            )
        
        self.schema_path = schema_path
        self.schema = self._load_schema()
    
    def _load_schema(self):
        """
        加载 JSON Schema
        
        Returns:
            dict: Schema 定义
        """
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            print(f"成功加载 Schema: {self.schema_path}")
            return schema
        except Exception as e:
            print(f"加载 Schema 失败: {e}")
            sys.exit(1)
    
    def validate_file(self, file_path):
        """
        验证单个预制函数文件
        
        Args:
            file_path: 预制函数文件路径
            
        Returns:
            bool: 验证是否成功
        """
        print(f"\n验证文件: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                prefab_functions = json.load(f)
            
            # 验证整个文件
            validate(instance=prefab_functions, schema=self.schema)
            
            print(f"✓ 验证成功: {file_path}")
            print(f"  包含 {len(prefab_functions)} 个预制函数")
            
            # 打印函数摘要
            for i, func in enumerate(prefab_functions, 1):
                print(f"  {i}. {func['name']} (ID: {func['function_id']}, Type: {func['function_type']})")
            
            return True
        except ValidationError as e:
            print(f"✗ 验证失败: {e.message}")
            print(f"  错误位置: {e.path}")
            return False
        except Exception as e:
            print(f"✗ 验证失败: {e}")
            return False
    
    def validate_directory(self, directory_path):
        """
        验证目录中的所有预制函数文件
        
        Args:
            directory_path: 目录路径
            
        Returns:
            bool: 所有文件是否验证成功
        """
        print(f"\n验证目录: {directory_path}")
        
        success_count = 0
        failure_count = 0
        
        # 查找所有 JSON 文件
        for filename in os.listdir(directory_path):
            if filename.endswith('.json') and '_prefab_functions' in filename:
                file_path = os.path.join(directory_path, filename)
                if self.validate_file(file_path):
                    success_count += 1
                else:
                    failure_count += 1
        
        print(f"\n验证完成:")
        print(f"  成功: {success_count} 个文件")
        print(f"  失败: {failure_count} 个文件")
        
        return failure_count == 0
    
    def validate_function(self, function_data):
        """
        验证单个预制函数数据
        
        Args:
            function_data: 预制函数数据字典
            
        Returns:
            bool: 验证是否成功
        """
        try:
            # 创建一个包含单个函数的列表，因为 Schema 定义的是数组
            validate(instance=[function_data], schema=self.schema)
            return True
        except ValidationError:
            return False

def main():
    """主函数"""
    validator = PrefabFunctionSchemaValidator()
    
    # 验证默认目录中的预制函数文件
    prefab_functions_dir = os.path.join(current_dir, '..')
    validator.validate_directory(prefab_functions_dir)

if __name__ == '__main__':
    main()
