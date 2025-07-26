# Claude Code Agents for DevSecOps Orchestrator

This document captures the complete list of Claude Code agents implemented in the AI-powered DevSecOps Orchestrator project. These agents operate as autonomous task-specific subprocesses within a CI/CD pipeline and are coordinated by an orchestrator agent for seamless code validation, transformation, and documentation.

---

## 1. `code-review`
**Purpose:** Performs general-purpose code reviews for logic errors, bad practices, anti-patterns, and maintainability.  
**Trigger:** Every time new or modified code is submitted.

## 2. `test-engineer`
**Purpose:** Generates and/or validates unit tests and integration tests for code that passes initial review.  
**Trigger:** After successful code review.

## 3. `execution-agent`
**Purpose:** Executes code or tests in a sandboxed environment to verify behavior and test correctness.  
**Trigger:** After tests are generated or updated.

## 4. `security-auditor`
**Purpose:** Performs static security analysis. Flags potential CVEs, unsafe libraries, injection vectors, secrets, etc.  
**Trigger:** After code passes functional tests.

## 5. `docstring-generator`
**Purpose:** Adds or updates docstrings for functions, classes, and modules to ensure inline developer documentation.  
**Trigger:** After successful audit and test pass.

## 6. `refactorer`
**Purpose:** Identifies and proposes improvements to structure, naming, and code modularity without altering functionality.  
**Trigger:** After tests and documentation generation.

## 7. `diff-annotator`
**Purpose:** Provides human-readable explanations of changes between commits or branches with impact analysis.  
**Trigger:** At the time of pull request or commit diff view.

## 8. `pr-summarizer`
**Purpose:** Summarizes code contributions, changes, rationale, and impact into a clean PR description or changelog.  
**Trigger:** On PR creation.

## 9. `orchestrator-agent`
**Purpose:** Central control agent that tracks project state, determines agent execution order, queues task routing, and monitors completion or error states.  
**Trigger:** Always running as the CI/CD pipeline backbone.

---

Each agent is configured manually using Claude Code's personal agent setup and invoked automatically via task flow orchestration or interactively via the Claude Code console, API, or future dashboard interface.
