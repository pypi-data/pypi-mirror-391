from setuptools import setup, find_packages
setup(
    name="Watanpy1",
    version="22",
    author="watan",
    author_email="fuckyou@gmail.com",
    description="null",
    packages=find_packages(),
    install_requires=[
        "user_agent",
        "requests",
        "MedoSigner",
        "pycryptodome"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)