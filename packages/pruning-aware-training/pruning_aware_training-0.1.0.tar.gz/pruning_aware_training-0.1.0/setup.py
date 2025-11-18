from setuptools import setup, find_packages
setup(
    name="pruning-aware-training",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["torch>=1.10", "torchvision", "numpy"],
    author="Avraham Raviv",
    description="A framework for structured channel pruning in PyTorch",
    license="MIT",
    python_requires=">=3.8",
)
