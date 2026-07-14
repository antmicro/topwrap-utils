# Syntax

To support automating the creation of REPL's, new metadata needs to be assigned to the Topwrap design YAML.
The metadata tells the plugin how to map relevant aspects of the design to the configuration settings of Renode's peripherals.

## Overview

Here's a quick overview of how the metadata is specified in the design YAML:

```yaml
# ... 
extensions:                     # The "extensions" tag
  renode_peripheral_gen:        # Metadata field for this plugin
    supported_peripherals:      # List of "IP-core to Renode peripheral"-mappings
      - target:                 # Fully qualified module ID
          name: "..."
          vendor: "..."
          library: "..."
        renode_device: "..."    # The name of the Renode peripheral
        map:                    # Mapping between the peripheral's configuration
                                # fields and properties of the instantiated
                                # ip-core
          - dest: "..."         #  Renode-peripheral config
            src: "..."          #  Topwrap design property
    output:                     # A list of configuration files to generate
      - filename: "..."         #  Output file name
        filter: []              #  IP-cores to include
        includes: []            #  List of other .repl files to include
```

## Plugin metadata

Topwrap supports adding non-standard metadata to the design description.
The metadata for this plugin is placed under `extensions.renode_peripheral_gen`.
Two settings need to be specified: the [`supported_peripherals`](#syntax-of-mapping) and the [`output`](#output).

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

It can be relevant to output sub-sets of the design into different platform description files.
To support this, several outputs can be configured via the `output` key.
In addition to the `filename`-key, the `filter`-key can be used to select which instantiated IP-cores should be output.
The filter is specified as a sequence of rules (see [rule syntax](#rule-syntax)), applied in order.
If the platform description depends on other files, their paths can be imported via the `includes` keyword.

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

