from setuptools import setup, find_packages
from pathlib import Path

# تنظیمات پایه
VERSION = "2.0.0"
PACKAGE_NAME = "ancientlinesoftheworld"
MODULE_NAME = "ancient"

# خواندن توضیحات
root = Path(__file__).parent
long_description = (root / "README.md").read_text(encoding="utf-8")

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description="تبدیل متن به خطوط باستانی مانند پهلوی و میخی",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Amir Hossein Khazaei",
    author_email="amirhossinpython03@gmail.com",
    url="https://github.com/amirhossinpython/ancientlinesoftheworld-",
    license="MIT",
    
    # تنظیمات پکیج
    packages=find_packages(include=[MODULE_NAME, f"{MODULE_NAME}.*"]),
    package_dir={"": "."},
    package_data={
        MODULE_NAME: ["data/*.json"]
    },
    
    # وابستگی‌ها
    install_requires=[
        "deep-translator>=1.11.0",
    ],
    
    # تنظیمات پایتون
    python_requires=">=3.8",
    
    # طبقه‌بندی‌های صحیح
    classifiers=[
        "Development Status :: 4 - Beta",
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
    
    keywords="ancient scripts persian pahlavi cuneiform",
    
    # اسکریپت کنسولی (اختیاری)
    entry_points={
        "console_scripts": [
            "ancient-convert=ancient.cli:main",
        ],
    },
    
    # تنظیمات توسعه
    extras_require={
        "dev": [
            "pytest>=7.0",
            "twine>=4.0",
        ],
    }
)