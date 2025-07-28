"""backend.orchestrator – DevSecOps AI Orchestrator core package.

This package lives under *backend.orchestrator* to keep the repository
organised.  Unfortunately a few consumer modules – including some tests that
ship with the project – attempt to import it directly via the shorter
``orchestrator`` module path::

    from orchestrator.event_bus import EventBus

To stay backwards-compatible we *alias* the current package to that top-level
name at **import time**.  This approach avoids the need for physical
duplicates or `sys.path` hacks sprinkled throughout the code-base.
"""

from __future__ import annotations

import importlib
import sys as _sys

# ---------------------------------------------------------------------------
# Expose *backend.orchestrator* as a top-level alias (``orchestrator``)
# ---------------------------------------------------------------------------

_sys.modules.setdefault("orchestrator", _sys.modules[__name__])


def _export_submodule(name: str) -> None:  # noqa: D401 – small helper, not public API
    """Re-export *backend.orchestrator.<name>* under *orchestrator.<name>*.

    Ensures that ``import orchestrator.<name>`` returns the exact same module
    object as ``import backend.orchestrator.<name>`` so that there is no
    ambiguity or duplication.
    """

    full = f"backend.orchestrator.{name}"
    module = importlib.import_module(full)
    _sys.modules[f"orchestrator.{name}"] = module


# Eagerly publish the most frequently used sub-modules.  If any of them is
# missing (e.g. optional dependencies) we silently ignore the error so that
# late-binding remains possible.
for _submodule in (
    "event_bus",
    "task_router",
    "agent_manager",
    "models",
    "agents",
):
    try:
        _export_submodule(_submodule)
    except ModuleNotFoundError:
        pass

