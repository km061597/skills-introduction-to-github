# CLAUDE.md

## Repository Overview

This is a **GitHub Skills** educational repository designed to teach new users the fundamentals of GitHub. It's an interactive, automated learning exercise that guides users through creating branches, making commits, opening pull requests, and merging changes.

**Repository Type:** Educational Exercise (GitHub Skills)
**Primary Language:** Markdown, YAML
**License:** MIT
**Automation:** GitHub Actions workflows

---

## Repository Purpose

This repository serves as an interactive tutorial for newcomers to GitHub. Users learn by doing:
1. Creating a branch (`my-first-branch`)
2. Committing a file (`PROFILE.md`)
3. Opening a pull request
4. Merging the pull request

The exercise is fully automated using GitHub Actions, providing real-time feedback through GitHub Issues.

---

## Directory Structure

```
.
├── .github/
│   ├── steps/                     # Step-by-step instructional content
│   │   ├── 1-create-a-branch.md
│   │   ├── 2-commit-a-file.md
│   │   ├── 3-open-a-pull-request.md
│   │   ├── 4-merge-your-pull-request.md
│   │   └── x-review.md
│   └── workflows/                 # GitHub Actions automation
│       ├── 0-start-exercise.yml
│       ├── 1-create-a-branch.yml
│       ├── 2-commit-a-file.yml
│       ├── 3-open-a-pull-request.yml
│       └── 4-merge-your-pull-request.yml
├── .gitignore                     # Standard ignores for compiled files, logs, OS files
├── LICENSE                        # MIT License from GitHub
└── README.md                      # Main landing page with exercise instructions
```

### Key Directory Explanations

**`.github/steps/`**
- Contains markdown files with step-by-step instructions
- Each file corresponds to one lesson in the exercise
- Posted as comments to GitHub Issues by automated workflows
- Uses images and formatting to guide learners visually

**`.github/workflows/`**
- Automated GitHub Actions that drive the exercise progression
- Each workflow corresponds to a step and validates user actions
- Workflows are enabled/disabled sequentially as user progresses
- Integrates with `skills/exercise-toolkit` for common functionality

---

## Technical Architecture

### Workflow System

The repository uses a **step-based progression model** powered by GitHub Actions:

1. **Step 0 - Start Exercise** (`0-start-exercise.yml`)
   - Triggers: Push to `main` branch
   - Creates the initial GitHub Issue for the exercise
   - Posts Step 1 instructions as a comment
   - Enables Step 1 workflow

2. **Step 1 - Create a Branch** (`1-create-a-branch.yml`)
   - Triggers: Push to `my-first-branch` branch
   - Validates: Branch name is exactly `my-first-branch`
   - Posts Step 2 instructions
   - Disables itself, enables Step 2 workflow

3. **Step 2 - Commit a File** (`2-commit-a-file.yml`)
   - Triggers: File changes on `my-first-branch`
   - Validates: `PROFILE.md` file exists in root
   - Posts Step 3 instructions
   - Progression continues similarly...

4. **Step 3 - Open a Pull Request** (`3-open-a-pull-request.yml`)
   - Validates pull request creation
   - Posts Step 4 instructions

5. **Step 4 - Merge Pull Request** (`4-merge-your-pull-request.yml`)
   - Validates merge completion
   - Completes the exercise

### Workflow Permissions

All workflows require these permissions:
- `contents: read/write` - Read repository content, update README
- `actions: write` - Enable/disable workflows programmatically
- `issues: write` - Create and comment on Issues for feedback

### Integration with Exercise Toolkit

Workflows use the reusable `skills/exercise-toolkit` repository (v0.1.0):
- `find-exercise-issue.yml` - Locates the exercise's tracking issue
- `start-exercise.yml` - Initializes new exercises
- Markdown templates for standardized feedback messages

---

## Development Workflows

### For AI Assistants Working in This Repository

#### Understanding the Exercise Flow

1. **Initial State**: Repository is template-based
2. **User Copies**: Creates their own copy from template
3. **Automation Starts**: First push to `main` triggers Step 0
4. **Progressive Learning**: Each action triggers next step
5. **Completion**: All workflows disabled, exercise complete

#### Key Conventions

**Branch Naming:**
- Expected learner branch: `my-first-branch` (exact match required)
- No prefixes or suffixes allowed for exercise validation
- Claude/AI branches should follow pattern: `claude/claude-md-{session-id}`

**File Expectations:**
- `PROFILE.md` must be created in repository root (not subdirectory)
- File content should be simple markdown
- Commit message convention: descriptive, imperative mood

**Pull Request Requirements:**
- Base branch: `main`
- Compare branch: `my-first-branch` (for learners)
- Title and description required for validation

#### Workflow Triggers

Be aware of automatic triggers:
- **Push events** trigger step validations
- **Branch creation** activates Step 1
- **File commits** activate Step 2
- **PR creation** activates Step 3
- **Merge** activates Step 4

### Modifying This Repository

**When creating new features or fixes:**

1. **Do NOT** interfere with the step progression system
2. **Do NOT** modify workflow files unless specifically requested
3. **Do NOT** create branches named `my-first-branch` (reserved for learners)
4. **Use** the designated Claude branch: `claude/claude-md-mi47dlavgaks3awn-01NyaBCHF9QSBEpbveAcjKzU`

