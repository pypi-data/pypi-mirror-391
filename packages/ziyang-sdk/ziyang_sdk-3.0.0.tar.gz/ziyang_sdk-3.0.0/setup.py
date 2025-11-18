from pathlib import Path

from setuptools import find_packages, setup

BASE_DIR = Path(__file__).parent.resolve()
README = (BASE_DIR / "README.md").read_text(encoding="utf-8") if (
    BASE_DIR / "README.md"
).exists() else ""

setup(
    name="ziyang-sdk",
    version="3.0.0",
    description="紫阳智库v3算力测试SDK",
    long_description=README,
    long_description_content_type="text/markdown",
    author="紫阳智库团队",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "matplotlib>=3.5.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ziyang-benchmark=ziyang.cli:main",
        ],
    },
)