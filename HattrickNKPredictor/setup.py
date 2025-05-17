from setuptools import setup, find_packages

setup(
    name="HattrickNKPredictor",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "selenium>=4.0.0",
        "beautifulsoup4>=4.0.0",
        "pandas>=1.0.0",
        "requests>=2.0.0",
    ],
    test_suite="HattrickNKPredictor.tests",
    entry_points={
        "console_scripts": [
            "ht-prediction=HattrickNKPredictor.main:main",
        ],
    },
    author="Veres Peter",
    description="Hattrick prediction game manager",
    python_requires=">=3.10",
)