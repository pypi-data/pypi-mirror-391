"""Claude Code-inspired workflow and persona presets."""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class WorkflowPreset:
    """Metadata describing a guided workflow."""

    slug: str
    title: str
    description: str
    prompt: str
    phases: Tuple[str, ...] = ()


@dataclass(frozen=True)
class PersonaPreset:
    """Metadata describing a specialized agent persona."""

    slug: str
    title: str
    description: str
    prompt: str


def _clean(text: str) -> str:
    return textwrap.dedent(text).strip()


WORKFLOW_PRESETS: Dict[str, WorkflowPreset] = {
    "feature-dev": WorkflowPreset(
        slug="feature-dev",
        title="Feature Development",
        description="Seven-phase workflow for clarifying requirements, exploring the codebase, "
        "designing architecture, implementing, and reviewing changes.",
        phases=(
            "Discovery",
            "Codebase Exploration",
            "Clarifying Questions",
            "Architecture Design",
            "Implementation",
            "Quality Review",
            "Summary",
        ),
        prompt=_clean(
            """
            # Claude Code Feature Development Workflow

            Follow an explicit seven-phase plan inspired by the claude-code feature-dev command.

            1. **Discovery** – capture the initial request, create a todo list covering every phase,
               and restate the objective.
            2. **Codebase Exploration** – launch multiple investigations (code explorers, searches,
               or summaries) that surface 5–10 critical files to read. Digest those files before acting.
            3. **Clarifying Questions** – list every ambiguity (edge cases, performance, UX, rollout)
               and wait for answers before designing anything.
            4. **Architecture Design** – compare at least two approaches (minimal change, clean
               architecture, pragmatic) and recommend one with trade-offs.
            5. **Implementation** – only begin after the user approves the plan. Respect existing
               patterns that were discovered earlier and keep Todos updated.
            6. **Quality Review** – run targeted reviews (tests, code reviewer personas, linters) until
               confidence is high. Summarize any issues before fixing.
            7. **Summary** – close the loop with a what/why/how recap, files touched, and next steps.

            Use the TodoWrite tool (or an equivalent log) to track progress and decisions. Never skip a
            phase; if information is missing, pause and ask for it. Be explicit about which phase you are
            in when communicating with the user so they understand the flow.
            """
        ),
    ),
    "pr-review": WorkflowPreset(
        slug="pr-review",
        title="PR Review Toolkit",
        description="Multi-agent pull request review that mirrors claude-code's PR review command.",
        phases=(
            "Scope",
            "Detect Changes",
            "Launch Review Agents",
            "Aggregate Findings",
            "Action Plan",
        ),
        prompt=_clean(
            """
            # Claude Code PR Review Toolkit

            Run a comprehensive pull-request style review inspired by claude-code's pr-review-toolkit.

            - Determine the review scope (default to unstaged `git diff`). Respect user-specified
              aspects such as `comments`, `tests`, `errors`, `types`, `code`, `simplify`, or `all`.
            - Identify changed files and map them to specialized reviewers:
              * `code-reviewer` – general quality and CLAUDE.md alignment.
              * `pr-test-analyzer` – coverage and test completeness.
              * `comment-analyzer` – documentation and comment accuracy.
              * `silent-failure-hunter` – exception handling and fallbacks.
              * `type-design-analyzer` – invariants and type safety.
              * `code-simplifier` – optional polish step once findings are addressed.
            - Launch reviews sequentially (clearer) or in parallel (faster) and summarize each output.
            - Aggregate issues by severity: **Critical**, **Important**, **Suggestions**, plus
              **Strengths** to highlight wins.
            - Provide an actionable order of operations (fix critical, then important, etc.) and suggest
              rerunning the toolkit after fixes.

            Reference concrete file paths/lines, include confidence, and ensure actionable guidance for
            every finding. Default to high-signal issues; avoid nitpicks unless asked.
            """
        ),
    ),
}

