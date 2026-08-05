# Copyright (c) 2026 Antmicro <www.antmicro.com>
# SPDX-License-Identifier: Apache-2.0

"""Bazel rules for topwrap: parse HDL into IP cores, assemble a library, generate a design wrapper."""

load("@rules_hdl//verilog:providers.bzl", "VerilogInfo", "make_dag_entry", "make_verilog_info")
load(":providers.bzl", "TopwrapLibraryInfo")

_TOPWRAP = "//:topwrap"

def _topwrap_parse_sources_impl(ctx):
    out = ctx.actions.declare_directory(ctx.attr.name)

    hdl_dag = depset(transitive = [dep[VerilogInfo].dag for dep in ctx.attr.deps])
    dag_entries = hdl_dag.to_list()

    src_files = depset([f for entry in dag_entries for f in entry.srcs])
    all_files = depset([f for entry in dag_entries for f in entry.srcs + entry.hdrs + entry.data])

    args = ctx.actions.args()
    args.add("--repo", out.path)
    args.add("repo")
    args.add("parse")
    args.add(ctx.attr.name)
    args.add_all(src_files)

    ctx.actions.run(
        executable = ctx.executable._topwrap,
        arguments = [args],
        inputs = all_files,
        outputs = [out],
        mnemonic = "TopwrapParse",
        progress_message = "Parsing IP cores into topwrap library %s" % ctx.attr.name,
    )

    verilog_info = make_verilog_info(old_infos = [dep[VerilogInfo] for dep in ctx.attr.deps])

    return [
        DefaultInfo(files = depset([out])),
        TopwrapLibraryInfo(library_dir = out, hdl_dag = hdl_dag),
        verilog_info,
    ]

topwrap_parse_sources = rule(
    doc = "Parses verilog_library sources into a topwrap library directory (cores/ only).",
    implementation = _topwrap_parse_sources_impl,
    attrs = {
        "deps": attr.label_list(
            doc = "verilog_library targets to parse.",
            providers = [VerilogInfo],
        ),
        "_topwrap": attr.label(
            default = Label(_TOPWRAP),
            executable = True,
            cfg = "exec",
        ),
    },
)

def _topwrap_core_impl(ctx):
    out = ctx.actions.declare_directory(ctx.attr.name)

    args = ctx.actions.args()
    args.add(out.path)

    # name becomes this core's resource name under cores/.
    args.add("--core", "%s=%s" % (ctx.attr.name, ctx.file.yaml.path))

    ctx.actions.run(
        executable = ctx.executable._assemble_library,
        arguments = [args],
        inputs = [ctx.file.yaml],
        outputs = [out],
        mnemonic = "TopwrapCore",
        progress_message = "Assembling topwrap core %s" % ctx.attr.name,
    )

    hdl_dag = depset(transitive = [dep[VerilogInfo].dag for dep in ctx.attr.deps])

    verilog_info = make_verilog_info(
        new_entries = [make_dag_entry(
            srcs = [],
            hdrs = [],
            data = [],
            deps = ctx.attr.deps,
            label = ctx.label,
            tags = [],
        )],
        old_infos = [dep[VerilogInfo] for dep in ctx.attr.deps],
    )

    return [
        DefaultInfo(files = depset([out])),
        TopwrapLibraryInfo(library_dir = out, hdl_dag = hdl_dag),
        verilog_info,
    ]

topwrap_core = rule(
    doc = "Wraps a hand-authored module.yaml as a TopwrapLibraryInfo target. `name` must match the yaml's id.name.",
    implementation = _topwrap_core_impl,
    attrs = {
        "yaml": attr.label(
            doc = "Hand-authored module.yaml IP-core description.",
            allow_single_file = [".yaml", ".yml"],
        ),
        "deps": attr.label_list(
            doc = "Optional targets providing this core's real HDL.",
            providers = [VerilogInfo],
        ),
        "_assemble_library": attr.label(
            default = Label("//:assemble_library"),
            executable = True,
            cfg = "exec",
        ),
    },
)

