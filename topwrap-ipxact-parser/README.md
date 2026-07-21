# topwrap-ipxact-parser

Copyright (c) 2026 [Antmicro](https://antmicro.com)

Generated IEEE 1685-2022 (IP-XACT) XML schema bindings, used by `topwrap`'s
IP-XACT frontend. This package has no dependency on `topwrap` itself and 
can be used standalone.

## Prerequisites

This package uses [`uv`](https://docs.astral.sh/uv/) as a package
manager and [`just`](https://just.systems) as a task runner. Install both
with:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install rust-just
```

## Example

`examples/parse_example.py` parses a minimal IP-XACT component
(`examples/simple_component.xml`) and prints its ports. Run it with:

```bash
just example
```

## Introduction

`topwrap_ipxact_parser/__init__.py` was generated using 
[generateDS](https://sourceforge.net/projects/generateds/) and
the IP-XACT 2022 schema.

It was necessary to patch generateDS and the IP-XACT schema sources; see the
patches in [`patches/`](patches/).

The schema is published by [Accellera](https://www.accellera.org/downloads/standards/ip-xact)
and is also mirrored on GitHub at
[edaa-org/IPXACT-Schema](https://github.com/edaa-org/IPXACT-Schema).

## How to generate

```bash
just regenerate
```

See the `justfile` for what this does.
