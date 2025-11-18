from setuptools import setup, find_packages

setup(
    name="hafoo_trade_sdk_test",
    version="1.0.6",
    author="KuBoy",
    author_email="1757378111@qq.com",
    description="Order Service SDK for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/KuBoy/hafoo_trade_sdk_test",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "cryptography>=46.0.1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    
)