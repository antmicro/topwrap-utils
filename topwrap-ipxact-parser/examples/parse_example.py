#!/usr/bin/env python3
# Copyright (c) 2026 Antmicro <www.antmicro.com>
# SPDX-License-Identifier: Apache-2.0

"""Parse a minimal IP-XACT component and print its ports."""

from pathlib import Path

import topwrap_ipxact_parser as ipxact

COMPONENT_PATH = Path(__file__).parent / "simple_component.xml"


def main() -> None:
    component = ipxact.parse(COMPONENT_PATH, True)

    print(f"Component: {component.vendor}:{component.library}:{component.name}:{component.version}")
    for port in component.model.ports.port:
        width = "1 bit"
        if port.wire.vectors:
            vector = port.wire.vectors.vector[0]
            width = f"[{vector.left.get_valueOf_()}:{vector.right.get_valueOf_()}]"
        print(f"  port {port.name}: {port.wire.direction} {width}")


if __name__ == "__main__":
    main()
