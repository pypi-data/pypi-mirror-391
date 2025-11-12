from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="causal_time_series",
    version="0.0.2",
    description='Python library for causal time series modeling',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nikosga/cts/tree/main',
    author='Nick Gavriil',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        "matplotlib",
        "pandas",
        "numpy",
        "scikit-learn"
    ],
    python_requires=">=3.7",
)