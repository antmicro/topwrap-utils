# Topwrap Bazel rules

Copyright (c) 2026 [Antmicro](https://www.antmicro.com)

Bazel rules for parsing HDL into Topwrap IP descriptions, assembling libraries
and generating design wrappers. Compatible with
[bazel_rules_hdl](https://github.com/hdl/bazel_rules_hdl).

## Setup

Use [example/MODULE.bazel](example/MODULE.bazel) and
[example/.bazelrc](example/.bazelrc) as the integration reference, including the
root-module dependency overrides and [Python 3.13 patch](example/patches/).

Run the standalone example:

```sh
cd example
bazel run //:my_design_gui
```

## Rules

Load rules from `@rules_topwrap//:defs.bzl`.

| Rule | Purpose |
| --- | --- |
| `topwrap_parse_sources` | Parse HDL targets into IP descriptions. |
| `topwrap_core` | Register a hand-authored IP description and its HDL dependencies. |
| `topwrap_library` | Assemble cores, interface definitions and mappings. |
| `topwrap_design` | Generate a wrapper providing `VerilogInfo`. |
| `topwrap_gui` | Launch the Topwrap GUI. |
| `topwrap_design_gui` | Launch the GUI with a design and its libraries. |

Parsing supports custom inference libraries (`libraries`), module selection
(`modules`) and optional interface emission (`emit_interfaces`). See
[example/BUILD.bazel](example/BUILD.bazel) for usage, packaging and synthesis.

## Dependencies

Update and validate the Python lockfile from this directory:

```sh
bazel run //:requirements.update
bazel test //:requirements.test
```
