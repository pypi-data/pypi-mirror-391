# FleCSI Sandbox

This skeleton project will get you started with building and running a
FleCSI-based application.

# Building & Running

The steps in the following sections will help you to build and run your
project.

## Spack Environment

Spack is the easiest way to build this project. You can install spack
and create a suitable build environment with these steps:

_Clone spack_
```shell
$ git clone git@github.com:spack/spack.git ~/.spack
```
(Cloning spack into _~/.spack_ keeps clutter to a minmum.)

_Source the appropriate spack configuration file for your shell_
```shell
$ source ~/.spack/share/spack/setup-env.sh
```

_Create and build a spack environment_
```shell
$ spack env create flecsi support/env.yaml
$ spacktivate flecsi
$ spack concretize -f
$ spack install
```

## Build & Run

With your spack environment still activated, you can build your project with
these steps:
```shell
$ mkdir build
$ cd build
$ cmake ..
$ make
```
Once your build is complete, you can run your application like:
```shell
$ app/myproject
```
