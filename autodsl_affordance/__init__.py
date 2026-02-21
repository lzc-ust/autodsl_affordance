"""
AutoDSL Affordance Module

This module provides functionality for StarCraft II AI, including:
- Prefab function system for tactical decision making
- Linkage graph for unit relationships
- Race-specific unit implementations
- Performance monitoring and evaluation
"""

__version__ = "1.0.0"
__author__ = "AutoDSL Team"

# 导出核心组件
from autodsl_affordance.core.prefab_system import PrefabFunctionHandler, PrefabPerformanceMonitor
from autodsl_affordance.core.linkage_graph.manager.prefab_function_manager import PrefabFunctionManager

__all__ = [
    "PrefabFunctionHandler",
    "PrefabPerformanceMonitor",
    "PrefabFunctionManager"
]
