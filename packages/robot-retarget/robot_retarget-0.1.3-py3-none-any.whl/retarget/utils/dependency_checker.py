#!/usr/bin/env python3
"""依赖检查工具"""

import importlib
import sys
from .isaacgym_installer import IsaacGymInstaller

class DependencyChecker:
    """检查和管理项目依赖"""
    
    DEPENDENCIES = {
        # 标准依赖
        "easydict": {"type": "standard", "description": "简易字典操作"},
        "hydra": {"type": "standard", "description": "配置管理", "package": "hydra-core"},
        "imageio": {"type": "standard", "description": "图像IO"},
        "joblib": {"type": "standard", "description": "并行计算"},
        "loop_rate_limiters": {"type": "standard", "description": "循环速率限制", "package": "loop-rate-limiters"},
        "lxml": {"type": "standard", "description": "XML/HTML处理"},
        "matplotlib": {"type": "standard", "description": "绘图库"},
        "mink": {"type": "standard", "description": "3D数据处理"},
        "numpy": {"type": "standard", "description": "数值计算"},
        "omegaconf": {"type": "standard", "description": "配置管理"},
        "open3d": {"type": "standard", "description": "3D数据处理"},
        "yaml": {"type": "standard", "description": "YAML处理", "package": "PyYAML"},
        "rich": {"type": "standard", "description": "终端美化"},
        "scipy": {"type": "standard", "description": "科学计算"},
        "smplx": {"type": "standard", "description": "SMPL人体模型"},
        "tensordict": {"type": "standard", "description": "张量字典"},
        "torch": {"type": "standard", "description": "深度学习框架"},
        "tqdm": {"type": "standard", "description": "进度条"},
        
        # 特殊依赖
        "mujoco": {
            "type": "special", 
            "description": "物理仿真引擎",
            "install_hint": "pip install mujoco",
            "notes": "需要接受许可证: https://mujoco.org/download",
            "optional": True
        },
        "isaacgym": {
            "type": "special",
            "description": "NVIDIA Isaac Gym",
            "install_hint": "使用: retarget-install-isaacgym",
            "notes": "包含在包内，需要源码安装",
            "optional": False
        },
    }
    
    @classmethod
    def check_dependency(cls, name):
        """检查单个依赖"""
        if name not in cls.DEPENDENCIES:
            return False, f"未知依赖: {name}"
        
        info = cls.DEPENDENCIES[name]
        
        # 特殊处理 isaacgym
        if name == "isaacgym":
            installed, message = IsaacGymInstaller.is_isaacgym_installed()
            if installed:
                return True, "已安装 (源码方式)"
            else:
                return False, "未安装，需要源码安装"
        
        # 实际检查的包名
        package_name = info.get("package", name)
        
        try:
            __import__(package_name)
            return True, f"{info['description']}"
        except ImportError:
            if info.get("optional", False):
                return False, f"可选依赖: {info['description']}"
            else:
                return False, f"必需依赖: {info['description']}"
    
    @classmethod
    def generate_report(cls):
        """生成依赖报告"""
        print("🤖 Robot Retarget - 依赖状态报告")
        print("=" * 60)
        
        required_missing = []
        optional_missing = []
        
        for name in cls.DEPENDENCIES:
            available, message = cls.check_dependency(name)
            info = cls.DEPENDENCIES[name]
            
            status = "✅" if available else "❌"
            if not available and not info.get("optional", False):
                required_missing.append((name, message))
            elif not available:
                optional_missing.append((name, message))
            
            print(f"{status} {name:25} {message}")
        
        print("=" * 60)
        
        # 提供指导
        if required_missing:
            print("\n🚨 缺失的必需依赖:")
            for name, message in required_missing:
                print(f"   - {name}: {message}")
                if name == "isaacgym":
                    print("     💡 运行: retarget-install-isaacgym")
        
        if optional_missing:
            print("\n💡 缺失的可选依赖（某些功能不可用）:")
            for name, message in optional_missing:
                info = cls.DEPENDENCIES[name]
                print(f"   - {name}: {message}")
                if "install_hint" in info:
                    print(f"     安装: {info['install_hint']}")
                if "notes" in info:
                    print(f"     说明: {info['notes']}")
        
        return len(required_missing) == 0

def main():
    """命令行入口"""
    if DependencyChecker.generate_report():
        print("\n🎉 所有必需依赖已就绪！")
        sys.exit(0)
    else:
        print("\n❌ 请安装缺失的必需依赖。")
        sys.exit(1)

if __name__ == "__main__":
    main()