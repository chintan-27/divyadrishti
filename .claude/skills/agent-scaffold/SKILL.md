---
name: agent-scaffold
description: Scaffold a new agent module following the project's agent architecture. Creates the directory structure, base class, and boilerplate.
argument-hint: [agent-name]
user-invocable: true
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Agent Scaffolder

Create a new agent for: $ARGUMENTS

## Architecture Reference

Agents are independent workers that:
- Read/write to PostgreSQL
- Publish events through Redis Streams
- Are scheduled by the Supervisor Agent
- Live under `agents/{agent_name}/`

## Directory Structure to Create

```
agents/{agent_name}/
├── __init__.py
├── agent.py         # Main agent class with run() method
├── config.py        # Agent-specific configuration
└── tests/
    ├── __init__.py
    └── test_agent.py
```

## Instructions

1. Check the existing agents directory for established patterns — reuse the base class and conventions
2. Create the agent module with a clear `run()` entry point
3. Define the Redis Stream channels this agent reads from and writes to
4. Add Pydantic config for any agent-specific settings
5. Create a basic test file
6. Reference the phase plans in `.claude/` for what this agent should do

## Event Channels (from Phase 1)
- `hn.discovery`, `hn.content`, `nlp.opinion`, `nlp.embedding`
- `metric.mapping`, `metric.gardening`, `metric.rollups`, `moderation.ui`
