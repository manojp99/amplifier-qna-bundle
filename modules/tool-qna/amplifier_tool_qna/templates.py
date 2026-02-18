"""Built-in Q&A templates for common requirements-gathering scenarios."""

from .models import Question, QuestionType, Section, Template

# ---------------------------------------------------------------------------
# Template 1 – Software Feature Requirements
# ---------------------------------------------------------------------------
_software_requirements = Template(
    id="software_requirements",
    name="Software Feature Requirements",
    description="Comprehensive template for gathering software feature requirements including functional needs, non-functional requirements, and project constraints.",
    sections=[
        Section(
            id="overview",
            title="Project Overview",
            description="High-level information about the project and its goals.",
            guidance="Start by understanding the big picture. Ask about the project name and purpose conversationally, then dig into who it's for and why it matters. If the user gives a vague description, ask a follow-up to sharpen it.",
            questions=[
                Question(
                    id="proj_name",
                    text="What is the name of the project or feature?",
                    type=QuestionType.TEXT,
                    hint="A short, descriptive name that the team will use to refer to this work.",
                ),
                Question(
                    id="proj_description",
                    text="Provide a brief description of the project or feature.",
                    type=QuestionType.TEXT,
                    hint="2-3 sentences summarising the purpose and scope.",
                ),
                Question(
                    id="target_users",
                    text="Who are the target users?",
                    type=QuestionType.TEXT,
                    hint="Describe the primary user personas or roles.",
                ),
                Question(
                    id="business_value",
                    text="What business problem does this solve?",
                    type=QuestionType.TEXT,
                    hint="Explain the value proposition or pain point being addressed.",
                ),
                Question(
                    id="priority",
                    text="What is the overall priority of this project?",
                    type=QuestionType.CHOICE,
                    options=["Critical", "High", "Medium", "Low"],
                ),
            ],
        ),
        Section(
            id="functional",
            title="Functional Requirements",
            description="What the system should do.",
            guidance="Explore what the system needs to do. The listed questions cover key features, workflows, and integrations, but probe deeper based on what the user says. If they mention a feature, ask what happens on error or at scale. Record unexpected insights as notes.",
            questions=[
                Question(
                    id="key_features",
                    text="List the key features or capabilities required.",
                    type=QuestionType.TEXT,
                    hint="Describe each feature briefly. Separate distinct features with line breaks.",
                ),
                Question(
                    id="user_workflows",
                    text="Describe the primary user workflows or use cases.",
                    type=QuestionType.TEXT,
                    hint="Step-by-step flows the user will follow.",
                ),
                Question(
                    id="integrations_needed",
                    text="Are there any third-party integrations required?",
                    type=QuestionType.YES_NO,
                ),
                Question(
                    id="integration_details",
                    text="Which systems or APIs need to be integrated?",
                    type=QuestionType.TEXT,
                    condition=("integrations_needed", True),
                    hint="List each integration and the type of data exchanged.",
                ),
                Question(
                    id="data_requirements",
                    text="What data does the feature need to store or process?",
                    type=QuestionType.TEXT,
                    hint="Describe key data entities, volumes, and retention needs.",
                ),
            ],
        ),
        Section(
            id="non_functional",
            title="Non-Functional Requirements",
            description="Quality attributes and constraints on how the system operates.",
            guidance="Users often overlook non-functional requirements. Gently probe for performance, security, and availability expectations. If the user isn't sure, help them think through it with examples rather than skipping.",
            questions=[
                Question(
                    id="has_perf_requirements",
                    text="Are there specific performance requirements?",
                    type=QuestionType.YES_NO,
                ),
                Question(
                    id="perf_targets",
                    text="What are the specific performance targets?",
                    type=QuestionType.TEXT,
                    condition=("has_perf_requirements", True),
                    hint="e.g. response time < 200ms, throughput > 1000 req/s.",
                ),
                Question(
                    id="availability",
                    text="What availability or uptime level is required?",
                    type=QuestionType.CHOICE,
                    options=[
                        "99.9% (8.7h downtime/yr)",
                        "99.5% (1.8d downtime/yr)",
                        "99% (3.65d downtime/yr)",
                        "Best effort",
                    ],
                ),
                Question(
                    id="security_requirements",
                    text="Describe any security or compliance requirements.",
                    type=QuestionType.TEXT,
                    required=False,
                    hint="e.g. encryption at rest, GDPR, SOC 2, role-based access.",
                ),
                Question(
                    id="scalability",
                    text="How many concurrent users or requests should the system support?",
                    type=QuestionType.TEXT,
                    required=False,
                    hint="Current expectations and growth projections.",
                ),
            ],
        ),
        Section(
            id="constraints",
            title="Constraints & Timeline",
            description="Budget, timeline, and technical constraints.",
            guidance="Be direct but tactful about constraints. Users sometimes avoid mentioning budget or deadline pressure unless asked. Frame questions as planning aids, not interrogation.",
            questions=[
                Question(
                    id="deadline",
                    text="Is there a hard deadline or target launch date?",
                    type=QuestionType.TEXT,
                    required=False,
                    hint="Provide a date or timeframe (e.g. Q3 2025).",
                ),
                Question(
                    id="budget_constrained",
                    text="Are there budget constraints that affect technology choices?",
                    type=QuestionType.YES_NO,
                ),
                Question(
                    id="budget_details",
                    text="Describe the budget constraints.",
                    type=QuestionType.TEXT,
                    condition=("budget_constrained", True),
                ),
                Question(
                    id="tech_constraints",
                    text="Are there any technology or platform constraints?",
                    type=QuestionType.TEXT,
                    required=False,
                    hint="e.g. must use Python 3.11+, must run on AWS, must be containerised.",
                ),
                Question(
                    id="additional_notes",
                    text="Any additional notes or context?",
                    type=QuestionType.TEXT,
                    required=False,
                ),
            ],
        ),
    ],
)

