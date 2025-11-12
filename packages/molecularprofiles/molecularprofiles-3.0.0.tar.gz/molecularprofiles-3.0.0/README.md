# molecularprofiles

A collection of routines to read an analyze meteorological data in `grib2` format.

See [project documentation](http://cta-array-elements.gitlab-pages.cta-observatory.org/ccf/MDPs/) for API docs.

## Development installation:

- Clone the code with git:
  ```shell
  > git clone https://gitlab.cta-observatory.org/cta-array-elements/ccf/mdps.git
  ```
- Checkout an appropriate branch (currently, dev branch contains the most recent code):
  ```shell
  git checkout -b <branch_name>
  ```
- Use `mamba` to setup a clean environment
  ```shell
  > mamba create -n molecularprofiles -c conda-forge python==3.12
  > mamba activate molecularprofiles
  ```
- Install molecularprofiles in editable mode with test dependencies:
  ```shell
  > pip install -e.[test,doc,dev]
  ```
- Don't forget to install a pre-commit hook:
  ```shell
  > pre-commit install
  ```
