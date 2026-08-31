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


def get_dependencies():
    plugin_path = importlib.resources.files("axi_interconnect_generator_plugin")
    files = [
        f"{plugin_path}/third_party/common_cells/src/cc_addr_decode_dync.sv",
        f"{plugin_path}/third_party/common_cells/src/cc_spill_register_flushable.sv",
        f"{plugin_path}/third_party/common_cells/src/cc_delta_counter.sv",
        f"{plugin_path}/third_party/common_cells/src/cc_lzc.sv",
        f"{plugin_path}/third_party/common_cells/src/cc_addr_decode.sv",
        f"{plugin_path}/third_party/axi/src/axi_demux_id_counters.sv",
        f"{plugin_path}/third_party/common_cells/src/cc_fifo.sv",
        f"{plugin_path}/third_party/common_cells/src/cc_spill_register.sv",
        f"{plugin_path}/third_party/common_cells/src/cc_counter.sv",
        f"{plugin_path}/third_party/common_cells/src/cc_rr_arb_tree.sv",
        f"{plugin_path}/third_party/common_cells/src/cc_pkg.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/binary_to_gray.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/cb_filter_pkg.sv",
        f"{plugin_path}/third_party/common_cells/src/cc_onehot.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/cf_math_pkg.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/clk_int_div.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/credit_counter.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/delta_counter.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/ecc_pkg.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/edge_propagator_tx.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/exp_backoff.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/fifo_v3.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/gray_to_binary.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/isochronous_4phase_handshake.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/isochronous_spill_register.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/lfsr.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/lfsr_16bit.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/lfsr_8bit.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/multiaddr_decode.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/mv_filter.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/onehot_to_bin.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/plru_tree.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/passthrough_stream_fifo.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/popcount.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/rr_arb_tree.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/rstgen_bypass.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/serial_deglitch.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/shift_reg.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/shift_reg_gated.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/spill_register_flushable.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/stream_demux.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/stream_filter.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/stream_fork.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/stream_intf.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/stream_join.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/stream_join_dynamic.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/stream_mux.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/stream_throttle.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/sub_per_hash.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/sync.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/sync_wedge.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/unread.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/read.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/cdc_reset_ctrlr_pkg.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/addr_decode_dync.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/cdc_2phase.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/cdc_4phase.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/cb_filter.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/cdc_fifo_2phase.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/counter.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/ecc_decode.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/ecc_encode.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/edge_detect.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/lzc.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/max_counter.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/rstgen.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/spill_register.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/stream_delay.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/stream_fifo.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/stream_fork_dynamic.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/clk_mux_glitch_free.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/addr_decode.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/addr_decode_napot.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/cdc_reset_ctrlr.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/cdc_fifo_gray.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/fall_through_register.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/id_queue.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/stream_to_mem.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/stream_arbiter_flushable.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/stream_fifo_optimal_wrap.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/stream_register.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/stream_xbar.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/cdc_fifo_gray_clearable.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/cdc_2phase_clearable.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/mem_to_banks_detailed.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/stream_arbiter.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/stream_omega_net.sv",
        f"{plugin_path}/third_party/common_cells/src/deprecated/mem_to_banks.sv",
        f"{plugin_path}/third_party/axi/src/axi_pkg.sv",
        f"{plugin_path}/third_party/axi/src/axi_intf.sv",
        f"{plugin_path}/third_party/axi/src/axi_atop_filter.sv",
        f"{plugin_path}/third_party/axi/src/axi_burst_splitter_gran.sv",
        f"{plugin_path}/third_party/axi/src/axi_burst_unwrap.sv",
        f"{plugin_path}/third_party/axi/src/axi_bus_compare.sv",
        f"{plugin_path}/third_party/axi/src/axi_cdc_dst.sv",
        f"{plugin_path}/third_party/axi/src/axi_cdc_src.sv",
        f"{plugin_path}/third_party/axi/src/axi_cut.sv",
        f"{plugin_path}/third_party/axi/src/axi_delayer.sv",
        f"{plugin_path}/third_party/axi/src/axi_demux_simple.sv",
        f"{plugin_path}/third_party/axi/src/axi_dw_downsizer.sv",
        f"{plugin_path}/third_party/axi/src/axi_dw_upsizer.sv",
        f"{plugin_path}/third_party/axi/src/axi_fifo.sv",
        f"{plugin_path}/third_party/axi/src/axi_fifo_delay_dyn.sv",
        f"{plugin_path}/third_party/axi/src/axi_id_remap.sv",
        f"{plugin_path}/third_party/axi/src/axi_id_prepend.sv",
        f"{plugin_path}/third_party/axi/src/axi_isolate.sv",
        f"{plugin_path}/third_party/axi/src/axi_join.sv",
        f"{plugin_path}/third_party/axi/src/axi_lite_demux.sv",
        f"{plugin_path}/third_party/axi/src/axi_lite_dw_converter.sv",
        f"{plugin_path}/third_party/axi/src/axi_lite_from_mem.sv",
        f"{plugin_path}/third_party/axi/src/axi_lite_join.sv",
        f"{plugin_path}/third_party/axi/src/axi_lite_lfsr.sv",
        f"{plugin_path}/third_party/axi/src/axi_lite_mailbox.sv",
        f"{plugin_path}/third_party/axi/src/axi_lite_mux.sv",
        f"{plugin_path}/third_party/axi/src/axi_lite_regs.sv",
        f"{plugin_path}/third_party/axi/src/axi_lite_to_apb.sv",
        f"{plugin_path}/third_party/axi/src/axi_lite_to_axi.sv",
        f"{plugin_path}/third_party/axi/src/axi_modify_address.sv",
        f"{plugin_path}/third_party/axi/src/axi_mux.sv",
        f"{plugin_path}/third_party/axi/src/axi_rw_join.sv",
        f"{plugin_path}/third_party/axi/src/axi_rw_split.sv",
        f"{plugin_path}/third_party/axi/src/axi_serializer.sv",
        f"{plugin_path}/third_party/axi/src/axi_slave_compare.sv",
        f"{plugin_path}/third_party/axi/src/axi_throttle.sv",
        f"{plugin_path}/third_party/axi/src/axi_to_detailed_mem.sv",
        f"{plugin_path}/third_party/axi/src/axi_burst_splitter.sv",
        f"{plugin_path}/third_party/axi/src/axi_cdc.sv",
        f"{plugin_path}/third_party/axi/src/axi_demux.sv",
        f"{plugin_path}/third_party/axi/src/axi_err_slv.sv",
        f"{plugin_path}/third_party/axi/src/axi_dw_converter.sv",
        f"{plugin_path}/third_party/axi/src/axi_from_mem.sv",
        f"{plugin_path}/third_party/axi/src/axi_id_serialize.sv",
        f"{plugin_path}/third_party/axi/src/axi_lfsr.sv",
        f"{plugin_path}/third_party/axi/src/axi_multicut.sv",
        f"{plugin_path}/third_party/axi/src/axi_to_axi_lite.sv",
        f"{plugin_path}/third_party/axi/src/axi_to_mem.sv",
        f"{plugin_path}/third_party/axi/src/axi_zero_mem.sv",
        f"{plugin_path}/third_party/axi/src/axi_interleaved_xbar.sv",
        f"{plugin_path}/third_party/axi/src/axi_iw_converter.sv",
        f"{plugin_path}/third_party/axi/src/axi_lite_xbar.sv",
        f"{plugin_path}/third_party/axi/src/axi_xbar_unmuxed.sv",
        f"{plugin_path}/third_party/axi/src/axi_to_mem_banked.sv",
        f"{plugin_path}/third_party/axi/src/axi_to_mem_interleaved.sv",
        f"{plugin_path}/third_party/axi/src/axi_to_mem_split.sv",
        f"{plugin_path}/third_party/axi/src/axi_xbar.sv",
        f"{plugin_path}/third_party/axi/src/axi_xp.sv",
    ]
    return files


def get_includes():
    plugin_path = importlib.resources.files("axi_interconnect_generator_plugin")
    files = [
        f"{plugin_path}/third_party/common_cells/include",
        f"{plugin_path}/third_party/axi/include",
    ]
    return files
