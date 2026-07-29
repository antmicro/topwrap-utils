from dataclasses import dataclass
from functools import cache
from pathlib import Path

from jinja2 import Template
from topwrap.model.design import Design
from topwrap.model.module import Module
from typing_extensions import Optional, cast

from renode_plugin.repl import RenodeMapping

TEMPLATES_DIR = Path(__file__).parent / "templates"
TEMPLATE_NAME = "cpu_uart.j2"

# Why load the template here? Due to some **really** weird bug,
# *if* the template is constructed while the plugin-runner in topwrap
# is running hooks, python will suffer a segfault when shutting down
# (yes, segfault). This does not happen if the template is loaded
# here (or at some point before any hooks are invoked).
TEMPLATE = Template((TEMPLATES_DIR / TEMPLATE_NAME).read_text())


@cache
def _load_template(name: str) -> Template:
    path = TEMPLATES_DIR / name
    template = path.read_text()
    return Template(template)


@dataclass
class CPUInfo:
    name: str  # name of cpu module instance
    elf: str  # path to elf


class RESC_Simple:
    def __init__(
        self,
        design_name: str,
        repl_path: str,
        cpu: Optional[str] = None,
        elf: Optional[str] = None,
        analyzers: Optional[list[str]] = None,
    ):
        self._name = design_name
        self._cpu = cpu
        self._analyzers = [] if analyzers is None else analyzers
        self._elf = elf
        self._repl_path = repl_path

        if not self._is_valid():
            raise ValueError(f"Missing elf file for CPU {self._cpu}")

    def _is_valid(self) -> bool:
        no_cpu = self._cpu is None
        return no_cpu or self._elf is not None

    def render_template(self) -> str:
        keys = {"name": self._name, "repl_path": self._repl_path, "analyzers": self._analyzers}

        if self._cpu is not None and self._elf is not None:
            keys.update({"cpu": CPUInfo(self._cpu, self._elf)})

        return TEMPLATE.render(**keys)

    @staticmethod
    def from_top_module(top_module: Module, repl_path: str, renode_map: RenodeMapping):
        if top_module.design is None:
            raise ValueError(f"{top_module.id.combined()} is not a top level module")
        design = cast(Design, top_module.design)
        name = design.parent.id.name

        extension_data = design.extensions.find_by_name("renode_resc")

        if extension_data is None:
            return RESC_Simple(design_name=name, repl_path=repl_path)

        data = extension_data.data
        if not isinstance(data, dict):
            raise TypeError(
                f"extension field {extension_data.name} in {top_module.id.combined()} is not a dict"
            )

        collected_keys: set[str] = set()

        cpu_name = None
        elf_path = None
        analyzers = []

        if "cpu" in data:
            collected_keys.add("cpu")

            cpu_info = data["cpu"]

            if not isinstance(cpu_info, list) and not all(isinstance(i, str) for i in cpu_info):
                raise TypeError(
                    f"extension field {extension_data.name}.cpu is not a list of strings"
                )

            if len(cpu_info) != 2:
                raise ValueError(
                    f"extension field {extension_data.name}.cpu can only contain two items"
                )

            cpu_name, elf_path = cast(list[str], cpu_info)

        if "analyze" in data:
            collected_keys.add("analyze")

            analyzers_list = data["analyze"]

            if not isinstance(analyzers_list, list) and not all(
                isinstance(a, str) for a in analyzers_list
            ):
                raise TypeError(
                    f"extension field {extension_data.name}.analyze is not a list of strings"
                )

            analyzers = cast(list[str], analyzers_list)

        if cpu_name and cpu_name not in renode_map:
            raise ValueError(f"{cpu_name} does not have a Renode peripheral map")

        for analyzer in analyzers:
            if analyzer not in renode_map:
                raise ValueError(f"{analyzer} does not have a Renode peripheral map")

        return RESC_Simple(
            design_name=name, repl_path=repl_path, cpu=cpu_name, elf=elf_path, analyzers=analyzers
        )
