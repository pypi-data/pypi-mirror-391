from setuptools import setup, find_packages

setup(
    name="crudini_simple",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points="""
        [console_scripts]
        crudini_simple=crudini_simple.cli:main
    """,
    author="hjl",
    author_email="hjl@hjl.com",
    description="A CLI tool for managing INI files.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/hujianli94/crudini_simple",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
)
