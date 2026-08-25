"""Capability answers list skill demos instead of platform features."""

from __future__ import annotations

from core.agent_harness.prompts.assistant import (
    build_assistant_system_prompt,
    build_handoff_guidance_block,
)
from core.agent_harness.prompts.skills.loader import (
    clear_skills_caches,
    list_action_skills,
    load_skills_demo_block,
    load_skills_index,
)


def test_skills_demo_block_lists_frontmatter_demos_only() -> None:
    clear_skills_caches()
    demos = {skill.name: skill.demo for skill in list_action_skills() if skill.demo}

    assert demos == {
        "architecture-audit": "Audit this repo's architecture and give me a sequenced refactor plan",
        "github-ci-fix": "Find open PRs with failing CI and fix them",
        "github-security-fix": "Remediate the open Dependabot and CodeQL alerts",
        "morning-report": "Set up a weekday morning briefing with weather and news",
    }
    block = load_skills_demo_block()
    assert "ONLY the skill demos" in block
    assert "Do not list platform features" in block
    for prompt in demos.values():
        assert prompt in block


def test_assistant_prompt_includes_skill_demos() -> None:
    clear_skills_caches()
    prompt = build_assistant_system_prompt("ref", "hist")

    assert "ONLY the skill demos" in prompt
    assert "Audit this repo's architecture and give me a sequenced refactor plan" in prompt
    assert "Find open PRs with failing CI and fix them" in prompt
    assert "Remediate the open Dependabot and CodeQL alerts" in prompt
    assert "Set up a weekday morning briefing with weather and news" in prompt


def test_capability_handoff_guidance_forbids_a_platform_dump() -> None:
    block = build_handoff_guidance_block(("chat:capabilities",))

    assert "skill-demo rule" in block
    assert "platform features" in block
    assert "Want-me-to" in block
    assert build_handoff_guidance_block(("chat:greeting",)) == ""


def test_skills_index_routes_capability_questions_to_handoff() -> None:
    clear_skills_caches()
    index = load_skills_index()

    assert "what can you do" in index
    assert 'assistant_handoff(content="chat:capabilities", requires_gather=false)' in index
