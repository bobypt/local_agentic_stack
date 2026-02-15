"""
Support agent: checks price and catalogue using the MCP server (JSON-RPC 2.0).
Follows the poet pattern: single Agent with tools.
"""
import os
from google.adk import Agent
from . import prompt
from .tools import catalogue_retrieve

MODEL = os.getenv("SUPPORT_AGENT_MODEL", "gemini-2.0-flash-exp")

support_agent = Agent(
    model=MODEL,
    name="support_agent",
    instruction=prompt.SUPPORT_AGENT_PROMPT,
    output_key="support_output",
    tools=[catalogue_retrieve],
)

root_agent = support_agent
