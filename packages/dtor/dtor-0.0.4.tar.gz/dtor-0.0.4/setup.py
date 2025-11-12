from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="dtor",
    version="0.0.4",
    description="A Tor process management library",
    author="Ahmad Yousuf",
    author_email="0xAhmadYousuf@protonmail.com",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8",
    url="https://github.com/QudsLab/dtor",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: Security",
    ],
    keywords="tor, proxy, anonymity, privacy, hidden-service, onion",
    project_urls={
        "Bug Reports": "https://github.com/QudsLab/dtor/issues",
        "Source": "https://github.com/QudsLab/dtor",
    },
)