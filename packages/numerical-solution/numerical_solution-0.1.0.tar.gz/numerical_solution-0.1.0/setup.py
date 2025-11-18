from setuptools import setup, find_packages

setup(
    name="numerical_solution",
    version="0.1.0",
    author="Eshayat Zamil Sharaf",
    author_email="imsharaf10@gmail.com",
    description="Numerical Methods library ",
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