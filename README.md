# Common-util: A common library for easily setting up utilities

## Supported Python Versions

Python 3.7.6  
This library may work on later versions of 3

## Installation

### Install Using `pip`

```sh
pip install git+https://github.com/j4nusl1n/common-util.git
```

Check whether this package is successfully installed

```sh
pip list | grep commonutil
```

## Usage

```python
# main package
import commonutil

# import all subpackages defined in __all__ inside commonutil/__init__.py
from commonutil import *
```

## Generating Docs

1. Make a symbolic link of the README.md of the repository

    ```sh
    ln -s doc/source/README.md ./README.md
    ```

2. Generate from module docstring using `autodoc`

    ```sh
    sphinx-apidoc -f -o source/ ../commonutil/
    ```

3. Generate full documents in HTML format

    ```sh
    cd ./doc
    make clean && make html
    ```

## Utility Submodules

- db: connect to databases by using YAML configurations
- google_app: connect to Google applications using Google Python client library
