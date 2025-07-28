"""Public exports for orchestrator agents.

This module performs safe, lazy imports so that individual agent classes can be
imported even when optional dependencies (or the full package hierarchy) are
absent.  This is helpful for external test suites that run

    `from agents.docstring_generator import DocstringGeneratorAgent`

directly from the project root.
"""

from __future__ import annotations

try:
    from .base_agent import BaseAgent  # always present
except ImportError:
    import sys
    import os
    # Ensure we can find the base module
    current_dir = os.path.dirname(__file__)
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    from base_agent import BaseAgent  # always present

_export_names: list[str] = ["BaseAgent"]


def _safe_import(module_name: str, symbol: str) -> None:  # pragma: no cover
    """Attempt to import *symbol* from the sibling *module_name*.

    Any ImportError (or other exception) is swallowed so that the absence of an
    optional dependency does not break importers that only need a single agent
    class.
    """

    try:
        # Try relative import first
        try:
            mod = __import__(f"{__name__}.{module_name}", fromlist=[symbol])
        except ImportError:
            # Try absolute import
            import sys
            import os
            current_dir = os.path.dirname(__file__)
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            mod = __import__(module_name, fromlist=[symbol])
        
        globals()[symbol] = getattr(mod, symbol)
        _export_names.append(symbol)
    except Exception as e:
        # For debugging, print the error
        import sys
        print(f"Warning: Could not import {symbol} from {module_name}: {e}", file=sys.stderr)
        pass


_safe_import("code_review_agent", "CodeReviewAgent")
_safe_import("test_engineer_agent", "TestEngineerAgent")
_safe_import("execution_agent", "ExecutionAgent")
_safe_import("security_auditor_agent", "SecurityAuditorAgent")
_safe_import("docstring_generator_agent", "DocstringGeneratorAgent")
_safe_import("refactorer_agent", "RefactorerAgent")
_safe_import("diff_annotator_agent", "DiffAnnotatorAgent")
_safe_import("pr_summarizer_agent", "PRSummarizerAgent")
_safe_import("orchestrator_agent", "OrchestratorAgent")

__all__ = _export_names

