#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预制函数系统单元测试
"""

import os
import sys
import json
import tempfile
import unittest

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../../../'))
sys.path.append(project_root)

# 导入测试对象
sys.path.append(os.path.join(current_dir, '../utils'))
from schema_validator import PrefabFunctionSchemaValidator
from migrate_prefab_functions import PrefabFunctionMigrator
from autodsl_affordance.core.linkage_graph.manager.prefab_function_manager import PrefabFunctionManager

class TestPrefabFunctionSystem(unittest.TestCase):
    """预制函数系统测试类"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 预制函数 Schema 路径
        self.schema_path = os.path.join(current_dir, '../schema/prefab_function.schema.json')
        
        # 示例预制函数
        self.example_function = {
            "function_id": "TEST_INTERACTION_001",
            "function_type": "interaction",
            "name": "test_focus_fire",
            "description": "测试集中火力攻击",
            "strategy_description": "测试策略描述",
            "tactic_category": "offense",
            "linkage_type": "interaction",
            "execution_type": "attack",
            "source_unit": "all_friendly",
            "target_unit": "highest_threat_enemy",
            "execution_flow": [
                "set_target(all_friendly, highest_threat_enemy)",
                "attack(all_friendly, highest_threat_enemy)"
            ],
            "evidence": [
                "测试证据1",
                "测试证据2"
            ],
            "confidence": 0.9
        }
        
        # 创建测试用的预制函数文件
        self.test_file_path = os.path.join(self.temp_dir, 'test_prefab_functions.json')
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            json.dump([self.example_function], f, ensure_ascii=False, indent=2)
    
    def tearDown(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_schema_validator(self):
        """测试 Schema 验证器"""
        print("\n=== 测试 Schema 验证器 ===")
        
        # 初始化验证器
        validator = PrefabFunctionSchemaValidator(self.schema_path)
        
        # 测试有效的函数
        self.assertTrue(validator.validate_function(self.example_function))
        print("✓ 有效函数验证成功")
        
        # 测试无效的函数（缺少必要字段）
        invalid_function = self.example_function.copy()
        del invalid_function['function_type']
        self.assertFalse(validator.validate_function(invalid_function))
        print("✓ 无效函数验证失败")
        
        # 测试验证文件
        self.assertTrue(validator.validate_file(self.test_file_path))
        print("✓ 文件验证成功")
    
    def test_migration(self):
        """测试数据迁移"""
        print("\n=== 测试数据迁移 ===")
        
        # 初始化迁移器
        migrator = PrefabFunctionMigrator()
        
        # 创建输出文件路径
        output_path = os.path.join(self.temp_dir, 'migrated_prefab_functions.json')
        
        # 测试迁移
        result = migrator.migrate_file(self.test_file_path, output_path)
        self.assertTrue(result)
        print("✓ 数据迁移成功")
        
        # 验证迁移后的文件
        with open(output_path, 'r', encoding='utf-8') as f:
            migrated_functions = json.load(f)
        
        self.assertEqual(len(migrated_functions), 1)
        migrated_function = migrated_functions[0]
        
        # 验证必要字段存在
        required_fields = [
            'function_id', 'function_type', 'name', 'description',
            'strategy_description', 'tactic_category', 'linkage_type',
            'execution_type', 'execution_flow'
        ]
        
        for field in required_fields:
            self.assertIn(field, migrated_function)
        print("✓ 迁移后字段验证成功")
    
    def test_prefab_function_manager(self):
        """测试 PrefabFunctionManager"""
        print("\n=== 测试 PrefabFunctionManager ===")
        
        # 初始化管理器
        manager = PrefabFunctionManager()
        
        # 测试加载预制函数
        result = manager.load_prefab_functions(self.test_file_path)
        self.assertTrue(result)
        print("✓ 加载预制函数成功")
        
        # 测试函数数量
        self.assertEqual(manager.get_function_count(), 1)
        print("✓ 函数数量验证成功")
        
        # 测试获取函数
        function = manager.get_function_by_id("TEST_INTERACTION_001")
        self.assertIsNotNone(function)
        self.assertEqual(function['name'], "test_focus_fire")
        print("✓ 获取函数成功")
        
        # 测试添加函数
        new_function = self.example_function.copy()
        new_function['function_id'] = "TEST_INTERACTION_002"
        new_function['name'] = "test_new_function"
        
        result = manager.add_prefab_function(new_function)
        self.assertTrue(result)
        self.assertEqual(manager.get_function_count(), 2)
        print("✓ 添加函数成功")
        
        # 测试获取最优函数
        # 创建模拟游戏状态
        mock_game_state = {
            'friendly_count': 5,
            'enemy_count': 3,
            'friendly_unit_types': {'Marine': 3, 'Marauder': 2},
            'enemy_unit_types': {'Zealot': 2, 'Stalker': 1},
            'has_low_health_units': False,
            'has_energy_units': True
        }
        
        # 创建模拟观察
        mock_observation = {
            'text': 'Test observation',
            'unit_info': []
        }
        
        optimal_functions = manager.get_optimal_functions(mock_observation, mock_game_state)
        self.assertGreaterEqual(len(optimal_functions), 0)
        print("✓ 获取最优函数成功")
    
    def test_integration(self):
        """测试集成功能"""
        print("\n=== 测试集成功能 ===")
        
        # 1. 迁移数据
        migrator = PrefabFunctionMigrator()
        output_path = os.path.join(self.temp_dir, 'migrated_prefab_functions.json')
        migrator.migrate_file(self.test_file_path, output_path)
        
        # 2. 加载迁移后的数据
        manager = PrefabFunctionManager()
        manager.load_prefab_functions(output_path)
        
        # 3. 验证功能
        self.assertEqual(manager.get_function_count(), 1)
        function = manager.get_function_by_id("TEST_INTERACTION_001")
        self.assertIsNotNone(function)
        print("✓ 集成测试成功")

if __name__ == '__main__':
    unittest.main()
