from setuptools import setup, find_packages

setup(
    name="chatsee-ai",  # The name you will use to pip install
    version="0.2.0",  # <-- CHANGE 1: Updated version to 0.1.3
    author="Chatsee Team",
    author_email="kunal.golani@isynergytech.com",
    description="A Python SDK for Chatsee AI.",
    
    # This automatically finds your 'chatsee' package folder
    packages=find_packages(),
    
    # This lists the other libraries your SDK depends on
    install_requires=[
        "requests>=2.31.0",
    ],
    
    # Other classifiers
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", # Choose a license
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)