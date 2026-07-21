# Introduction

This [Topwrap](https://antmicro.github.io/topwrap/index.html)-plugin helps in automating the creation of a testable [Renode platform definition (REPL)](https://renode.readthedocs.io/en/latest/advanced/platform_description_format.html), based upon a Topwrap [design YAML](https://antmicro.github.io/topwrap/description_files.html#design-description).
The plugin extends the Topwrap design YAML with [new metadata fields](./syntax.md) to specify how instantiated IP cores should map to Renode peripherals or CPUs.
In addition, the plugin will also interpret the memory maps belonging to any interconnection network in the design and translate this to Renode's system bus.

## Quick start

The plugin works seamlessly with Topwraps build pipeline.
Just download and install the plugin from the official repository ([https://github.com/antmicro/topwrap-utils.git](https://github.com/antmicro/topwrap-utils.git)) in the same environment as Topwrap.
The plugin is then invoked automatically by Topwrap and the REPL's are placed in the same output directory as the top-level module.
In the same directory as your `design.yaml`, using the [`uv`](https://docs.astral.sh/uv/) package manager:

```bash
uv venv # set up the environment
uv pip install "git+https://github.com/antmicro/topwrap.git" # if not already installed
uv pip install "git+https://github.com/antmicro/topwrap-utils.git#subdirectory=topwrap-renode-plugin"
uv run topwrap build -d design.yaml -b build # outputs are placed in ./build
```

:::{note}
For custom IP-cores, the plugin can not infer what Renode peripheral would match the IP.
The metadata has to be specified, see the [usage section](./usage.md) for how to add these settings yourself.
However, if you're importing IP's from [https://github.com/antmicro/topwrap-cores.git](https://github.com/antmicro/topwrap-cores.git), these settings will be set-up for you. 
:::

