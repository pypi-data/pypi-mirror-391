Use the `mcp__gemini-workflow__analyze_codebase_with_gemini` tool with the following focus description:

**PROJECT CONTEXT:**
This is pypi-workflow-generator - a Python tool that creates CI/CD workflow templates (Jinja2 *.j2 files) for other Python PyPI projects. It generates GitHub Actions workflows, pyproject.toml configurations, and release automation for downstream users.

**Key Project Characteristics:**
- Template files: hitoshura25_pypi_workflow_generator/*.j2 (generates workflows for other projects)
- Dogfooding: This project uses its own generated workflows in .github/workflows/
- Dual nature: Both a generator tool (Python code) and a consumer of its own templates
- Template architecture: Jinja2 templates with variable substitution for customization
- Build system: Uses setuptools-scm for versioning, pyproject.toml-based packaging

**USER REQUEST:**
{ARGUMENTS}

**Analysis Instructions for Gemini:**
When analyzing this codebase, always consider:
1. The relationship between template files (*.j2) and the Python code that renders them
2. How this project dogfoods its own generated workflows
3. The dual impact of changes (affects both template generation and this project's usage)
4. Template variable usage and how they're substituted during generation
5. Patterns that appear in both templates and this project's own files

Parameters:
- **focus_description**: The full context above including project context and user request
- **directories**: Optional - specific directories to analyze (comma-separated)
- **file_patterns**: Optional - file patterns to include (e.g., "*.py,*.j2,*.yml")
- **exclude_patterns**: Optional - patterns to exclude (e.g., "*/tests/*,*/build/*")

Example usage:
- `/gemini-analyze How is version management implemented across templates and code?`
- `/gemini-analyze Find all places where requirements.txt is referenced`
- `/gemini-analyze Identify inconsistencies between templates and dogfooding workflows`
