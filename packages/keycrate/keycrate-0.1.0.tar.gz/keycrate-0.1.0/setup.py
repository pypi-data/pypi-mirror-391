from setuptools import setup, find_packages

setup(
    name="keycrate",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.0.0",
        "hwid>=0.1.0",
    ],
    python_requires=">=3.8",
    description="Simple Keycrate license authentication SDK",
    author="keycrate",
    url="https://github.com/keycrate/keycrate-sdk/sdks/python",
)
