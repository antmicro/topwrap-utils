# Syntax

To support automating the creation of REPL's, metadata needs to exist in the IP-cores or the design YAML.
The metadata tells the plugin how to map relevant aspects of the design to the configuration settings of Renode's peripherals.

## Overview

Here's a quick overview of how the metadata is specified in the IP-core YAML:

```yaml
# ...
extensions:                 # The "extensions" tag
  renode_peripheral_gen:    # Metadata field for this plugin
    renode_device: "..."    # The name of the Renode peripheral (required)
    map:                    # Mapping between the peripheral's configuration 
                            # fields and properties of the instantiated
                            # ip-core (optional)
      - dest: "..."         #  Renode-peripheral config
        src: "..."          #  Topwrap design property
```

In the design YAML, you have the *option* to configure the output artifacts.
It's also possible to override the Renode-peripheral mapping from the IP-cores's modules. 
In those scenarios, you have to target any IP-core by it's module ID.

```yaml
# ... 
extensions:                              # The "extensions" tag
  renode_peripheral_gen:                 # Metadata field for this plugin
    supported_peripherals:               # List of "IP-core to Renode peripheral"-mappings (optional)
      - target:                          # Fully qualified module ID (required)
          name: "..."
          vendor: "..."
          library: "..."
        renode_device: "..."             # The name of the Renode peripheral (required)
        map:                             # Mapping between the peripheral's configuration
                                         # fields and properties of the instantiated
                                         # ip-core (optional)
          - dest: "..."                  #  Renode-peripheral config
            src: "..."                   #  Topwrap design property
    output:                              # A list of configuration files to generate (optional)
      - filename: "..."                  #  Output file name
        filter: []                       #  IP-cores to include
        includes: []                     #  List of other .repl files to include
  renode_resc:                           # Settings related to RESC file generation (optional)
      cpus:                              # List of IP-cores to mark as CPU's, with relative path
                                         # to ELF-files.
        - ["cpu_core", "./path/to/elf"]
                                         # containing binary.
      analyze: []                        # List of IP cores to use `showAnalyzer` on 
      features: []                       # List of features to add to the RESC
```

## Plugin metadata

Topwrap supports adding non-standard metadata to the design description.
The metadata for this plugin is placed under `extensions.renode_peripheral_gen`.

## Syntax of mapping

The `src` key in `supported_peripherals[*].map` describes what property of an instantiated design that should be mapped to a Renode peripheral's configuration field.
It has the following syntax

```
.<source>.<symbol>
```

where `<source>` is either `connections` or `memory_map`.
The `connections` *source* references **constant (input) port-connections**, converted to an integer.
The value of `<symbol>` chooses the name of the input port from which the plugin will grab this value.

In contrast, the `memory_map` *source* can be used to reference either the `size` or the `address` of a memory map.
If the IP-core is not directly connected to the interconnect where this memory map is defined (for example if the IP core is connected via a bridge), the plugin will figure out which memory map encompasses the target IP core.

## Output

It can be relevant to output sub-sets of the design into different REPL's.
To support this, several outputs can be configured via the `output` key.
In addition to the `filename`-key, the `filter`-key can be used to select which instantiated IP-cores should be output.
The filter is specified as a sequence of rules (see [rule syntax](#rule-syntax)), applied in order.
If the platform description depends on other files, their paths can be imported via the `includes` keyword.

If no `output` is specified, the default output `platform.repl` containing all peripherals will be output.

### Rule syntax

A filter is specified as a list of rules (where each rule is a string).
Each rule will either add or remove IP-cores from the output.
The rules are applied in order and can negate each-other.

A rule is one of:

- `*` - Include every IP-core
- `<name>` - Include an IP-core with name `<name>`
- `-<name>` - Remove an IP-core with name `<name>`

### Output example

Assuming the design has the following IP-cores: `A`, `B` and `C`. If you want to group `A` and `B` together into one platform
description while `C` is placed in a separate one that imports the previous, you would specify it as such:

```yaml
output:
  - filename: "A_and_B.repl"
    filter: [
      "*",                        # Include all IP's
      "-C"                        # Remove C
    ]
    includes: []
  - filename: "C.repl"
    filter: ["C"]                 # Only use C
    includes: ["A_and_B.repl"]    # Include previous file 
```

## Renode RESC generation

RESC files are always generated next to the REPL-file.
In order to be useful, you need to specify at least one CPU and a binary to run.
You can optionally add analyzers to peripherals, which will output useful information to the console.

The `renode_resc` key is used in the design file to control the what's included in the `.resc` file.
The current format is limited to a single cpu and a list of mapped IP-cores for which to setup analyzers. 

The `cpu` key is a list containing two items: the name of the IP core which acts as the CPU and the path to an `.elf`-file containing the binary to run (relative to the output directory of the `topwrap` build folder).
The `analyze` key is a list of IP-cores which should be "analyzed" (i.e. used with `showAnalyzer`).
This is necessary for UART peripherals to also see their output.

What's contained in the RESC file can controlled via the `features` key, which is a list of feature tags.
The supported feature tags are:

| Tag name      | Description |
|-|-|
| `no_run`      | The RESC file will not instruct Renode to run a simulation. This is useful if an external tool invokes `run` |
| `reset_macro` | The RESC file will contain a macro, `$reset`, which will instruct Renode reset the CPU and upload the ELF-file binaries. |
| `mem_mailbox` | This will add an watcher listening on address `0x80f80000`, which will log any values written to that address. |

