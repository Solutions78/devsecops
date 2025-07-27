"""Public exports for orchestrator agents.

This module performs safe, lazy imports so that individual agent classes can be
imported even when optional dependencies (or the full package hierarchy) are
absent.  This is helpful for external test suites that run

    `from agents.docstring_generator import DocstringGeneratorAgent`

directly from the project root.
"""

from __future__ import annotations

from .base import BaseAgent  # always present

_export_names: list[str] = ["BaseAgent"]


def _safe_import(module_name: str, symbol: str) -> None:  # pragma: no cover
    """Attempt to import *symbol* from the sibling *module_name*.

    Any ImportError (or other exception) is swallowed so that the absence of an
    optional dependency does not break importers that only need a single agent
    class.
    """

    try:
        mod = __import__(f"{__name__}.{module_name}", fromlist=[symbol])
        globals()[symbol] = getattr(mod, symbol)
        _export_names.append(symbol)
    except Exception:
        # Skip modules that cannot be imported in the current environment.
        pass


_safe_import("code_review", "CodeReviewAgent")
_safe_import("test_engineer", "TestEngineerAgent")
_safe_import("execution_agent", "ExecutionAgent")
_safe_import("security_auditor", "SecurityAuditorAgent")
_safe_import("docstring_generator", "DocstringGeneratorAgent")
_safe_import("refactorer", "RefactorerAgent")
_safe_import("diff_annotator", "DiffAnnotatorAgent")
_safe_import("pr_summarizer", "PRSummarizerAgent")
_safe_import("orchestrator_agent", "OrchestratorAgent")

__all__ = _export_names

