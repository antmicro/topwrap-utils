import logging
from pathlib import Path

from topwrap.model.design import Design
from topwrap.plugin.base import BasePlugin, BuildContext, OutputDir
from typing_extensions import cast

from renode_plugin.repl import (
    RENODE_GUEST_PAGE_SIZE,
    REPL_PREAMBLE,
    RenodeDeviceFieldResolve,
    RenodeMapping,
    RenodePlatform,
    create_resolvers,
    create_resolvers_mod,
    parse_external,
    parse_output_maps,
    render_hex,
    resolve_memorymap,
    resolve_top_output,
)
from renode_plugin.resc import RESC_Simple

logger = logging.getLogger(__name__)


class RenodePeripheralGen(BasePlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.outputs: dict[str, str] = {}

    def post_transform(self, ctx: BuildContext):
        top_module = ctx.top_module
        if not top_module:
            logger.error("expected top module to exist")
            exit(1)

        if not top_module.design:
            logger.error("expected top-level design")
            exit(1)

        resolvers: dict[str, RenodeDeviceFieldResolve] = {}

        for mod in ctx.repo_modules:
            res = create_resolvers_mod(mod)
            if res:
                module_id = res.get_module_id().combined()
                if module_id in resolvers:
                    logger.error(
                        "internal error, duplicate modules encountered when creating resolvers"
                    )
                    exit(1)
                resolvers[module_id] = res

        top_design = cast(Design, top_module.design)

        output_maps = parse_output_maps(top_design)

        for resolver in create_resolvers(top_design):
            module_id = resolver.get_module_id().combined()
            logger.info(f"top level design overrides resolver for {module_id}")
            resolvers[module_id] = resolver

        resolver_list = list(resolvers.values())
        renode_mapping = RenodeMapping.create_mapping(resolver_list, top_design)

        memory_map = resolve_memorymap(top_design, renode_mapping)

        for i_name, mm in memory_map.items():
            if mm is None:
                logger.info(f"Resolved memory map for {i_name}: (,)")
            else:
                logger.info(
                    f"Resolved memory map for {i_name}: "
                    f"({render_hex(mm.offset, 4)}, {mm.get_aligned_size(RENODE_GUEST_PAGE_SIZE)})"
                )

        platform = RenodePlatform.define(renode_mapping, memory_map)

        if not output_maps:
            print(platform.render_config(REPL_PREAMBLE, [], None))

        for output in output_maps:
            src = platform.render_config(REPL_PREAMBLE, output.includes, output.device_filter)
            self.outputs[output.filename] = src

        resc_gen = RESC_Simple.from_top_module(top_module, renode_mapping)

        if not resc_gen.has_repl():
            external_input = parse_external(top_design)
            top_output = resolve_top_output(output_maps, external_input)
            resc_gen.set_repl_path(top_output.filename)

        self.outputs[str(Path(top_output.filename).with_suffix(".resc"))] = (
            resc_gen.render_template()
        )

    def pre_output_writing(self, ctx: BuildContext, target_dir: OutputDir):
        for filename, src in self.outputs.items():
            out_path = target_dir.target_dir / filename
            if out_path.exists() and out_path.is_dir():
                logger.error("cannot write to a directory")
                exit(1)
            if out_path.suffix == ".repl":
                logger.info(f"writing REPL: {out_path}")
            if out_path.suffix == ".resc":
                logger.info(f"writing RESC: {out_path}")
            out_path.write_text(src)
