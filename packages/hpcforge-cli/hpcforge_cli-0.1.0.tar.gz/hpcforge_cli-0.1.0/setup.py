from setuptools import setup, find_packages

setup(
    name="hpcforge-cli",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "questionary",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "hpcforge=hpctools.cli:cli",
        ],
    },
    author="Diogo Silva",
    author_email="diogo.coelho.silva@gmail.com",
    description="A lightweight CLI toolkit for HPC automation (Makefiles, SLURM jobs, templates)",
    license="MIT",
    python_requires=">=3.8",
    url="https://github.com/diogocsilva12/hpctools",
)