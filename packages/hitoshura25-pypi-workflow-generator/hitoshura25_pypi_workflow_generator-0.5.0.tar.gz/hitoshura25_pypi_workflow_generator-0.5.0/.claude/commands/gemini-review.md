Use the `mcp__gemini-workflow__review_code_with_gemini` tool to perform comprehensive code review.

**PROJECT CONTEXT:**
This is pypi-workflow-generator - a Python tool that creates CI/CD workflow templates (Jinja2 *.j2 files) for other Python PyPI projects. It generates GitHub Actions workflows, pyproject.toml configurations, and release automation for downstream users.

**Key Review Considerations:**
- Template files: hitoshura25_pypi_workflow_generator/*.j2 (generates workflows for other projects)
- Dogfooding: This project uses its own generated workflows in .github/workflows/
- Dual impact: Changes affect BOTH template files AND this project's own implementation
- Template consistency: Ensure templates and dogfooding workflows stay in sync
- Downstream impact: Template changes affect all users who generate workflows
- Build system: Uses setuptools-scm for versioning, pyproject.toml-based packaging

**USER REQUEST:**
{ARGUMENTS}

**Review Instructions for Gemini:**
When reviewing code changes, always check:
1. If template files (*.j2) were modified, were corresponding dogfooding files updated?
2. If dogfooding workflows were modified, should templates be updated too?
3. Are template variables correctly used and documented?
4. Will changes break downstream projects using generated workflows?
5. Is MANIFEST.in updated if new template files were added?
6. Are documentation and specs/ updated to reflect changes?

Parameters:
- **files**: Optional - specific files to review (comma-separated paths)
- **review_focus**: Optional - areas to focus on (e.g., "template consistency", "dogfooding sync", "downstream compatibility")
- **spec_path**: Optional - path to specification to review against (usually in specs/)
- **output_path**: Optional - where to save the review report

Example usage:
- `/gemini-review Check if template and dogfooding workflow changes are consistent`
- `/gemini-review Review changes for downstream compatibility issues`
- `/gemini-review Verify workflow template changes against specs/consolidate-dependencies.md`
