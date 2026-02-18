---
behavior:
  name: qna
  description: Structured Q&A tool and requirements analyst agent for gathering requirements from users.
  tools:
    - module: tool-qna
      source: modules/tool-qna
      config:
        custom_templates_dir: templates/
        questions_per_batch: 5
  agents:
    - agents/requirements-analyst
  context:
    include:
      - context/qna-instructions.md
---
