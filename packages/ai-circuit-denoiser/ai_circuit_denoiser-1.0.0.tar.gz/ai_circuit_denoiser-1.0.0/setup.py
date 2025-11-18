from setuptools import setup, find_packages
import os

# 读取README内容
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取现有的requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-circuit-denoiser",
    version="1.0.0",
    author="Michael Zhou",
    author_email="your-email@example.com",
    description="AI-powered circuit signal denoising tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/michaelforex277/AI-Circuit-Denoiser",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    package_data={
        "circuit_denoiser": [
            "widgets/*.py",
        ]
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "circuit-denoiser=circuit_denoiser.main:main",
        ],
    },
    keywords="signal-processing, circuit, denoising, ai, deep-learning",
)
