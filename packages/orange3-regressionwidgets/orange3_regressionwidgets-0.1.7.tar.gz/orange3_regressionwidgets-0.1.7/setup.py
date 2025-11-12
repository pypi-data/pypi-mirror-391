from pathlib import Path
from setuptools import setup, find_namespace_packages

README_PATH = Path(__file__).parent / "README.md"
long_description = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""

setup(
    name="orange3-regressionwidgets",
    version="0.1.7",
    description="Orange add-on with regression summary and backward elimination widgets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Laurent Pauwels",
    author_email="laurent.pauwels@nyu.edu",
    url="https://github.com/laurentpauwels/orange3-regressionwidgets",
    project_urls={
        "Source": "https://github.com/laurentpauwels/orange3-regressionwidgets",
        "Bug Tracker": "https://github.com/laurentpauwels/orange3-regressionwidgets/issues",
    },
    license="MIT",
    packages=find_namespace_packages(include=["orangecontrib.*"]),
    namespace_packages=["orangecontrib"],
    include_package_data=True,
    package_data={
        "orangecontrib.regressionsummary.widgets": ["icons/*.svg", "widgets.json"],
    },
    zip_safe=False,
    entry_points={
        "orange.widgets": (
            "Regression = orangecontrib.regressionsummary.widgets",
        ),
        "orange.canvas.help": (
            "html-index = orangecontrib.regressionsummary.widgets:WIDGET_HELP_PATH",
        ),
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "Orange3>=3.30.0",
        "statsmodels>=0.13.0",
        "pandas>=1.3.0",
        "numpy",
        "PyQt5>=5.15.0",
    ],
    python_requires=">=3.8",
)
