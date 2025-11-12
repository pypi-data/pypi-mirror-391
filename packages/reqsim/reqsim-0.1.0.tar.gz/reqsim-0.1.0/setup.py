from setuptools import setup, find_packages

setup(
    name="reqsim",
    version="0.1.0",
    author="Baning Philip Amponsah",
    author_email="baningphilip@gmail.com",
    description="A lightweight HTTP request simulator and API benchmark tool",
    packages=find_packages(),
    install_requires=["aiohttp"],
    entry_points={
        "console_scripts": [
            "reqsim=reqsim.cli:main",
        ],
    },
    python_requires=">=3.8",
)
