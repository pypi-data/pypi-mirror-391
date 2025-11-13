#!/usr/bin/env python3
"""Isaac Gym 安装命令"""

import sys
import os

# 添加 src 到路径以便导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from retarget.utils.isaacgym_installer import IsaacGymInstaller

def main():
    print("🚀 Isaac Gym 安装工具")
    print("=" * 50)
    
    success = IsaacGymInstaller.check_and_install()
    
    if success:
        print("\n✅ Isaac Gym 安装完成！")
        sys.exit(0)
    else:
        print("\n❌ Isaac Gym 安装失败，请手动安装")
        sys.exit(1)

if __name__ == "__main__":
    main()