def _topwrap_library_impl(ctx):
    out = ctx.actions.declare_directory(ctx.attr.name)

    parsed_dirs = [dep[TopwrapLibraryInfo].library_dir for dep in ctx.attr.cores]
    interfaces = ctx.files.interfaces
    mappings = ctx.files.mappings

    args = ctx.actions.args()
    args.add(out.path)
    args.add_all(parsed_dirs, before_each = "--parsed-dir", expand_directories = False)
    args.add_all(interfaces, before_each = "--interface")
    args.add_all(mappings, before_each = "--mapping")

    ctx.actions.run(
        executable = ctx.executable._assemble_library,
        arguments = [args],
        inputs = depset(parsed_dirs + interfaces + mappings),
        outputs = [out],
        mnemonic = "TopwrapAssembleLibrary",
        progress_message = "Assembling topwrap library %s" % ctx.attr.name,
    )

    hdl_dag = depset(transitive = [dep[TopwrapLibraryInfo].hdl_dag for dep in ctx.attr.cores])

    return [
        DefaultInfo(files = depset([out])),
        TopwrapLibraryInfo(library_dir = out, hdl_dag = hdl_dag),
    ]

topwrap_library = rule(
    doc = "Assembles a topwrap library (cores/, interfaces/, mappings/). `name` matches design.yaml's repo[name]:...",
    implementation = _topwrap_library_impl,
    attrs = {
        "cores": attr.label_list(
            doc = "topwrap_parse_sources and/or topwrap_core targets to merge in.",
            providers = [TopwrapLibraryInfo],
        ),
        "interfaces": attr.label_list(
            doc = "Interface definition YAMLs to include under interfaces/.",
            allow_files = [".yaml", ".yml"],
        ),
        "mappings": attr.label_list(
            doc = "Interface port mapping YAMLs to include under mappings/.",
            allow_files = [".yaml", ".yml"],
        ),
        "_assemble_library": attr.label(
            default = Label("//:assemble_library"),
            executable = True,
            cfg = "exec",
        ),
    },
)

def _topwrap_design_impl(ctx):
    build_dir = ctx.actions.declare_directory(ctx.attr.name + "_build")
    top_sv = ctx.actions.declare_file(ctx.attr.name + ".sv")

    library_dirs = [dep[TopwrapLibraryInfo].library_dir for dep in ctx.attr.deps]

    args = ctx.actions.args()
    args.add_all(library_dirs, before_each = "--repo", expand_directories = False)
    args.add("build")
    args.add("--design", ctx.file.design)
    args.add("--build-dir", build_dir.path)

    ctx.actions.run(
        executable = ctx.executable._topwrap,
        arguments = [args],
        inputs = depset([ctx.file.design] + library_dirs),
        outputs = [build_dir],
        mnemonic = "TopwrapBuild",
        progress_message = "Generating top-level design %s" % ctx.attr.name,
    )

    # topwrap names the output after the design's top module, not the
    # target name, so normalize it to a single known File.
    ctx.actions.run_shell(
        command = """
        set -euo pipefail
        files=("$1"/*.sv)
        if [ "${#files[@]}" -ne 1 ]; then
          echo "expected exactly one .sv file in $1, got: ${files[*]}" >&2
          exit 1
        fi
        cp "${files[0]}" "$2"
        """,
        arguments = [build_dir.path, top_sv.path],
        inputs = [build_dir],
        outputs = [top_sv],
        mnemonic = "TopwrapNormalizeOutput",
    )

    inherited_dag = depset(
        transitive = [dep[TopwrapLibraryInfo].hdl_dag for dep in ctx.attr.deps],
    )
    new_entry = make_dag_entry(
        srcs = [top_sv],
        hdrs = [],
        data = [],
        deps = [],
        label = ctx.label,
        tags = [],
    )
    verilog_info = VerilogInfo(dag = depset(
        direct = [new_entry],
        order = "postorder",
        transitive = [inherited_dag],
    ))

    return [
        DefaultInfo(files = depset([top_sv])),
        verilog_info,
    ]

topwrap_design = rule(
    doc = "Generates a top-level wrapper from a topwrap design.yaml as a VerilogInfo node.",
    implementation = _topwrap_design_impl,
    attrs = {
        "design": attr.label(
            doc = "The design.yaml to build.",
            allow_single_file = [".yaml", ".yml"],
        ),
        "deps": attr.label_list(
            doc = "topwrap_library targets resolving this design's repo[name]:... references.",
            providers = [TopwrapLibraryInfo],
        ),
        "_topwrap": attr.label(
            default = Label(_TOPWRAP),
            executable = True,
            cfg = "exec",
        ),
    },
)

