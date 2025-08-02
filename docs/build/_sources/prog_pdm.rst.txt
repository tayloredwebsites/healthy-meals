Python Package and Dependency Manager (PDM)
===========================================


Note: we are no longer using /requirements.txt to keep our dependencies up to date.  We are using pyproject.toml with `PDM Project <https://github.com/pdm-project/pdm>`_, which provides excellent [dependency management](https://pdm-project.org/latest/usage/dependency/) features, such as dependency tree, groups, locking, etc.  The [Anna-Lena Popkes review of tools](https://alpopkes.com/posts/python/packaging_tools/) said that PDM was the only reviewed tool that provides all of the following:

- Python version management: ✅
- Package management: ✅
- Environment management: ✅
- Building a package: ✅
- Publishing a package: ✅

According to the `PDM Working with Virtual Environments Page <https://pdm-project.org/en/latest/usage/venv/>`_, PDM works with Virtual Environments.  We are currently using the standard .env that we set up during the installation of this project, and by default, PDM uses the same virtual environment (in <project_root>/.venv).  See: `location of virtuanenvs <https://pdm-project.org/en/latest/usage/venv/#the-location-of-virtualenvs>`_.

.. todo:: Followup on features listed in the `PDM Advanced Usage page <https://pdm-project.org/en/latest/usage/advanced/>`_

    - According to the `PDM Advanced Usage page (nox section) <https://pdm-project.org/en/latest/usage/advanced/#use-nox-as-the-runner>`_ PDM works with `nox <https://nox.thea.codes/en/stable/>`_, and we have been successfully using nox with PDM.
    - We may need to use the `Continuous Integration with Github Actions <https://pdm-project.org/en/latest/usage/advanced/#use-pdm-in-continuous-integration>`_ feature for that the tests are all passing for the code passed up to the server.  See:  :doc:`Continuous Integration Guide <prog_ci>`.
    - Ensure that `PDM works properly in Docker <https://pdm-project.org/en/latest/usage/advanced/#use-pdm-in-a-multi-stage-dockerfile>`_.