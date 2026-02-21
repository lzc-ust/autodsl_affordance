from typing import List, Dict, Any, Optional
from autodsl_affordance.races.protoss import ProtossGatewayUnit
from autodsl_affordance.core.base_units.unit import Cost, Position
from autodsl_affordance.utils.json_loader import UnitJsonLoader

"""
Protoss Adept 单位类定义模块

本模块实现了星际争霸2中星灵族的使徒单位类，基于sc2_unit_info数据抽象。
这个类包含了使徒的所有能力、属性和战术行为，专为VLM接口设计。

根据用户要求的步骤5和6：
- 操作化方法：提供了执行级指令和参数
- 语义落地：确定了类属性和方法的具体值

执行单元文档：
- 执行单元：ProtossAdept
- 唯一类名：ProtossAdept
- 继承关系：Unit -> ProtossUnit -> ProtossGroundUnit -> ProtossGatewayUnit -> ProtossAdept
- 类语法结构：包含核心标识、游戏状态、成本、属性、攻击、能力、构建、战术等多个维度
"""

class ProtossAdept(ProtossGatewayUnit):
    """
    星灵族使徒(Protoss Adept)单位类
    
    继承链: Unit -> ProtossUnit -> ProtossGroundUnit -> ProtossGatewayUnit -> ProtossAdept
    
    核心特性:
    - 具有灵能转移(Psi-Transfer)能力，可以快速移动到指定位置并短暂形成幻影
    - 对轻甲单位有额外伤害加成(+12)
    - 移动速度快，适合骚扰和清理敌方工人
    - 主要用于骚扰和侦察任务
    
    执行级能力:
    - use_psionic_transfer: 执行灵能转移
    - harass_workers: 骚扰敌方工人
    - attack_light_units: 攻击轻甲单位
    - scout_area: 侦察指定区域
    
    属性维度设计:
    1. 核心标识属性：唯一类名、种族、单位类型、描述
    2. 游戏状态属性：位置、状态、选中状态
    3. 成本属性：矿物、气体、补给、建造时间
    4. 单位统计属性：生命值、护盾、能量、视野、速度等
    5. 攻击属性：伤害、伤害类型、额外伤害、攻击速度等
    6. 特殊能力：灵能转移的详细参数
    7. 构建信息：建造来源、前置需求、快捷键
    8. 战术信息：强势对抗、弱势对抗
    9. VLM接口信息：LLM接口、视觉识别、战术上下文
    """
    
    def __init__(self, dev_mode=False):
        """
        初始化ProtossAdept实例
        
        参数:
            dev_mode: 是否启用开发模式，默认为False
                    - 开发模式下：数据缺失或加载失败时会抛出异常
                    - 正常模式下：数据缺失或加载失败时会使用默认值
        
        处理流程:
            1. 初始化父类
            2. 设置核心标识属性
            3. 初始化各类属性值为空或默认值
            4. 使用统一的JSON加载工具类加载单位数据（可选启用开发模式）
            5. 增强VLM接口
            
        异常:
            UnitDataMissingError, UnitFileNotFoundError: 开发模式下数据缺失或文件不存在时抛出
        """
        super().__init__()
        # 确保使用标准的类名作为唯一标识符
        self.unique_class_name: str = "ProtossAdept"
        
        # 初始化核心属性
        self.description: str = ""
        self.cost: Cost = Cost(mineral=0, vespene=0, supply=0, time=0)
        
        # 战斗属性
        self.attack: Dict[str, Any] = {}
        self.unit_stats: Dict[str, Any] = {}
        self.abilities: Dict[str, Dict[str, Any]] = {}
        
        # 战术属性
        self.strong_against: List[str] = []
        self.weak_against: List[str] = []
        self.build_from: str = ""
        self.requirements: str = ""
        self.hotkey: str = ""
        
        # 使用统一的JSON加载工具类加载数据，传入开发模式参数
        self._load_data(dev_mode=dev_mode)
        
        # VLM优化
        self._enhance_vlm_interface()
    
    def _load_data(self, dev_mode=False):
        """使用统一的JSON加载工具类加载单位数据
        
        使用UnitJsonLoader来加载JSON数据，避免重复代码并提高健壮性
        
        参数:
            dev_mode: 是否启用开发模式，开发模式下会在数据缺失时抛出异常
        
        异常:
            UnitDataMissingError, UnitFileNotFoundError: 开发模式下数据缺失或文件不存在时抛出
        """
        print(f"[数据加载] 使用统一加载工具类加载 {self.unique_class_name} 数据")
        print(f"[数据加载] 当前模式: {'开发模式' if dev_mode else '正常模式'}")
        
        # 创建加载器实例，启用开发模式
        loader = UnitJsonLoader(dev_mode=dev_mode)
        
        # 加载并应用数据
        try:
            load_success = loader.load_and_apply(self.unique_class_name, self)
            
            # 在开发模式下，即使返回成功也检查关键属性
            if dev_mode:
                # 检查关键属性是否被正确设置
                required_attributes = ['description', 'cost', 'unit_stats', 'attack']
                for attr in required_attributes:
                    if not hasattr(self, attr) or not getattr(self, attr):
                        from autodsl_affordance.core.base_units.json_loader import UnitDataMissingError
                        raise UnitDataMissingError(f"[开发模式] 关键属性 {attr} 未被正确设置")
            
            # 在非开发模式下，如果加载失败，设置默认值
            if not load_success:
                print(f"[警告] 使用加载工具类加载失败，设置默认值")
                self._set_default_values(dev_mode=dev_mode)
        except Exception as e:
            if dev_mode:
                # 在开发模式下直接抛出异常
                raise
            # 在非开发模式下捕获异常并使用默认值
            print(f"[警告] 加载数据时出错: {e}，设置默认值")
            self._set_default_values(dev_mode=dev_mode)
    
    def _set_default_values(self, dev_mode=False):
        """设置默认值，当JSON文件不存在或解析失败时使用
        
        参数:
            dev_mode: 是否启用开发模式，开发模式下不会设置默认值而是抛出异常
        
        异常:
            UnitDataMissingError: 开发模式下调用此方法时抛出，表示数据缺失
        """
        # 在开发模式下，不设置默认值，而是抛出异常
        if dev_mode:
            from autodsl_affordance.core.base_units.json_loader import UnitDataMissingError
            raise UnitDataMissingError("[开发模式] 数据加载失败，且不允许使用默认值，请检查JSON文件")
        
        # 非开发模式下，设置默认值
        print("使用默认配置值初始化ProtossAdept...")
        
        # 基础信息
        self.description = "Protoss的骚扰单位，拥有灵能转移能力。"
        self.race = "Protoss"
        self.unit_type = "Gateway Unit"
        
        # 成本信息
        self.cost = Cost(mineral=100, vespene=25, supply=2, time=27)
        
        # 攻击信息 - 详细定义
        self.attack = {
            "targets": ["Ground"],
            "damage": 10,
            "damage_upgrade": 1,
            "dps": {"base": 7.1, "with_upgrade": 12.5},
            "cooldown": {"base": 1.41, "with_upgrade": 0.83},
            "bonus_damage": {"value": 12, "upgrade": 1, "vs": "Light"},
            "range": 4
        }
        
        # 单位属性 - 详细定义
        self.unit_stats = {
            "health": 70,
            "shield": 70,
            "armor": 1,
            "armor_upgrade": 1,
            "attributes": ["Light", "Biological"],
            "sight": 10,
            "speed": 3.5,
            "cargo_size": 2,
            "energy": 50,
            "energy_max": 100
        }
        
        # 能力信息 - 详细定义灵能转移
        self.abilities = {
            "psionic_transfer": {
                "name": "灵能转移",
                "description": "在目标位置创建一个传送门，使徒快速移动过去并留下一个短暂的幻影",
                "cooldown": 11,
                "energy_cost": 50,
                "shade_duration": 3.5,
                "range": 12
            }
        }
        
        # 战术信息 - 详细定义
        self.strong_against = ["Worker", "Marine", "Zergling", "Zealot", "Stalker"]
        self.weak_against = ["Roach", "Marauder", "Immortal", "Raven"]
        self.build_from = "Gateway"
        self.requirements = "Cybernetics Core"
        self.hotkey = "D"
        
        # 更新VLM接口
        self._enhance_vlm_interface()
    
    def _enhance_vlm_interface(self):
        """增强VLM接口，添加详细的语义描述和执行指令
        
        步骤5-6：操作化方法与语义落地
        根据sc2_unit_info数据抽象定义，为VLM提供完整的接口描述
        确保VLM能够准确理解单位的能力和使用场景
        
        功能:
            - 定义llm_interface: 提供给LLM的完整接口描述
            - 定义visual_recognition: 提供给视觉模型的识别特征
            - 定义tactical_context: 提供战术上下文和使用场景
        """
        # 基础信息
        self.llm_interface = {
            "unique_class_name": self.unique_class_name,
            "description": self.description,
            "race": self.race,
            "unit_type": self.unit_type,
            "cost": {
                "mineral": self.cost.mineral,
                "vespene": self.cost.vespene,
                "supply": self.cost.supply,
                "time": self.cost.time
            },
            "abilities": self.abilities,
            "stats": self.unit_stats,
            "build_from": self.build_from,
            "requirements": self.requirements,
            "strong_against": self.strong_against,
            "weak_against": self.weak_against,
            "hotkey": self.hotkey,
            # 基于sc2_unit_info数据抽象的额外属性
            "movement_type": "Ground",
            "attack_type": "Melee",
            "range_type": "Short",
            "production_building": "Gateway",
            "tech_requirements": self.requirements,
            "unit_category": "Light",
            "can_attack_ground": True,
            "can_attack_air": False,
            "execution_methods": [
                {
                    "method_name": "use_psionic_transfer",
                    "description": "执行灵能转移能力，创建一个传送门并立即移动",
                    "parameters": [
                        {"name": "target_position", "type": "Position", "description": "目标传送位置，必须在12范围内"}
                    ],
                    "execution_instructions": [
                        "验证目标位置在灵能转移范围内(最大12)",
                        "检查当前能量是否满足转移需求(至少50能量)",
                        "确认冷却时间已就绪",
                        "执行传送并扣除50能量",
                        "设置11秒冷却时间",
                        "创建持续3.5秒的幻影单位",
                        "更新当前位置"
                    ],
                    "preconditions": [
                        "unit_stats['energy'] >= 50",
                        "abilities['psionic_transfer']['cooldown'] == 0",
                        "目标位置距离 <= 12"
                    ]
                },
                {
                    "method_name": "harass_workers",
                    "description": "骚扰敌方工人，优先攻击资源收集单位",
                    "parameters": [
                        {"name": "target_area", "type": "Position", "description": "骚扰目标区域（敌方资源点）"},
                        {"name": "retreat_position", "type": "Position", "description": "撤退位置（安全点）"},
                        {"name": "attack_duration", "type": "float", "description": "攻击持续时间(秒)"}
                    ],
                    "execution_instructions": [
                        "评估目标区域的安全程度",
                        "移动到最佳攻击位置",
                        "优先攻击工人单位",
                        "利用对轻甲单位的额外伤害(+12 vs Light)",
                        "监控自身生命值和受到的威胁",
                        "生命值低于30%或攻击时间结束时开始撤退",
                        "优先使用灵能转移撤退（如果能量足够）"
                    ],
                    "tactical_advice": "骚扰后立即撤退，避免与敌方主力单位正面交战"
                },
                {
                    "method_name": "attack_light_units",
                    "description": "攻击轻甲单位，利用额外伤害优势",
                    "parameters": [
                        {"name": "targets", "type": "List[str]", "description": "目标单位列表"}
                    ],
                    "execution_instructions": [
                        "验证目标是否为轻甲单位",
                        "确认目标在攻击范围内(2)",
                        "优先攻击脆弱的轻甲单位",
                        "利用对轻甲单位的额外伤害优势(+12)",
                        "监控战斗状态并适时调整战术"
                    ],
                    "damage_info": {
                        "base_damage": self.attack['damage'],
                        "bonus_damage": self.attack['bonus_damage']['value'],
                        "bonus_target": self.attack['bonus_damage']['vs']
                    }
                },
                {
                    "method_name": "scout_area",
                    "description": "侦察指定区域，收集敌方情报",
                    "parameters": [
                        {"name": "target_position", "type": "Position", "description": "侦察目标位置"},
                        {"name": "search_radius", "type": "float", "description": "搜索半径"}
                    ],
                    "execution_instructions": [
                        "移动到侦察位置附近",
                        "使用视野范围(10)搜索区域",
                        "识别敌方单位和建筑",
                        "收集战术情报",
                        "安全撤退"
                    ],
                    "scouting_abilities": "利用速度和灵能转移进行快速侦察和撤离"
                }
            ]
        }
        
        # 视觉识别增强
        self.visual_recognition = {
            "unit_identifier": self.unique_class_name,
            "race_identifier": self.race,
            "unit_type_identifier": self.unit_type,
            "color_scheme": "Protoss blue and gold",
            "silhouette": "Slim humanoid with glowing features",
            "size_category": "Medium",
            "distinctive_features": ["Energy blade", "Glowing eyes", "Advanced psionic features", "Hovering animation"],
            "visual_patterns": [
                "蓝色能量护盾视觉效果",
                "使用灵能转移时的特殊动画和传送门效果",
                "攻击时释放能量刃的视觉效果",
                "移动时的悬浮效果"
            ],
            # 基于sc2_unit_info的额外视觉特征
            "unit_size": "Medium",
            "shield_color": "Blue",
            "special_effects": ["Psionic transfer portal", "Energy blade attack", "Shield regeneration"],
            "recognition_priority": "High",
            "unique_animations": ["Psionic transfer", "Shade creation", "Energy blade strike"]
        }
        
        # 战术上下文增强
        self.tactical_context = {
            "primary_role": "Harassment",
            "secondary_roles": ["Scouting", "Hit-and-run attacks", "Map control", "Flanking"],
            "effective_situations": [
                "Worker harassment", 
                "Picking off lone units", 
                "Flanking", 
                "Scouting enemy expansions",
                "Early game pressure",
                "Defending against light unit rushes"
            ],
            "vulnerable_situations": [
                "Large group battles", 
                "Against armored units", 
                "Low on energy",
                "Facing area-of-effect attacks",
                "Without support units"
            ],
            "tactical_patterns": [
                "利用灵能转移快速切入敌方基地",
                "攻击工人后立即使用灵能转移撤退",
                "在狭窄区域使用灵能转移伏击敌方单位",
                "配合哨兵(Sentry)的力场创造进攻路径",
                "利用灵能转移绕过敌方防御"
            ],
            "energy_management": "优先保存能量用于灵能转移，避免在不必要的情况下消耗",
            "withdrawal_conditions": [
                "生命值低于30%",
                "能量不足以使用灵能转移",
                "面对重装甲单位",
                "敌方防御力量增强"
            ],
            # 基于sc2_unit_info的额外战术信息
            "counter_units": ["Marine with Stim (Terran)", "Zergling (Zerg)", "Stalker (Protoss)"],
            "synergy_units": ["Sentry", "Zealot", "Warp Prism"],
            "effective_timing": "Early to mid game",
            "optimal_group_size": "Small groups (2-4 units)",
            "micro_techniques": ["Shade distraction", "Split damage", "Hit-and-run"]
        }
    
    def use_psionic_transfer(self, target_position: Position) -> bool:
        """使用灵能转移能力
        
        参数:
            target_position (Position): 目标传送位置
            
        返回:
            bool: 转移是否成功
            
        执行级指令:
            1. 验证目标位置在灵能转移范围内
            2. 检查当前能量是否满足转移需求
            3. 确认冷却时间已就绪
            4. 执行传送并扣除能量
            5. 设置冷却时间
            6. 创建短暂的幻影单位
            7. 更新当前位置
        """
        # 检查能量是否足够
        current_energy = self.unit_stats.get('energy', 0)
        energy_cost = self.abilities.get('psionic_transfer', {}).get('energy_cost', 50)
        
        if current_energy < energy_cost:
            print(f"[执行失败] {self.unique_class_name} 能量不足({current_energy}/{energy_cost})，无法使用灵能转移")
            return False
        
        # 检查冷却时间是否就绪
        cooldown = self.abilities.get('psionic_transfer', {}).get('cooldown', 0)
        if cooldown > 0:
            print(f"[执行失败] {self.unique_class_name} 灵能转移冷却中，还需等待 {cooldown:.1f} 秒")
            return False
        
        # 计算距离
        current_position = self.position
        distance = ((target_position.x - current_position.x) ** 2 + 
                   (target_position.y - current_position.y) ** 2) ** 0.5
        
        max_range = self.abilities.get('psionic_transfer', {}).get('range', 12)
        if distance > max_range:
            print(f"[执行失败] {self.unique_class_name} 目标位置超出灵能转移范围({distance:.1f}/{max_range})")
            return False
        
        # 执行转移 - 详细的执行级指令日志
        print(f"[执行步骤1/4] {self.unique_class_name} 开始灵能转移准备")
        print(f"[执行步骤2/4] {self.unique_class_name} 创建灵能传送门在位置 {target_position}")
        print(f"[执行步骤3/4] {self.unique_class_name} 从 {current_position} 通过传送门移动")
        
        # 扣除能量
        self.unit_stats['energy'] = current_energy - energy_cost
        print(f"[执行步骤4/4] 扣除能量 {energy_cost}，剩余能量 {self.unit_stats['energy']}")
        
        # 设置冷却时间
        cooldown_duration = self.abilities['psionic_transfer'].get('cooldown', 11)
        self.abilities['psionic_transfer']['cooldown'] = cooldown_duration
        print(f"[执行结果] 灵能转移完成，设置冷却时间 {cooldown_duration} 秒")
        
        # 创建幻影
        shade_duration = self.abilities['psionic_transfer'].get('shade_duration', 3.5)
        print(f"[执行结果] 创建幻影单位，持续 {shade_duration} 秒")
        
        # 更新位置
        self.position = target_position
        print(f"[执行完成] {self.unique_class_name} 成功转移到 {target_position}")
        
        return True
    
    def harass_workers(self, target_area: Position, retreat_position: Position, attack_duration: float = 5.0) -> bool:
        """骚扰敌方工人
        
        参数:
            target_area (Position): 骚扰目标区域（敌方基地中的资源收集区域）
            retreat_position (Position): 撤退位置（安全的撤离点）
            attack_duration (float): 攻击持续时间（秒），默认为5秒
            
        返回:
            bool: 骚扰任务是否成功完成
            
        执行级指令:
            1. 评估目标区域的安全程度
            2. 移动到最佳攻击位置
            3. 优先攻击工人单位
            4. 监控自身生命值和受到的威胁
            5. 在指定时间或生命危险时开始撤退
            6. 根据能量情况选择撤退方式
            7. 确认安全撤离
        """
        print(f"[战术执行] {self.unique_class_name} 开始工人骚扰任务")
        print(f"[目标设置] 攻击区域: {target_area}, 撤退位置: {retreat_position}, 攻击持续时间: {attack_duration}秒")
        
        # 初始生命值
        initial_health = self.unit_stats.get('health', 70)
        
        # 移动到目标区域
        print(f"[执行步骤1/5] 移动到目标区域 {target_area}")
        self.move_to(target_area)
        
        # 攻击工人 - 详细的执行指令
        print(f"[执行步骤2/5] 开始攻击敌方工人，持续 {attack_duration} 秒")
        print(f"[战术执行] 优先攻击未受保护的工人")
        print(f"[战术执行] 利用对轻甲单位的额外伤害 ({self.attack['bonus_damage']['value']} vs {self.attack['bonus_damage']['vs']})")
        
        # 模拟战斗造成的伤害
        damage_taken = 20  # 假设承受了一些伤害
        self.unit_stats['health'] = max(0, initial_health - damage_taken)
        print(f"[战斗反馈] 承受 {damage_taken} 点伤害，剩余生命值 {self.unit_stats['health']}")
        
        # 检查是否需要撤退
        health_percent = (self.unit_stats['health'] / initial_health) * 100
        if health_percent < 30:
            print(f"[战术决策] 生命值低于30%，紧急撤退")
        else:
            print(f"[战术决策] 攻击时间结束，开始撤退")
        
        # 检查是否可以使用灵能转移撤退
        print(f"[执行步骤3/5] 开始撤退操作")
        current_energy = self.unit_stats.get('energy', 0)
        if current_energy >= 50:
            print(f"[执行步骤4/5] 使用灵能转移撤退到 {retreat_position}")
            transfer_success = self.use_psionic_transfer(retreat_position)
            if transfer_success:
                print(f"[战术执行] 成功使用灵能转移撤离")
            else:
                print(f"[战术执行] 灵能转移失败，改为常规移动撤退")
                self.move_to(retreat_position)
        else:
            print(f"[执行步骤4/5] 能量不足({current_energy}/50)，直接撤退到 {retreat_position}")
            self.move_to(retreat_position)
        
        # 任务完成评估
        print(f"[执行步骤5/5] 到达撤退位置 {retreat_position}")
        print(f"[任务完成] 骚扰任务完成，剩余生命值: {self.unit_stats['health']}, 剩余能量: {self.unit_stats['energy']}")
        
        return True
        
    def attack_light_units(self, targets: List[str]) -> bool:
        """攻击轻甲单位
        
        参数:
            targets (List[str]): 目标单位名称列表
            
        返回:
            bool: 攻击操作是否执行
            
        执行级指令:
            1. 验证目标是否为轻甲单位
            2. 确认目标在攻击范围内
            3. 优先攻击对轻甲单位有额外伤害加成
            4. 监控战斗状态并适时调整战术
        """
        if not targets:
            print(f"[执行失败] 没有提供有效的攻击目标")
            return False
            
        print(f"[战术执行] {self.unique_class_name} 开始攻击轻甲单位")
        print(f"[目标列表] {', '.join(targets)}")
        
        # 检查是否有对轻甲单位的额外伤害
        bonus_damage = self.attack.get('bonus_damage', {})
        if bonus_damage.get('vs', '').lower() == 'light':
            print(f"[战术优势] 利用对轻甲单位的额外伤害: +{bonus_damage.get('value', 0)}")
        else:
            print(f"[战术提醒] 注意: 该单位对轻甲单位没有特殊伤害加成")
            
        # 模拟攻击每个目标
        for target in targets:
            print(f"[执行步骤] 攻击目标: {target}")
            print(f"[攻击参数] 基础伤害: {self.attack.get('damage', 0)}, 攻击范围: {self.attack.get('range', 0)}")
            
        print(f"[执行完成] 攻击操作执行完毕")
        return True
        
    def scout_area(self, target_position: Position, search_radius: float = 8.0) -> Dict[str, Any]:
        """侦察指定区域
        
        参数:
            target_position (Position): 侦察目标位置
            search_radius (float): 搜索半径，默认为8.0
            
        返回:
            Dict[str, Any]: 侦察结果
            
        执行级指令:
            1. 移动到侦察位置附近
            2. 使用视野范围搜索区域
            3. 识别敌方单位和建筑
            4. 收集战术情报
            5. 安全撤退
        """
        print(f"[侦察任务] {self.unique_class_name} 开始侦察任务")
        print(f"[侦察参数] 目标位置: {target_position}, 搜索半径: {search_radius}")
        
        # 移动到目标位置
        print(f"[执行步骤1/4] 移动到侦察位置附近")
        self.move_to(target_position)
        
        # 模拟搜索
        print(f"[执行步骤2/4] 使用视野范围({self.unit_stats.get('sight', 10)})进行搜索")
        
        # 模拟发现结果
        scout_results = {
            "position": target_position,
            "timestamp": "current",
            "enemy_units": [],
            "enemy_structures": [],
            "terrain_features": [],
            "resource_deposits": []
        }
        
        print(f"[执行步骤3/4] 收集侦察情报")
        print(f"[执行步骤4/4] 侦察完成，开始撤退")
        
        return scout_results