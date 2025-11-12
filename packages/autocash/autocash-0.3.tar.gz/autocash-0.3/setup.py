from setuptools import setup, find_packages

setup(
    name="autocash",
    version="0.3",
    author="KingZero",
    author_email="KingZero@darksidehost.com",
    description="AutoCash payments gateway lib",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/LSEGITHUB/VFCashPython",
    packages=find_packages(),
    install_requires=[
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    license="MIT"
)
