

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup_args = setup(
    name="pycltMath",
    version='0.1.0',
    author="Liting Chen",
    author_email="1792700459@qq.com",
    description="一个简单的数学运行包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='Apache License, Version 2.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'pandas',
        'matplotlib',
        'importlib_resources; python_version < "3.9"',
    ],
    classifiers=[
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    include_package_data=True,
)
