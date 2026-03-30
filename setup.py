from setuptools import setup

setup(
    name='insurance-claims-api',
    version='1.0',
    packages=['src'],
    install_requires=[
        'fastapi',
        'uvicorn',
        'pydantic',
        'pytest',
        'pytest-asyncio',
        'httpx',
        'coverage',
        'pytest-cov'
    ]
)