def _gui_launcher_runfiles(ctx, extra_files = []):
    runfiles = ctx.runfiles(files = extra_files)
    runfiles = runfiles.merge(ctx.attr._topwrap[DefaultInfo].default_runfiles)
    return runfiles.merge(ctx.attr._bash_runfiles[DefaultInfo].default_runfiles)

def _gui_launcher_header(ctx):
    # Bazel Bash runfiles library init, v3. Verbatim copy of the boilerplate
    # documented at:
    # https://github.com/bazelbuild/rules_shell/blob/main/shell/runfiles/runfiles.bash#L70-L80
    runfiles_bash_init = """
f=bazel_tools/tools/bash/runfiles/runfiles.bash
source "${RUNFILES_DIR:-/dev/null}/$f" 2>/dev/null || \\
  source "$(grep -sm1 "^$f " "${RUNFILES_MANIFEST_FILE:-/dev/null}" | cut -f2- -d' ')" 2>/dev/null || \\
  source "$0.runfiles/$f" 2>/dev/null || \\
  source "$(grep -sm1 "^$f " "$0.runfiles_manifest" | cut -f2- -d' ')" 2>/dev/null || \\
  source "$(grep -sm1 "^$f " "$0.exe.runfiles_manifest" | cut -f2- -d' ')" 2>/dev/null || \\
  { echo >&2 "ERROR: cannot find $f"; exit 1; }
f=
"""
    return (
        "#!/usr/bin/env bash\nset -euo pipefail\n" + runfiles_bash_init +
        '\nTOPWRAP="$(rlocation %s/%s)"\n' % (ctx.workspace_name, ctx.executable._topwrap.short_path)
    )

_GUI_LAUNCHER_ATTRS = {
    "_topwrap": attr.label(default = Label(_TOPWRAP), executable = True, cfg = "exec"),
    "_bash_runfiles": attr.label(default = Label("@bazel_tools//tools/bash/runfiles")),
}

def _topwrap_gui_impl(ctx):
    launcher = ctx.actions.declare_file(ctx.label.name)
    content = _gui_launcher_header(ctx) + 'exec "$TOPWRAP" gui --preserve-parent-state "$@"\n'
    ctx.actions.write(output = launcher, content = content, is_executable = True)
    return [DefaultInfo(executable = launcher, runfiles = _gui_launcher_runfiles(ctx))]

topwrap_gui = rule(
    doc = "Runnable `topwrap gui` (forwards extra `bazel run` args).",
    implementation = _topwrap_gui_impl,
    executable = True,
    attrs = _GUI_LAUNCHER_ATTRS,
)

def _topwrap_design_gui_impl(ctx):
    launcher = ctx.actions.declare_file(ctx.label.name)
    library_dirs = [dep[TopwrapLibraryInfo].library_dir for dep in ctx.attr.deps]

    repo_flags = "".join([
        '--repo "$(rlocation %s/%s)" ' % (ctx.workspace_name, d.short_path)
        for d in library_dirs
    ])
    design_rloc = "%s/%s" % (ctx.workspace_name, ctx.file.design.short_path)

    content = _gui_launcher_header(ctx) + 'exec "$TOPWRAP" %sgui --preserve-parent-state --design "$(rlocation %s)" "$@"\n' % (repo_flags, design_rloc)
    ctx.actions.write(output = launcher, content = content, is_executable = True)

    runfiles = _gui_launcher_runfiles(ctx, extra_files = [ctx.file.design] + library_dirs)
    return [DefaultInfo(executable = launcher, runfiles = runfiles)]

topwrap_design_gui = rule(
    doc = "Runnable GUI launcher pre-populated with a design.yaml and topwrap_library deps.",
    implementation = _topwrap_design_gui_impl,
    executable = True,
    attrs = dict(
        _GUI_LAUNCHER_ATTRS,
        design = attr.label(
            doc = "The design.yaml to open.",
            allow_single_file = [".yaml", ".yml"],
        ),
        deps = attr.label_list(
            doc = "topwrap_library targets.",
            providers = [TopwrapLibraryInfo],
        ),
    ),
)
