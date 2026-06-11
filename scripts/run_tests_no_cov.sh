#!/usr/bin/env bash
PYTHON=${PYTHON:-.venv/bin/python}
"$PYTHON" -m pytest -o addopts= "$@"
