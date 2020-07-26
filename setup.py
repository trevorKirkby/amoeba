
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="amoeba",
    version="0.0.1",
    author="Trevor & David Kirkby",
    author_email="trevor.p.kirkby@gmail.com",
    description="A topical game",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/trevorKirkby/amoeba",
    packages=setuptools.find_packages(),
    install_requires=["pyyaml"],
    include_package_data=True,
    entry_points={
        'console_scripts': ['amoeba=amoeba.main:main']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
