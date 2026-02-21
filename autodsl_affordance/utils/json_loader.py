import os
import re
import json
import warnings
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

# 自定义异常类
class UnitDataMissingError(Exception):
    """当单位数据缺失或不完整时抛出的异常"""
    pass

class UnitFileNotFoundError(Exception):
    """当单位JSON文件不存在时抛出的异常"""
    pass

class UnitDataValidationError(Exception):
    """当单位数据验证失败时抛出的异常"""
    pass

@dataclass
class UnitDataVersion:
    """单位数据版本信息"""
    major: int = 1
    minor: int = 0
    patch: int = 0
    
    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

class UnitJsonLoader:
    """
    单位JSON数据加载器 - 提供通用的JSON数据加载功能
    
    这个类封装了所有单位共享的JSON数据加载逻辑，包括：
    - 文件路径构建
    - 错误处理
    - 数据验证
    - 各种属性的安全提取
    - 默认值处理
    - 数据版本管理
    """
    
    # 支持的数据版本
    SUPPORTED_VERSIONS = [
        UnitDataVersion(1, 0, 0),
        UnitDataVersion(1, 1, 0)
    ]
    
    # 必要字段定义
    REQUIRED_FIELDS = {
        'basic': ['description'],
        'cost': ['mineral', 'vespene', 'supply'],
        'unit_stats': ['health', 'armor', 'speed'],
        'abilities': []
    }
    
    def __init__(self, target_instance=None, dev_mode: bool = False):
        """
        初始化JSON加载器
        
        参数:
            target_instance: 目标实例对象，将被加载的数据属性设置到该实例
            dev_mode: 是否启用开发模式，开发模式下遇到数据缺失会抛出异常而不是使用默认值
        """
        self.target_instance = target_instance
        self.dev_mode = dev_mode
        self.base_dir = self._get_base_dir()
        self.json_dir = os.path.join(self.base_dir, 'sc2_unit_info')
        self.current_version = UnitDataVersion(1, 0, 0)
        
        if self.dev_mode:
            warnings.warn("[警告] JSON加载器已启用开发模式，数据缺失时将抛出异常", UserWarning)
    
    def _get_base_dir(self) -> str:
        """
        获取项目基础目录
        
        返回:
            str: 基础目录路径
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 向上找到autodsl_affordance目录
        max_levels = 5  # 最大尝试层级
        for i in range(max_levels):
            if os.path.basename(current_dir) == 'autodsl_affordance':
                return current_dir
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:  # 已经到达根目录
                break
            current_dir = parent_dir
        
        # 作为后备，使用直接的相对路径计算
        fallback_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        print(f"[警告] 无法找到autodsl_affordance目录，使用后备路径: {fallback_path}")
        return fallback_path
    
    def load_unit_data(self, unit_class_name: str) -> Dict[str, Any]:
        """
        加载单位数据
        
        参数:
            unit_class_name: 单位类名
            
        返回:
            Dict[str, Any]: 加载的数据字典
            
        异常:
            UnitFileNotFoundError: 开发模式下找不到单位文件时抛出
            UnitDataValidationError: 数据验证失败时抛出
        """
        print(f"[数据加载] 开始从 {self.json_dir} 加载 {unit_class_name} 单位数据")
        
        # 尝试不同的文件名格式
        file_paths = self._get_possible_file_paths(unit_class_name)
        
        for json_file_path in file_paths:
            print(f"[数据加载] 尝试读取文件: {json_file_path}")
            
            # 文件系统检查
            if not self._validate_file(json_file_path):
                continue
            
            try:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"[数据加载] 成功解析JSON文件，包含 {len(data)} 个键值对")
                    
                    # 验证数据版本
                    self._validate_data_version(data)
                    
                    # 验证数据完整性
                    self._validate_data_integrity(data)
                    
                    return data
            except json.JSONDecodeError as e:
                print(f"[错误] JSON文件格式错误 {json_file_path}: {e}")
                print(f"[错误] 错误位置: 行 {e.lineno}, 列 {e.colno}")
            except UnicodeDecodeError:
                print(f"[错误] 编码错误: 文件编码不是UTF-8")
            except MemoryError:
                print(f"[错误] 内存错误: 文件可能过大")
            except UnitDataValidationError as e:
                print(f"[错误] 数据验证失败: {e}")
                if self.dev_mode:
                    raise
            except Exception as e:
                print(f"[错误] 读取文件时出错: {e}")
                if self.dev_mode:
                    import traceback
                    traceback.print_exc()
        
        error_msg = f"[错误] 无法从任何文件加载 {unit_class_name} 的数据"
        print(error_msg)
        
        if self.dev_mode:
            raise UnitFileNotFoundError(error_msg)
        
        return {}
    
    def _get_possible_file_paths(self, unit_class_name: str) -> List[str]:
        """
        获取可能的文件路径列表
        
        参数:
            unit_class_name: 单位类名
            
        返回:
            List[str]: 文件路径列表
        """
        file_paths = []
        
        # 尝试不同的命名格式
        formats = [
            f"{unit_class_name}.json",
            f"{re.sub(r'(?<=[a-z])(?=[A-Z])', '_', unit_class_name)}.json",  # 使用下划线连接类名中的大写分隔
            f"{unit_class_name.replace('_', ' ')}.json",
            f"{unit_class_name.replace(' ', '_')}.json"
        ]
        
        # 去重并添加路径
        for fmt in list(set(formats)):
            file_paths.append(os.path.join(self.json_dir, fmt))
        
        return file_paths
    
    def _validate_file(self, file_path: str) -> bool:
        """
        验证文件是否有效
        
        参数:
            file_path: 文件路径
            
        返回:
            bool: 是否有效
        """
        # 检查目录是否存在
        if not os.path.exists(self.json_dir):
            print(f"[错误] JSON目录不存在: {self.json_dir}")
            return False
            
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"[警告] 文件不存在: {file_path}")
            return False
            
        # 检查权限
        if not os.access(file_path, os.R_OK):
            print(f"[错误] 没有权限读取文件: {file_path}")
            return False
            
        # 检查文件大小
        try:
            file_size = os.path.getsize(file_path)
            if file_size > 1000000:  # 1MB限制
                print(f"[错误] 文件过大: {file_size} 字节 (最大允许1MB)")
                return False
        except Exception as e:
            print(f"[错误] 获取文件大小失败: {e}")
            return False
            
        return True
    
    def _validate_data_version(self, data: Dict[str, Any]) -> None:
        """
        验证数据版本
        
        参数:
            data: 加载的数据字典
            
        异常:
            UnitDataValidationError: 版本不支持时抛出
        """
        version_str = data.get('version', '1.0.0')
        print(f"[数据验证] 检测到数据版本: {version_str}")
        
        try:
            # 解析版本号
            major, minor, patch = map(int, version_str.split('.'))
            data_version = UnitDataVersion(major, minor, patch)
            
            # 检查版本是否受支持
            if data_version not in self.SUPPORTED_VERSIONS:
                if self.dev_mode:
                    raise UnitDataValidationError(f"不支持的数据版本: {version_str}, 支持的版本: {[str(v) for v in self.SUPPORTED_VERSIONS]}")
                else:
                    warnings.warn(f"[警告] 使用不支持的数据版本: {version_str}", UserWarning)
            
            self.current_version = data_version
        except ValueError:
            if self.dev_mode:
                raise UnitDataValidationError(f"无效的版本格式: {version_str}, 应为 X.Y.Z 格式")
            else:
                warnings.warn(f"[警告] 无效的版本格式: {version_str}, 使用默认版本 1.0.0", UserWarning)
    
    def _validate_data_integrity(self, data: Dict[str, Any]) -> None:
        """
        验证数据完整性
        
        参数:
            data: 加载的数据字典
            
        异常:
            UnitDataValidationError: 数据不完整时抛出
        """
        print(f"[数据验证] 开始验证数据完整性")
        
        missing_fields = []
        
        # 验证基本信息
        for field in self.REQUIRED_FIELDS['basic']:
            if field not in data:
                missing_fields.append(f"基本信息: {field}")
        
        # 验证成本信息
        cost_data = data.get('cost', {})
        for field in self.REQUIRED_FIELDS['cost']:
            if field not in cost_data:
                missing_fields.append(f"成本信息: {field}")
        
        # 验证单位属性
        unit_stats = data.get('unit_stats', {})
        for field in self.REQUIRED_FIELDS['unit_stats']:
            if field not in unit_stats:
                missing_fields.append(f"单位属性: {field}")
        
        # 如果有缺失字段，根据模式决定是否抛出异常
        if missing_fields:
            error_msg = f"数据不完整，缺少以下字段: {', '.join(missing_fields)}"
            if self.dev_mode:
                raise UnitDataValidationError(error_msg)
            else:
                warnings.warn(f"[警告] {error_msg}", UserWarning)
                print(f"[警告] {error_msg}")
        
        print(f"[数据验证] 数据完整性验证通过")
    
    def apply_data_to_instance(self, data: Dict[str, Any], instance=None) -> None:
        """
        将加载的数据应用到实例
        
        参数:
            data: 加载的数据
            instance: 目标实例，如果为None则使用初始化时的目标实例
        """
        target = instance or self.target_instance
        if not target:
            print("[错误] 没有提供目标实例")
            return
            
        try:
            # 加载各类数据
            self._apply_basic_info(data, target)
            self._apply_cost_info(data, target)
            self._apply_attack_info(data, target)
            self._apply_unit_stats(data, target)
            self._apply_abilities(data, target)
            self._apply_tactical_info(data, target)
            
            print(f"[数据加载] 成功将数据应用到 {target.unique_class_name}")
        except Exception as e:
            print(f"[错误] 应用数据到实例时出错: {e}")
            import traceback
            print(f"[错误详情] {traceback.format_exc()}")
    
    def load_and_apply(self, unit_class_name: str, instance=None) -> bool:
        """
        一次性完成加载和应用
        
        参数:
            unit_class_name: 单位类名
            instance: 目标实例
            
        返回:
            bool: 是否成功
            
        异常:
            UnitDataMissingError, UnitFileNotFoundError: 开发模式下数据缺失或文件不存在时抛出
        """
        try:
            data = self.load_unit_data(unit_class_name)
            if data:
                self.apply_data_to_instance(data, instance)
                return True
            else:
                if self.dev_mode:
                    raise UnitDataMissingError(f"[开发模式] 加载的数据为空，类名: {unit_class_name}")
                print(f"[警告] 使用开发模式选项: {unit_class_name}")
                return False
        except (UnitDataMissingError, UnitFileNotFoundError):
            raise
        except Exception as e:
            if self.dev_mode:
                raise UnitDataMissingError(f"[开发模式] 加载并应用数据时出错: {e}") from e
            print(f"[错误] 加载并应用数据时出错: {e}")
            return False
    
    # 数据应用方法
    def _apply_basic_info(self, data: Dict[str, Any], target) -> None:
        """
        应用基本信息
        
        异常:
            UnitDataMissingError: 开发模式下描述缺失时抛出
        """
        description_keys = ['Description', 'description', 'Description_EN', 'desc']
        
        found = False
        for key in description_keys:
            if key in data:
                target.description = str(data[key])
                found = True
                break
        
        if not found:
            if self.dev_mode:
                raise UnitDataMissingError(f"[开发模式] 找不到描述信息，尝试的键: {description_keys}")
            if not hasattr(target, 'description'):
                target.description = '单位描述'
                
        print(f"[数据加载] 描述: {target.description[:50]}...")
    
    def _apply_cost_info(self, data: Dict[str, Any], target) -> None:
        """
        应用成本信息
        
        异常:
            UnitDataMissingError: 开发模式下成本信息缺失时抛出
        """
        cost_data = None
        cost_keys = ['Cost', 'cost', 'BuildCost', 'build_cost']
        
        for key in cost_keys:
            if key in data:
                cost_data = data[key]
                break
        
        if not cost_data:
            if self.dev_mode:
                raise UnitDataMissingError(f"[开发模式] 找不到成本信息，尝试的键: {cost_keys}")
            cost_data = {}
        
        # 安全获取成本数据
        mineral = self._safe_get_numeric(cost_data, ['mineral', 'Mineral', 'minerals'], 0, "mineral_cost")
        vespene = self._safe_get_numeric(cost_data, ['vespene', 'Vespene', 'gas', 'Gas'], 0, "vespene_cost")
        supply = self._safe_get_numeric(cost_data, ['supply', 'Supply', 'population', 'Population'], 1, "supply_cost")
        time = self._safe_get_numeric(cost_data, ['game_time', 'time', 'BuildTime', 'build_time'], 0, "build_time")
        
        # 尝试导入Cost类
        try:
            from .unit import Cost
            target.cost = Cost(mineral=mineral, vespene=vespene, supply=supply, time=time)
        except ImportError:
            # 如果无法导入Cost类，使用字典形式
            target.cost = {
                'mineral': mineral,
                'vespene': vespene,
                'supply': supply,
                'time': time
            }
            
        print(f"[数据加载] 成本: 矿物={mineral}, 气体={vespene}, 补给={supply}, 时间={time}")
    
    def _apply_attack_info(self, data: Dict[str, Any], target) -> None:
        """
        应用攻击信息
        """
        attack_data = None
        attack_keys = ['Attack', 'attack', 'Attacks', 'attacks']
        
        for key in attack_keys:
            if key in data:
                attack_data = data[key]
                break
        
        if not attack_data:
            attack_data = {}
        
        # 安全提取攻击数据
        targets = str(attack_data.get('Targets', '')).strip()
        damage_str = str(attack_data.get('Damage', '0')).strip()
        dps_str = str(attack_data.get('DPS', '0')).strip()
        cooldown_str = str(attack_data.get('Cooldown', '0')).strip()
        bonus_str = str(attack_data.get('Bonus', '')).strip()
        range_val = self._safe_get_numeric(attack_data, ['Range', 'range'], 1)
        
        # 构建攻击信息字典
        attack_info = {
            "targets": [target.strip() for target in targets.split(',') if target.strip()] if targets else ["Ground"],
            "damage": self._extract_base_value(damage_str),
            "damage_upgrade": self._extract_upgrade_value(damage_str),
            "dps": {
                "base": self._extract_first_dps(dps_str),
                "with_upgrade": self._extract_second_dps(dps_str)
            },
            "cooldown": {
                "base": self._extract_first_cooldown(cooldown_str),
                "with_upgrade": self._extract_second_cooldown(cooldown_str)
            },
            "bonus_damage": {
                "value": self._extract_bonus_base_value(bonus_str),
                "upgrade": self._extract_bonus_upgrade_value(bonus_str),
                "vs": self._extract_bonus_target(bonus_str)
            },
            "range": range_val
        }
        
        target.attack = attack_info
        print(f"[数据加载] 攻击信息: 伤害={attack_info['damage']}, 射程={attack_info['range']}")
        
    def _apply_combat_info(self, data: Dict[str, Any], target) -> None:
        """
        应用战斗属性信息
        
        异常:
            UnitDataMissingError: 开发模式下战斗信息缺失时抛出
        """
        combat_data = None
        combat_keys = ['Combat', 'combat', 'Battle', 'battle']
        
        for key in combat_keys:
            if key in data:
                combat_data = data[key]
                break
        
        if not combat_data:
            if self.dev_mode:
                raise UnitDataMissingError(f"[开发模式] 找不到战斗信息，尝试的键: {combat_keys}")
            combat_data = {}
        
        # 安全获取战斗属性
        damage = self._safe_get_numeric(combat_data, ['damage', 'Damage', 'dmg'], 5, "damage")
        attack_range = self._safe_get_numeric(combat_data, ['attack_range', 'Range', 'range'], 3, "attack_range")
        attack_speed = self._safe_get_numeric(combat_data, ['attack_speed', 'Speed', 'speed'], 1, "attack_speed")
        
        # 设置战斗属性
        target.damage = damage
        target.attack_range = attack_range
        target.attack_speed = attack_speed
        
        print(f"[数据加载] 战斗属性: 伤害={damage}, 射程={attack_range}, 攻击速度={attack_speed}")
    
    def _apply_unit_stats(self, data: Dict[str, Any], target) -> None:
        """
        应用单位属性
        
        异常:
            UnitDataMissingError: 开发模式下单位属性信息缺失时抛出
        """
        unit_stats_data = None
        stats_keys = ['Unit stats', 'unit_stats', 'Stats', 'stats']
        
        for key in stats_keys:
            if key in data:
                unit_stats_data = data[key]
                break
        
        if not unit_stats_data:
            if self.dev_mode:
                raise UnitDataMissingError(f"[开发模式] 找不到单位属性信息，尝试的键: {stats_keys}")
            unit_stats_data = {}
        
        # 解析防御值
        defense_str = str(unit_stats_data.get('Defense', '')).strip()
        if not defense_str:
            if self.dev_mode:
                raise UnitDataMissingError("[开发模式] 防御值缺失")
            defense_str = '0 0 0'
        defense_values = self._parse_defense_values(defense_str, "defense")
        
        # 安全提取属性数据
        attributes_str = str(unit_stats_data.get('Attributes', '')).strip()
        if not attributes_str and self.dev_mode:
            raise UnitDataMissingError("[开发模式] 属性信息缺失")
        
        # 使用辅助方法安全获取数值
        sight = self._safe_get_numeric(unit_stats_data, ['Sight', 'sight', 'vision', 'Vision'], 5, "sight")
        speed = self._safe_get_numeric(unit_stats_data, ['Speed', 'speed', 'movement_speed'], 1.0, "speed")
        cargo_size = self._safe_get_numeric(unit_stats_data, ['Cargo size', 'cargo_size', 'cargo'], 1, "cargo_size")
        
        # 构建单位属性字典
        unit_stats = {
            "health": defense_values[0],
            "shield": defense_values[1],
            "armor": defense_values[2],
            "armor_upgrade": self._extract_armor_upgrade(defense_str),
            "attributes": [attr.strip() for attr in attributes_str.split(',') if attr.strip()] if attributes_str else [],
            "sight": sight,
            "speed": speed,
            "cargo_size": cargo_size,
            "energy": 50,
            "energy_max": 100
        }
        
        target.unit_stats = unit_stats
        print(f"[数据加载] 单位属性: 生命={unit_stats['health']}, 护盾={unit_stats['shield']}, 速度={unit_stats['speed']}")
    
    def _apply_abilities(self, data: Dict[str, Any], target) -> None:
        """
        应用能力信息
        """
        ability_data = None
        ability_keys = ['Ability', 'ability', 'Abilities', 'abilities']
        
        for key in ability_keys:
            if key in data:
                ability_data = data[key]
                break
        
        if not ability_data:
            ability_data = {}
        
        # 构建能力字典
        abilities = {}
        
        # 处理能力数据
        if isinstance(ability_data, dict):
            # 处理单个能力对象
            self._process_single_ability(ability_data, abilities)
        elif isinstance(ability_data, list):
            # 处理能力列表
            for ability_item in ability_data:
                if isinstance(ability_item, dict):
                    self._process_single_ability(ability_item, abilities)
        
        # 处理通用能力
        self._process_generic_abilities(data, abilities)
        
        target.abilities = abilities
        print(f"[数据加载] 能力: 加载了 {len(abilities)} 个特殊能力")
    
    def _process_single_ability(self, ability_item: Dict[str, Any], abilities: Dict[str, Any]) -> None:
        """
        处理单个能力对象
        
        参数:
            ability_item: 单个能力数据
            abilities: 能力字典，用于存储处理后的能力
        """
        try:
            # 提取能力名称
            ability_name = str(ability_item.get('Name', ability_item.get('name', 'Unknown'))).strip().lower()
            if not ability_name or ability_name == 'unknown':
                return
            
            # 提取能力信息
            cooldown = self._safe_get_numeric(ability_item, ['Cooldown', 'cooldown', 'cd'], 0, "cooldown")
            energy_cost = self._safe_get_numeric(ability_item, ['Energy Cost', 'energy_cost', 'energy'], 0, "energy_cost")
            range_val = self._safe_get_numeric(ability_item, ['Range', 'range'], 0, "range")
            description = str(ability_item.get('Description', ability_item.get('description', ''))).strip()
            hotkey = str(ability_item.get('Hotkey', ability_item.get('hotkey', ''))).strip()
            
            # 构建能力字典
            abilities[ability_name] = {
                "name": ability_name.capitalize(),
                "description": description,
                "cooldown": cooldown,
                "energy_cost": energy_cost,
                "range": range_val,
                "hotkey": hotkey,
                "researched": False,
                "cooldown_remaining": 0
            }
        except Exception as e:
            print(f"[警告] 处理能力数据时出错: {e}")
    
    def _process_generic_abilities(self, data: Dict[str, Any], abilities: Dict[str, Any]) -> None:
        """
        处理通用能力
        
        参数:
            data: 完整的数据字典
            abilities: 能力字典，用于存储处理后的能力
        """
        # 根据单位类型和属性添加通用能力
        # 示例：检查是否有灵能转移能力
        if any(key in str(data).lower() for key in ['transfer', 'teleport', 'warp']):
            if 'psionic_transfer' not in abilities:
                abilities['psionic_transfer'] = {
                    "name": "灵能转移",
                    "description": "在目标位置创建一个传送门，快速移动过去",
                    "cooldown": 11,
                    "energy_cost": 50,
                    "range": 12,
                    "researched": False,
                    "cooldown_remaining": 0
                }
        
        # 示例：检查是否有冲锋能力
        if any(key in str(data).lower() for key in ['charge', 'rush']):
            if 'charge' not in abilities:
                abilities['charge'] = {
                    "name": "冲锋",
                    "description": "快速冲向目标单位",
                    "cooldown": 7,
                    "energy_cost": 0,
                    "range": 7.5,
                    "researched": False,
                    "cooldown_remaining": 0
                }
        
        # 可以根据单位类型扩展更多通用能力
    
    def _apply_tactical_info(self, data: Dict[str, Any], target) -> None:
        """
        应用战术信息
        """
        # 加载强势对抗信息
        strong_against_data = data.get('Strong against', data.get('strong_against', data.get('counter', [])))
        target.strong_against = self._ensure_list(strong_against_data)
        
        # 加载弱势对抗信息
        weak_against_data = data.get('Weak against', data.get('weak_against', data.get('countered_by', [])))
        target.weak_against = self._ensure_list(weak_against_data)
        
        # 加载建造信息
        target.build_from = str(data.get('Built From', data.get('built_from', data.get('buildFrom', 'Unknown'))))
        target.requirements = str(data.get('Requirements', data.get('requirements', data.get('tech_requirement', ''))))
        target.hotkey = str(data.get('Hotkey', data.get('hotkey', '')))
        
        print(f"[数据加载] 战术信息: 强势对抗={len(target.strong_against)}个单位, 建造来源={target.build_from}")
    
    # 数据处理辅助方法
    def _safe_get_numeric(self, data: Dict[str, Any], possible_keys: List[str], default: Union[int, float], field_name: str = "") -> Union[int, float]:
        """
        安全地从字典中获取数值
        
        参数:
            data: 数据字典
            possible_keys: 可能的键名列表
            default: 默认值
            field_name: 字段名称，用于错误信息
            
        返回:
            Union[int, float]: 提取的数值或默认值
            
        异常:
            UnitDataMissingError: 开发模式下找不到值时抛出
        """
        try:
            if not isinstance(data, dict):
                if self.dev_mode:
                    raise UnitDataMissingError(f"[开发模式] 数据格式错误，期望字典类型但得到 {type(data).__name__}，字段: {field_name}")
                return default
                
            for key in possible_keys:
                if key in data:
                    value = data[key]
                    # 尝试转换为数值
                    if isinstance(value, (int, float)):
                        return value
                    if isinstance(value, str):
                        # 尝试从字符串中提取数字
                        match = re.search(r'\d+\.?\d*', value)
                        if match:
                            num_str = match.group(0)
                            return int(num_str) if '.' not in num_str else float(num_str)
                        elif self.dev_mode:
                            raise UnitDataMissingError(f"[开发模式] 无法从字符串 '{value}' 中提取数字，字段: {field_name}")
            
            if self.dev_mode:
                raise UnitDataMissingError(f"[开发模式] 找不到数值字段，尝试的键: {possible_keys}，字段: {field_name}")
            
            return default
        except UnitDataMissingError:
            raise
        except Exception as e:
            if self.dev_mode:
                raise UnitDataMissingError(f"[开发模式] 获取数值时出错: {e}，字段: {field_name}") from e
            return default
    
    def _ensure_list(self, value: Any, field_name: str = "") -> List[str]:
        """
        确保返回值是列表类型
        
        参数:
            value: 任意类型的值
            field_name: 字段名称，用于错误信息
            
        返回:
            List[str]: 转换后的列表
            
        异常:
            UnitDataMissingError: 开发模式下无法转换时抛出
        """
        try:
            if isinstance(value, list):
                result = [str(item).strip() for item in value if item]
                if not result and self.dev_mode:
                    raise UnitDataMissingError(f"[开发模式] 列表为空，字段: {field_name}")
                return result
            elif isinstance(value, str):
                # 尝试按逗号分割字符串
                result = [item.strip() for item in value.split(',') if item.strip()]
                if not result and self.dev_mode:
                    raise UnitDataMissingError(f"[开发模式] 无法从字符串 '{value}' 中解析列表，字段: {field_name}")
                return result
            elif value is not None:
                return [str(value).strip()]
            else:
                if self.dev_mode:
                    raise UnitDataMissingError(f"[开发模式] 值为None，字段: {field_name}")
                return []
        except UnitDataMissingError:
            raise
        except Exception as e:
            if self.dev_mode:
                raise UnitDataMissingError(f"[开发模式] 转换列表时出错: {e}，字段: {field_name}") from e
            return []
    
    def _extract_base_value(self, value_str: str, field_name: str = "base") -> int:
        """
        提取基础值
        
        参数:
            value_str: 包含数值的字符串
            field_name: 字段名称，用于错误信息
            
        返回:
            int: 提取的基础值
            
        异常:
            UnitDataMissingError: 开发模式下无法提取时抛出
        """
        try:
            # 移除括号内的内容
            clean_str = re.sub(r'\s*\([^)]*\)\s*', '', value_str)
            # 取第一个数字
            match = re.search(r'\d+', clean_str)
            if match:
                return int(match.group(0))
            
            if self.dev_mode:
                raise UnitDataMissingError(f"[开发模式] 无法从 '{value_str}' 中提取基础值，字段: {field_name}")
            return 0
        except UnitDataMissingError:
            raise
        except Exception as e:
            if self.dev_mode:
                raise UnitDataMissingError(f"[开发模式] 提取基础值时出错: {e}，字段: {field_name}") from e
            return 0
    
    def _extract_upgrade_value(self, value_str: str) -> int:
        """
        提取升级值
        """
        try:
            # 查找括号内的+数值
            match = re.search(r'\(\s*\+\s*(\d+)\s*\)', value_str)
            return int(match.group(1)) if match else 0
        except Exception:
            return 0
    
    def _extract_first_dps(self, dps_str: str) -> float:
        """
        提取第一个DPS值
        """
        try:
            match = re.search(r'(\d+\.?\d*)', dps_str)
            return float(match.group(1)) if match else 0.0
        except Exception:
            return 0.0
    
    def _extract_second_dps(self, dps_str: str) -> float:
        """
        提取第二个DPS值
        """
        try:
            matches = re.findall(r'(\d+\.?\d*)', dps_str)
            return float(matches[1]) if len(matches) > 1 else 0.0
        except Exception:
            return 0.0
    
    def _extract_first_cooldown(self, cooldown_str: str) -> float:
        """
        提取第一个冷却时间
        """
        return self._extract_first_dps(cooldown_str)
    
    def _extract_second_cooldown(self, cooldown_str: str) -> float:
        """
        提取第二个冷却时间
        """
        return self._extract_second_dps(cooldown_str)
    
    def _extract_bonus_base_value(self, bonus_str: str) -> int:
        """
        提取额外伤害基础值
        """
        try:
            match = re.search(r'(\d+)\s*vs', bonus_str, re.IGNORECASE)
            return int(match.group(1)) if match else 0
        except Exception:
            return 0
    
    def _extract_bonus_upgrade_value(self, bonus_str: str) -> int:
        """
        提取额外伤害升级值
        """
        try:
            match = re.search(r'(\d+)\s*vs.*\(\s*\+\s*(\d+)\s*\)', bonus_str, re.IGNORECASE)
            return int(match.group(2)) if match else 0
        except Exception:
            return 0
    
    def _extract_bonus_target(self, bonus_str: str) -> str:
        """
        提取额外伤害目标
        """
        try:
            match = re.search(r'vs\s+(\w+)', bonus_str, re.IGNORECASE)
            return match.group(1).capitalize() if match else ''
        except Exception:
            return ''
    
    def _parse_defense_values(self, defense_str: str, field_name: str = "defense") -> List[float]:
        """
        解析防御值字符串为列表
        
        参数:
            defense_str: 防御值字符串
            field_name: 字段名称，用于错误报告
            
        返回:
            List[float]: [health, shield, armor]
            
        异常:
            UnitDataMissingError: 开发模式下解析失败时抛出
        """
        try:
            # 提取所有数字
            numbers = re.findall(r'\d+', defense_str)
            values = []
            
            # 确保至少有3个值
            for i in range(3):
                if i < len(numbers):
                    values.append(float(numbers[i]))
                else:
                    if self.dev_mode:
                        raise UnitDataMissingError(f"[开发模式] {field_name} 值不完整，至少需要3个数值，当前: {len(numbers)}")
                    values.append(0.0)
                    
            return values
        except UnitDataMissingError:
            raise
        except Exception as e:
            if self.dev_mode:
                raise UnitDataMissingError(f"[开发模式] 解析{field_name}值失败: {defense_str}, 错误: {e}") from e
            print(f"[警告] 解析{field_name}值失败: {defense_str}, 错误: {e}")
            return [0.0, 0.0, 0.0]
    
    def _extract_armor_upgrade(self, defense_str: str) -> int:
        """
        提取护甲升级值
        """
        return self._extract_upgrade_value(defense_str)

# 提供一个全局的加载器实例，方便直接使用
global_loader = UnitJsonLoader()

# 便捷函数
def load_unit_data(unit_class_name: str) -> Dict[str, Any]:
    """便捷加载函数"""
    return global_loader.load_unit_data(unit_class_name)

def load_and_apply(unit_class_name: str, instance) -> bool:
    """便捷加载并应用函数"""
    return global_loader.load_and_apply(unit_class_name, instance)