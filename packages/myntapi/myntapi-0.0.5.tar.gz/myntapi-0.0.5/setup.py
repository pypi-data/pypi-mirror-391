from setuptools import setup, find_packages

with open("README.md", "r",encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="myntapi",
    version="0.0.5",
    author="zebu",
    author_email="it@zebuetrade.com",
    description="This PIP package used for Algo traders",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/Zebu-Dev/Mynt-PY-Api-Package.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'NorenRestApiPy>=0.0.22',
        'requests>=2.31.0',
        'websocket_client>=1.6.0',
        'pandas>=1.6.0',
        'pyyaml>=6.0'
    ],
)
