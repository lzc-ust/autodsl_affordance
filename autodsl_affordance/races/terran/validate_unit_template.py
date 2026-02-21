#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单位类模板验证工具

用于验证Terran单位类是否符合标准模板规范
"""

import os
import sys
import inspect
import importlib.util
from typing import Dict, List, Any, Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# 标准模板要求的方法列表
REQUIRED_METHODS = {
    "__init__": True,
    "_set_default_values": True,
    "_load_unit_data": True,
    "_set_hardcoded_data": True,
    "_apply_custom_kwargs": True,
    "_enhance_vlm_interface": True,
    "to_dict": True
}

# 文档字符串要求的关键字
DOCSTRING_REQUIREMENTS = {
    "__init__": ["初始化", "Args", "kwargs"],
    "_set_default_values": ["默认值", "初始值"],
    "_load_unit_data": ["JSON文件", "加载数据"],
    "_apply_custom_kwargs": ["自定义参数"],
    "_enhance_vlm_interface": ["VLM接口", "语言模型"],
    "to_dict": ["字典表示", "Returns"]
}

class ValidationResult:
    """验证结果类"""
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.passed = True
        self.warnings: List[str] = []
        self.errors: List[str] = []
    
    def add_warning(self, message: str):
        """添加警告"""
        self.warnings.append(message)
    
    def add_error(self, message: str):
        """添加错误"""
        self.errors.append(message)
        self.passed = False
    
    def get_summary(self) -> str:
        """获取验证结果摘要"""
        lines = [f"文件: {self.file_path}"]
        if self.passed:
            lines.append("✓ 通过验证")
        else:
            lines.append("✗ 验证失败")
        
        if self.errors:
            lines.append("\n错误:")
            for error in self.errors:
                lines.append(f"  - {error}")
        
        if self.warnings:
            lines.append("\n警告:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
        
        return "\n".join(lines)

def validate_docstring(method_name: str, docstring: Optional[str], result: ValidationResult):
    """验证方法的文档字符串"""
    if not docstring:
        result.add_error(f"方法 {method_name} 缺少文档字符串")
        return
    
    # 检查多行文档字符串
    if "\n" not in docstring:
        result.add_warning(f"方法 {method_name} 的文档字符串应包含多行描述")
    
    # 检查关键字
    if method_name in DOCSTRING_REQUIREMENTS:
        for keyword in DOCSTRING_REQUIREMENTS[method_name]:
            if keyword not in docstring:
                result.add_warning(f"方法 {method_name} 的文档字符串缺少关键字 '{keyword}'")

def validate_method_signature(method_obj, method_name: str, result: ValidationResult):
    """验证方法签名"""
    sig = inspect.signature(method_obj)
    
    # 验证__init__方法
    if method_name == "__init__":
        if "**kwargs" not in str(sig):
            result.add_error(f"__init__ 方法必须接受 **kwargs 参数")

def validate_class_methods(class_obj, result: ValidationResult):
    """验证类的方法"""
    class_name = class_obj.__name__
    
    # 检查必需的方法
    for method_name in REQUIRED_METHODS:
        if not hasattr(class_obj, method_name):
            result.add_error(f"类 {class_name} 缺少必需方法 {method_name}")
        else:
            method_obj = getattr(class_obj, method_name)
            if not callable(method_obj):
                result.add_error(f"{method_name} 不是可调用的方法")
            else:
                # 验证文档字符串
                validate_docstring(method_name, method_obj.__doc__, result)
                # 验证方法签名
                validate_method_signature(method_obj, method_name, result)

def validate_class_docstring(class_obj, result: ValidationResult):
    """验证类文档字符串"""
    if not class_obj.__doc__:
        result.add_error(f"类 {class_obj.__name__} 缺少文档字符串")
        return
    
    docstring = class_obj.__doc__
    if "\n\n" not in docstring:
        result.add_warning(f"类 {class_obj.__name__} 的文档字符串应包含详细描述")

def load_class_from_file(file_path: str) -> Optional[type]:
    """从文件加载类"""
    try:
        # 添加文件所在目录到系统路径
        dir_path = os.path.dirname(file_path)
        sys.path.append(dir_path)
        
        # 导入模块
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # 找到主要的类
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and name.startswith("Terran") and obj.__module__ == module_name:
                    return obj
    except Exception as e:
        print(f"加载文件 {file_path} 时出错: {e}")
        # 打印完整的错误堆栈，帮助调试
        import traceback
        traceback.print_exc()
    
    return None

def validate_unit_file(file_path: str) -> ValidationResult:
    """验证单位文件"""
    result = ValidationResult(file_path)
    
    # 加载类
    unit_class = load_class_from_file(file_path)
    if not unit_class:
        result.add_error("无法加载单位类")
        return result
    
    # 验证类文档字符串
    validate_class_docstring(unit_class, result)
    
    # 验证类方法
    validate_class_methods(unit_class, result)
    
    return result

def validate_directory(directory_path: str) -> List[ValidationResult]:
    """验证目录下的所有单位文件"""
    results = []
    
    # 遍历目录
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py") and not file.startswith("__init__") and not file.startswith("validate_"):
                file_path = os.path.join(root, file)
                result = validate_unit_file(file_path)
                results.append(result)
    
    return results

def main():
    """主函数"""
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 验证指定文件或整个目录
    if len(sys.argv) > 1:
        target = sys.argv[1]
        target_path = os.path.abspath(target)
        
        if os.path.isfile(target_path):
            results = [validate_unit_file(target_path)]
        elif os.path.isdir(target_path):
            results = validate_directory(target_path)
        else:
            print(f"错误: {target} 不是有效的文件或目录")
            return 1
    else:
        # 默认验证当前目录
        results = validate_directory(current_dir)
    
    # 打印结果
    passed_count = 0
    failed_count = 0
    
    for result in results:
        print(result.get_summary())
        print("-" * 60)
        if result.passed:
            passed_count += 1
        else:
            failed_count += 1
    
    # 打印总体统计
    print(f"验证完成: 通过 {passed_count}, 失败 {failed_count}")
    
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())