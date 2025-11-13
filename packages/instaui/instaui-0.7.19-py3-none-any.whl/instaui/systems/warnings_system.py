import warnings
import sys
from typing import Type


RED = "\033[91m"
RESET = "\033[0m"

# 记录已警告过的消息（防止重复）
_warned_messages = set()


def _colored_showwarning(message, category, filename, lineno, file=None, line=None):
    """统一彩色输出函数"""
    if file is None:
        file = sys.stderr
    print(f"{RED}{category.__name__}:{message} {RESET}({filename}:{lineno})", file=file)


def _warn_colored(message: str, category: Type[Warning], stacklevel: int):
    """内部方法：执行彩色警告输出"""
    original_showwarning = warnings.showwarning
    warnings.showwarning = _colored_showwarning
    try:
        warnings.warn(message, category=category, stacklevel=stacklevel)
    finally:
        warnings.showwarning = original_showwarning


def warn_once(message: str, category: Type[Warning] = UserWarning, stacklevel: int = 2):
    """
    打印红色警告（只打印一次）
    """
    if message in _warned_messages:
        return
    _warned_messages.add(message)
    _warn_colored(message, category, stacklevel)


def warn_always(
    message: str, category: Type[Warning] = UserWarning, stacklevel: int = 2
):
    """
    打印红色警告（每次调用都打印）
    """
    _warn_colored(message, category, stacklevel)
