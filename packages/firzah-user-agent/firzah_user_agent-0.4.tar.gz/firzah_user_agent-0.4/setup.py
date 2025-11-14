from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
import sys

# Definisi ekstensi C++
ext_modules = [
    Extension(
        name="firzah_user_agent.user_agent",  # output: firzah_user_agent/user_agent.so
        sources=["firzah_user_agent/user_agent.cpp"],
        language="c++",
        extra_compile_args=["-std=c++17"],  # bisa diganti sesuai kebutuhan
    )
]

setup(
    name="firzah_user_agent",
    version="0.4",
    packages=find_packages(),
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    install_requires=[
        # dependencies Python (kalau ada)
    ],
)