#!/usr/bin/env python3
# Copyright (c) 2026 Antmicro <www.antmicro.com>
# SPDX-License-Identifier: Apache-2.0

"""Assembles a topwrap library directory (cores/, interfaces/, mappings/).
Invoked by the topwrap_library and topwrap_core Bazel rules."""

import argparse
import shutil
import sys
from pathlib import Path


def copy_tree_contents(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for entry in src.iterdir():
        target = dst / entry.name
        if target.exists():
            raise SystemExit(f"duplicate entry '{entry.name}' under {dst}")
        if entry.is_dir():
            shutil.copytree(entry, target)
        else:
            shutil.copy2(entry, target)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dir")
    parser.add_argument("--parsed-dir", action="append", default=[])
    parser.add_argument("--core", action="append", default=[], help="NAME=PATH")
    parser.add_argument("--interface", action="append", default=[])
    parser.add_argument("--mapping", action="append", default=[])
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    cores_dir = out_dir / "cores"
    interfaces_dir = out_dir / "interfaces"
    mappings_dir = out_dir / "mappings"

    for parsed_dir in args.parsed_dir:
        parsed_cores = Path(parsed_dir) / "cores"
        if parsed_cores.is_dir():
            copy_tree_contents(parsed_cores, cores_dir)

    for core_entry in args.core:
        name, _, path = core_entry.partition("=")
        dest = cores_dir / name
        if dest.exists():
            raise SystemExit(f"duplicate core '{name}' under {cores_dir}")
        dest.mkdir(parents=True)
        shutil.copy2(Path(path), dest / "module.yaml")

    for iface_yaml in args.interface:
        src = Path(iface_yaml)
        interfaces_dir.mkdir(parents=True, exist_ok=True)
        dest = interfaces_dir / src.name
        if dest.exists():
            raise SystemExit(f"duplicate interface '{src.name}' under {interfaces_dir}")
        shutil.copy2(src, dest)

    for mapping_yaml in args.mapping:
        src = Path(mapping_yaml)
        mappings_dir.mkdir(parents=True, exist_ok=True)
        dest = mappings_dir / src.name
        if dest.exists():
            raise SystemExit(f"duplicate mapping '{src.name}' under {mappings_dir}")
        shutil.copy2(src, dest)

    return 0


if __name__ == "__main__":
    sys.exit(main())
