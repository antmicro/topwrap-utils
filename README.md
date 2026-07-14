# Topwrap Renode Plugin

Copyright (c) 2026 [Antmicro](https://www.antmicro.com)

This plugin allows [Topwrap](https://github.com/antmicro/topwrap) to optionally translate a design into a representable [Renode](https://renode.io) platform description format, REPL-files.
For a thorough description of REPL-files, see the [Renode documentation](https://renode.readthedocs.io/en/latest/advanced/platform_description_format.html).
These platform files can be used to [test designs in Renode](https://renode.readthedocs.io/en/latest/introduction/testing.html).

## Installation

This plugin is available as a python package and can be installed from this repo using for example `pip`:

```shell
$ pip install "git+https://github.com/antmicro/topwrap-renode-plugin.git"
```

## Usage

As a Topwrap plugin, `renode_plugin` is automatically invoked when Topwrap builds a top-level module.
Other than having the plugin installed in the same environment that you use Topwrap to build, you need to add metadata to your design YAML.
To learn more about how this metadata is defined, please read the [documentation](https://antmicro.github.io/topwrap-renode-plugin/usage.html) and check out the [examples](./examples/) directory.

## Examples

A quick overview of how the plugin is configured and sample use cases can be found in the [examples](./examples/) directory.

In each example, a makefile is provided which shows how the plugin is invoked using Topwrap.
All examples can be run using:

```shell
$ cd examples
$ make run_tests
```

## Documentation

Documentation can be found in [docs/](./docs/)

