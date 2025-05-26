#!/bin/bash

# Ensure we're in the Nix development environment
nix-shell nix/shell.nix --command "python -m pytest tests/example_test_integration.py::test_example_integration -v -s --capture=no --tb=short"