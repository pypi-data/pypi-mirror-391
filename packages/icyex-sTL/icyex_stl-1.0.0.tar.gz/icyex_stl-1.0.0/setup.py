from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="icyex-sTL",
    version="2.09.169",
    author="IcyEx",
    author_email="m.sajjadd89@gmail.com",
    description="Telegram user information extractor with risk analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hunter_sfcb/icyex-sTL",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "python-telegram-bot>=20.0",
        "requests>=2.25.0",
    ],
    keywords="telegram user info extractor risk analysis",
)