**Safe modifications:**
- Documentation improvements (README.md, this file)
- Step content enhancements (.github/steps/*.md)
- .gitignore updates
- LICENSE or metadata changes

**Risky modifications:**
- Workflow YAML files (breaks automation)
- Branch naming expectations (breaks validation)
- File path expectations (breaks validation)

---

## Content Structure

### README.md
- Landing page for the exercise
- Explains what learners will build (profile README)
- Prerequisites: None (beginner-friendly)
- Time estimate: < 1 hour
- Links to start the exercise

### Step Files

Each step file follows this structure:
1. **Title** - Step number and action
2. **Context** - "You did X!" celebration
3. **Explanation** - Concepts and definitions
4. **Resources** - Links to GitHub Docs, videos
5. **Activity** - Step-by-step instructions with screenshots
6. **Troubleshooting** - Common issues and solutions

Visual aids extensively used:
- Screenshots of GitHub UI
- Arrows and highlights pointing to relevant buttons
- Example images of expected results

---

## Git Conventions

### Commit Messages
- Use imperative mood: "Add PROFILE.md" not "Added PROFILE.md"
- Keep first line concise (< 50 chars when possible)
- Provide context in description for complex changes

### Branch Strategy
- `main` - stable, template state
- `my-first-branch` - learner's working branch
- `claude/*` - AI assistant branches with session ID

### Merge Strategy
- Exercise uses standard merge (no squash, no rebase)
- Preserves commit history for learning purposes

---

## Key Concepts Taught

### 1. Repository
A project containing files, folders, and version history

### 2. Branch
A parallel version of the repository for isolated changes

### 3. Commit
A snapshot of changes to files and folders

### 4. Pull Request
A proposal to merge changes with discussion and review

### 5. Merge
Combining changes from one branch into another

---

## Dependencies

### External Actions Used
- `actions/checkout@v4` - Check out repository code
- `skills/action-text-variables@v1` - Template variable substitution
- `skills/exercise-toolkit/.github/workflows/*@v0.1.0` - Reusable workflows

### External Resources Referenced
- GitHub Docs (docs.github.com)
- YouTube videos explaining GitHub concepts
- GitHub Skills platform

---

## Troubleshooting Common Issues

### Workflows Not Triggering

**Symptom:** User completes step but gets no feedback

**Common Causes:**
1. Branch name doesn't match exactly (`my-first-branch`)
2. File not in expected location (must be root, not subdirectory)
3. Workflow disabled or not enabled yet
4. Repository is still a template

**AI Assistant Actions:**
- Verify exact branch name
- Check file paths carefully
- Review workflow status
- Confirm repository is a real copy, not template

### Multiple Issues Created

**Symptom:** Multiple exercise issues exist

**Cause:** Workflow triggered multiple times

**Resolution:** Exercise toolkit should handle this, uses `find-exercise-issue` to locate correct issue

---

## AI Assistant Guidelines

### When Helping Users

1. **Respect the Learning Flow**
   - Don't skip steps or automate the entire exercise
   - Guide users to perform actions themselves
   - Explain "why" not just "how"

2. **Branch Awareness**
   - Always check current branch before operations
   - Don't accidentally work on `my-first-branch` when helping
   - Use Claude-specific branches for assistance

3. **Validation Requirements**
   - Remember exact string matching for branch names
   - File paths must be exact (root level)
   - Commit messages should follow conventions

4. **Workflow Interference**
   - Avoid triggering workflows unintentionally
   - Be aware push events trigger validations
   - Don't modify workflow files unless explicitly requested

### When Modifying Repository

1. **Use Designated Branch**
   - Work on: `claude/claude-md-mi47dlavgaks3awn-01NyaBCHF9QSBEpbveAcjKzU`
   - Never use: `my-first-branch` (reserved for learners)
   - Never push to: `main` (unless updating template)

2. **Test Workflow Impact**
   - Consider if changes affect automation
   - Verify step content accuracy
   - Ensure links and resources still valid

3. **Documentation Updates**
   - Update this file when making structural changes
   - Keep README.md synchronized with actual behavior
   - Update step files if UI/process changes

---

## Educational Philosophy

This repository embodies GitHub's **learn by doing** approach:

- **Hands-on**: Users perform actual Git operations
- **Immediate Feedback**: Automated validation and next steps
- **Visual Guidance**: Screenshots and UI highlights
- **Progressive Complexity**: Simple to advanced concepts
- **Real-world Application**: Building actual profile README
- **Safety**: Template-based, low-risk environment

---

## Version Information

- **Exercise Toolkit Version:** v0.1.0
- **Actions Checkout:** v4
- **Text Variables Action:** v1

---

## Additional Resources

### For Learners
- [GitHub Docs - About Repositories](https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories)
- [GitHub Docs - About Branches](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-branches)
- [GitHub Docs - About Commits](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/about-commits)
- [GitHub Docs - About Pull Requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)
- [GitHub Docs - Profile README](https://docs.github.com/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/managing-your-profile-readme)

### For Contributors
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Skills Platform](https://skills.github.com/)
- [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md)

---

## Maintenance Notes

**Last Updated:** 2025-11-18
**Repository Status:** Active Educational Exercise
**Target Audience:** New GitHub users, students, developers new to version control

**Future Considerations:**
- Keep screenshots updated with GitHub UI changes
- Monitor exercise-toolkit for updates
- Update links if GitHub Docs URLs change
- Consider additional steps for advanced concepts
- Gather learner feedback for improvements

---

## License

MIT License - Copyright (c) GitHub, Inc.

See [LICENSE](LICENSE) file for full text.
