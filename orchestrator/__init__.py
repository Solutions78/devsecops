# This shim package exists solely for backward-compatibility with test suites or
# external code that import `orchestrator.*` directly.  The actual code lives
# in `backend.orchestrator`.  We re-export that package under the top-level
# name `orchestrator` so the two import paths resolve to the same module
# object, preventing duplication or import errors.

from importlib import import_module
import sys as _sys

_backend_pkg = import_module("backend.orchestrator")

# Expose public attributes of backend.orchestrator at this level.
globals().update({name: getattr(_backend_pkg, name) for name in dir(_backend_pkg) if not name.startswith("__")})

# Make sure `sys.modules["orchestrator"]` (this package) and
# `sys.modules["backend.orchestrator"]` refer to the same object so that
# subsequent sub-module imports (e.g. `orchestrator.event_bus`) work
# seamlessly.
_sys.modules[__name__] = _backend_pkg

