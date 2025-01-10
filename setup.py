# TernaryChartProject/setup.py
from setuptools import setup, find_packages

setup(
    name="ternarychart",
    version="1.2.0",  # Updated version
    packages=find_packages(),
    install_requires=[
        "mysql-connector-python==8.2.0",
        "protobuf>=4.21.1,<6",
        "streamlit==1.41.1",
        "altair==5.5.0",
        "pandas==2.2.3",
        "numpy==2.2.1",
        "matplotlib==3.10.0",
        "seaborn==0.13.2",
        "gspread>=5.0.0",
        "google-auth>=1.0.0",
        "fpdf==1.7.2",
        "rich==13.9.4",
        "python-ternary==1.0.8",
        # Add other dependencies as needed
    ],
    python_requires=">=3.8",
    description="A project for plotting and analyzing ternary charts",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/Microglyphics/modern-ternary",  # Update with your project URL
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
