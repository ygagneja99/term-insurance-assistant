from setuptools import setup, find_packages

setup(
    name="term-insurance-assistant",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "flask",
        "requests",
        "python-dotenv",
        "openai"
    ],
    author="Yuvraj",
    description="A term insurance assistant chatbot",
    python_requires=">=3.8",
) 