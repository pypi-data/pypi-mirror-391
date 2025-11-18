import pybind11
from setuptools import Extension, setup

# 定义扩展模块
ext_modules = [
    Extension(
        "cpp_module.cpp_extension",  # Python模块的导入路径/名称
        sources=["cpp_module/cpp_extension.cpp"],  # C++源文件
        include_dirs=[
            pybind11.get_include(),  # 获取pybind11的头文件路径
            # 这里可以添加其他C++库的头文件路径，例如 '/usr/local/include'
        ],
        language="c++",
        # 设置C++编译 flags，例如使用C++17标准
        extra_compile_args=["-std=c++17", "-O3"],
    ),
]

setup(
    name="example_cpp",
    version="0.1.0",
    description="A sample Python package with a C++ extension using pybind11",
    author="RL",
    author_email="your.email@example.com",
    packages=["cpp_module"],  # 告诉setuptools包含纯Python包
    ext_modules=ext_modules,  # 指定扩展模块
    install_requires=["pybind11>=3.0"],  # 声明依赖
    setup_requires=["pybind11>=3.0"],  # 构建时依赖
    zip_safe=False,
    python_requires=">=3.14",
)
