from setuptools import setup, find_packages

setup(
    name="igdb-complete-scraper",
    version="1.0.0",
    author="Khashayar",
    description="اسکریپت خودکار برای دریافت اطلاعات کامل بازی‌ها از IGDB",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/khashayardev/igdb-complete-scraper",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "requests>=2.31.0",
    ],
)
