# FleCSI Sandbox Package (flecsi_sandbox)

The _flecsi_sandbox_ package provides the _skelf_ tool to create skeleton
FleCSI-based application projects, suitable for experimentation, or as the
starting point for a real application.

# Developer Notes

## Create Python Environment

The best way to build this package for development is to create a python
environment:
```shell
$ python -m venv --prompt skelf-devel .venv
$ source .venv/bin/activate
$ pip install build twine
```
Then you can build like:
```shell
$ pip install -ve .
```

## Publish

```shell
$ twine upload dist/*
```
