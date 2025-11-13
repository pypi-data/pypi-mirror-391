"""
Robot Retarget - 高级机器人运动重定向系统
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# 显式导入子模块，这样它们可以通过 retarget.utils 访问
from . import utils
from . import third_party
from . import install_isaacgym

# 导出主要功能
__all__ = ['utils', 'third_party', 'install_isaacgym']