# ---------------------------------------------------------------------------
# Template 2 – User Story Gathering
# ---------------------------------------------------------------------------
_user_story = Template(
    id="user_story",
    name="User Story Gathering",
    description="Structured template for capturing user stories with context, acceptance criteria, and priority.",
    sections=[
        Section(
            id="user_context",
            title="User Context",
            description="Understand the user and their current situation.",
            guidance="Build empathy for the user. Understand who they are, what they do today, and what frustrates them. Let the user tell their story before moving to specifics.",
            questions=[
                Question(
                    id="persona",
                    text="Who is the user? Describe the persona or role.",
                    type=QuestionType.TEXT,
                    hint="e.g. 'A marketing manager who schedules campaigns weekly.'",
                ),
                Question(
                    id="experience_level",
                    text="What is the user's technical experience level?",
                    type=QuestionType.CHOICE,
                    options=[
                        "Non-technical",
                        "Basic",
                        "Intermediate",
                        "Advanced",
                        "Expert",
                    ],
                ),
                Question(
                    id="current_workflow",
                    text="How does the user currently accomplish this task?",
                    type=QuestionType.TEXT,
                    hint="Describe the existing process, even if manual.",
                ),
                Question(
                    id="pain_points",
                    text="What are the main pain points with the current approach?",
                    type=QuestionType.TEXT,
                    hint="What frustrates the user or wastes their time?",
                ),
            ],
        ),
        Section(
            id="story_details",
            title="Story Details",
            description="The core user story content.",
            guidance="Help the user articulate the classic 'As a [persona], I want [goal], so that [benefit]' pattern. If they struggle with motivation, help them connect the feature to a real outcome.",
            questions=[
                Question(
                    id="goal",
                    text="What does the user want to accomplish?",
                    type=QuestionType.TEXT,
                    hint="Complete the sentence: 'I want to ...'",
                ),
                Question(
                    id="motivation",
                    text="Why does the user want this? What value does it provide?",
                    type=QuestionType.TEXT,
                    hint="Complete the sentence: 'So that ...'",
                ),
                Question(
                    id="desired_outcome",
                    text="What does success look like for the user?",
                    type=QuestionType.TEXT,
                ),
                Question(
                    id="story_priority",
                    text="How would you rate the priority of this story?",
                    type=QuestionType.CHOICE,
                    options=["Must-have", "Should-have", "Nice-to-have"],
                ),
            ],
        ),
        Section(
            id="acceptance",
            title="Acceptance Criteria",
            description="Conditions that must be true for the story to be considered done.",
            guidance="Push for specificity. Vague acceptance criteria lead to disputes later. Help the user think in given/when/then terms or concrete checklists.",
            questions=[
                Question(
                    id="acceptance_criteria",
                    text="List the acceptance criteria (given/when/then or simple checklist).",
                    type=QuestionType.TEXT,
                    hint="Be specific and testable.",
                ),
                Question(
                    id="edge_cases",
                    text="Are there known edge cases or error scenarios to handle?",
                    type=QuestionType.TEXT,
                    required=False,
                ),
                Question(
                    id="has_dependencies",
                    text="Does this story depend on other stories or systems?",
                    type=QuestionType.YES_NO,
                ),
                Question(
                    id="dependency_details",
                    text="Describe the dependencies.",
                    type=QuestionType.TEXT,
                    condition=("has_dependencies", True),
                ),
            ],
        ),
    ],
)

