import os
import platform
import sys


def use_generic_cpu_on_windows_arm64():
    # LLVM aborts with "incomplete machine model" when targeting some Windows
    # ARM64 CPUs (e.g. Snapdragon X, "oryon-1"), so target a generic CPU there.
    if sys.platform != "win32" or platform.machine() != "ARM64":
        return
    if "NUMBA_CPU_NAME" in os.environ:
        return

    os.environ["NUMBA_CPU_NAME"] = "generic"

    from numba.core import codegen, config
    from numba.core.registry import cpu_target
    from numba.core.runtime import nrt

    config.reload_config()

    # Numba builds its code generator for the host CPU when the first function
    # is decorated, usually before it loads Rocket-FFT through its extension
    # entry point. At that point at most the NRT has been compiled, so rebuild
    # the code generator and recompile the NRT with it.
    if "_toplevel_target_context" not in cpu_target.__dict__:
        return
    target_context = cpu_target.target_context
    target_context._internal_codegen = codegen.JITCPUCodegen("numba.exec")
    if nrt.rtsys._init:
        nrt.rtsys._init = False
        nrt.rtsys.initialize(target_context)
