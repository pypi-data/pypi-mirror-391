from setuptools import setup, find_packages

setup(
    name="gr-mytestmodule",
    version="0.1.0",
    description="Un modulo GNU Radio di esempio scritto in Python",
    author="Pietro Rocchio",
    #author_email="tuaemail@example.com",
    license="GPLv3",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    install_requires=[],
    include_package_data=True,
    entry_points={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
    ],
)
