from setuptools import setup, find_packages

setup(
    name="nltk_com_fsd",
    version="0.1.2",
    description="Demo package with greet function and text file",
    author="Your Name",
    author_email="you@example.com",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "nltk_com_fsd": ["*.txt"],
    },
    python_requires=">=3.7",
)
