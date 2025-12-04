"""
Prompts package for Craigslist Agent.
Contains system prompts, workflows, and templates for lead analysis.
"""

from .system_prompt import (
    get_system_prompt,
    get_workflow_instructions,
    get_step_instructions,
    get_complete_prompt,
    SYSTEM_PROMPT,
    WORKFLOW_INSTRUCTIONS,
    LEAD_SCORING_ALGORITHM,
    VALUE_PROP_EXAMPLES,
    PAIN_POINTS_BY_INDUSTRY,
    CALL_SCRIPT_TEMPLATE,
    DASHBOARD_TEMPLATE
)

__all__ = [
    'get_system_prompt',
    'get_workflow_instructions',
    'get_step_instructions',
    'get_complete_prompt',
    'SYSTEM_PROMPT',
    'WORKFLOW_INSTRUCTIONS',
    'LEAD_SCORING_ALGORITHM',
    'VALUE_PROP_EXAMPLES',
    'PAIN_POINTS_BY_INDUSTRY',
    'CALL_SCRIPT_TEMPLATE',
    'DASHBOARD_TEMPLATE'
]
