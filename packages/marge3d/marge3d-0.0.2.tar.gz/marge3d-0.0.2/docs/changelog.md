# Changelog

📜 _History of the main changes in the code, in complement to the commit history._

## From scripts to a proper package

### Package structure

Creation of the `marge3D` folder, containing a `__init__.py` file so it can be imported as a python package. Then :

- `Dtche_J_parameters_3D.py` -> [`marge3D/params.py`](../marge3d/params.py)
- `Dtche_J_cls_3D.py` -> [`marge3D/numeric.py`](../marge3d/numeric.py)
- `Analy_obj_3D.py` -> [`marge3D/analytic.py`](../marge3d/analytic.py)
- `Vortex_Fld_3D.py` -> [`marge3D/fields.py`](../marge3d/fields.py)

> 💡 All import statements have been updated


### Class naming

Most class in `marge3D` have been renamed to follow the [standard Python conventions (PEP8)](https://peps.python.org/pep-0008), that is :

- `mr_parameter` -> `DaitcheParameters`
- `maxey_riley_analytic_3d` -> `AnalyticalSolver`
- `maxey_riley_Daitche_3d` -> `NumericalSolver`
- `velocity_field_3d` -> `VelocityField3D`

> 💡 All import statements have been updated, and unnecessary inheritances to the base `object` class have been removed


### Package setup

Created the `pyproject.toml` file at the root of the repository, containing this :

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "marge3d"
version = "0.0.1"
description = "Solver for Maxey-Riley-Gatignol (MaRGE) in 3D"
dependencies = [
    "numpy",
    "scipy",
    "matplotlib",
]
requires-python = ">=3.10"
maintainers = [
    {name = "Vamika Rathi", email = "vamika.rathi@tuhh.de"},
    {name = "Finn Sommer", email = "finn.sommer@tuhh.de"},
]
readme = "README.md"
license = {file = "LICENSE"}
classifiers = [
    "Development Status :: 3 - Alpha",

    "Topic :: Scientific/Engineering :: Mathematics",

    "License :: OSI Approved :: BSD License",

    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
]

[project.urls]
Homepage = "https://github.com/CompMath-TUHH/MaRGE_3D_solver"
Tracker = "https://github.com/CompMath-TUHH/MaRGE_3D_solver/issues"
```

This allows to install locally the package now using

```bash
pip install -e .
```

> 💡 The `-e` option installs in editable mode, creating link to the `marge3d` package in the Python environment rather than copying the package into it.
> That way, any local modification on the package is automatically taken into account.

In addition, a base [`LICENSE`](../LICENSE) file is added in the root folder.


### Continuous testing

1. added first tests in the [tests](../tests) folder (order convergence VS analytical solution)
2. added the `tests` optional dependencies in `pyproject.toml`
```toml
# previous content ...
[project.optional-dependencies]
tests = [
    "flake8",
    "pytest",
]
```
3. added the `ci_pipeline.yml` file in a `.github/workflows` folder, containing :
```yml
name: CI pipeline ⚙️

on:
  push:
    branches: [ "main" ]
  pull_request:

jobs:
  test-code:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python: ['3.10', '3.11', '3.12', '3.13', '3.14']
    defaults:
      run:
        shell: bash -l {0}

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 2
    - name: Set up Python ${{ matrix.python }}
      uses: actions/setup-python@v4
      with:
        python-version: "${{ matrix.python }}"
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install .[tests]
    - name: Lint with flake8
      run: |
        # stop if there are Python syntax errors or undefined names
        flake8 ./marge3d ./tests --count --select=E9,F63,F7,F82 --show-source --statistics
    - name: Run pytest
      run: |
        pytest --continue-on-collection-errors -v --durations=0 ./tests
```

Now, all tests are run on every commit done to the `main` branch, but can also be run locally using

```bash
pip install -e .[tests]
pytest -v ./tests
```


### Test coverage

📜 _It's nice to have test for your package, it's better to have coverage analysis checking how much of your code is tested (and preferably 100%)._

First, complete the `pyproject.toml` file with an additional `tests` dependency (`pytest-cov`),
and add the following coverage options :

```toml
[project.optional-dependencies]
tests = [
    "flake8",
    "pytest",
    "pytest-cov",
    "pytest-timeout",
    "coverage[toml]",
]

[tool.coverage.run]
relative_files = true
concurrency = ['multiprocessing']
include = ['*/marge3d/*']

[tool.coverage.report]
skip_empty = true
# Regexes for lines to exclude from consideration
exclude_lines = [
    # Enable the standard pragma
    'pragma: no cover',

    # Don't complain if tests don't hit defensive assertion code:
    'raise',
    'except',

    # Ignore footer of scripts
    'if __name__ == "__main__":',
    ]
```

Now, test can be run with a coverage report using :

```bash
pip install -e .[tests]
pytest --cov --cov-branch --cov-report=html -v ./tests
```

This will generate an HTML report with file-by-file test coverage in the `htmlcov/index.html` file,
that can open with you favorite browser.

> 💡 Note that the `htmlcov` folder is added in the [`.gitignore` file](../.gitignore)

Finally, modify the last part of the [`ci_pipeline.yml` file](../.github/workflows/ci_pipeline.yml) :

```yml
- name: Run pytest
  run: |
    pytest --cov --cov-report=xml -v --durations=0 ./tests
- name: Upload coverage reports to Codecov
  uses: codecov/codecov-action@v5
  if: github.repository_owner == 'CompMath-TUHH' && matrix.python == '3.13'
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    slug: CompMath-TUHH/MaRGE_3D_solver
```

This will upload a coverage report to [codecov](https://app.codecov.io/github/CompMath-TUHH) each time
a modification is made on the `main` branch, or when someone do a pull request.

> 💡 In particular, it will follow at each code modification if the coverage improved (or not ...)

Finally, some badges can now be added at the top of the [`README.md` file](../README.md) :

```md
[![Repo status](https://www.repostatus.org/badges/latest/active.svg)](https://github.com/CompMath-TUHH/MaRGE_3D_solver)
[![CI pipeline](https://github.com/CompMath-TUHH/MaRGE_3D_solver/actions/workflows/ci_pipeline.yml/badge.svg)](https://github.com/CompMath-TUHH/MaRGE_3D_solver/actions/workflows/ci_pipeline.yml)
[![Coverage](https://codecov.io/github/CompMath-TUHH/MaRGE_3D_solver/graph/badge.svg?token=5Q6GS039XF)](https://codecov.io/github/CompMath-TUHH/MaRGE_3D_solver)
```

> 💡 The `Coverage` badge must be retrieved directly from the [codecov](https://app.codecov.io/github/CompMath-TUHH) interface


### Dedicated scripts folder

All remaining scripts are moved in a [`scripts`](../scripts) folder, and name are changed to be more explicit :

- `Analy_obj_3D.py` -> `run_analytical_solution.py`
- `Dtche_obj_3D` -> `run_Daitche_solution.py`
- `Conv_3D` -> `run_convergence.py`


### Adding documentation

In the [`docs`](../docs) folder, template for documentation is added inspired from [qmat](https://github.com/Parallel-in-Time/qmat/tree/main/docs). In particular, it added :

- the `docs` dependencies in `pyproject.toml`
- a base [`index.rst`](./index.rst) and [`conf.py`](./conf.py) file for `sphinx` (documentation builder)
- a [`logo.png`](./logo.png) quickly generated from a plot and some additional CSS and favicon files in [`_static`](./_static)
- a [`Makefile`] to easily build the documentation in a `_build/html` folder using the command
```bash
make html
```

### Setup online documentation

Use of [ReadTheDocs](https://app.readthedocs.org), which requires the [.readthedocs.yaml](./.readthedocs.yaml) file, and some configuration on GitHub and ReadTheDocs dashboard.
Once it's done, a new badge can be added on the top of the main `README.md` file :

```md
[![Read the Docs](https://img.shields.io/readthedocs/marge-3d-solver?logo=readthedocs)](https://marge-3d-solver.readthedocs.io/)
```


### Setup PyPI package

This requires the [publish.yml](../.github/workflows/publish.yml) file and the addition of new publisher on [PyPI](https://pypi.org).
Once the latter is set, the `Publish to PyPI 📦` workflow has to be triggered manually on the
[GitHub action panel](https://github.com/CompMath-TUHH/MaRGE_3D_solver/actions)
to publish the first package version `0.0.1`.
In addition, a first release is done with the tag `v0.0.1` on the [GitHub releases page](https://github.com/CompMath-TUHH/MaRGE_3D_solver/releases)

Also, some new badges can be added to the documentation and main `README.md` file :

```md
[![PyPI - Package](https://img.shields.io/pypi/v/marge3d?logo=python)](https://pypi.org/project/marge3d)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/marge3d?logo=pypi)](https://pypistats.org/packages/marge3d)
```

### Setup the Zenodo release

Once Zenodo is connected to the [CompMath-TUHH GitHub organization](https://github.com/CompMath-TUHH),
then it will follow all releases published on GitHub and create a unique DOI for it.

In particular, one can keep now track of the latest DOI using this Badge :

```md
[![DOI](https://zenodo.org/badge/1090126264.svg)](https://doi.org/10.5281/zenodo.17601798)
```