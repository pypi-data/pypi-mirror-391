Use the `mcp__gemini-workflow__ask_gemini` tool for general-purpose questions with optional full codebase context (2M token window).

**PROJECT CONTEXT (included when codebase context is loaded):**
This is pypi-workflow-generator - a Python tool that creates CI/CD workflow templates (Jinja2 *.j2 files) for other Python PyPI projects. It generates GitHub Actions workflows, pyproject.toml configurations, and release automation for downstream users.

**Key Project Characteristics:**
- Template files: hitoshura25_pypi_workflow_generator/*.j2 (generates workflows for other projects)
- Dogfooding: This project uses its own generated workflows in .github/workflows/
- Dual nature: Both a generator tool (Python code) and a consumer of its own templates
- Template architecture: Jinja2 templates with variable substitution for customization
- Build system: Uses setuptools-scm for versioning, pyproject.toml-based packaging

**USER QUESTION:**
{ARGUMENTS}

**When answering, consider:**
- The relationship between template files (*.j2) and dogfooding implementations
- How changes might affect both template generation and this project's own usage
- The downstream impact on projects that use generated workflows
- The template variable system and customization options

Parameters:
- **prompt**: The full context above including project context and user question
- **include_codebase_context**: Set to true to load full codebase (recommended for most questions)
- **context_id**: Optional - reuse cached context from previous call
- **temperature**: Optional - temperature for generation (0.0-1.0, default varies)

Example usage:
- `/gemini-ask How does the versioning system work in this project?`
- `/gemini-ask What would break if I renamed the main module?`
- `/gemini-ask How do template variables get substituted during generation?`
- `/gemini-ask Compare the dogfooding workflow to the template - are they in sync?`

**Tip**: Use this as the catch-all when the other specialized commands don't fit, or when you want Gemini's broader analysis capabilities.
