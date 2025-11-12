from setuptools import setup, find_packages

setup(
    name="eduml",  # Name on PyPI (should be all lowercase)
    version="1.0.0",
    author="Varnit Patel",
    author_email="varnitpatel001@gmail.com",
    description="A learning-focused, educational ML toolkit with clean implementations and explainability.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/varnitpatel001/eduml",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "seaborn",
        "scikit-learn",
        "textwrap3",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Education",
        "Development Status :: 4 - Beta"
    ],
    license="MIT",
    python_requires=">=3.8",
)
