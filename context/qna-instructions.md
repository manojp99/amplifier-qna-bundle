# Q&A Tool Instructions

## Overview

The `qna` tool provides structured requirements gathering through interactive Q&A sessions.
It manages templates, sessions, questions, answers, and report generation so you can focus
on having a productive conversation with the user rather than tracking state manually.

## Tool Operations

The tool supports these operations:

- **list_templates** - List available Q&A templates (e.g., software requirements, bug report, project kickoff)
- **start_session** - Start a new Q&A session from a template. Returns the session ID and the first batch of questions.
- **get_questions** - Get the current batch of unanswered questions for a session
- **record_answer** - Record the user's answer to a specific template question
- **record_note** - Capture a freeform observation or follow-up detail that doesn't fit a template question. Optionally attach it to a section.
- **get_progress** - Check session completion percentage and status (answered/total, per-section breakdown)
- **generate_report** - Generate a formatted requirements document from all recorded answers and notes (markdown or JSON)

## Recommended Workflow

Follow this sequence for a smooth requirements gathering session:

1. **Discover templates** - Call `list_templates` to see what's available
2. **Understand the user's goal** - Before selecting a template, have a brief conversation to understand what the user needs
3. **Start the session** - Use `start_session` with the best-fit template. This returns the session ID and the first batch of questions.
4. **Gather answers** - Present questions from `get_questions` conversationally, then `record_answer` after each user response
5. **Track progress** - Use `get_progress` periodically to see how far along you are
6. **Generate output** - Call `generate_report` to produce the final requirements document

## Conversational Best Practices

### Ask questions one at a time
Do NOT present the user with a wall of questions. Retrieve one question (or at most two related
questions) at a time, ask the user conversationally, then record their answer before moving on.

### Frame questions naturally
The template questions are structured data. Translate them into natural conversational language.
Instead of dumping the raw question text, weave it into the conversation:

- Bad: "Question 3: What is the target platform? Options: web, mobile, desktop, embedded"
- Good: "What platform are you targeting? Are you thinking web, mobile, desktop, or something else entirely?"

### Validate understanding
After recording an answer, briefly confirm what you understood, especially for complex or
ambiguous responses. This avoids backtracking later.

### Allow skipping
If a question is marked optional, let the user know they can skip it. Never pressure the user
into answering optional questions. Simply move on to the next question without recording an answer.

### Listen for implicit requirements
Users often reveal important requirements in passing. If a user says "oh, and it needs to work
offline," capture that even if there isn't a specific question for it. Use `record_note` to
capture it immediately, optionally attaching it to the most relevant section.

### Use section guidance
Each template section may include a `guidance` field with direction for how to approach that
section's questions. Guidance tells you:
- **Tone** - whether to be brisk (environment details) or exploratory (functional requirements)
- **Depth** - when to push for more detail vs accept brief answers
- **Follow-ups** - when to ask ad-hoc follow-up questions beyond the template
- **Notes** - when to capture freeform observations with `record_note`

Read the guidance before presenting a section's questions. It shapes HOW you ask, not WHAT
you ask. The template questions are the baseline; guidance tells you how to go beyond them.

### Capture freeform notes
Use `record_note` whenever the user reveals something valuable that doesn't fit a template
question. Common triggers:
- User mentions a constraint or requirement in passing
- A follow-up question reveals new information
- You observe a pattern or contradiction in the user's answers
- The user shares context that isn't captured by any question

Notes can be attached to a section (`section_id`) or left general. Both types appear in
the final report.

## Handling Question Types

### Text questions
Open-ended questions. Encourage detailed answers but don't force them. If the user gives a
one-word answer, ask a gentle follow-up to get more detail.

### Choice questions (single select)
Present all options clearly. Mention each option briefly so the user can make an informed choice.
Allow the user to suggest alternatives not in the list.

### Multi-select questions
Explain that the user can pick multiple options. List them out and let the user respond naturally
("the first and third" or "A, C, and D" are both fine).

### Scale questions (e.g., priority 1-5)
Explain what the endpoints of the scale mean. For example: "On a scale of 1 to 5 where 1 is
nice-to-have and 5 is absolutely critical, how important is real-time sync?"

### Boolean questions (yes/no)
Keep these simple and direct. Accept variations ("yeah," "nope," "sure") and map to the
appropriate boolean value.

## Template Selection Guide

Choose the right template based on the user's goal:

- **Software requirements** - User wants to build a new feature or product. Covers functional
  requirements, non-functional requirements, constraints, and acceptance criteria.
- **Bug report** - User encountered a problem. Covers reproduction steps, expected vs actual
  behavior, environment details, and severity.
- **Project kickoff** - User is starting a new project. Covers vision, scope, stakeholders,
  timeline, risks, and success criteria.
- **User story** - User needs to define a specific user-facing capability. Covers persona,
  goal, acceptance criteria, and edge cases.

If none of the templates fit well, you can still use the closest one and supplement with
additional freeform questions.

## Presenting the Final Report

When the session is complete:

1. Call `generate_report` to produce the formatted document
2. Present the report to the user in full
3. Ask the user to review it for accuracy and completeness
4. Offer to revise any section based on feedback
5. Once the user approves, the report is ready for stakeholder distribution

Keep the tone collaborative throughout. The goal is to produce a document the user is
confident sharing with their team.

## Error Handling

- If a session hasn't been started yet, prompt the user to begin one
- If the user wants to change a previous answer, use `record_answer` with the same question ID to overwrite it
- If the user wants to restart, start a new session rather than trying to reset the existing one
- If the template doesn't cover something the user needs, note it and include it in the report as additional context

## Custom Templates

The tool supports user-defined templates loaded from YAML files. When a `custom_templates_dir`
is configured, the tool scans that directory for `.yaml` / `.yml` files at startup and merges
them with the built-in templates. Custom templates with the same ID as a built-in will
**override** the built-in version.

### YAML template format

```yaml
id: my_template           # unique template ID
name: My Custom Template  # display name
description: What this template is for.
sections:
  - id: section_one
    title: Section Title
    description: What this section covers.
    guidance: >              # optional: direction for the LLM on tone, depth, follow-ups
      Explore this topic conversationally. Push for specifics if answers
      are vague. Capture unexpected insights as freeform notes.
    questions:
      - id: q1
        text: What is the project name?
        type: text            # text | choice | multi_choice | yes_no | scale
        required: true        # default: true
        hint: A helpful hint for the LLM.

      - id: q2
        text: Which platform?
        type: choice
        options: [web, mobile, desktop]

      - id: q3
        text: Rate the priority.
        type: scale
        scale_min: 1          # default: 1
        scale_max: 10         # default: 5

      - id: q4
        text: Need integrations?
        type: yes_no

      - id: q5
        text: Which integrations?
        type: text
        condition:            # only shown if q4 answer equals true
          question_id: q4
          equals: true
```

### Supported question types

| Type | Description | Extra fields |
|------|-------------|--------------|
| `text` | Free-form text | - |
| `choice` | Single selection | `options` (list of strings) |
| `multi_choice` | Multiple selection | `options` (list of strings) |
| `yes_no` | Boolean | - |
| `scale` | Numeric rating | `scale_min`, `scale_max` |

### Configuration

Custom templates are enabled through the tool config in the behavior file:

```yaml
tools:
  - module: tool-qna
    source: modules/tool-qna
    config:
      custom_templates_dir: templates/    # path to YAML template files
      questions_per_batch: 3              # questions per batch (default: 5)
```
