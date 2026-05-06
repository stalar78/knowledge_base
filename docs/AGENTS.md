# Agents and Roles

## Project Governance

The project is managed in a structured architect-led workflow.

The user works with an Architect who defines the architecture, documentation, roadmap, and task delegation strategy.

AI coding agents are used as executors, not as project leaders.

## Architect

The Architect is responsible for:

- project architecture;
- project roadmap;
- markdown documentation;
- task decomposition;
- choosing the correct executor;
- writing prompts for AI agents in English;
- reviewing agent reports;
- accepting completed steps;
- sending tasks back for revision when needed;
- deciding when to create separate GPT chats for specific courses.

The Architect is the “brain” of the project.

## User

The user is responsible for:

- running commands locally;
- placing files into the project;
- copying generated files when needed;
- sending full changed files or agent reports back to the Architect;
- deciding whether to continue, pause, or adjust the project direction.

## SourceCraft / Copilot

Use SourceCraft or Copilot for simple and local tasks.

Appropriate tasks:

- creating basic files;
- small Python scripts;
- simple refactoring;
- README edits;
- `.gitignore` updates;
- simple CLI improvements;
- formatting changes;
- minor documentation updates when the Architect provides exact content.

Do not use SourceCraft/Copilot for major architectural decisions.

## Codex

Use Codex for complex implementation tasks.

Appropriate tasks:

- batch processing architecture;
- OpenAI API integration;
- robust CLI design;
- error handling strategy;
- test creation;
- video-to-audio automation;
- pipeline orchestration;
- large refactoring;
- multi-stage processing;
- configuration system;
- course-level analysis workflow.

Codex should receive precise English prompts from the Architect.

## Documentation Strategy

To save agent tokens, the Architect prepares documentation files directly in markdown format whenever possible.

The user downloads these `.md` files and places them into the correct project folder.

This applies especially to:

```text
docs/PROJECT_OVERVIEW.md
docs/ARCHITECTURE.md
docs/WORKFLOW.md
docs/ROADMAP.md
docs/AGENTS.md
```

## Agent Prompt Language

All prompts for SourceCraft, Copilot, and Codex should be written in English.

The conversation between the user and the Architect remains in Russian.

## Review Process

After an agent completes a task, the user sends back:

- full changed files; or
- concise agent report; or
- both, when needed.

The Architect then decides:

```text
Accept the step
```

or:

```text
Return for revision
```

## Separate GPT Chats for Courses

After the software is created, each course should be analyzed in a separate GPT chat.

The main project chat remains responsible for:

- architecture;
- software development;
- documentation;
- prompts;
- agent management.

Course-specific chats are responsible for:

- transcript analysis;
- lesson summaries;
- course maps;
- learning decisions;
- Obsidian notes for that course only.

This separation prevents context mixing between unrelated courses.
