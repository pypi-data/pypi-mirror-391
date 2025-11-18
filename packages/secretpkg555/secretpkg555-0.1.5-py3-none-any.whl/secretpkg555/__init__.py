__version__ = "0.1.5"
__author__ = "None555"

# 导入 _patch 模块时会自动应用补丁（用户无感知）
from . import _patch

# 导出核心模块供用户使用
from . import core_logic

__all__ = ['core_logic']