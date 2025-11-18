from setuptools import setup, find_packages
from pathlib import Path

VERSION = "2.1.0"
PACKAGE_NAME = "ancientlinesoftheworld"
MODULE_NAME = "ancient"

root = Path(__file__).parent
long_description = (root / "README.md").read_text(encoding="utf-8")

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description="Convert Persian and English text to ancient scripts like Pahlavi, Avestan, Cuneiform, and Manichaean.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Amir Hossein Khazaei",
    author_email="amirhossinpython03@gmail.com",
    url="https://github.com/amirhossinpython/ancientlinesoftheworld-",
    license="MIT",

    packages=find_packages(include=[MODULE_NAME, f"{MODULE_NAME}.*"]),
    include_package_data=True,
    package_data={
        MODULE_NAME: [
            "background.jpg",
            "NotoSansCuneiform-Regular.ttf",
            "data/*.json"
        ],
    },

    install_requires=[
        "deep-translator>=1.11.0",
        "Pillow>=9.0.0"
    ],

    python_requires=">=3.8",

    classifiers=[
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Education",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Text Processing :: Linguistic",
    "Topic :: Software Development :: Libraries :: Python Modules",
],


    entry_points={
        "console_scripts": [
            "ancient-convert=ancient.cli:main",
        ],
    }
)
