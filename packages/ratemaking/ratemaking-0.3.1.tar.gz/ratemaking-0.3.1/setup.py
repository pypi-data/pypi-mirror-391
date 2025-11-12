from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ratemaking",
    version="0.3.1",
    author="Hugo Latendresse",
    author_email="hugolatendresse@gmail.com",  # Update this with your actual email
    description="A comprehensive Python library for P&C actuarial ratemaking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/little-croissant/ratemaking",  # Update with your GitHub URL
    project_urls={
        "Bug Reports": "https://github.com/little-croissant/ratemaking/issues",
        "Source": "https://github.com/little-croissant/ratemaking",
        "Documentation": "https://github.com/little-croissant/ratemaking#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="actuarial ratemaking credibility complements trending insurance P&C casualty property",
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.0.0",
            "numpy>=1.20.0",
            "pandas>=1.3.0",
            "pyperclip>=1.8.0",
            "pyautogui>=0.9.0",
            "watchdog>=2.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black",
            "flake8",
            "mypy",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
