# PyLunix Icon Kit

[![Version](https://img.shields.io/badge/version-v1.0.0-forestgreen)](#)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](#)
[![Qt](https://img.shields.io/badge/Qt-PyQt5-blue)](#)

`pylunix_icon_kit` is a Python tool that automatically generates **Qt resource files** (`.qrc`), **compiled resource modules** (`_rc.py`), and **Python icon accessor classes** from a folder of icon themes.  

It is designed for **PyQt5** (Qt-based GUI projects), helping you manage icon resources more easily with automatic code generation.

---

## ✨ Features

- 🔄 **Automatic resource generation**
  - Converts `.svg` files into Qt `.qrc` and Python `_rc.py` modules.
- 🏷️ **Python icon class generator**
  - Creates a strongly-typed Python class with constants for all icons in your theme.
- 🎨 **Colorized icons**
  - `IconAccessor` lets you dynamically render SVG icons with custom colors.
- 📂 **Smart output folder handling**
  - Automatically creates `{theme}_icon` output directory and can rename it to `{theme}_icon`.
- 🧹 **Cleanup support**
  - Removes old generated files before creating new ones.
- 🛠️ **CLI & Python API**
  - Works as a command-line tool or directly as a Python module.


## 📦 Installation

To install the package from PyPI, simply run:

```bash
pip install pylunix_icon_kit
```
This will install the latest released version of the PyLunix Icon Generator.

Requires:
* Python 3.8+ (tested on 3.8, 3.9, 3.10, 3.11)
* PyQt5 (provides `QIcon`, `QPixmap`, `QSvgRenderer`, and the `pyrcc5` compiler)
* Qt Resource Compiler (`pyrcc5`)
  * Installed automatically with `PyQt5`.
  * Make sure it is available in your `PATH`. You can verify by running:
    ```bash
    pyrcc5 --version
    ```

If you prefer local development, clone the repo and install in editable mode:

```bash
git clone https://github.com/JIA-WEI-LI/pylunix_icon_kit.git
cd pylunix_icon_kit
pip install -e .
```

## 🚀 Usage

PyLunix Icon Generator can be used in **two ways**:
1. As a **Command Line Interface (CLI)** tool.
2. As a **Python API** directly in your project.

### CLI

The CLI tool is the fastest way to generate Qt resource files and Python icon classes.

#### Basic Command
```bash
pylunix_icon_kit --icons_dir ./icons
```

* `--icons_dir`

    Path to your icon theme folder (the directory containing .svg, .png, or .ico files).
    This is a required argument.

* `--output_dir`

    Optional. Custom folder to store generated files.
    If not provided, the generator creates a folder named {theme}_icon in the parent directory of your icons.

* `--clean`
  
    If provided, the tool removes previously generated files before creating new ones.
    This is useful to avoid leftover or outdated files when you are frequently regenerating resources.

#### Example
```bash
# Generate icons and clean previous output
pylunix_icon_kit --icons_dir ./icons --clean

# Generate with a custom output folder
pylunix_icon_kit --icons_dir ./icons --output_dir ./my_generated_icons
```

---

### Python API

You can also integrate the generator directly into your Python workflow.  
This is useful if you want to regenerate resources as part of a build step or unit test.

```python
from pylunix_icon_kit.generator import IconGenerator

# Create a generator instance
gen = IconGenerator(
    base_dir=".",          # Base project directory (usually root of your repo)
    icons_dir="./icons",   # Input icons folder
    output_dir=None        # Optional: custom output folder
)

# Generate resources
gen.generate_all_themes(clean_first=True)
```

* `base_dir`

    Root directory of your project. Used as the working directory for pyrcc5.

* `icons_dir`
  
    Path to your folder containing theme subdirectories with icons.

* `output_dir`
  
    Custom folder to place generated .qrc, _rc.py, and *_icon.py files.
    If omitted, the generator chooses {theme}_icon.

* `clean_first`
  
    If True, previously generated files will be deleted before new ones are created.

## 📂 Example Output

Suppose you have the following folder:
```bash
icons/
└── dark/
    ├── home.svg
    ├── search.svg
    └── settings.svg
```
When you run:
```bash
pylunix_icon_kit --icons_dir ./icons
```

Generated output (`dark_icon/`):

```bash
dark_icon/
 ├── resources_dark.qrc       # Qt resource file listing all icons
 ├── resources_dark_rc.py     # Compiled resource module (used by PyQt5)
 └── dark_icon.py             # Auto-generated Python icon accessor class
```

---

### Generated Python icon class

Example of the generated class (`dark_icon.py`):

```python
from . import resources_dark_rc

class DarkIcon:
    """Auto-generated icons for the 'dark' theme."""

    HOME = IconAccessor(":dark/home.svg")
    SEARCH = IconAccessor(":dark/search.svg")
    SETTINGS = IconAccessor(":dark/settings.svg")
```

Usage in PyQt5:
```python
from dark_icon import DarkIcon
from PyQt5.QtCore import QSize

button.setIcon(DarkIcon.HOME)
button.setIcon(DarkIcon.HOME("#00AAFF", size=QSize(24, 24)))
```

Here:

* DarkIcon.HOME is an IconAccessor, which behaves like a callable string.
* You can call it with a color (hex or named color) and a QSize to create a colored QIcon at runtime.
* If no color is provided, the original SVG/PNG/ICO is used.

## ⚠️ Development Status

This project is currently under **active development**.  
That means:
- The API and generated file formats may still change before `v1.0.0`.  
- Bugs may exist, especially with different icon folder structures.  
- Contributions are very welcome!  

👉 Please report issues or request new features on the [GitHub Issues page](https://github.com/JIA-WEI-LI/pylunix_icon_kit/issues).

## 📄 License

This project is released under the **MIT License**.  

You are free to use, modify, and distribute it with attribution.  
See the full license text in [LICENSE](./LICENSE).