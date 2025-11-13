from setuptools import setup, find_packages

setup(
    name="crystalwindow",  # name users install with pip
    version="3.5",  # follow semver: major.minor.patch
    packages=find_packages(include=["crystalwindow", "crystalwindow.*"]),
    include_package_data=True,
    author="CrystalBallyHereXD",
    author_email="mavilla.519@gmail.com",
    description=(
        "A simple window and GUI helper built on Tkinter — the easier way "
        "to make apps! Made by Crystal (mee)!!"
    ),
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",

    python_requires=">=3.6",  # Tkinter works best with modern Python versions

    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: User Interfaces",
        "License :: OSI Approved :: MIT License",  # if you have one
    ],
    keywords="tkinter gui window easy wrapper crystalwindow crystal cw",
)
