from setuptools import setup, find_packages

setup(
    name="stocklens-sdk",  # PyPI name (must be unique)
    version="1.0.1",
    author="Karthik R S",
    author_email="karthikrajesh9010@gmail.com",
    description="AI-Powered Stock Sentiment and Trend Analysis SDK",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/karthikrajesh10/stocklens_sdk",  # (optional but recommended)
    packages=find_packages(),
    install_requires=[
        "textblob",
        "requests",
        "flask",
        "flask-cors",
        "gtts",
        "pandas",
        "yfinance",
        "scikit-learn"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
