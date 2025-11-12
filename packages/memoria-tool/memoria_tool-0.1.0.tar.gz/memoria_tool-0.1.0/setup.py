from setuptools import setup, find_packages

setup(
    name="memoria-tool",
    version="0.1.0",
    author="IM_GJ",
    description="Local-first digital memory management library",
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
        "nltk"
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
            "whatsapp-python"
        ],
    },
    python_requires=">=3.9",
    license="MIT",
    url="https://github.com/ImGJUser1/memoria-tool",  # optional
)
