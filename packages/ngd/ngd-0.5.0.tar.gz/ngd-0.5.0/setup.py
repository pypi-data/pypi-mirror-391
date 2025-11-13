from pathlib import Path

from setuptools import setup, find_packages


README = Path(__file__).parent / "README.md"

setup(
    name="ngd",
    version="0.5.0",
    packages=find_packages(),
    install_requires=[
        "flask>=2.0.0",
        "requests>=2.25.0"
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive programming tutorials package with 25 essential programs",
    long_description=README.read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ngd",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Education",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: System :: Systems Administration",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Networking",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.7",
    keywords="programming, tutorials, git, flask, docker, kubernetes, jenkins, android, database, web-development, devops",
) 