from setuptools import setup, find_packages
from pathlib import Path

# Read README.md for PyPI long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="memoria-tool",
    version="0.1.9",
    author="IM_GJ",
    author_email="imgj.3195@.com",  
    description="Local-first digital memory management library with semantic AI and privacy controls.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/imGJUser1/memoria-tool",  
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "faiss-cpu",
        "sentence-transformers",
        "cryptography",
        "sqlalchemy",
        "watchdog",
        "pandas",
        "numpy",
        "browserhistory",
        "transformers",
        "scikit-learn",
        "nltk",
    ],
    extras_require={
        "cloud": [
            "google-generativeai",
            "openai",
            "anthropic",
            "slack-sdk",
            "google-api-python-client",
            "google-auth-oauthlib",
            "google-auth",
            "notion-client",
            "whatsapp-python",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security :: Cryptography",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="memory ai semantic-search privacy faiss transformers",
)
