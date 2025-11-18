#!/usr/bin/env python3
"""Isaac Gym 安装管理器"""

import os
import subprocess
import sys
import importlib

class IsaacGymInstaller:
    """管理 Isaac Gym 的安装"""
    
    @classmethod
    def get_isaacgym_path(cls):
        """获取 Isaac Gym 源码路径"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        isaacgym_path = os.path.join(current_dir, "..", "..", "third_party", "isaacgym")
        return os.path.abspath(isaacgym_path)
    
    @classmethod
    def is_isaacgym_installed(cls):
        """检查 Isaac Gym 是否已安装"""
        try:
            import isaacgym
            return True, "已安装"
        except ImportError as e:
            return False, f"未安装: {e}"
    
    @classmethod
    def install_isaacgym(cls):
        """安装 Isaac Gym"""
        isaacgym_path = cls.get_isaacgym_path()
        python_dir = os.path.join(isaacgym_path, "python")
        
        if not os.path.exists(python_dir):
            return False, f"Isaac Gym python 目录不存在: {python_dir}"
        
        if not os.path.exists(os.path.join(python_dir, "setup.py")):
            return False, f"Isaac Gym setup.py 不存在"
        
        print(f"📦 正在安装 Isaac Gym 从: {python_dir}")
        
        try:
            # 运行 pip install -e .
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", python_dir],
                capture_output=True,
                text=True,
                cwd=python_dir
            )
            
            if result.returncode == 0:
                return True, "安装成功"
            else:
                return False, f"安装失败: {result.stderr}"
                
        except Exception as e:
            return False, f"安装异常: {e}"
    
    @classmethod
    def check_and_install(cls):
        """检查并在需要时安装 Isaac Gym"""
        installed, message = cls.is_isaacgym_installed()
        
        if installed:
            print("✅ Isaac Gym 已安装")
            return True
        
        print("❌ Isaac Gym 未安装")
        print("🚀 尝试自动安装...")
        
        success, install_message = cls.install_isaacgym()
        if success:
            print("✅ Isaac Gym 安装成功")
            return True
        else:
            print(f"❌ Isaac Gym 安装失败: {install_message}")
            print("\n💡 请手动安装 Isaac Gym:")
            print(f"   1. 进入目录: {cls.get_isaacgym_path()}/python")
            print("   2. 运行: pip install -e .")
            return False