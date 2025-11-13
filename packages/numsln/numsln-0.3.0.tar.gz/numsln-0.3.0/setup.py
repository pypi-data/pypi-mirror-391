from setuptools import setup, find_packages

setup(
    name="numsln",
    version="0.3.0",
    author="EZ Sharaf",
    author_email="imsharaf10@gmail.com",
    description="Numerical methods library ",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "seaborn",
        "tqdm",
        "sympy"
    ],
    python_requires=">=3.8",
)