from setuptools import setup, find_packages

setup(
    name="lpsolver",
    version="0.1.2",
    description="A Python Linear Programming Solver with Xpress-like syntax",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="nitesh.singh1423.nl@gmail.com",
    packages=find_packages(),
    install_requires=["numpy>=1.20.0"],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)