from setuptools import find_packages, setup

long_description = ""
with open("README.md") as ifp:
    long_description = ifp.read()

setup(
    name="humbug",
    version="0.3.2",
    packages=find_packages(),
    package_data={"humbug": ["py.typed"]},
    install_requires=["requests", "dataclasses; python_version=='3.6'"],
    extras_require={
        "dev": [
            "black",
            "mypy",
            "wheel",
            "types-pkg_resources",
            "types-requests",
            "types-dataclasses",
            "types-psutil",
        ],
        "distribute": ["setuptools", "twine", "wheel"],
        "profile": ["psutil", "GPUtil", "types-psutil"],
    },
    description="Humbug: Do you build developer tools? Humbug helps you know your users.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Bugout.dev",
    author_email="engineering@bugout.dev",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries",
    ],
    url="https://github.com/bugout-dev/humbug",
)
