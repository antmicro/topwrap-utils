# Copyright (c) 2026 Antmicro <www.antmicro.com>
# SPDX-License-Identifier: Apache-2.0

"""Providers used to compose topwrap Bazel rules."""

TopwrapLibraryInfo = provider(
    doc = """A topwrap library directory (cores/, interfaces/, mappings/)""",
    fields = {
        "library_dir": "Directory artifact holding the assembled library (topwrap repo).",
        "hdl_dag": "depset of VerilogInfo DAG entries from the real HDL this library's cores were parsed from.",
    },
)
