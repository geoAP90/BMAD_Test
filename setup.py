from setuptools import setup

setup(
    name="insurance-claims-api",
    version="1.0.0",
    packages=["src"],
    install_requires=["fastapi", "uvicorn", "pydantic"],
    author="Your Name",
    author_email="your@email.com"
)