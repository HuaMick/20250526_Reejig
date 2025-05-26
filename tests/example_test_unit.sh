#!/bin/bash

# Ensure we're in the Nix development environment
nix-shell nix/shell.nix --command "python -m pytest tests/example_test_unit.py::test_example_function_operation -v --tb=short"


