"""
Generator Agent — convenience re-export from template_generator module.
The main agent lives at agents/template_generator_agent.py and follows
the BaseAgent pattern. This module re-exports it for import convenience.
"""
from agents.template_generator_agent import TemplateGeneratorAgent  # noqa: F401

__all__ = ["TemplateGeneratorAgent"]
