from setuptools import setup, find_packages

setup(
    name="ChronoFidelius",  # The name of your package on PyPI
    version="1.1.2",        # Version number of your package
    description="A Python library for for plaintext encryption using homophonic substitution and historical character frequencies.",
    long_description=open("README.md").read(),  # Read the contents of README.md
    long_description_content_type="text/markdown",  # Specify Markdown format for README
    author="Micaella Bruton",  # Replace with your name
    author_email="micaella.bruton@ling.su.se",  # Replace with your email
    url="https://github.com/mbruton0426/ChronoFidelius",  # Replace with your GitHub repo URL
    license="Apache License 2.0",  # License for your package
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Minimum Python version
    packages=find_packages(),  # Automatically find all packages in your project
    install_requires=[],  # List of dependencies (empty for now if no external libraries are needed)
    include_package_data=True,  # Include files specified in MANIFEST.in
)
