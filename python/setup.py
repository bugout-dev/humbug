from setuptools import find_packages, setup

long_description = ""
with open("README.md") as ifp:
    long_description = ifp.read()

setup(
    name="flypaper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        "dev": ["black", "mypy", "wheel"],
        "distribute": ["twine"],
    },
    description="Flypaper: Do you build developer tools? Flypaper helps you know your users.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Bugout.dev",
    author_email="engineering@bugout.dev",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
    ],
    url="https://github.com/bugout-dev/flypaper",
)
