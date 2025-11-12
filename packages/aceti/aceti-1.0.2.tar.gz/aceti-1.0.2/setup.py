from setuptools import setup

# Minimal shim setup.py — keep pyproject.toml as single source of metadata
# This file exists for legacy tools / `pip install .` and intentionally
# does not duplicate metadata declared in pyproject.toml.

if __name__ == "__main__":
    setup()
