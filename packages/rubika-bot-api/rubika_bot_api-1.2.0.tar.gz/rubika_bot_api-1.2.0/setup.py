from setuptools import setup
from pathlib import Path

here = Path(__file__).parent
readme = (here / "README.md").read_text(encoding="utf-8") if (here / "README.md").exists() else ""

setup(
    name="rubika-bot-api",
    version="1.2.0",
    description="A powerful asynchronous/synchronous library for Rubika Bot API with a focus on high performance.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="rubika api bot",
    author_email="0x01101101@proton.me",
    url="https://github.com/rubika-bot-api/rubika_bot_api",
    license="MIT",
    packages=["rubika_bot_api"],
    python_requires=">=3.7",
    install_requires=[
        "aiohttp>=3.9.0",
        "aiofiles>=23.2.1",
        "ujson>=5.8.0",
        "orjson>=3.9.10",
        "aiodns>=3.1.1",
        "asyncio-throttle>=1.0.2",
        "aiohttp-socks>=0.8.4",
        "cryptography>=41.0.5",
        "brotli>=1.1.0",
        "tqdm-4.67.1",
        "filetype-1.2.0",
        "requests",
        "pytz",
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Topic :: Internet",
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
    ],
)