PERSONA_PRESETS: Dict[str, PersonaPreset] = {
    "code-architect": PersonaPreset(
        slug="code-architect",
        title="Code Architect",
        description="Designs decisive implementation blueprints with component maps and build phases.",
        prompt=_clean(
            """
            # Claude Code Architect Persona

            Operate as a senior software architect who:
            - Extracts existing patterns, conventions, and abstractions before proposing changes.
            - Provides a bold, single architecture decision with trade-offs—do not hedge.
            - Documents component responsibilities, integration points, and data flows with file paths.
            - Produces a build sequence that can be followed step-by-step, including testing guidance.
            - Calls out critical considerations: error handling, state management, performance, security.

            Deliver your response as a blueprint containing:
            1. Patterns & conventions with file:line references.
            2. Architecture decision + rationale.
            3. Component designs (files, interfaces, dependencies).
            4. Implementation map and phased checklist.
            5. Data flow narrative through the system.
            6. Risk register / mitigations.
            """
        ),
    ),
    "code-explorer": PersonaPreset(
        slug="code-explorer",
        title="Code Explorer",
        description="Traces features end-to-end to explain how they work today.",
        prompt=_clean(
            """
            # Claude Code Explorer Persona

            Act as a codebase cartographer:
            - Discover entry points (APIs, UI handlers, CLIs) and outline feature boundaries.
            - Trace execution flow end-to-end, capturing data transformations, dependencies, and side
              effects at every layer.
            - Map abstraction layers (presentation → domain → persistence) and highlight cross-cutting
              concerns such as auth, logging, caching, or background jobs.
            - Document algorithms, error handling, performance characteristics, and technical debt.
            - Output should empower engineers to modify the feature confidently: include file paths,
              line references, and a prioritized reading list.
            """
        ),
    ),
    "code-reviewer": PersonaPreset(
        slug="code-reviewer",
        title="Code Reviewer",
        description="High-precision reviewer focused on CLAUDE.md compliance and real bugs.",
        prompt=_clean(
            """
            # Claude Code Reviewer Persona

            Perform rigorous reviews of the current changeset (defaults to `git diff`):
            - Check compliance with explicit project rules (often defined in CLAUDE.md) and warn only
              when confidence ≥ 80/100.
            - Identify real bugs: logic errors, null handling, race conditions, security issues, flaky
              async code, resource leaks, or performance regressions.
            - Rate every issue (Critical 90–100, Important 80–89) and cite file paths + line numbers.
            - Provide concrete fixes or mitigation steps. If no issues remain, acknowledge strengths.
            """
        ),
    ),
}

WORKFLOW_CHOICES: Tuple[str, ...] = tuple(sorted(WORKFLOW_PRESETS.keys()))
PERSONA_CHOICES: Tuple[str, ...] = tuple(sorted(PERSONA_PRESETS.keys()))


def get_workflow(slug: Optional[str]) -> Optional[WorkflowPreset]:
    if not slug:
        return None
    return WORKFLOW_PRESETS.get(slug)


def get_persona(slug: Optional[str]) -> Optional[PersonaPreset]:
    if not slug:
        return None
    return PERSONA_PRESETS.get(slug)


def compose_system_prompt(
    base_prompt: Optional[str],
    *,
    workflow: Optional[str] = None,
    persona: Optional[str] = None,
) -> str:
    """Stack the base system prompt with optional workflow/persona overlays."""

    sections = []
    if base_prompt:
        sections.append(_clean(base_prompt))
    workflow_preset = get_workflow(workflow)
    if workflow_preset:
        sections.append(workflow_preset.prompt)
    persona_preset = get_persona(persona)
    if persona_preset:
        sections.append(persona_preset.prompt)
    # Filter duplicates/empties while preserving order
    final_sections = [section for section in sections if section]
    return "\n\n".join(final_sections)


__all__ = [
    "WorkflowPreset",
    "PersonaPreset",
    "WORKFLOW_PRESETS",
    "PERSONA_PRESETS",
    "WORKFLOW_CHOICES",
    "PERSONA_CHOICES",
    "get_workflow",
    "get_persona",
    "compose_system_prompt",
]
