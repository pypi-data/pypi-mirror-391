Use the `mcp__gemini-workflow__create_specification_with_gemini` tool with the following feature description:

**PROJECT CONTEXT:**
This is pypi-workflow-generator - a Python tool that creates CI/CD workflow templates (Jinja2 *.j2 files) for other Python PyPI projects. It generates GitHub Actions workflows, pyproject.toml configurations, and release automation for downstream users.

**Key Project Characteristics:**
- Template files: hitoshura25_pypi_workflow_generator/*.j2 (generates workflows for other projects)
- Dogfooding: This project uses its own generated workflows in .github/workflows/
- Dual impact: Changes affect BOTH template files AND this project's own implementation
- Template propagation: Template changes affect all downstream users who generate workflows
- Build system: Uses setuptools-scm for versioning, pyproject.toml-based packaging

**USER REQUEST:**
{ARGUMENTS}

**Analysis Instructions for Gemini:**
1. Identify all affected *.j2 template files that generate code for downstream projects
2. Identify this project's own workflow files that need changes (dogfooding)
3. Check for references in MANIFEST.in, README.md, documentation, and specs/
4. Consider both the generation logic (Python code) and generated outputs (templates)
5. Create implementation tasks for BOTH template updates AND this project's dogfooding
6. Ensure changes work for both generated projects and this project itself

Set output_path to: specs/{sanitized-feature-name}.md

Parameters:
- **feature_description**: The full context above including project context and user request
- **context_id**: Optional - reuse cached context from previous analysis
- **spec_template**: Optional - specific template format to use
- **output_path**: Will be set to specs/ directory

Example usage:
- `/gemini-spec Consolidate dependency management to pyproject.toml`
- `/gemini-spec Update Python version pinning strategy`
