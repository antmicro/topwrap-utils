import importlib.resources
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict

import yaml


def generate_interconnect(config: Dict, name: str):
    plugin_path = importlib.resources.files("axi_interconnect_generator_plugin")
    original_path = sys.path
    original_path.append(str(plugin_path / "third_party" / "axi" / "scripts"))
    import axi_intercon_gen

    with (
        tempfile.NamedTemporaryFile(mode="w") as config_file,
        tempfile.NamedTemporaryFile(mode="r") as sv_file,
        tempfile.TemporaryDirectory() as temp_dir_str,
    ):
        temp_dir = Path(temp_dir_str)
        old_path = os.getcwd()
        try:
            os.chdir(temp_dir)

            params = config.get("parameters", {})
            params["output_file"] = sv_file.name
            config["parameters"] = params

            yaml_config = yaml.safe_dump(config)
            config_file.write(yaml_config)
            config_file.flush()

            axi_intercon_gen.AxiIntercon(name, config_file.name).write()
            out = sv_file.read()
            return out
        finally:
            os.chdir(old_path)
            sys.path = original_path


def _bender_files(package_path):
    """Return the HDL sources enabled by default in a Bender manifest."""
    manifest = yaml.safe_load((package_path / "Bender.yml").read_text())
    # NOTE: Exact string match, uses targets these vendored manifests define today.
    default_targets = {"not(all(xilinx,vivado_ipx))", "not(cc_no_deprecated)"}
    source_paths = []
    for entry in manifest["sources"]:
        if isinstance(entry, str):
            source_paths.append(entry)
        elif entry.get("target") in default_targets:
            source_paths.extend(entry["files"])
    return [str(package_path / path) for path in source_paths]


def get_dependencies():
    """Return the vendored common_cells and AXI sources in compile order."""
    plugin_path = importlib.resources.files("axi_interconnect_generator_plugin")
    third_party = plugin_path / "third_party"
    return _bender_files(third_party / "common_cells") + _bender_files(third_party / "axi")


def get_includes():
    plugin_path = importlib.resources.files("axi_interconnect_generator_plugin")
    files = [
        f"{plugin_path}/third_party/common_cells/include",
        f"{plugin_path}/third_party/axi/include",
    ]
    return files