# ---------------------------------------------------------------------------
# Template 3 – Bug / Issue Report
# ---------------------------------------------------------------------------
_bug_report = Template(
    id="bug_report",
    name="Bug / Issue Report",
    description="Structured template for reporting bugs with environment details, reproduction steps, and impact assessment.",
    sections=[
        Section(
            id="environment",
            title="Environment",
            description="Details about the environment where the issue occurs.",
            guidance="Collect environment details quickly. These are factual questions, so keep the pace brisk. If the user doesn't know a version number, suggest how to find it.",
            questions=[
                Question(
                    id="software_version",
                    text="What version of the software are you using?",
                    type=QuestionType.TEXT,
                    hint="e.g. v2.4.1 or commit hash.",
                ),
                Question(
                    id="os_platform",
                    text="What operating system and platform are you on?",
                    type=QuestionType.TEXT,
                    hint="e.g. macOS 14.2, Ubuntu 22.04, Windows 11.",
                ),
                Question(
                    id="browser_or_runtime",
                    text="Which browser or runtime is involved (if applicable)?",
                    type=QuestionType.TEXT,
                    required=False,
                    hint="e.g. Chrome 120, Node 20, Python 3.12.",
                ),
            ],
        ),
        Section(
            id="description",
            title="Issue Description",
            description="What happened and what was expected.",
            guidance="Get a clear picture of expected vs actual behavior. If the user is frustrated, let them vent briefly, then guide them to specifics. Ask for exact error messages when available.",
            questions=[
                Question(
                    id="summary",
                    text="Provide a one-line summary of the issue.",
                    type=QuestionType.TEXT,
                ),
                Question(
                    id="expected_behavior",
                    text="What did you expect to happen?",
                    type=QuestionType.TEXT,
                ),
                Question(
                    id="actual_behavior",
                    text="What actually happened?",
                    type=QuestionType.TEXT,
                ),
                Question(
                    id="has_logs",
                    text="Do you have error messages or log output to share?",
                    type=QuestionType.YES_NO,
                ),
                Question(
                    id="log_output",
                    text="Paste the relevant error messages or log output.",
                    type=QuestionType.TEXT,
                    condition=("has_logs", True),
                    hint="Include stack traces if available.",
                ),
            ],
        ),
        Section(
            id="reproduction",
            title="Reproduction",
            description="Steps to reproduce the issue.",
            guidance="Reproduction steps are the most valuable part of a bug report. Walk the user through writing clear numbered steps. If they say 'it just happens', ask what they were doing immediately before.",
            questions=[
                Question(
                    id="repro_steps",
                    text="List the steps to reproduce the issue.",
                    type=QuestionType.TEXT,
                    hint="Numbered step-by-step instructions.",
                ),
                Question(
                    id="frequency",
                    text="How often does this issue occur?",
                    type=QuestionType.CHOICE,
                    options=[
                        "Every time",
                        "Frequently (>50%)",
                        "Sometimes (~25%)",
                        "Rarely (<10%)",
                        "Only once so far",
                    ],
                ),
                Question(
                    id="has_workaround",
                    text="Is there a known workaround?",
                    type=QuestionType.YES_NO,
                ),
                Question(
                    id="workaround_details",
                    text="Describe the workaround.",
                    type=QuestionType.TEXT,
                    condition=("has_workaround", True),
                ),
            ],
        ),
        Section(
            id="impact",
            title="Impact",
            description="How severe is the issue and who is affected.",
            guidance="Help the user quantify impact. 'It's bad' isn't actionable for triage. Ask how many users are affected, whether there's revenue impact, and if there's a deadline driving urgency.",
            questions=[
                Question(
                    id="severity",
                    text="How severe is this issue?",
                    type=QuestionType.CHOICE,
                    options=[
                        "Blocker - cannot proceed",
                        "Critical - major feature broken",
                        "Major - feature impaired",
                        "Minor - cosmetic or low-impact",
                        "Trivial",
                    ],
                ),
                Question(
                    id="users_affected",
                    text="How many users or teams are affected?",
                    type=QuestionType.TEXT,
                    required=False,
                ),
            ],
        ),
    ],
)

