from setuptools import setup, find_packages

setup(
    name="PySaveUtils",
    version="0.1.1",
    author="Dead0000012",
    author_email="dead0000012@gmail.com",
    description="Набор утилит для генерации случайных данных и проверки пользовательского ввода.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dead0000012/PySaveUtils",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
