# Usage

The plugin automates the creation of REPL files, but it requires the user to assign renode devices to IP-cores before it can be used.

## General flow

The general flow:

1. Start off with a design in Topwrap. 
2. Make a decision on which IP-cores you can/want to emulate in Renode (see list of [supported peripherals](https://renode.readthedocs.io/en/latest/introduction/supported-boards.html#supported-peripherals)).
3. Review the configuration settings required for the selected peripherals.
4. Map design properties of *your* IP-cores to the configuration settings of the Renode peripherals.
5. For complex designs, also make a decision if you want to split up configurations into different outputs.

Note that more steps are required to [test with Renode](https://renode.readthedocs.io/en/latest/introduction/testing.html), the plugin only generates the REPL's.

## Assigning Renode devices

In order to generate a REPL for a design, the plugin takes as input metadata that maps properties of IP-core modules to Renode peripherals and their configuration settings.
This metadata is specified in the Topwrap design YAML (see [syntax](./syntax.md)) and requires familiarity with the [Design description format](https://antmicro.github.io/topwrap/description_files.html#design-description).
There is no inference of assignments, so this step is **required**.

## Generating platform definitions

The plugin is automatically invoked by Topwrap's plugin manager during the build process (see the [Getting started](https://antmicro.github.io/topwrap/getting_started.html#getting-started) guide) if it is installed using a python package manager, like [pip](https://pypi.org/project/pip/) or [uv](https://docs.astral.sh/uv/).

### Example

The [examples directory](https://github.com/antmicro/topwrap-utils/tree/main/topwrap-renode-plugin/examples) contain example designs and makefiles for building them. Assuming you have an existing Topwrap design with all Renode metadata filled in, the following commands would create REPL-files as an artifact while building the top-level design:

```bash
cd path/to/project # contains topwrap.yaml and design description
uv venv
uv pip install "topwrap @ git+https://github.com/antmicro/topwrap"
uv pip install "topwrap-renode-plugin @ git+https://github.com/antmicro/topwrap-utils.git#subdirectory=topwrap-renode-plugin"
uv run topwrap build -d . -b build
```

The REPL's are placed in `./build`.