# ---------------------------------------------------------------------------
# Template 4 – Project Kickoff
# ---------------------------------------------------------------------------
_project_kickoff = Template(
    id="project_kickoff",
    name="Project Kickoff",
    description="Template for project kickoff meetings covering vision, stakeholders, scope, and risk identification.",
    sections=[
        Section(
            id="vision",
            title="Vision & Objectives",
            description="The big picture for the project.",
            guidance="Start aspirational. Help the user paint a picture of the ideal outcome before diving into details. If objectives are vague, push for measurable targets.",
            questions=[
                Question(
                    id="project_vision",
                    text="What is the project vision? Describe the desired end state.",
                    type=QuestionType.TEXT,
                    hint="One or two sentences painting the ideal outcome.",
                ),
                Question(
                    id="business_objectives",
                    text="What are the primary business objectives?",
                    type=QuestionType.TEXT,
                    hint="List measurable objectives (e.g. reduce churn by 10%).",
                ),
                Question(
                    id="success_metrics",
                    text="How will success be measured?",
                    type=QuestionType.TEXT,
                    hint="KPIs, OKRs, or concrete metrics.",
                ),
                Question(
                    id="strategic_alignment",
                    text="How does this project align with broader company strategy?",
                    type=QuestionType.TEXT,
                    required=False,
                ),
            ],
        ),
        Section(
            id="stakeholders",
            title="Stakeholders",
            description="Who is involved and who will be affected.",
            guidance="Identify the people and roles involved. Ask about decision-makers, end users, and anyone who could block progress. Note any political dynamics as freeform notes.",
            questions=[
                Question(
                    id="key_stakeholders",
                    text="Who are the key stakeholders and decision-makers?",
                    type=QuestionType.TEXT,
                    hint="Names and roles.",
                ),
                Question(
                    id="target_audience",
                    text="Who is the target audience or end user?",
                    type=QuestionType.TEXT,
                ),
                Question(
                    id="team_composition",
                    text="What does the project team look like?",
                    type=QuestionType.TEXT,
                    required=False,
                    hint="Roles, team size, availability.",
                ),
            ],
        ),
        Section(
            id="scope",
            title="Scope",
            description="What is in and out of scope.",
            guidance="Scope definition prevents future pain. Push for explicit 'out of scope' items - users rarely volunteer these but always appreciate having them documented.",
            questions=[
                Question(
                    id="must_have_features",
                    text="What are the must-have features or deliverables?",
                    type=QuestionType.TEXT,
                    hint="The non-negotiable items for launch.",
                ),
                Question(
                    id="nice_to_have_features",
                    text="What are the nice-to-have features?",
                    type=QuestionType.TEXT,
                    required=False,
                    hint="Items to include if time and budget allow.",
                ),
                Question(
                    id="out_of_scope",
                    text="What is explicitly out of scope?",
                    type=QuestionType.TEXT,
                    required=False,
                    hint="Prevents scope creep by documenting exclusions early.",
                ),
                Question(
                    id="has_milestones",
                    text="Have milestones or phases been identified?",
                    type=QuestionType.YES_NO,
                ),
                Question(
                    id="milestone_details",
                    text="Describe the milestones or phases.",
                    type=QuestionType.TEXT,
                    condition=("has_milestones", True),
                    hint="Include target dates if known.",
                ),
            ],
        ),
        Section(
            id="risks",
            title="Risks & Dependencies",
            description="Known risks and external dependencies.",
            guidance="People underestimate risk. Ask about technical unknowns, team availability, and external dependencies. If the user says 'no risks', gently challenge with common risk categories.",
            questions=[
                Question(
                    id="known_risks",
                    text="What are the known risks to the project?",
                    type=QuestionType.TEXT,
                    hint="Technical, organisational, or market risks.",
                ),
                Question(
                    id="risk_severity",
                    text="Rate the overall risk level for this project.",
                    type=QuestionType.SCALE,
                    scale_min=1,
                    scale_max=5,
                    hint="1 = very low risk, 5 = very high risk.",
                ),
                Question(
                    id="external_dependencies",
                    text="Are there external dependencies (vendors, APIs, other teams)?",
                    type=QuestionType.TEXT,
                    required=False,
                ),
                Question(
                    id="kickoff_notes",
                    text="Any additional notes or open questions for the team?",
                    type=QuestionType.TEXT,
                    required=False,
                ),
            ],
        ),
    ],
)

# ---------------------------------------------------------------------------
# Public registry
# ---------------------------------------------------------------------------
TEMPLATES: dict[str, Template] = {
    t.id: t
    for t in [
        _software_requirements,
        _user_story,
        _bug_report,
        _project_kickoff,
    ]
}
