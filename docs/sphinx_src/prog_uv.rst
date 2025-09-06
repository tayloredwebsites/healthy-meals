UV - Ffast Python Package and Project Manager
=============================================


Note: we are no longer using /requirements.txt to keep our dependencies up to date.  We are using pyproject.toml with `UV <https://docs.astral.sh/uv/>`_, which provides excellent [features](https://docs.astral.sh/uv/getting-started/features/)

See the tutorial: [Managing Python Projects With uv: An All-in-One Solution](https://realpython.com/python-uv/)

 The tutorial has a quick list of key uv features for managing Python projects:

    - Fast dependency installation: Installs dependencies really fast, which is especially useful for large dependency trees.
    - Virtual environment management: Automatically creates and manages virtual environments.
    - Python version management: Allows the installation and management of multiple Python versions.
    - Project initialization: Scaffolds a full Python project, including the root directory, Git repository, virtual environment, pyproject.toml, README, and more.
    - Dependency management: Installs, updates, removes, and locks direct and transitive dependencies, which allows for environment reproducibility.
    - Package builds and publication management: Allows you to build and publish packages to package repositories like the Python Package Index (PyPI).
    - Developer tooling support: Installs and lets you run development tools, such as pytest, Black, and Ruff.
