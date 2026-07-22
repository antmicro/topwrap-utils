from sys import argv

import axi_interconnect_generator_plugin

if __name__ == "__main__":
    if len(argv) <= 1:
        print(f"Usage: {argv[0]} <output_file>")
    config = {
        "parameters": {
            "slaves": {
                "subordinate1": {"offset": 0x5000, "size": 0x100},
                "subordinate2": {"offset": 0x6000, "size": 0x100},
            },
            "masters": {
                "manager1": {"id_width": 2, "slaves": ["subordinate1", "subordinate2"]},
                "manager2": {"id_width": 2, "slaves": ["subordinate1", "subordinate2"]},
            },
            "atop": False,
        },
        "vlnv": "vendor:library:axi_intercon:1.0",
    }

    out = axi_interconnect_generator_plugin.generate_interconnect(config, "simple_interconnect")
    with open(argv[1], "w") as f:
        print(f"Writing to {argv[1]}")
        f.write(out)
