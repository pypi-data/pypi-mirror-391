# My Text Emojifier

A simple Python library to replace or append emojis to text using NLTK for smart matching.

## Installation

```bash
pip install my-text-emojifier
```

## Usage

> **Note:** The import name is `emoji_lib`.

```python
from emoji_lib import replace_with_emoji, append_emoji

text = "I loved my happy dogs!"

# Replace
print(replace_with_emoji(text))
# Output: I ❤️ my 😄 🐶!

# Append
print(append_emoji(text))
# Output: I loved ❤️ my happy 😄 dogs 🐶!
```

## Project Structure

Your project folder is `my-text-emojifier`, but the Python package you distribute is `emoji_lib` (what users import). This is a common pattern—for example, you `pip install scikit-learn` but `import sklearn`.

The Python code remains unchanged:
- `emoji_lib/core.py` — contains the NLTK logic
- `emoji_lib/__init__.py` — contains the package imports

## Build & Upload Commands

### 1. Build Your Package

```bash
python setup.py sdist bdist_wheel
```

This creates distribution files like `my-text-emojifier-0.1.0.tar.gz` in your `dist/` folder.

### 2. Upload to TestPyPI

```bash
twine upload --repository testpypi dist/*
```

### 3. Test Your Package

```bash
# Deactivate and delete your old test environment first!
pip install -i https://test.pypi.org/simple/ my-text-emojifier
```

### 4. Upload to Real PyPI

```bash
twine upload dist/*
```
