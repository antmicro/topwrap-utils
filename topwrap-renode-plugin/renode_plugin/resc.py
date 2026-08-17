from dataclasses import dataclass
from functools import cache
from pathlib import Path

from jinja2 import Template
from topwrap.model.design import Design
from topwrap.model.module import Module
from typing_extensions import Any, Optional, cast

from renode_plugin.repl import RenodeMapping

TEMPLATES_DIR = Path(__file__).parent / "templates"
TEMPLATE_NAME = "cpu_uart.j2"

# Why load the template here? Due to some **really** weird bug,
# *if* the template is constructed while the plugin-runner in topwrap
# is running hooks, python will suffer a segfault when shutting down
# (yes, segfault). This does not happen if the template is loaded
# here (or at some point before any hooks are invoked).
TEMPLATE = Template((TEMPLATES_DIR / TEMPLATE_NAME).read_text())

FEATURES = frozenset(["no_run", "reset_macro", "mem_mailbox"])


@cache
def _load_template(name: str) -> Template:
    path = TEMPLATES_DIR / name
    template = path.read_text()
    return Template(template)


@dataclass
class CPUInfo:
    name: str  # name of cpu module instance
    elf: str  # path to elf


def _parse_cpus(name: str, cpu_info: Any, renode_map: RenodeMapping) -> tuple[list[str], list[str]]:
    cpu_names = []
    elf_paths = []

    if (
        not isinstance(cpu_info, list)
        and not all(isinstance(entry, list) for entry in cpu_info)
        and not all(all(isinstance(item, str) for item in entry) for entry in cpu_info)
    ):
        raise TypeError(f"extension field {name}.cpus is not a list of cpu-elf pairs")

    if not all(len(entry) == 2 for entry in cpu_info):
        raise ValueError(f"extension field {name}.cpus[*] can only contain two items")

    for entry in cast(list[list[str]], cpu_info):
        cpu_name, elf_path = entry

        if cpu_name not in renode_map:
            raise ValueError(f"{cpu_name} does not have a Renode peripheral map")

        cpu_names.append(cpu_name)
        elf_paths.append(elf_path)

    return cpu_names, elf_paths


def _parse_analyze(name: str, analyzers_list: Any, renode_map: RenodeMapping) -> list[str]:
    if not isinstance(analyzers_list, list) and not all(isinstance(a, str) for a in analyzers_list):
        raise TypeError(f"extension field {name}.analyze is not a list of strings")

    analyzers = cast(list[str], analyzers_list)

    for analyzer in analyzers:
        if analyzer not in renode_map:
            raise ValueError(f"{analyzer} does not have a Renode peripheral map")

    return analyzers


def _parse_features(name: str, features: Any) -> set[str]:
    if not isinstance(features, list) and not all(isinstance(f, str) for f in features):
        raise TypeError(f"extension field {name}.features is not a list of strings")

    for f in features:
        if f not in FEATURES:
            raise ValueError(f"Unknown feature {f}")

    return set(cast(list[str], features))


def _parse_repl(name: str, repl: Any) -> str:
    if not isinstance(repl, str):
        raise TypeError(f"extension field {name}.repl is not a string")
    return repl


class RESC_Simple:
    def __init__(
        self,
        design_name: str,
        repl_path: Optional[str] = None,
        cpus: Optional[list[str]] = None,
        elfs: Optional[list[str]] = None,
        analyzers: Optional[list[str]] = None,
        features: Optional[set[str]] = None,
    ):
        self._name = design_name
        self._cpus = cpus
        self._analyzers = [] if analyzers is None else analyzers
        self._elfs = elfs
        self._repl_path = repl_path
        self._features = features

        if not self._is_valid():
            raise ValueError("Missing elf file for one or more CPUs")

    def _is_valid(self) -> bool:
        return self._cpus is None or (self._elfs is not None and len(self._cpus) == len(self._elfs))

    def has_repl(self) -> bool:
        return self._repl_path is not None

    def set_repl_path(self, path: str):
        self._repl_path = path

    def render_template(self) -> str:
        keys = {
            "name": self._name,
            "repl_path": self._repl_path,
            "analyzers": self._analyzers,
            "start": True,
            "reset_macro": False,
            "add_mem_mailbox": False,
        }

        if self._cpus is not None and self._elfs is not None:
            cpus = []
            for cpu, elf in zip(self._cpus, self._elfs, strict=False):
                cpus.append(CPUInfo(cpu, elf))
            keys.update({"cpus": cpus})

        if self._features:
            if "no_run" in self._features:
                keys["start"] = False
            if "reset_macro" in self._features:
                keys["reset_macro"] = True
            if "mem_mailbox" in self._features:
                keys["add_mem_mailbox"] = True

        return TEMPLATE.render(**keys)

    @staticmethod
    def from_top_module(top_module: Module, renode_map: RenodeMapping) -> "RESC_Simple":
        if top_module.design is None:
            raise ValueError(f"{top_module.id.combined()} is not a top level module")
        design = cast(Design, top_module.design)
        name = design.parent.id.name

        extension_data = design.extensions.find_by_name("renode_resc")

        if extension_data is None:
            return RESC_Simple(design_name=name)

        data = extension_data.data
        if not isinstance(data, dict):
            raise TypeError(
                f"extension field {extension_data.name} in {top_module.id.combined()} is not a dict"
            )

        repl_path = None
        cpu_names = []
        elf_paths = []
        analyzers = []
        feature_set = None

        if "cpus" in data:
            cpu_names, elf_paths = _parse_cpus(extension_data.name, data["cpus"], renode_map)

        if "analyze" in data:
            analyzers = _parse_analyze(extension_data.name, data["analyze"], renode_map)

        if "features" in data:
            feature_set = _parse_features(extension_data.name, data["features"])

        if "repl" in data:
            repl_path = _parse_repl(extension_data.name, data["repl"])

        return RESC_Simple(
            design_name=name,
            repl_path=repl_path,
            cpus=cpu_names,
            elfs=elf_paths,
            analyzers=analyzers,
            features=feature_set,
        )
