from typing import Dict, Any
from autodsl_affordance.races.protoss import ProtossGatewayUnit
from autodsl_affordance.core.base_units.unit import Cost, Position

class ProtossStalker(ProtossGatewayUnit):
    """
    Protoss Stalker unit class - 神族追猎者单位
    追猎者是一种机动远程单位，具备闪烁能力，优秀的对空和对地能力
    """
    
    def __init__(self, **kwargs):
        """初始化追猎者单位"""
        # 调用父类初始化方法，这会设置_inheritance_chain等必要属性
        # 注意：不要将development_mode传递给父类
        super().__init__()
        
        # 设置单位基本信息
        self.unique_class_name = "ProtossStalker"
        self.unit_name = "Stalker"
        self.unit_type = "Gateway Unit"
        
        # 初始化状态
        self.position = Position(0, 0)
        self.development_mode = kwargs.get('development_mode', False)
        
        # 初始化属性
        self.description = ""
        self.cost = None
        self.attack = {}
        self.unit_stats = {}
        self.abilities = {}
        self.tactical_info = {}
        self.strong_against = []
        self.weak_against = []
        self.upgrades = {}
        
        # 加载单位数据
        self._load_data()
        # 设置默认值
        self._set_default_values()
        # VLM接口增强
        self._enhance_vlm_interface()
    
    def _load_data(self):
        """加载单位数据，可以从JSON文件或硬编码数据获取"""
        try:
            # 尝试从JSON文件加载数据
            import os
            # 计算JSON文件路径
            current_dir = os.path.dirname(__file__)
            # 路径调整：向上三级目录，然后进入sc2_unit_info目录
            json_path = os.path.join(
                current_dir,  # 当前文件目录
                "..", "..", "..",  # 向上三级：ground_units -> protoss -> races
                "sc2_unit_info",  # 进入sc2_unit_info目录
                f"Protoss_Stalker.json"  # 文件名
            )
            
            # 如果JSON文件存在，尝试加载
            if os.path.exists(json_path):
                import json
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # 解析JSON数据
                self._parse_json_data(data)
            else:
                # JSON文件不存在，使用硬编码数据作为后备
                print(f"警告: JSON文件不存在，使用硬编码数据: {json_path}")
                self._set_hardcoded_data()
        except Exception as e:
            if self.development_mode:
                raise e
            print(f"警告: 无法加载{self.unique_class_name}的数据: {e}")
            # 使用硬编码数据作为后备
            self._set_hardcoded_data()
    
    def _parse_json_data(self, data: Dict[str, Any]):
        """解析JSON数据"""
        # 从之前的代码重构而来
        pass
    
    def _set_hardcoded_data(self):
        """设置硬编码的单位数据作为后备"""
        # 设置默认单位数据，类似于_set_default_values方法但更完整
        self.description = "追猎者 - 神族机动远程单位，具备闪烁能力，优秀的对空和对地能力，适合机动战术和地图控制。"
        self.cost = Cost(mineral=125, vespene=50, supply=2, time=30)
        self.attack = {
            "targets": ["Ground", "Air"],
            "damage": 13,
            "damage_upgrade": 1,
            "dps": {"base": 9.7, "vs_armored": 13.4},
            "cooldown": 1.34,
            "range": 6,
            "bonus_damage": {
                "value": 5,
                "upgrade": 1,
                "vs": "Armored"
            }
        }
        self.unit_stats = {
            "health": 80,
            "shield": 80,
            "armor": 1,
            "armor_upgrade": 1,
            "attributes": ["Armored", "Mechanical"],
            "sight": 10,
            "speed": 4.13,
            "cargo_size": 2
        }
        self.abilities = {
            "blink": {
                "name": "Blink",
                "researched": False,
                "cooldown": 7,
                "range": 7.5,
                "description": "允许追猎者瞬间移动到附近位置",
                "hotkey": "B"
            }
        }
        self.strong_against = ["Marine", "Marauder", "Roach", "Hydralisk"]
        self.weak_against = ["Zealot", "Stalker", "Zergling", "Baneling"]
        self.upgrades = {
            "blink_research": {
                "name": "Blink Research",
                "mineral_cost": 150,
                "vespene_cost": 150,
                "research_time": 121,
                "researched_from": "Twilight Council",
                "effect": "追猎者获得闪烁能力"
            }
        }
        self.tactical_info = {
            "strong_against": ["Marine", "Marauder", "Roach", "Hydralisk"],
            "weak_against": ["Zealot", "Stalker", "Zergling", "Baneling"],
            "synergies": ["Colossus", "Phoenix", "Sentry", "Zealot"]
        }
    
    def use_blink(self, position):
        """使用闪烁能力移动到指定位置"""
        if self.abilities.get("blink", {}).get("researched", False):
            result = {
                "success": True,
                "message": f"追猎者闪烁到位置 {position}",
                "cost": {"cooldown": 7}
            }
            return result
        else:
            return {
                "success": False,
                "message": "闪烁能力尚未研究",
                "required_research": "Blink Research"
            }
    
    def engage_at_range(self, target):
        """在远程攻击范围内与敌人交战"""
        # 验证目标存在
        if not target:
            return {
                "success": False,
                "message": "目标不存在"
            }
        
        result = {
            "success": True,
            "message": f"追猎者在远程攻击范围内攻击目标 {target}",
            "damage": self.attack["damage"],
            "range": self.attack["range"]
        }
        
        # 检查是否对装甲单位有额外伤害
        if hasattr(target, "attributes") and "Armored" in target.attributes:
            result["bonus_damage"] = self.attack["bonus_damage"]["value"]
            result["message"] += f"，对装甲单位造成额外伤害"
        
        return result
    
    def retreat_and_blink(self, retreat_position):
        """边撤退边使用闪烁战术"""
        # 检查闪烁是否已研究
        if not self.abilities.get("blink", {}).get("researched", False):
            return {
                "success": False,
                "message": "闪烁能力尚未研究",
                "required_research": "Blink Research"
            }
        
        # 模拟低血量判断
        if self.unit_stats["health"] > 40:  # 假设40是低血量阈值
            return {
                "success": False,
                "message": "血量未达到撤退阈值"
            }
        
        return {
            "success": True,
            "message": f"追猎者边撤退边闪烁到位置 {retreat_position}",
            "tactic": "hit_and_run"
        }
    
    def setup_ambush(self, ambush_position, target_area):
        """设置闪烁伏击"""
        # 检查闪烁是否已研究
        if not self.abilities.get("blink", {}).get("researched", False):
            return {
                "success": False,
                "message": "闪烁能力尚未研究",
                "required_research": "Blink Research"
            }
        
        # 验证目标区域
        if not target_area:
            return {
                "success": False,
                "message": "目标区域无效"
            }
        
        return {
            "success": True,
            "message": f"追猎者在位置 {ambush_position} 设置闪烁伏击，目标区域: {target_area}",
            "ambush_ready": True
        }
    
    def _set_default_values(self):
        """设置默认值，确保属性完整性"""
        if not self.description:
            if self.development_mode:
                raise ValueError("单位描述不能为空")
            self.description = "神族机动远程单位，具备闪烁能力，优秀的对空和对地能力"
        
        if not self.cost:
            self.cost = Cost(mineral=125, vespene=50, supply=2, time=30)
        
        if not self.attack:
            self.attack = {
                "targets": ["Ground", "Air"],
                "damage": 13, "damage_upgrade": 1,
                "dps": {"base": 9.7, "vs_armored": 13.4},
                "cooldown": 1.34,
                "bonus_damage": {"value": 5, "upgrade": 1, "vs": "Armored"},
                "range": 6, "applies_slow": True
            }
        
        if not self.unit_stats:
            self.unit_stats = {
                "health": 80, "shield": 80, "armor": 1, "armor_upgrade": 1,
                "attributes": ["Armored", "Mechanical"],
                "sight": 10, "speed": 4.13, "cargo_size": 2
            }
        
        if not self.abilities:
            self.abilities = {
                "blink": {"researched": False, "cooldown": 7, "range": 7.5}
            }
        
        if not self.tactical_info:
            self.tactical_info = {
                "strong_against": ["Void Ray", "Mutalisk", "Oracle", "Phoenix", "Reaper"],
                "weak_against": ["Marauder", "Immortal", "Zergling", "Roach", "Siege Tank"],
                "synergies": ["Colossus", "Phoenix"]
            }
    
    def _enhance_vlm_interface(self):
        """增强VLM接口，优化视觉和语言模型交互"""
        # 初始化接口字典（如果不存在）
        if not hasattr(self, 'llm_interface'):
            self.llm_interface = {}
        if not hasattr(self, 'visual_recognition'):
            self.visual_recognition = {}
        if not hasattr(self, 'tactical_context'):
            self.tactical_context = {}
        
        # 动态获取战术信息
        general_tactics = self.tactical_info.get('General', '') if hasattr(self, 'tactical_info') else ''
        
        self.llm_interface.update({
            "natural_language_aliases": ["追猎者", "stalker", "闪烁单位", "四足机械兵", "瞬移猎手"],
            "role_description": self.description,
            "tactical_keywords": ["闪烁微操", "防空", "狙击", "地图控制", "移动战", "骚扰", "突围", "追击"],
            "primary_role": ["防空", "骚扰", "狙击", "地图控制", "机动支援"],
            "common_tactics": ["闪烁撤退", "坦克狙击", "追击空军", "分矿防守", "关键目标击杀", "闪烁接近", "拉扯消耗"],
            "special_abilities": ["闪烁（Blink）"],
            "micro_techniques": ["闪烁拉扯", "集火空军", "绕后包抄", "狙击重甲", "分矿防守"],
            "visual_recognition_features": ["四足机械", "粒子步枪", "闪烁时蓝色特效"],
            "competitive_insights": general_tactics
        })
        
        self.visual_recognition.update({
            "identifying_features": ["四足机械", "粒子步枪", "闪烁时蓝色特效"],
            "minimap_characteristics": "蓝色小点",
            "unique_visual_queues": ["粒子束攻击", "闪烁传送"],
            "llm_vision_prompt": "识别画面中的追猎者 - 四足机械单位，手持粒子步枪"
        })
        
        self.tactical_context.update({
            "early_game": ["侦察", "防御骚扰", "对空防御"],
            "mid_game": ["闪烁骚扰", "坦克狙击", "空军拦截"],
            "late_game": ["机动支援", "关键目标狙击", "包抄支援"],
            "counters": self.weak_against if hasattr(self, 'weak_against') else [],
            "countered_by": self.strong_against if hasattr(self, 'strong_against') else [],
            "synergies": [f"与{s}配合" for s in self.tactical_info.get("synergies", [])] if hasattr(self, 'tactical_info') else [],
            "vs_protoss": self.tactical_info.get('Vs. Protoss', '') if hasattr(self, 'tactical_info') else '',
            "vs_terran": self.tactical_info.get('Vs. Terran', '') if hasattr(self, 'tactical_info') else '',
            "vs_zerg": self.tactical_info.get('Vs. Zerg', '') if hasattr(self, 'tactical_info') else ''
        })
        
        # 定义预置函数候选（符合标准模板要求）
        self.prefab_function_candidates = [
            {
                "function_name": "stalker_anti_air_defense",
                "description": "追猎者防空防御并拦截敌方空军",
                "parameters": {
                    "air_targets": "空中目标列表",
                    "priority_target": "优先目标"
                },
                "execution_flow": [
                    "anti_air_defense(air_targets)",
                    "focus_fire_air_unit(priority_target)",
                    "blink_chase_air()"
                ]
            },
            {
                "function_name": "stalker_blink_maneuver",
                "description": "追猎者使用闪烁进行战术机动",
                "parameters": {
                    "target_position": "目标位置",
                    "maneuver_type": "机动类型 (retreat/advance/flank)"
                },
                "execution_flow": [
                    "use_blink(target_position)",
                    "reposition_for_advantage()",
                    "regroup_if_needed()"
                ]
            },
            {
                "function_name": "stalker_snipe_armored",
                "description": "追猎者狙击敌方装甲单位",
                "parameters": {
                    "armored_target": "装甲目标",
                    "target_position": "目标位置"
                },
                "execution_flow": [
                    "use_blink(target_position)",
                    "snipe_armored_unit(armored_target, target_position)",
                    "retreat_if_vulnerable()"
                ]
            }
        ]