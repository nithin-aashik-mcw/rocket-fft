import os
import platform
import sys


def use_generic_cpu_on_windows_arm64():
    # Target a generic CPU on Windows ARM64 unless the user chose one
    if sys.platform != "win32" or platform.machine() != "ARM64":
        return
    if "NUMBA_CPU_NAME" in os.environ:
        return

    os.environ["NUMBA_CPU_NAME"] = "generic"

    from numba.core import codegen, config
    from numba.core.registry import cpu_target
    from numba.core.runtime import nrt

    config.reload_config()

    # The codegen may already exist for the host CPU; rebuild it and the NRT
    if "_toplevel_target_context" not in cpu_target.__dict__:
        return
    target_context = cpu_target.target_context
    target_context._internal_codegen = codegen.JITCPUCodegen("numba.exec")
    if nrt.rtsys._init:
        nrt.rtsys._init = False
        nrt.rtsys.initialize(target_context)
