from setuptools import setup, find_packages

setup(
    name="tunnel-client",
    version="1.0.0",
    description="Tunnel client for tunnel.tunneloon.online",
    packages=find_packages(include=["client*", "shared*"]),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
        "websockets>=12.0",
        "httpx>=0.25.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "sqlalchemy>=2.0.0",
        "aiosqlite>=0.19.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "tunnel-client=client.client:cli",
        ],
    },
    python_requires=">=3.10",
)

