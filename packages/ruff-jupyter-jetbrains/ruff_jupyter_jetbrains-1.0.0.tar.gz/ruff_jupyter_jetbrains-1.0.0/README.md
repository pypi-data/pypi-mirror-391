[![python](https://img.shields.io/badge/python-3.14-gray?style=for-the-badge&logo=python&logoColor=FFD43B&color=306998)](https://www.python.org/)
[![pypi](https://img.shields.io/pypi/v/ruff-jupyter-jetbrains?style=for-the-badge&logo=pypi&logoColor=f8d45f&color=306998)](https://pypi.org/project/ruff-jupyter-jetbrains/)
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=for-the-badge)](https://docs.astral.sh/ruff/)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json&style=for-the-badge)](https://docs.astral.sh/ty/)
[![tests](https://img.shields.io/github/actions/workflow/status/OliverSieweke/ruff-jupyter-jetbrains/test.yml?style=for-the-badge&label=Tests&logo=github)](https://github.com/OliverSieweke/ruff-jupyter-jetbrains/actions/workflows/test.yml)


<br>

<!--suppress HtmlDeprecatedAttribute -->
<p align="center">
  <img width="20%" src="https://raw.githubusercontent.com/OliverSieweke/ruff-jupyter-jetbrains/main/assets/ruff.png" alt="Ruff Logo">
  <img width="20%" src="https://raw.githubusercontent.com/OliverSieweke/ruff-jupyter-jetbrains/main/assets/jetbrains.png" alt="Ruff Logo">
</p>

<!--suppress HtmlDeprecatedAttribute -->
<p align="center">
<img width="70%" src="https://raw.githubusercontent.com/OliverSieweke/ruff-jupyter-jetbrains/main/assets/demonstration.gif" alt="demonstration">
</p>

# ruff-jupyter-jetbrains

`ruff-jupyter-jetbrains` is a python package that is designed to be run as a file watcher tool in JetBrains IDEs to display ruff linting inspections in Jupyter notebooks.

## Usage

1. Install the package in your environment, using your package manager of choice. E.g:

   ```
   uv add --dev ruff-jupyter-jetbrains
   ```

2. Ensure you have the JetBrains [File Watchers](https://plugins.jetbrains.com/plugin/7177-file-watchers) plugin enabled.
3. Under Settings > Tools > File Watchers, configure a new file watcher with the following settings:
	- File type: `Jupyter Notebook`
	- Program: `uv` (or your tool of choice)
	- Arguments: `run ruff-jupyter-jetbrains $FilePath$`
	- Show console: `Never` (unless you need to debug)
	- Output Filters: `$FILE_PATH$:$LINE$:$COLUMN$: $MESSAGE$`

<!--suppress HtmlDeprecatedAttribute -->
<p align="center">
<img width="50%" src="https://raw.githubusercontent.com/OliverSieweke/ruff-jupyter-jetbrains/main/assets/settings.png" alt="settings">
</p>

4. Set your desired severity level and color scheme under Settings > Editor > Inspections > File watcher problems

### Alternative Usage

If you want to keep your project dependencies minimal, you could also use an isolated runner like `uvx`, without installing the package in your environment. In that case ignore step 1 above and use the following settings instead:

- Program: `uvx`
- Arguments: `ruff-jupyter-jetbrains $FilePath$`

---


## How it works

JetBrains maintains an intermediary notebook representation that differs from the raw notebook JSON content: each cell source appears as is in order and is marked up with a comment line that specifies its type (`# %%` for code and `# %%m` for markdown).

In addition, custom JetBrains file watchers can show inspection messages when their output can be parsed into a file path, line, column and message.

With that knowledge the `ruff` linting output can be used and converted to a format compatible with JetBrains file watchers.



> [!WARNING]
>
> This little tool, while functional, is only meant as a workaround. Ideally, this functionality should live in a proper plugin that makes use of the language server protocol. This was motivated by a standing [issue](https://github.com/koxudaxi/ruff-pycharm-plugin/issues/352) in the [Ruff plugin](https://plugins.jetbrains.com/plugin/20574-ruff) and my lack of Kotlin knowledge to fix it at the root.



---

## Development

### Setup

Clone the repo:

```
git clone https://github.com/OliverSieweke/ruff-jupyter-jetbrains.git
```

This project uses `uv` as a **project manager**. To set up the environment, ensure `uv` is [installed](https://docs.astral.sh/uv/getting-started/installation/) and run:

```shell
uv sync
```

To ensure code follows the project’s guidelines, install **pre-commit hooks** with:

```shell
pre-commit install
```

### **Code Standards**

`ruff` is used as a **formatter** and can be run with:

```shell
ruff format
```

`ruff` is used as a **linter** and code can be checked with:

```shell
ruff check
```

`ty` is used as a **type checker** and code can be checked with:

```shell
ty check
```

**Tests** are handled by `pytest` and can be run with:

```
pytest
```

