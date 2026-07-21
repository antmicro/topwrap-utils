# Introduction

This [Topwrap](https://antmicro.github.io/topwrap/index.html)-plugin helps in automating the creation of a testable [Renode platform definition (REPL)](https://renode.readthedocs.io/en/latest/advanced/platform_description_format.html), based upon a Topwrap [design YAML](https://antmicro.github.io/topwrap/description_files.html#design-description).
The plugin extends the Topwrap design YAML with [new metadata fields](./syntax.md) to specify how instantiated IP cores should map to Renode peripherals or CPUs.
In addition, the plugin will also interpret the memory maps belonging to any interconnection network in the design and translate this to Renode's system bus.

