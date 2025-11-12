from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="nexshell",
    version="1.0.0",
    author="NexShell Team",
    author_email="contact@nexshell.dev",
    description="A beautiful and feature-rich AI-powered CLI chatbot using Google Gemini",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/nexshell",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Communications :: Chat",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "nexshell=nexshell.cli:main",
        ],
    },
    include_package_data=True,
    keywords="chatbot ai gemini cli assistant terminal conversational-ai",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/nexshell/issues",
        "Source": "https://github.com/yourusername/nexshell",
        "Documentation": "https://github.com/yourusername/nexshell#readme",
    },
)
