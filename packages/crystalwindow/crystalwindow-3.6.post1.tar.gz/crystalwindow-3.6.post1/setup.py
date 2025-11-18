from setuptools import setup, find_packages

setup(
    name="crystalwindow",
    version="3.6.post1",  # Force metadata refresh
    packages=find_packages(include=["crystalwindow", "crystalwindow.*"]),
    include_package_data=True,

    author="CrystalBallyHereXD",
    author_email="mavilla.519@gmail.com",

    description="A Tkinter powered window + GUI toolkit made by Crystal (MEEEEEE)! Easier apps, smoother UI and all-in-one helpers!",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",

    python_requires=">=3.6",

    url="https://pypi.org/project/crystalwindow/",  # 🔥 REQUIRED FOR SEARCH ENGINES

    project_urls={
        "Homepage": "https://pypi.org/project/crystalwindow/",
        "PiWheels": "https://www.piwheels.org/project/crystalwindow/",
        "Documentation": "https://pypi.org/project/crystalwindow/",
    },

    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: User Interfaces",
        "License :: OSI Approved :: MIT License",
    ],

    keywords="tkinter gui window toolkit easy crystalwindow crystal cw player moveable easygui python py file math gravity hex color",
)
