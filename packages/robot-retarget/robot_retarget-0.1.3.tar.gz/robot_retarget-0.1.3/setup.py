from setuptools import setup, find_packages
import os

# 使用 pipreqs 生成的精确版本
STANDARD_DEPENDENCIES = [
    "easydict==1.13",
    "hydra-core==1.3.2", 
    "imageio==2.37.2",
    "joblib==1.5.2",
    "loop-rate-limiters==1.2.0",
    "lxml==6.0.2",
    "matplotlib>=3.7,<3.10",
    "mink==0.0.13",
    "numpy>=1.21,<3.0",
    "omegaconf==2.3.0",
    "open3d>=0.17",
    "PyYAML==6.0.3",
    "rich==14.2.0",
    "scipy>=1.8,<1.12",
    "smplx==0.1.28",
    "tensordict==0.10.0",
    "torch>=2.0,<2.9",
    "tqdm==4.67.1",
    "setuptools==80.9.0",  # 构建工具，通常不需要但保留
]

setup(
    name="robot-retarget",
    version="0.1.3",
    author="dongyi",
    author_email="3308449881@qq.com",
    description="Advanced robot motion retargeting system for humanoid robots",
    long_description=open("README.md").read() if os.path.exists("README.md") else "Robot motion retargeting project with SMPL and MuJoCo support",
    long_description_content_type="text/markdown",
    url="https://github.com/dongyi/robot-retarget",
    
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    
    python_requires=">=3.8,<3.11",
    install_requires=STANDARD_DEPENDENCIES,
    
    # 可选依赖组
    extras_require={
        'simulation': [
            "mujoco==3.3.7",
        ],
        'dev': [
            "pytest>=6.0",
            "black>=22.0", 
            "flake8>=4.0",
        ],
        'all': STANDARD_DEPENDENCIES + ["mujoco==3.3.7"],
    },
    
    # 入口点
    entry_points={
        'console_scripts': [
            'robot-retarget=retarget.__main__:main',
            'retarget-check-deps=retarget.utils.dependency_checker:main',
            'retarget-install-isaacgym=retarget.install_isaacgym:main', 
        ],
    },
    
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent", 
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Robotics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    
    keywords=["robot", "retargeting", "motion", "smpl", "mujoco", "humanoid"],
    include_package_data=True,
)