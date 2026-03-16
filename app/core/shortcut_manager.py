"""
Shortcut Manager - 统一管理快捷键和按键处理
"""

import tkinter as tk
import platform
from typing import List, Callable, Optional, Set, Dict
from pynput import keyboard
from app.core.log import logger

# 平台检测
PLATFORM = platform.system()
IS_MAC = PLATFORM == 'Darwin'

# 统一的修饰键状态值定义
MODIFIER_STATES = {
    'Darwin': {
        'Control': 0x4,
        'Shift': 0x1,
        'Alt': 0x10,  # Option key on macOS
        'Command': 0x8  # Command key on macOS
    },
    'Windows': {
        'Control': 0x4,
        'Shift': 0x1,
        'Alt': 0x8,
        'Command': 0x10  # Meta key on Windows
    },
    'Linux': {
        'Control': 0x4,
        'Shift': 0x1,
        'Alt': 0x8,
        'Command': 0x10  # Meta key on Linux
    }
}

# 修饰键别名映射
MODIFIER_ALIASES = {
    'Meta': 'Command',  # Meta 键是 Command 键的别名
    'Command': 'Command'  # Command 键的别名是自身
}

# 获取当前平台的修饰键状态值
CURRENT_PLATFORM_MODIFIERS = MODIFIER_STATES.get(PLATFORM, MODIFIER_STATES['Linux'])


