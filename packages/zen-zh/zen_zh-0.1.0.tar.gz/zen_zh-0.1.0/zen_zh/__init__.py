from __future__ import annotations
import os
import sys
from .data import ZEN_LINES  
try:
    import colorama
    colorama.init()  # 在 windows 上需要初始化
    ANSI = True
except Exception:
    ANSI = False

def _colored(text: str, style: str) -> str:
    # 简单的颜色风格映射，可扩展
    if not ANSI:
        return text
    # 使用 colorama 的 Fore / Style 字段（不写具体颜色常量以便可扩展）
    from colorama import Fore, Style
    if style == "title":
        return Style.BRIGHT + Fore.CYAN + text + Style.RESET_ALL
    if style == "line":
        return Fore.GREEN + text + Style.RESET_ALL
    return text

def print_zen():
    # 标题
    title = "The Zen of Python — 中文译文（来自 Tim Peters 的 PEP 20） by hygroupseries"
    print(_colored(title, "title"), file=sys.stdout)
    print("", file=sys.stdout)
    for i, line in enumerate(ZEN_LINES, 1):
        print(_colored(f"{i:2d}. {line}", "line"), file=sys.stdout)

# 自动打印（除非设置了环境变量或在交互式 'python -c' 中被隐藏）
if not os.environ.get("ZEN_ZH_SILENT"):
    try:
        # 仅在顶级导入时打印（import 多次不会重复）
        print_zen()
    except Exception:
        # 避免在导入时抛异常打断使用者
        pass

# 继续向外暴露原始数据（如果用户想程序化使用）
__all__ = ["ZEN_LINES", "print_zen"]