from setuptools import setup, find_packages  # type: ignore

with open(
    "README.md",
    "r",
) as f:
    long_description = f.read()

setup(
    name="goodfractions",
    version="0.0.1",
    description="Improvement of the fractions module from the standard library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="josek98",
    author_email="josemmsscc98@gmail.com",
    url="https://github.com/josek98/goodfractions",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[],
    extras_require={"dev": ["pytest>=7.0", "twine>=4.0.2"]},
)
