# Topwrap Bazel rules

Copyright (c) 2026 [Antmicro](https://www.antmicro.com)

Bazel rules for using [topwrap](https://github.com/antmicro/topwrap) to parse
IP cores and generate top-level design wrappers. Compatible with
[`bazel_rules_hdl`](https://github.com/hdl/bazel_rules_hdl).

## Setup

Add to your `MODULE.bazel`:

```python
bazel_dep(name = "rules_python", version = "0.40.0")

pip = use_extension("@rules_python//python/extensions:pip.bzl", "pip")
pip.parse(
    hub_name = "pip",
    python_version = "3.13",  # must match rules_hdl's own pip vendor hub
    requirements_lock = "//:requirements_lock.txt",
)
use_repo(pip, "pip")

bazel_dep(name = "rules_hdl")
git_override(
    module_name = "rules_hdl",
    commit = "94e28d604085707499fd5aa1fd96519b1acda216",
    remote = "https://github.com/hdl/bazel_rules_hdl.git",
)

single_version_override(module_name = "rules_cc", version = "0.2.11")
single_version_override(module_name = "rules_pycross", version = "0.8.3")

bazel_dep(name = "openroad", repo_name = "org_theopenroadproject")
bazel_dep(name = "rules_7zip", version = "0.0.1")

git_override(
    module_name = "rules_7zip",
    commit = "03a10b5796eac0aed122cf52064ed15785610857",
    remote = "https://github.com/zaucy/rules_7zip.git",
)
git_override(
    module_name = "openroad",
    commit = "d046747ad39bfc5e032eb5c548ad8dfb441e228b",
    init_submodules = True,
    patch_strip = 1,
    patches = ["//dependency_support/openroad:slang_path.patch"],  # fixes a broken @slang path
    remote = "https://github.com/The-OpenROAD-Project/OpenROAD.git",
)
git_override(
    module_name = "qt-bazel",
    commit = "886104974c2fd72439f2c33b5deebf0fe4649df7",
    remote = "https://github.com/The-OpenROAD-Project/qt_bazel_prebuilts",
)

bazel_dep(name = "toolchains_llvm", version = "1.4.0")

llvm = use_extension("@toolchains_llvm//toolchain/extensions:llvm.bzl", "llvm")
llvm.toolchain(cxx_standard = {"": "c++20"}, llvm_version = "19.1.7")
use_repo(llvm, "llvm_toolchain")
register_toolchains("@llvm_toolchain//:all")
```

`requirements_lock.txt` needs every transitive dependency pinned, not just
`topwrap` (`pip.parse` doesn't resolve transitively). Manage it with:

```sh
bazel run //:requirements.update
bazel test //:requirements.test
```

## Rules

Load from `//:defs.bzl`: `topwrap_parse_sources`, `topwrap_core`,
`topwrap_library`, `topwrap_design`, `topwrap_gui`, `topwrap_design_gui`.

* Parse IP `verilog_library` targets into core descriptions

```python
topwrap_parse_sources(
    name = "parsed_ip",
    deps = ["//ip:uart_lib", "//ip:spi_lib"],
)
```

* Use hand-authored `module.yaml`, with optional (but recommended) HDL.
`name` must match the yaml's `id.name` and any `repo[...]:...` reference.
`deps` accepts raw `verilog_library` targets and/or other `topwrap_core`/
`topwrap_parse_sources` targets, so one core can depend on another:

```python
topwrap_core(
    name = "fifo",
    yaml = "fifo/module.yaml",
    deps = ["//ip:fifo_lib"],
)

topwrap_core(
    name = "axi_protocol_converter",
    yaml = "axi_core/module.yaml",
    deps = ["//ip:axi_core_lib", ":fifo"],   # HDL dep + core dep
)
```

* Assemble a library, named after `name`, matched by `design.yaml`'s `repo[name]:...`:

```python
topwrap_library(
    name = "my_library",
    cores = [":parsed_ip", ":axi_protocol_converter"],
    interfaces = ["axi_core/axi4.yaml"],   # optional
    mappings = ["axi_core/axi4_map.yaml"], # optional
)
```

* Generate the top-level wrapper. Returns `VerilogInfo` provider 
so it can be used anywhere a `verilog_library` is expected

```python
topwrap_design(
    name = "my_design",
    design = "design.yaml",
    deps = [":my_library"],
)

```

* Run GUI on a topwrap design

```python
topwrap_design_gui(
    name = "my_design_gui",
    design = "design.yaml",
    deps = [":my_library"],
)
```
```sh
bazel run //example:my_design_gui
```

* Package a `topwrap_library`'s output is a plain directory artifact

```python
load("@rules_pkg//pkg:tar.bzl", "pkg_tar")

pkg_tar(
    name = "my_library_pkg",
    srcs = [":my_library"],
)
```

See `example/` for a complete working instance.
