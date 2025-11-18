from setuptools import setup, find_packages

setup(
    name="pwq_qr_gen_4",
    version="4.0.4",
    author="pawlexcode95",
    description="A fully customizable QR code generator with support for colors, logos, and links.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license_files=["LICENSE"],
    python_requires=">=3.11",
    packages=find_packages(where="."),
    install_requires=[
        "pillow",
    ],
    url="https://github.com/pawlexcode95/PWQ-QR-Gen-4-A-Fully-Customizable-QR-Code-Generator",
    project_urls={
        "Homepage": "https://github.com/pawlexcode95/PWQ-QR-Gen-4-A-Fully-Customizable-QR-Code-Generator",
        "Script": "https://github.com/pawlexcode95/PWQ-QR-Gen-4-A-Fully-Customizable-QR-Code-Generator/blob/main/PWQ_QR_Gen_4.py",
        "Issues": "https://github.com/pawlexcode95/PWQ-QR-Gen-4-A-Fully-Customizable-QR-Code-Generator/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