class ShortcutManager:
    """统一管理快捷键和按键处理的类"""
    
    def __init__(self):
        """初始化快捷键管理器"""
        self.platform = platform.system()
        
    def normalize_shortcut(self, shortcut: str) -> str:
        """标准化快捷键字符串
        
        Args:
            shortcut: 快捷键字符串（例如 'Ctrl+b'）
            
        Returns:
            标准化后的快捷键字符串
        """
        # 替换常见的修饰键别名
        replacements = {
            'Ctrl': 'Control',
            'Cmd': 'Command',
            'Win': 'Command',
            'Opt': 'Alt'
        }
        
        result = shortcut
        for old, new in replacements.items():
            result = result.replace(old, new)
        
        return result
    
    def get_tk_shortcut(self, shortcut: str) -> str:
        """将快捷键字符串转换为Tkinter绑定格式
        Args:
            shortcut: 快捷键字符串（例如 'Control+b'）
        Returns:
            Tkinter兼容的快捷键字符串
        """
        normalized = self.normalize_shortcut(shortcut)
        return normalized.replace('+', '-')
    
    def parse_hotkey_for_pynput(self, hotkey: str) -> Optional[Set]:
        """解析快捷键字符串为pynput键集合
        Args:
            hotkey: 快捷键字符串（例如 'Control+b'）
        Returns:
            pynput键对象的集合，如果解析失败则返回None
        """
        try:
            # 标准化快捷键字符串
            normalized_hotkey = self.normalize_shortcut(hotkey)
            parts = normalized_hotkey.split('+')
            keys = set()
            
            for part in parts:
                part = part.strip()
                if part == 'Command':
                    keys.add(keyboard.Key.cmd)
                elif part == 'Control':
                    keys.add(keyboard.Key.ctrl)
                elif part == 'Shift':
                    keys.add(keyboard.Key.shift)
                elif part == 'Alt':
                    keys.add(keyboard.Key.alt)
                elif len(part) == 1:
                    keys.add(part.lower())
                else:
                    # 处理特殊键
                    key_map = {
                        'Enter': keyboard.Key.enter,
                        'Esc': keyboard.Key.esc,
                        'Tab': keyboard.Key.tab,
                        'Space': keyboard.Key.space,
                        'Up': keyboard.Key.up,
                        'Down': keyboard.Key.down,
                        'Left': keyboard.Key.left,
                        'Right': keyboard.Key.right,
                        'Home': keyboard.Key.home,
                        'End': keyboard.Key.end,
                        'PageUp': keyboard.Key.page_up,
                        'PageDown': keyboard.Key.page_down,
                        'Backspace': keyboard.Key.backspace,
                        'Delete': keyboard.Key.delete
                    }
                    if part in key_map:
                        keys.add(key_map[part])
                    else:
                        logger.warning(f"未知的键: {part}")
            
            return keys
        except Exception as e:
            logger.error(f"解析快捷键失败: {e}")
            return None
    
    def bind_hotkey(self, widget, shortcuts: List[str], action: Callable):
        """绑定快捷键动作到多个快捷键
        Args:
            widget: 要绑定快捷键的Tkinter组件
            shortcuts: 快捷键字符串列表（例如 ['Ctrl+z', 'Command+z']）
            action: 按下快捷键时调用的函数
        """
        for shortcut in shortcuts:
            # 转换快捷键字符串为Tkinter绑定格式
            tk_shortcut = self.get_tk_shortcut(shortcut)
            widget.bind(f'<{tk_shortcut}>', action)
            # 为三部分快捷键绑定反向顺序（例如 Ctrl+Shift+z）
            parts = shortcut.split('+')
            if parts and len(parts) == 3:
                # 转换每个部分以兼容Tkinter
                part0 = self.normalize_shortcut(parts[0])
                part1 = self.normalize_shortcut(parts[1])
                part2 = self.normalize_shortcut(parts[2])
                widget.bind(f'<{part1}-{part0}-{part2}>', action)
            elif parts and len(parts) == 4:
                # 转换每个部分以兼容Tkinter
                part0 = self.normalize_shortcut(parts[0])
                part1 = self.normalize_shortcut(parts[1])
                part2 = self.normalize_shortcut(parts[2])
                part3 = self.normalize_shortcut(parts[3])
                widget.bind(f'<{part0}-{part2}-{part1}-{part3}>', action)
                widget.bind(f'<{part1}-{part0}-{part2}-{part3}>', action)
                widget.bind(f'<{part1}-{part2}-{part0}-{part3}>', action)
                widget.bind(f'<{part2}-{part1}-{part0}-{part3}>', action)
                widget.bind(f'<{part2}-{part0}-{part1}-{part3}>', action)
    
    def is_shortcut_pressed(self, event, shortcut: str) -> bool:
        """检查是否按下了指定的快捷键
        Args:
            event: 键盘事件
            shortcut: 快捷键字符串（例如 'Control+b'）
        Returns:
            如果按下了快捷键则返回True，否则返回False
        """
        try:
            normalized = self.normalize_shortcut(shortcut)
            parts = normalized.split('+')
            
            if len(parts) == 1:
                # 没有修饰键，只检查按键
                return event.keysym.lower() == parts[0].lower()
            else:
                # 有修饰键
                modifiers = parts[:-1]
                key = parts[-1]
                
                # 检查按键是否匹配
                # 处理大小写和特殊情况
                key_match = False
                if event.keysym.lower() == key.lower():
                    key_match = True
                # 处理字符键的特殊情况
                elif event.char and event.char.lower() == key.lower():
                    key_match = True
                
                if not key_match:
                    return False
                
                # 检查修饰键是否按下
                # 使用统一的修饰键状态值定义
                modifier_states = {}
                for mod, state_value in CURRENT_PLATFORM_MODIFIERS.items():
                    modifier_states[mod] = event.state & state_value != 0
                
                # 检查所有必需的修饰键是否按下
                required_modifiers_pressed = True
                for modifier in modifiers:
                    # 处理修饰键别名
                    mod_alias = MODIFIER_ALIASES.get(modifier, modifier)
                    if not modifier_states.get(mod_alias, False):
                        required_modifiers_pressed = False
                        break
                
                if not required_modifiers_pressed:
                    return False
                
                # 严格检查修饰键，确保没有额外的修饰键被按下
                # 这样可以避免长快捷键（如 Control+Shift+b）被匹配到短快捷键（如 Control+b）上
                pressed_modifiers = [mod for mod, pressed in modifier_states.items() if pressed]
                
                # 处理修饰键别名
                normalized_modifiers = []
                for mod in modifiers:
                    normalized_modifiers.append(MODIFIER_ALIASES.get(mod, mod))
                
                # 检查修饰键数量是否匹配
                for modifier in normalized_modifiers:
                    if not modifier_states.get(modifier, False):
                        return False
                
                # 确保按下的修饰键与必需的修饰键完全匹配（考虑别名）
                for mod in pressed_modifiers:
                    mod_alias = MODIFIER_ALIASES.get(mod, mod)
                    if mod_alias not in normalized_modifiers:
                        return False
                
                return True
        except Exception as e:
            logger.error(f"检查快捷键失败: {e}")
            return False
    
    def bind_editor_shortcuts(self, widget, config, shortcut_configs={}):
        """统一绑定编辑器的所有快捷键
        Args:
            widget: 要绑定快捷键的Tkinter组件
            config: 配置对象，包含shortcuts属性
            shortcut_configs: 包含所有快捷键配置的字典，格式为:
                {
                    'action_name': { 'keys': ['快捷键1', '快捷键2'], 'action': 动作函数 },
                    ...
                }
        """
        # 绑定每个快捷键
        for action_name, config_item in shortcut_configs.items():
            # 从配置中获取快捷键，如果没有则使用默认值
            shortcut_keys = config.shortcuts.get(action_name, config_item.get('keys', []))
            logger.info(f"绑定快捷键: {action_name} -> {shortcut_keys}")
            # 获取对应的动作函数
            action_func = config_item.get('action')
            if action_func:
                self.bind_hotkey(widget, shortcut_keys, action_func)
    



# 创建全局快捷键管理器实例
shortcut_manager = ShortcutManager()